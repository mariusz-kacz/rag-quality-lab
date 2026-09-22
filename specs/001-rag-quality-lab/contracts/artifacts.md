# Artifact Contract: RAG Quality Lab

Artifacts are machine-readable files written by the CLI. JSON is the default contract format for traces, corpus summaries, and ingestion summaries.

## Trace Artifact

**Path Pattern**

`artifacts/traces/<trace_id>.json`

**Required Top-Level Fields**

- `schema_version`
- `trace_id`
- `created_at`
- `question`
- `retrieval_mode`
- `route_decision`
- `retrieval_results`
- `context_build`
- `answer_result`
- `citation_validation`
- `model_usage`

**Required Diagnostics**

- evaluation traces retain `question.question_id`; ad hoc traces may use `null`
- `route_decision` is `null` for baseline retrieval, which bypasses the router
- routed traces include category scores for all five categories, the router threshold, and the fallback flag
- ranked retrieved chunks
- estimated tokens per retrieved chunk
- included chunks
- excluded chunks with reasons
- final estimated context size
- output token limit
- actual input/output/total token usage when available

## Corpus Summary Artifact

**Required Top-Level Fields**

- `schema_version`
- `source_count`
- `categories`
- `license_summary`
- `pinned_version`
- `sources`
- `validation_errors`

## Ingestion Summary Artifact

**Required Top-Level Fields**

- `schema_version`
- `collection`
- `source_count`
- `chunk_count`
- `category_counts`
- `embedding_model`
- `ingested_chunks`
- `validation_errors`
