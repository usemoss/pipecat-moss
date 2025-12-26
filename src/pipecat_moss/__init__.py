"""Moss vector database integration for Pipecat."""

from __future__ import annotations

from inferedge_moss import (
    AddDocumentsOptions,
    DocumentInfo,
    GetDocumentsOptions,
    IndexInfo,
    MossClient,
    SearchResult,
)
from .retrieval import MossRetrievalService

__all__ = [
    "AddDocumentsOptions",
    "DocumentInfo",
    "GetDocumentsOptions",
    "IndexInfo",
    "MossClient",
    "MossRetrievalService",
    "SearchResult",
]
