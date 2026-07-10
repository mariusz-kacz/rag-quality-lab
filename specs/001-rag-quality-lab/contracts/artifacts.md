# Artifact Contract: RAG Quality Lab

Artifacts are machine-readable files written by the CLI. JSON is the default contract format for traces, evaluation runs, corpus summaries, and ingestion summaries.

## Trace Artifact

**Path Pattern**

`artifacts/traces/<trace_id>.json`

**Required Top-Level Fields**

- `schema_version`
- `benchmark_scope`
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
- `metric_counts`
- `questions`
- `trace_paths`

**Required Metrics**

- `routing_accuracy`
- `fallback_rate`
- `hit_rate_at_k`
- `mrr`
- `citation_source_match`
- `no_answer_accuracy`
- `average_context_tokens`
- `average_included_chunks`

Rate metrics should include raw numerator and denominator values in `metric_counts`. Metrics that are not applicable for a mode must be present with `null` and a reason in the Markdown report. `routing_accuracy` is not applicable for `baseline-vector` because baseline retrieval does not use route filtering.

## Markdown Evaluation Report

**Path Pattern**

`artifacts/eval/<run_id>.md`

**Required Sections**

- Run summary
- Retrieval mode and configuration
- Aggregate metrics
- Per-question table
- Request-response pairs
- Token-budget diagnostics
- No-answer cases
- Citation validation failures
- Limitations and interpretation notes

The report must identify the small, manually curated benchmark scope and render counts alongside percentages for rate metrics where a numerator and denominator are available.

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
