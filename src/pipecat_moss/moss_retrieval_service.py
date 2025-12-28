#
# Copyright (c) 20242025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

"""Retrieval service manager for Moss vector indexes."""

from __future__ import annotations

from inferedge_moss import MossClient
from loguru import logger

from .moss_index_processor import MossIndexProcessor

__all__ = ["MossRetrievalService"]


class MossRetrievalService:
    """Retrieval service manager for Moss vector indexes."""

    def __init__(
        self,
        *,
        project_id: str | None = None,
        project_key: str | None = None,
        top_k: int = 5,
        alpha: float = 0.8,
        system_prompt: str = "Here is additional context retrieved from database:\n\n",
        **kwargs,
    ):
        """Store shared client and default retrieval settings."""
        self._client = MossClient(project_id=project_id, project_key=project_key)
        self._defaults = {
            "top_k": top_k,
            "alpha": alpha,
            "system_prompt": system_prompt,
            **kwargs,
        }
        logger.info(f"Initialized MossRetrievalService for project: {project_id}")

    async def load_index(self, index_name: str):
        """Explicitly load an index before using the pipeline."""
        try:
            logger.info(f"Loading index: {index_name}")
            await self._client.load_index(index_name)
            logger.info(f"Index loaded: {index_name}")
        except Exception as exc:  # pragma: no cover - pass-through
            logger.error(f"Failed to load index {index_name}: {exc}")
            raise exc

    def query(self, index_name: str, **kwargs) -> MossIndexProcessor:
        """Create a pipeline processor for a specific Moss index."""
        config = self._defaults.copy()
        config.update(kwargs)

        return MossIndexProcessor(
            client=self._client,
            index_name=index_name,
            **config,
        )
