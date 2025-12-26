# Pipecat Moss Integration

Moss delivers sub-10ms semantic retrieval, ensuring your Pipecat AI voice agents respond naturally without noticeable delays.

## Installation

Install the package

```bash
pip install pipecat-moss
```

## Prerequisites
- Moss project ID and project key (get them from [Moss Portal](https://portal.usemoss.dev))
- Deepgram, OpenAI, Cartesia API keys (to run the example)



## Usage with Pipecat Pipeline

Pipecat-Moss integrates seamlessly into a Pipecat pipeline, enabling efficient retrieval-based operations. It leverages Pipecat's modular architecture to inject semantic context for Voice AI Agents.

```python
import os
from inferedge_moss import MossClient
from pipecat_moss.retrieval import MossRetrievalService

moss_retrieval = MossRetrievalService(
    index_name=os.getenv("MOSS_INDEX_NAME"),
    top_k=top_k,
    system_prompt="Relevant passages from the Moss knowledge base:\n\n",
    max_documents=top_k,
    project_id=os.getenv("MOSS_PROJECT_ID"),
    project_key=os.getenv("MOSS_PROJECT_KEY"),
)

pipeline = Pipeline([
    transport.input(),               # audio/user input
    stt,                             # speech to text
    context_aggregator.user(),       # add user text to context
    retrieval_service,               # Moss retrieval service
    llm,                             # LLM generates response
    tts,                             # TTS synthesis
    transport.output(),              # stream audio back to user
    context_aggregator.assistant(),  # store assistant response
])
```

See `examples/moss-retrieval-demo.py` for a complete working example.

## Pipecat Compatibility

Tested with Pipecat v0.0.94. Please upgrade to this version (or newer) to ensure API compatibility with the snippets below.

## Running the Example

### Install dependencies:

To set up the development environment with all dependencies for running examples:

```bash
uv sync
```

### Setup Environment Variables
Create a `.env` file in the root directory with the following content:

```env
MOSS_PROJECT_ID= Your Moss Project ID
MOSS_PROJECT_KEY= Your Moss Project Key
MOSS_INDEX_NAME= Your Moss Index Name

DEEPGRAM_API_KEY= Your DEEPGRAM API KEY
CARTESIA_API_KEY= Your CARTESIA API KEY
OPENAI_API_KEY= Your OpenAI Key
```

Or pass them directly when creating the MossRetrievalService.

### Creating a Moss Index (One-time Setup)

Before using Moss in your pipeline, you need to create an index and populate it with documents:

```bash
python examples/moss-CreateIndex-demo.py
```

### Run the example:

```bash
python examples/moss-retrieval-demo.py
```

## Configuration Options

### MossRetrievalService

- `index_name` (required): Name of your Moss index
- `project_id` (required): Moss project ID (can use env var `MOSS_PROJECT_ID`)
- `project_key` (required): Moss project key (can use env var `MOSS_PROJECT_KEY`)
- `top_k` (default: 5): Number of documents to retrieve per query
- `alpha` (default: 0.8): Blends semantic and keyword search results (0.0 = keyword only, 1.0 = semantic only)
- `system_prompt` (default: "Here is additional context retrieved from memory:\n\n"): Prefix for retrieved documents
- `add_as_system_message` (default: True): Whether to add retrieved docs as a system message (vs user message)
- `deduplicate_queries` (default: True): Skip retrieval if the query hasn't changed
- `max_document_chars` (default: 2000): Maximum characters per document (longer documents are truncated)

## License

This integration is provided under a permissive open source license (BSD-2 or equivalent).

## Support

- [Moss Docs](https://docs.usemoss.dev)
- [Moss Discord](https://discord.com/invite/eMXExuafBR)
- [Pipecat Docs](https://docs.pipecat.ai)
