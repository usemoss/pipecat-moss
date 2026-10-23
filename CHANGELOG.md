# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-10-22

### Changed

- Depend on `moss>=1.20.0` instead of `inferedge-moss`; import from `moss`.
- Require `pipecat-ai>=1.8,<2` and Python 3.11+.
- `MossIndexProcessor` handles `LLMContextFrame` only and forwards the original frame, keeping fields such as `speculation`.
- Queries pass `QueryOptions(top_k, alpha)`.
- `MossRetrievalService` falls back to `MOSS_PROJECT_ID` / `MOSS_PROJECT_KEY` env vars.

### Removed

- `LLMMessagesFrame` and `OpenAILLMContextFrame` handling (removed in pipecat 1.8).
- `AddDocumentsOptions` re-export (gone from the Moss SDK; use `MutationOptions`).

## [0.0.2] - 2026-01-18

### Added

- Support for Pipecat v0.0.99.
- Support for LLMContext and LLMContextAggregatorPair
- removed deprecated OpenAILLMContext and OpenAILLMContextAggregatorPair

## [0.0.1] - 2025-12-29

### Added

- Initial release of `pipecat-moss` integration.
- `MossRetrievalService` for augmenting Pipecat LLM contexts with retrieved documents
- Example `moss-retrieval-demo.py` demonstrating a full voice pipeline with retrieval.
- `moss-create-index-demo.py` for creating and populating a Moss index.