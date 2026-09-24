# Quickstart: RAG Quality Lab

This guide validates the MVP end to end from corpus inspection through ingestion, single-query tracing.

## Prerequisites

- Python 3.12 installed.
- A reachable Qdrant instance.
- Azure OpenAI deployments for embeddings and LangChain-backed answer generation.
- Environment variables configured for Azure OpenAI and Qdrant.
- Curated corpus files present under `corpus/`.
- Golden question set present at `golden/questions.json`.

## Environment

Expected environment variables:

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

`QDRANT_API_KEY` may be empty for a local unauthenticated Qdrant instance.

## 1. Inspect the Corpus

```powershell
raglab corpus inspect
raglab corpus inspect --json
```

Expected outcome:

- Selected source pages are reported. The documented MVP target is 15-30 source pages, but ingestion should not fail solely because a structurally valid manifest is outside that range.
- Exactly five categories are present.
- Every source has slug, category, URL, license metadata, pinned version or commit, and local reference.
- Missing metadata or local files fail before ingestion.

## 2. Ingest into Qdrant

```powershell
raglab corpus ingest --collection rag_quality_lab --recreate
```

Expected outcome:

- Corpus metadata validates.
- Chunks are created with stable IDs and content hashes.
- Embeddings are created through Azure OpenAI.
- Chunks are written to Qdrant with category and provenance payloads.

## 3. Run an Answerable Query

```powershell
raglab query "How does retrieval augmented generation help with context grounding?" --mode routed-vector --top-k 5 --max-context-tokens 1000 --output-token-limit 500
```

Expected outcome:

- The query is routed to a category or falls back to all categories.
- Retrieved chunks are ranked.
- Context inclusion and exclusion decisions are printed or available in the trace.
- The answer includes citations that validate against selected context.
- A trace file is written under `artifacts/traces/`.

## 4. Run a No-Answer Query

```powershell
raglab query "What warranty does the project provide for enterprise production deployment?" --mode routed-vector
```

Expected outcome:

- The system returns an explicit no-answer response when retrieved evidence is insufficient.
- The trace shows retrieved evidence and the no-answer decision.

## 5. Inspect a Trace

```powershell
raglab trace inspect artifacts/traces/<trace_id>.json
```

Expected outcome:

- Routed queries show the route decision; baseline queries show routing as not applicable. Retrieval results, context budget, citations, validation result, and model usage when available are visible in both modes.

## Future Extension: Hybrid Retrieval

Hybrid lexical/vector retrieval is intentionally outside the MVP workflow. It may be added later if exact-term matching, BM25, or rank fusion becomes relevant to retrieval-quality experiments, but the current lab scope is limited to comparing `baseline-vector` and `routed-vector`.

## Validation References

- CLI behavior is defined in `specs/001-rag-quality-lab/contracts/cli.md`.
- Artifact schemas are defined in `specs/001-rag-quality-lab/contracts/artifacts.md`.
- Entities and validation rules are defined in `specs/001-rag-quality-lab/data-model.md`.
