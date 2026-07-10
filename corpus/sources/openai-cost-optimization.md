# Source snapshot

Source metadata:
- source_slug: openai-cost-optimization
- category: LLM settings, cost, and tokens
- upstream_url: https://developers.openai.com/api/docs/guides/cost-optimization
- source_markdown: https://developers.openai.com/api/docs/guides/cost-optimization.md
- license: OpenAI API docs reuse terms pending snapshot verification
- pinned_version: openai-api-docs@current-snapshot-2026-07-10
- snapshot_captured: 2026-07-10
- snapshot_type: normalized documentation digest from OpenAI API documentation page
- normalization: removed page chrome and navigation; retained cost-latency relationship, request reduction, token minimization, model selection, Batch API, flex processing, and RAG/evaluation workload implications

---
# Cost and latency reduction levers

The OpenAI cost optimization guide frames cost and latency as related operational concerns. Reducing unnecessary requests and tokens usually lowers both billable usage and time spent processing a request. For LLM applications, the durable cost levers are:

- reduce the number of model requests needed to complete a task;
- minimize input tokens by trimming prompts, history, and retrieved context;
- optimize for shorter model outputs when the product requirement allows it;
- select a smaller model when it preserves enough accuracy for the task.

These levers should be measured together. A smaller model may be less expensive and faster for routing, query rewriting, extraction, or simple classification. A larger model may still be justified for final answer synthesis, multi-document reasoning, or high-risk user-visible output. The cost decision should therefore be tied to stage-level quality evaluation, not only unit price.

## Reduce requests

Request count matters because every model call has overhead and can consume rate-limit budget. Multi-step RAG pipelines often accumulate model requests for routing, query rewriting, retrieval-needed classification, answer generation, citation checking, and evaluation. Some steps can be combined when they share the same inputs and produce compact structured output.

For example, a retrieval preparation step can produce both a rewritten standalone query and a boolean retrieval decision in one response. This reduces serial latency and request count. The same idea applies to small evaluator calls: several independent labels can sometimes be returned as one structured object when the model context and output schema remain manageable.

Request reduction should not hide distinct failure modes. If combining tasks makes routing less reliable or makes trace analysis harder, the saved request may not be worth the quality loss. Keep stage-level telemetry so cost optimizations can be evaluated against answer quality and retrieval behavior.

## Minimize tokens

Token minimization applies to both input and output. Input tokens include developer instructions, conversation state, retrieved chunks, source identifiers, schemas, tool definitions, and any few-shot examples. Output tokens include the answer, citations, reasoning-like explanation requested by the application, and structured fields.

In RAG systems, the highest-impact input-token controls are usually context selection and prompt layout:

- include only chunks that fit the evidence need and token budget;
- remove boilerplate, navigation, duplicated headings, and irrelevant retrieved text;
- avoid sending long history when a short contextualized query is enough;
- keep stable instructions and schemas compact but clear;
- reserve output budget explicitly so the model has room to answer.

Output-token controls should match the product contract. A short cited answer, a fixed JSON schema, or a small classification label can use a much lower output limit than an exploratory explanation. Over-large output reservations can increase rate-limit pressure and cost planning even when the model later emits fewer tokens.

## Select a smaller model

The guide recommends choosing models that balance lower cost and latency with maintained accuracy. In a RAG quality lab, model choice is not a single global setting. Different stages can have different requirements:

- small or cheaper models for deterministic-looking classification, route selection, query rewriting, or simple extraction;
- stronger models for answer synthesis from multiple chunks, nuanced no-answer decisions, or final user-visible wording;
- specialized or fine-tuned models for repeated narrow tasks when evaluation shows stable quality.

Model substitutions should be recorded in traces. A retrieval pipeline can look worse because the generator changed, even when retrieval is unchanged. Store the model name, prompt version, output-token limit, and context budget with each run so cost comparisons do not obscure quality regressions.

# Batch, flex processing, model choice, and token minimization

The cost guide points to asynchronous and lower-priority processing options for workloads that do not require immediate synchronous responses. These are especially relevant for corpus generation, offline evaluation, data enrichment, and repeated benchmark runs.

## Batch API

The Batch API is designed for asynchronous jobs. A client collects requests into a file, starts a batch job, checks status while it runs, and retrieves results after completion. This pattern is appropriate when throughput and cost matter more than immediate user-facing latency.

For this project, Batch-style processing maps to:

- running large golden-set or regression evaluations;
- scoring many retrieved-answer pairs with evaluator models;
- generating synthetic test candidates;
- enriching or classifying corpus metadata;
- rerunning non-interactive experiments after prompt or retrieval changes.

Batch processing should still preserve per-example identifiers. Each request should include enough metadata to map outputs back to the question, retrieval mode, corpus version, prompt version, and expected category. Without that mapping, lower cost comes at the expense of reproducibility.

## Flex processing

Flex processing offers lower costs for Chat Completions or Responses requests in exchange for slower response times and occasional resource unavailability. The guide positions it for non-production or lower-priority tasks such as model evaluations, data enrichment, and asynchronous workloads.

This makes flex processing a good fit for offline RAG evaluation runs when deadlines are loose and retry/resume behavior is already present. It is a poor default for interactive answer generation unless the user experience explicitly tolerates slower or occasionally unavailable responses.

## Practical cost trace fields

Cost optimization becomes actionable when traces include enough usage fields to explain the bill:

- model and API surface;
- prompt template version;
- input token estimate and API-reported input tokens when available;
- cached input tokens and cache-write tokens when available;
- output-token limit and actual output tokens;
- number of model requests per user question or evaluation item;
- whether the request used synchronous, batch, or flex processing;
- retry count and rate-limit behavior.

For RAG workloads, cost should be interpreted with quality metrics. A cheaper configuration that trims away relevant evidence, drops citations, or increases unsupported answers is not an improvement. A good cost optimization reduces waste while preserving enough retrieval and answer quality for the target task.
