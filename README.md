# RAG Quality Lab

RAG Quality Lab is a CLI-first Python project for inspecting retrieval-augmented generation quality. It keeps the corpus, golden questions, retrieval decisions, context budgets, citations, traces, and evaluation reports reviewable and reproducible.

The lab uses a curated local corpus, Azure AI Foundry models through an OpenAI-compatible project endpoint, and Qdrant for vector storage. It supports two retrieval modes:

- `baseline-vector`: searches the full collection.
- `routed-vector`: deterministically routes the question across five knowledge categories, then applies a category filter when routing confidence is high enough.

## Repository Map

- `src/rag_quality_lab/`: CLI, configuration, providers, retrieval, RAG, and evaluation code.
- `corpus/manifest.json`: provenance and local snapshot references for the curated corpus.
- `corpus/sources/`: 26 pinned Markdown source snapshots.
- `corpus/categories.json`: the five routing categories.
- `golden/questions.json`: answerable, no-answer, and boundary cases used by evaluation.
- `artifacts/traces/`: query traces.
- `artifacts/eval/`: evaluation JSON, Markdown reports, and evaluation traces.
- `tests/`: unit, contract, and integration tests.

## Prerequisites

- Python 3.12 or newer.
- [uv](https://docs.astral.sh/uv/).
- Docker or another way to run Qdrant at an HTTP URL.
- An Azure AI Foundry project with an OpenAI-compatible project endpoint, an embedding model deployment, and a chat model deployment that supports the Responses API.
- Either a Foundry API key or credentials available to `DefaultAzureCredential`.

## Quickstart

The following workflow was verified against the current CLI, a local Qdrant container, `text-embedding-3-small`, and a Foundry chat model.

1. Install the locked dependencies:

```console
uv sync
```

2. Start Qdrant:

```console
docker run --name rag-quality-lab-qdrant --rm -d -p 6333:6333 qdrant/qdrant
```

If Qdrant is already available at the URL you plan to configure, reuse that instance instead.

3. Create the local environment file.

Bash:

```bash
cp .env.example .env.local
```

PowerShell:

```powershell
Copy-Item .env.example .env.local
```

Edit `.env.local` with your Foundry endpoint and model deployment names:

```dotenv
FOUNDRY_OPENAI_BASE_URL=https://your-project.services.ai.azure.com/api/projects/your-project/openai/v1
FOUNDRY_API_KEY=
FOUNDRY_EMBEDDING_MODEL=text-embedding-3-small
FOUNDRY_CHAT_MODEL=gpt-4o-mini
FOUNDRY_REASONING_EFFORT=

QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
RAGLAB_QDRANT_COLLECTION=rag_quality_lab

RAGLAB_ROUTER_CATEGORY_MARGIN=0.15
```

Leave `FOUNDRY_API_KEY` empty to use `DefaultAzureCredential`; otherwise set the project API key. Leave `QDRANT_API_KEY` empty for the local container. Set `FOUNDRY_REASONING_EFFORT` only when the configured chat deployment supports that Responses API option.

4. Inspect and ingest the corpus:

```console
uv run raglab --env-file .env.local corpus inspect
uv run raglab --env-file .env.local corpus ingest
```

Ingestion validates the manifest and snapshots, deterministically creates chunks, embeds them, creates the configured Qdrant collection if needed, and upserts the vectors. Add `--recreate` to replace an existing collection before ingestion.

5. Run a routed query:

```console
uv run raglab --env-file .env.local query "Why should retrieved context be treated as data rather than instructions?" --mode routed-vector --top-k 3 --max-context-tokens 1000 --output-token-limit 500
```

The command prints the answer and citations, then writes a trace to `artifacts/traces/trace-<id>.json`.

6. Run the golden-set evaluation:

```console
uv run raglab --env-file .env.local eval run --mode routed-vector
```

This evaluates all questions in `golden/questions.json` and writes:

- `artifacts/eval/eval-routed-vector.json`
- `artifacts/eval/eval-routed-vector.md`
- per-question traces under `artifacts/eval/traces/routed-vector/`

Stop the quickstart Qdrant container when finished:

```console
docker stop rag-quality-lab-qdrant
```

## Configuration

`.env.local` is intentionally ignored by Git and is not loaded automatically. Pass it through the global `--env-file` option before the command name:

```console
uv run raglab --env-file .env.local <command>
```

Variables already present in the process environment take precedence over values in the file. The loader accepts blank lines, comments, quoted values, and optional `export` prefixes.

| Variable | Required | Purpose |
| --- | --- | --- |
| `FOUNDRY_OPENAI_BASE_URL` | Live model commands | Foundry project OpenAI v1 base URL. Endpoint suffixes such as `/responses` are normalized away. |
| `FOUNDRY_API_KEY` | No | Foundry project key. When empty, the provider obtains an Entra ID token through `DefaultAzureCredential`. |
| `FOUNDRY_EMBEDDING_MODEL` | Ingest, query, evaluation | Embedding model deployment name passed as the OpenAI `model`. |
| `FOUNDRY_CHAT_MODEL` | Query, evaluation | Chat model deployment name passed to the OpenAI Responses API. |
| `FOUNDRY_REASONING_EFFORT` | No | Optional reasoning effort forwarded to the Responses API. |
| `QDRANT_URL` | Ingest, query, evaluation | Qdrant HTTP URL. |
| `QDRANT_API_KEY` | No | Qdrant API key for a secured or hosted instance. |
| `RAGLAB_QDRANT_COLLECTION` | Ingest, query, evaluation | Collection used by the query pipeline and by ingestion unless `--collection` overrides it. |
| `RAGLAB_ROUTER_CATEGORY_MARGIN` | No | Includes categories whose score is within this margin of the winning route; default `0.15`. |

Model values are deployment identifiers, not separate Azure OpenAI deployment variables. The implementation uses the OpenAI Python SDK against the configured Foundry project base URL for both embeddings and Responses API generation.

## CLI Reference

Inspect the available commands and global options:

```console
uv run raglab --help
uv run raglab <command> --help
```

Inspect the local corpus without calling Foundry or Qdrant:

```console
uv run raglab corpus inspect
uv run raglab corpus inspect --json
```

Ingest into the collection from `.env.local`, override that collection, or rebuild it:

```console
uv run raglab --env-file .env.local corpus ingest
uv run raglab --env-file .env.local corpus ingest --collection another_collection
uv run raglab --env-file .env.local corpus ingest --recreate
```

Run a query in either supported retrieval mode:

```console
uv run raglab --env-file .env.local query "How does RAG ground an answer?" --mode baseline-vector
uv run raglab --env-file .env.local query "How does RAG ground an answer?" --mode routed-vector --json
```

Query defaults are `--top-k 3`, `--max-context-tokens 1000`, `--output-token-limit 500`, and `--trace-dir artifacts/traces`.

Inspect a saved trace:

```console
uv run raglab trace inspect artifacts/traces/<trace-id>.json
uv run raglab trace inspect artifacts/traces/<trace-id>.json --json
```

Evaluate one mode, then compare baseline and routed artifacts:

```console
uv run raglab --env-file .env.local eval run --mode baseline-vector
uv run raglab --env-file .env.local eval run --mode routed-vector
uv run raglab eval compare artifacts/eval/eval-baseline-vector.json artifacts/eval/eval-routed-vector.json --markdown artifacts/eval/comparison.md
```

Evaluation defaults are `--golden golden/questions.json`, `--artifacts-dir artifacts/eval`, `--top-k 3`, `--max-context-tokens 1000`, and `--output-token-limit 800`. Commands with `--json` emit machine-readable output; note that ingestion JSON includes every ingested chunk and can be large.

## Implementation

The runtime path is deliberately small and inspectable:

```text
local corpus snapshots
  -> validate and chunk
  -> Foundry OpenAI-compatible embeddings
  -> Qdrant cosine-vector collection

question
  -> deterministic embedding-based category routing
  -> baseline or category-filtered Qdrant retrieval
  -> bounded context assembly
  -> Foundry Responses API answer generation
  -> citation validation and persisted trace

golden questions
  -> traced query pipeline per retrieval mode
  -> retrieval, routing, citation, no-answer, and budget metrics
  -> JSON and Markdown reports
```

Provider integration is project-owned. The OpenAI SDK handles Foundry embeddings and Responses calls; `langchain-core` supplies prompt and message types used by generation. The project does not use the older Azure-specific environment variables or a `langchain-openai` Azure chat-model client.

Routed retrieval falls back to all categories when its top category score is below the configured confidence threshold. Context assembly admits retrieved chunks in rank order while they fit the token budget. Generation must cite selected chunks, and citation validation checks that every returned citation maps to included context. This is a context-membership check, not a claim-level factuality judge.

Evaluation reports include routing accuracy, fallback rate, recall at k, MRR, citation source match, no-answer accuracy, average context tokens, and average included chunks. These are lightweight regression signals over the checked-in golden set, not a comprehensive benchmark.

## Development

Run the full test suite:

```console
uv run pytest
```

The unit and integration tests use local fakes at external-service boundaries, so the test suite does not require live Foundry credentials or Qdrant.

## Scope

This is a portfolio-quality engineering lab, not a production RAG platform. It intentionally excludes a web UI, agent loop, live crawling, alternate providers, alternate vector stores, reranking, production authentication, and claim-level answer grading. The narrow scope keeps retrieval behavior, evidence selection, token budgets, citations, and evaluation artifacts easy to inspect.
