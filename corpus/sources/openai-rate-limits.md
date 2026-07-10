# Source snapshot

Source metadata:
- source_slug: openai-rate-limits
- category: LLM settings, cost, and tokens
- upstream_url: https://developers.openai.com/api/docs/guides/rate-limits
- source_markdown: https://developers.openai.com/api/docs/guides/rate-limits.md
- license: OpenAI API docs reuse terms pending snapshot verification
- pinned_version: openai-api-docs@current-snapshot-2026-07-10
- snapshot_captured: 2026-07-10
- snapshot_type: normalized documentation digest from OpenAI API documentation page
- normalization: removed page chrome, duplicate examples, and long code blocks; retained limit dimensions, usage tiers, shared model limits, response headers, retry guidance, batching, and ingestion/vector-store limits

---
# Rate-limit scope, usage tiers, and limit dimensions

The OpenAI rate limits guide describes rate limits as restrictions on how frequently a user or organization can access API services over a period of time. Limits protect service reliability, prevent abuse, and help allocate capacity fairly across users.

Rate limits are enforced across several dimensions. The exact set depends on model and API surface, but the guide names common dimensions:

- RPM: requests per minute;
- RPD: requests per day;
- TPM: tokens per minute;
- TPD: tokens per day;
- IPM: images per minute;
- audio minutes per minute for some streaming audio models.

A workload can hit whichever limit is exhausted first. A RAG system with many small routing calls may be request-bound. A system that sends long retrieved contexts may be token-bound. A batch ingestion or evaluation job may hit daily or ingestion-specific limits before it exhausts per-minute capacity.

## Usage tiers and model-specific limits

Rate-limit values vary by organization, usage tier, model, and endpoint. Usage tiers can increase as API usage grows and billing history develops, but clients should not assume a universal numeric limit. Applications should treat organization and model limits as configuration or observable account data.

Some models share limits. Falling back from one model to another only helps when the fallback model does not share the constrained budget or when the limiting dimension differs. A fallback strategy must therefore consider quality, cost, latency, and limit grouping together.

For evaluation runs, model-specific limits should be recorded with the run configuration when possible. Otherwise a failed or slow run can be misread as an evaluation-quality issue instead of a capacity or throttling issue.

## Token and request accounting

The guide distinguishes request limits from token limits. If requests per minute are the bottleneck but tokens per minute remain available, batching multiple tasks into a single request can improve throughput. If tokens per minute are the bottleneck, batching can make the problem worse unless the prompts are small and the combined output is controlled.

For RAG, the token-bound case is common because retrieved context can be large. Practical mitigations include:

- lower `top_k` or context budgets;
- trim duplicated or low-value retrieved chunks;
- reduce output-token limits to the answer shape actually needed;
- split offline workloads across time;
- lower concurrency for token-heavy stages.

For request-bound workflows, mitigations include:

- combine adjacent model steps when quality holds;
- batch small independent classification or grading tasks;
- cache deterministic decisions outside the model;
- pace worker concurrency with a shared rate limiter.

# Headers, shared limits, retries, batching, and ingestion limits

The current rate-limit documentation adds operational details that are more useful for production clients than a static retry notebook alone. A robust client should observe response metadata, retry only recoverable failures, and tune concurrency against the actual limiting resource.

## Response headers and observability

API responses can include rate-limit headers that expose useful state such as the applicable limit, remaining capacity, and reset timing. Header names vary by endpoint and limit type, but the operational pattern is stable: log rate-limit metadata alongside model, endpoint, token usage, and request stage.

For a RAG pipeline, rate-limit telemetry should identify where pressure occurs:

- route classification;
- query rewriting;
- embedding or retrieval preparation;
- answer generation;
- evaluator or grading calls;
- batch ingestion or file/vector-store operations.

This separation matters because each stage has different mitigation options. A final-answer generator that is token-bound should usually trim context or lower output budget. A classifier that is request-bound may benefit from batching, deterministic logic, or a smaller model with a different limit pool.

## Retry behavior

The guide recommends exponential backoff with jitter for retryable rate-limit errors. Retrying immediately can consume more of the same constrained budget and increase contention. Bounded retries avoid blocking workers indefinitely and make final failures visible.

Reliable retry behavior includes:

- retry only known transient errors such as selected rate-limit failures;
- add jitter so workers do not retry in synchronized bursts;
- cap total attempts or elapsed time;
- preserve idempotency and request identifiers for batch work;
- record retry count and final error in traces.

For user-facing RAG, retries trade reliability for latency. For offline evaluation, longer waits may be acceptable, but jobs should be resumable and should keep failed examples identifiable for later rerun.

## Batching and asynchronous workloads

The guide recommends the Batch API for large asynchronous request collections that do not require immediate responses. Batch jobs can avoid impacting synchronous request rate limits and are a natural fit for offline evaluation, enrichment, and corpus-scale processing.

For synchronous requests, batching can improve throughput when RPM is constrained and TPM capacity is available. A client can send several small tasks in one request and parse the outputs by schema. Batching should be avoided or used carefully when each task needs a large retrieved context, independent security boundaries, or strict per-user latency.

## File, vector-store, and ingestion limits

Rate limits are not limited to text generation. Retrieval systems may also interact with file uploads, vector stores, embeddings, and ingestion endpoints. These APIs can have their own limits, quotas, and processing constraints.

In a RAG quality lab, ingestion and evaluation should therefore be paced separately:

- corpus ingestion should cap upload and indexing concurrency;
- embedding jobs should monitor token and request limits;
- vector-store updates should handle asynchronous processing and partial failures;
- evaluation should distinguish retrieval/indexing failures from generation failures.

The durable rule is to optimize for the binding limit and make it observable. If the workload is request-bound, reduce or batch requests. If it is token-bound, trim input/output tokens and lower concurrency. If it is ingestion-bound, schedule or shard index work and preserve resumable state.
