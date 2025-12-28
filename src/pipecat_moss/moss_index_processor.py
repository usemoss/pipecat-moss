#
# Copyright (c) 20242025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

"""Pipeline processor that handles retrieval for a specific Moss index."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from inferedge_moss import MossClient, SearchResult
from loguru import logger
from pipecat.frames.frames import ErrorFrame, Frame, LLMContextFrame, LLMMessagesFrame, MetricsFrame
from pipecat.metrics.metrics import ProcessingMetricsData
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContextFrame
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor

__all__ = ["MossIndexProcessor"]


class MossIndexProcessor(FrameProcessor):
    """Pipeline processor that handles retrieval for a specific index."""

    def __init__(
        self,
        client: MossClient,
        index_name: str,
        top_k: int = 5,
        alpha: float = 0.8,
        system_prompt: str = "Here is additional context retrieved from database:\n\n",
        add_as_system_message: bool = True,
        deduplicate_queries: bool = True,
        max_document_chars: int = 2000,
        **kwargs,
    ):
        """Configure processor defaults for the specified index."""
        super().__init__(name=kwargs.get("name", f"MossRetrieval-{index_name}"))
        self._client = client
        self._index_name = index_name
        self._top_k = top_k
        self._alpha = alpha
        self._system_prompt = system_prompt
        self._add_as_system_message = add_as_system_message # If True add retrieved context as system message; else as user message
        self._deduplicate_queries = deduplicate_queries # If True, skip retrieval for repeated queries
        self._max_document_chars = max_document_chars # Max chars per retrieved document
        self._last_query: str | None = None

    def can_generate_metrics(self) -> bool:
        """Signal that this processor emits metrics frames."""
        return True

    async def retrieve_documents(self, query: str) -> SearchResult:
        """Retrieve documents for a given query."""

        # Perform the query against the Moss index
        result = await self._client.query(
            self._index_name,
            query,
            top_k=self._top_k,
            alpha=self._alpha,
        )

        # Emit retrieval latency metrics 
        if self.metrics_enabled:
            time_taken = getattr(result, "time_taken_ms", None)
            if time_taken is None and isinstance(result, dict):
                time_taken = result.get("time_taken_ms")

            # Log and push the time taken metric
            if time_taken is not None:
                logger.info(f"{self}: Retrieval latency: {time_taken}ms")
                await self.push_frame(
                    MetricsFrame(
                        data=[
                            ProcessingMetricsData(
                                processor=self.name,
                                value=time_taken / 1000.0,
                            )
                        ]
                    )
                )
        return result

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        """Process frames to extract queries and augment LLM context."""
        await super().process_frame(frame, direction)

        context = None
        messages = None

        if isinstance(frame, (LLMContextFrame, OpenAILLMContextFrame)):
            context = frame.context
        elif isinstance(frame, LLMMessagesFrame):
            messages = frame.messages
            context = LLMContext(messages)

        if not context:
            await self.push_frame(frame, direction)
            return

        try:
            context_messages = context.get_messages()
            latest_user_message = self._get_latest_user_text(context_messages)

            if latest_user_message and not (
                self._deduplicate_queries and self._last_query == latest_user_message
            ):
                search_result = await self.retrieve_documents(latest_user_message)

                if self._deduplicate_queries:
                    self._last_query = latest_user_message

                documents = getattr(search_result, "docs", []) or []
                if documents:
                    content = self._format_documents(documents)
                    role = "system" if self._add_as_system_message else "user"
                    context.add_message({"role": role, "content": content})

            if messages is not None:
                await self.push_frame(LLMMessagesFrame(context.get_messages()))
            elif isinstance(frame, (LLMContextFrame, OpenAILLMContextFrame)):
                await self.push_frame(type(frame)(context=context))  # type: ignore[arg-type]
            else:
                await self.push_frame(frame)

        except Exception as exc:  # pragma: no cover - defensive logging
            logger.exception(f"{self}: error while running retrieval: {exc}")
            await self.push_error(ErrorFrame(error=f"{self} retrieval error: {exc}"))

    @staticmethod
    def _get_latest_user_text(messages: Sequence[dict[str, Any]]) -> str | None:
        """Extract the latest user message text from a list of messages."""
        for m in reversed(messages):
            if m.get("role") == "user":
                content = m.get("content")
                if isinstance(content, str):
                    return content.strip()
                if isinstance(content, list):
                    return "\n".join(
                        c["text"] for c in content if c.get("type") == "text"
                    ).strip()
        return None

    def _format_documents(self, documents: Sequence[Any]) -> str:
        """Format retrieved documents from Moss into a single string for LLM context."""
        lines = [self._system_prompt.rstrip(), ""]
        for idx, doc in enumerate(documents, start=1):
            meta = doc.metadata or {}
            extras = []

            if source := meta.get("source"):
                extras.append(f"source={source}")
            if (score := getattr(doc, "score", None)) is not None:
                extras.append(f"score={score}")

            suffix = f" ({', '.join(extras)})" if extras else ""
            text = doc.text
            if self._max_document_chars and len(text) > self._max_document_chars:
                text = f"{text[: self._max_document_chars].rstrip()}\u2026"

            lines.append(f"{idx}. {text}{suffix}")
        return "\n".join(lines).strip()
