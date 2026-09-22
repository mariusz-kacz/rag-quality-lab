# RAG Quality Lab

RAG Quality Lab is a CLI-first Python retrieval-quality engineering lab for inspectable and reproducible experiments over a pinned corpus and a small curated benchmark. It keeps the corpus, golden questions, retrieval decisions, context budgets, citations, and traces reviewable and reproducible.

The lab uses a curated local corpus, Azure AI Foundry models through an OpenAI-compatible project endpoint, and Qdrant for vector storage. It supports two retrieval modes:

- `baseline-vector`: searches the full collection.
- `routed-vector`: deterministically routes the question across five knowledge categories, then applies one or more category filters when routing confidence is high enough.

## Repository Map

- `src/rag_quality_lab/`: CLI, configuration, providers, retrieval, RAG, and evaluation code.
- `corpus/manifest.json`: provenance and local snapshot references for the curated corpus.
- `corpus/sources/`: 26 pinned Markdown source snapshots.
- `corpus/categories.json`: the five routing categories.
- `golden/questions.json`: answerable, no-answer, and boundary cases used by evaluation.
- `artifacts/traces/`: query traces.
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
RAGLAB_ROUTER_CONFIDENCE_THRESHOLD=0.18
```

Leave `FOUNDRY_API_KEY` empty to use `DefaultAzureCredential`; otherwise set the project API key. Leave `QDRANT_API_KEY` empty for the local container. Set `FOUNDRY_REASONING_EFFORT` only when the configured chat deployment supports that Responses API option.

4. Inspect and ingest the corpus:

```console
uv run raglab --env-file .env.local corpus inspect
uv run raglab --env-file .env.local corpus ingest
```

Ingestion validates the manifest and snapshots, deterministically creates chunks, embeds them, creates the configured Qdrant collection if needed, and upserts the vectors. Each point stores an index fingerprint covering the complete chunk set and metadata, chunk-size setting, embedding deployment/model, and vector dimensions. Unchanged ingestion is repeatable; an existing point with a different or missing fingerprint blocks the write and directs you to `--recreate`. Use that flag to replace the disposable collection after changing index inputs or when upgrading a collection created without fingerprints.

Ingest into a collection from one process at a time: the fingerprint check and upsert are separate operations, not a concurrency lock. The check runs after embeddings are generated. A model change hidden behind unchanged deployment/model identifiers and dimensions cannot be detected; explicitly rebuild in that case.

5. Run a routed query:

```console
uv run raglab --env-file .env.local query "Why should retrieved context be treated as data rather than instructions?" --mode routed-vector --top-k 3 --max-context-tokens 1000 --output-token-limit 500
```

The command prints the answer and citations, then writes a trace to `artifacts/traces/trace-<id>.json`.

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
| `FOUNDRY_EMBEDDING_MODEL` | Ingest, query | Embedding model deployment name passed as the OpenAI `model`. |
| `FOUNDRY_CHAT_MODEL` | Query | Chat model deployment name passed to the OpenAI Responses API. |
| `FOUNDRY_REASONING_EFFORT` | No | Optional reasoning effort forwarded to the Responses API. |
| `QDRANT_URL` | Ingest, query | Qdrant HTTP URL. |
| `QDRANT_API_KEY` | No | Qdrant API key for a secured or hosted instance. |
| `RAGLAB_QDRANT_COLLECTION` | Ingest, query | Collection used by the query pipeline and by ingestion unless `--collection` overrides it. |
| `RAGLAB_ROUTER_CONFIDENCE_THRESHOLD` | No | Removes category filtering when the top similarity is below this threshold; default `0.18`. |
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

## Evaluation status

The legacy evaluator, commands, reports, and automated tests have been removed.
The benchmark cases and labels remain in `golden/questions.json`. Ragas
configuration and provider adapters are present; the replacement evaluation
workflow and CLI are not yet implemented. See [the evaluation plan](tasks/plan.md).

## Implementation

The runtime path is deliberately small and inspectable:

```text
local corpus snapshots
  -> validate and chunk
  -> Foundry OpenAI-compatible embeddings
  -> Qdrant cosine-vector collection

question
  -> baseline: global Qdrant retrieval (no category routing)
  -> routed: embedding-based category routing -> category-filtered Qdrant retrieval
  -> bounded context assembly
  -> Foundry Responses API answer generation
  -> citation validation and persisted trace

```

Provider integration is project-owned. The OpenAI SDK handles Foundry embeddings and Responses calls; `langchain-core` supplies prompt and message types used by generation. The project does not use the older Azure-specific environment variables or a `langchain-openai` Azure chat-model client.

Responses marked `incomplete` raise a provider error with the completion status and reason, even when partial text contains citations. Partial answers are rejected before citation validation.

Baseline retrieval bypasses the category router and performs one global vector search, so its trace records `route_decision: null`. Routed retrieval computes category scores; broad questions may search several categories through category-margin routing, while a top score below the confidence threshold removes category filtering and searches the full collection. Context assembly admits retrieved chunks in rank order while they fit the token budget. Generation must cite selected chunks, and citation validation checks that every returned citation maps to included context. This is a context-membership check, not a claim-level factuality judge.

The router uses heuristic embedding-similarity thresholds. Similarity scores are not calibrated probabilities, and the configured threshold and category margin are specific to the current embedding model, category descriptions, and benchmark.

Only the complete refusal sentence required by the prompt (`NO_ANSWER_TEXT`) is classified as no-answer, after normalizing case, whitespace, and trailing periods. Alternative refusal wording or a refusal prefix followed by additional text goes through normal answer and citation validation.

## Development

Run the full test suite:

```console
uv run pytest
```

The unit and integration tests use local fakes and the Qdrant client's local mode, so the test suite does not require live Foundry credentials or a Qdrant server. Ingestion regressions cover unchanged retries, incompatible updates, explicit rebuilds in memory, and fingerprint persistence after reopening disk storage. With qdrant-client 1.18.0 on Windows, local disk collection recreation can retain points; rebuild tests therefore use memory, while disk tests verify persistence. The application uses server-backed Qdrant via `QDRANT_URL`.

## Scope

This is a bounded retrieval-quality engineering lab, not a production RAG platform. It intentionally excludes a web UI, agent loop, live crawling, alternate providers, alternate vector stores, reranking, and production authentication. The narrow scope keeps retrieval behavior, evidence selection, token budgets, citations, and traces easy to inspect. Ragas answer-quality evaluation is planned separately.
