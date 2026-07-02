# Artifact Contract: RAG Quality Lab

Artifacts are machine-readable files written by the CLI. JSON is the default contract format for traces, evaluation runs, corpus summaries, and ingestion summaries.

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

- category scores for all five categories
- router threshold and fallback flag
- ranked retrieved chunks
- estimated tokens per retrieved chunk
- included chunks
- excluded chunks with reasons
- final estimated context size
- output token limit
- actual input/output/total token usage when available

## Evaluation Artifact

**Path Pattern**

`artifacts/eval/<run_id>.json`

**Required Top-Level Fields**

- `schema_version`
- `run_id`
- `created_at`
- `retrieval_mode`
- `golden_set_path`
- `configuration`
- `metrics`
- `questions`
- `trace_paths`

**Required Metrics**

- `routing_accuracy`
- `fallback_rate`
- `recall_at_k`
- `mrr`
- `citation_source_match`
- `no_answer_accuracy`
- `average_context_tokens`
- `average_included_chunks`

Metrics that are not applicable for a mode must be present with `null` and a `reason` field in the Markdown report.

## Markdown Evaluation Report

**Path Pattern**

`artifacts/eval/<run_id>.md`

**Required Sections**

- Run summary
- Retrieval mode and configuration
- Aggregate metrics
- Per-question table
- Token-budget diagnostics
- No-answer cases
- Citation validation failures
- Limitations and interpretation notes

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
