# RAG Quality Lab

RAG Quality Lab is a CLI-first Python project for making retrieval-augmented generation quality visible and testable. The goal is not to build another chatbot. The goal is to show the engineering pieces behind a reliable RAG system: curated source provenance, deterministic routing, retrieval modes, context budgeting, citation validation, traces, and lightweight evaluation.

The project is currently in an early implementation stage. The curated corpus, source snapshots, schemas, provider/config boundaries, tests, and planning artifacts are present. The full CLI workflows for corpus ingestion, querying, tracing, and evaluation are specified but still being implemented.

## What Is In This Repo

- `corpus/manifest.json`: curated source manifest with provenance, category, license, pinned version, local snapshot path, and section metadata.
- `corpus/sources/`: normalized local source snapshots for the corpus.
- `corpus/categories.json`: the five routing/evaluation knowledge categories.
- `src/rag_quality_lab/`: Python package scaffold, CLI shell, schemas, configuration, provider wrappers, and category definitions.
- `tests/`: unit, contract, and integration tests for the implemented foundation and planned behavior.
- `specs/001-rag-quality-lab/`: product spec, implementation plan, data model, CLI/artifact contracts, quickstart, and task plan.
- `artifacts/t019-corpus-materials-proposal.md`: rationale for the selected corpus materials.

## Corpus

The corpus is intentionally small and pinned so reviewers can inspect exactly what the system is allowed to know. The MVP target is 15-30 selected source pages: large enough to cover the five categories, but small enough to review manually and embed cheaply. That range is a curation guideline documented here and in the spec, not a hard ingestion invariant. The current corpus contains 27 source snapshots across five categories:

- `prompting techniques`
- `RAG and context handling`
- `RAG evaluation and quality`
- `LLM security and risks`
- `LLM settings, cost, and tokens`

Source families include Microsoft Learn, OpenAI Cookbook/API docs, OWASP Top 10 for LLM Applications, NIST, TREC, Wikipedia, and Hugging Face Evaluate. The local snapshots are normalized Markdown digests, not loose summaries: they preserve source metadata, expected section headings, substantive guidance, examples where useful, and source-specific caveats.

Security coverage includes OWASP pages for prompt injection, sensitive information disclosure, data/model poisoning, excessive agency, and vector/embedding weaknesses, plus the NIST generative AI risk profile.

## Intended Workflow

The planned CLI workflow is:

```powershell
raglab corpus inspect --json
raglab corpus ingest --collection rag_quality_lab --recreate
raglab query "How should a RAG system handle insufficient evidence?" --mode routed-vector
raglab trace inspect artifacts/traces/<trace_id>.json
raglab eval run --mode baseline-vector --golden golden/questions.json
raglab eval run --mode routed-vector --golden golden/questions.json
raglab eval compare artifacts/eval/<baseline>.json artifacts/eval/<routed>.json
```

As of this snapshot, treat the full workflow above as the target described by the spec and tests, not as a finished end-to-end demo.

## Setup

Requirements:

- Python 3.12+
- `uv` or another Python environment manager
- Qdrant for the planned ingestion/retrieval workflow
- Azure OpenAI deployments for embeddings and chat generation

Install dependencies:

```powershell
uv sync
```

Copy and edit environment settings:

```powershell
Copy-Item .env.example .env
```

Expected variables:

```text
AZURE_OPENAI_ENDPOINT
AZURE_OPENAI_API_KEY
AZURE_OPENAI_API_VERSION
AZURE_OPENAI_EMBEDDING_DEPLOYMENT
AZURE_OPENAI_CHAT_DEPLOYMENT
QDRANT_URL
QDRANT_API_KEY
RAGLAB_QDRANT_COLLECTION
```

Run tests:

```powershell
uv run pytest
```

Show the CLI shell:

```powershell
uv run raglab --help
uv run raglab version
```

## Design Notes

The MVP design keeps core RAG logic in plain Python instead of hiding behavior inside a large framework. The planned query path is:

1. Route the question with deterministic category embeddings.
2. Retrieve chunks with either all-corpus vector search or route-filtered vector search.
3. Build a bounded context and record included/excluded chunks.
4. Generate either a cited answer or an explicit no-answer response.
5. Validate citations against chunks actually included in context.
6. Persist a trace with route, retrieval, context, citation, and token-budget details.

Citation validation is deliberately scoped: it proves cited chunks were present in the selected context. It does not prove every generated claim is factually correct.

## Status

Completed or present:

- Python package metadata and CLI shell.
- Environment/configuration handling.
- Azure OpenAI provider wrapper boundary.
- Pydantic schemas for corpus, trace, evaluation, and artifacts.
- Five knowledge categories.
- Curated 27-source corpus and normalized local snapshots.
- Unit/contract/integration tests for the foundation and expected corpus behavior.

Still planned:

- Manifest loading service.
- Corpus inspection and ingestion commands.
- Chunking implementation.
- Qdrant store integration.
- Query pipeline, citation validation, and trace persistence.
- Golden question set and evaluation reports.
- Final sample artifacts.

See [tasks.md](specs/001-rag-quality-lab/tasks.md) for the current implementation checklist and [quickstart.md](specs/001-rag-quality-lab/quickstart.md) for the intended end-to-end workflow.

## Scope Boundaries

This is a portfolio-quality lab, not a production RAG platform. The MVP explicitly excludes a web UI, chatbot conversation state, LangGraph or agent frameworks, multi-corpus ingestion, multiple vector stores, multiple model providers, reranking, production deployment, user authentication, full internet crawling, and large evaluation frameworks.
