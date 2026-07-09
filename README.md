# RAG Quality Lab

RAG Quality Lab is a CLI-first Python project for making retrieval-augmented generation quality visible, reproducible, and reviewable. It is not a chatbot, agent framework, generic crawler, or production RAG platform. The project is a focused lab that exposes the engineering controls behind a RAG workflow: curated source provenance, deterministic category routing, vector retrieval, bounded context selection, cited answer generation, citation validation, persisted traces, and golden-set evaluation.

The repository is designed so a reviewer can inspect both the inputs and the outputs. Corpus snapshots live in the repo, Qdrant stores retrievable chunks at runtime, query traces are written as JSON, and evaluation runs produce comparable JSON and Markdown artifacts.

## Repository Map

- `src/rag_quality_lab/`: Typer CLI, configuration, provider boundaries, corpus, routing, retrieval, RAG, evaluation, and shared schema modules.
- `corpus/manifest.json`: curated corpus manifest with source slug, category, URL, license metadata, pinned version, local snapshot path, and section metadata.
- `corpus/categories.json`: the five knowledge categories used by routing and evaluation.
- `corpus/sources/`: normalized local Markdown snapshots for the pinned corpus.
- `golden/questions.json`: golden questions used to compare retrieval strategies.
- `artifacts/traces/`: default location for persisted query traces.
- `artifacts/eval/`: default location for evaluation JSON and Markdown reports.
- `specs/001-rag-quality-lab/`: feature spec, implementation plan, data model, contracts, quickstart, and task plan.
- `tests/`: unit, contract, and integration tests for the CLI contracts and domain behavior.

## Architecture

The application keeps orchestration in plain Python and uses external systems only at narrow boundaries:

- `rag_quality_lab.cli`: Typer command surface for corpus inspection, ingestion, single-query runs, trace inspection, evaluation runs, and evaluation comparison.
- `rag_quality_lab.config`: environment-driven runtime configuration for Azure OpenAI, Qdrant, retrieval limits, context budgets, and artifact paths.
- `rag_quality_lab.providers` and `rag_quality_lab.chat_models`: Azure OpenAI embedding and LangChain Azure chat-model boundaries.
- `rag_quality_lab.corpus`: manifest validation, corpus inspection, deterministic chunking, and ingestion orchestration.
- `rag_quality_lab.routing`: deterministic embedding-based category routing with fallback to all categories when confidence is too low.
- `rag_quality_lab.retrieval`: supported retrieval modes and Qdrant-backed vector search.
- `rag_quality_lab.rag`: context budgeting, answer generation, citation validation, query pipeline orchestration, and trace persistence.
- `rag_quality_lab.eval`: golden question validation, metric calculation, evaluation artifacts, Markdown reports, and comparison tables.
- `rag_quality_lab.schemas`: Pydantic schemas for corpus, retrieval, query traces, evaluations, and machine-readable artifacts.

The main runtime path is:

```text
corpus manifest + local snapshots
  -> inspect
  -> chunk
  -> embed with Azure OpenAI
  -> write vectors and payloads to Qdrant

question
  -> route across five category descriptions
  -> retrieve with baseline-vector or routed-vector
  -> build bounded context
  -> generate cited answer or explicit no-answer
  -> validate citations against selected context
  -> persist trace JSON

golden questions
  -> run the query pipeline per retrieval mode
  -> compute routing, retrieval, citation, no-answer, and budget metrics
  -> write JSON and Markdown evaluation artifacts
```

## CLI Workflow

Install dependencies:

```powershell
uv sync
```

Copy the example environment file and fill in Azure OpenAI and Qdrant settings:

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

Inspect the CLI:

```powershell
uv run raglab --help
uv run raglab version
```

Run the local test suite:

```powershell
uv run pytest
```

Inspect the curated corpus before writing anything to Qdrant:

```powershell
uv run raglab corpus inspect
uv run raglab corpus inspect --json
```

Ingest validated chunks into Qdrant:

```powershell
uv run raglab corpus ingest --collection rag_quality_lab --recreate
uv run raglab corpus ingest --collection rag_quality_lab --recreate --json
```

Run one traced query:

```powershell
uv run raglab query "How does retrieval augmented generation help with context grounding?" --mode routed-vector --top-k 6 --max-context-tokens 2500 --output-token-limit 500
```

Inspect a persisted trace:

```powershell
uv run raglab trace inspect artifacts/traces/<trace_id>.json
uv run raglab trace inspect artifacts/traces/<trace_id>.json --json
```

Run and compare retrieval evaluations:

```powershell
uv run raglab eval run --mode baseline-vector --golden golden/questions.json --artifacts-dir artifacts/eval --output-token-limit 800
uv run raglab eval run --mode routed-vector --golden golden/questions.json --artifacts-dir artifacts/eval --output-token-limit 800
uv run raglab eval compare artifacts/eval/<baseline_run>.json artifacts/eval/<routed_run>.json --markdown artifacts/eval/comparison.md
```

Human-readable output is the default. Commands that support `--json` emit machine-readable output for contract checks, saved samples, and downstream inspection.

## Sample Outputs And Artifacts

Representative quickstart validation output is intentionally checked in as plain files under `artifacts/` so the lab can be reviewed without rerunning live model and vector-store calls.

Corpus inspection confirms the curated corpus shape before ingestion:

```text
Corpus inspection
Sources: 27
Pinned version: huggingface-evaluate@main, microsoft-azure-ai-docs@main, microsoft-azure-docs@main, microsoft-generative-ai-for-beginners@75d89e41403186a1e3613297b1c5483c7d087e5f, nist-ai-600-1@2024-07, openai-api-docs@current-snapshot, openai-cookbook@8730772, owasp-llm-top-10@0205957, trec-common-evaluation-measures-2006, wikipedia@current-snapshot
Categories:
  - prompting techniques: 5
  - RAG and context handling: 5
  - RAG evaluation and quality: 6
  - LLM security and risks: 6
  - LLM settings, cost, and tokens: 5
Validation errors: none
```

A trace inspection shows the route, context budget, citation status, and model token accounting for a single query:

```text
Trace: trace-67fa1006210d44ca8c6b70742e7f2192
Question: How does retrieval augmented generation use retrieved context to ground an answer?
Mode: routed-vector
Route: RAG and context handling
Retrieved chunks: 6
Included chunks: 6
Excluded chunks: 0
Citation validation: valid
Model usage: 2971 tokens
```

Evaluation comparison output highlights the intended mode-level tradeoff: routed retrieval improves recall and MRR in this sample, while the baseline spends fewer average context tokens.

```text
Evaluation comparison
Artifacts: 2
routing_accuracy: baseline-vector=0.7, routed-vector=0.7, best=tie
fallback_rate: baseline-vector=0.0, routed-vector=0.0, best=tie
recall_at_k: baseline-vector=0.7, routed-vector=0.9, best=routed-vector
mrr: baseline-vector=0.55, routed-vector=0.61, best=routed-vector
citation_source_match: baseline-vector=0.7, routed-vector=0.7, best=tie
no_answer_accuracy: baseline-vector=1.0, routed-vector=1.0, best=tie
average_context_tokens: baseline-vector=1328.5, routed-vector=1417.0833333333333, best=baseline-vector
average_included_chunks: baseline-vector=6.0, routed-vector=6.0, best=tie
```

Sample artifacts produced by the quickstart flow:

- `artifacts/eval/eval-baseline-vector.json`
- `artifacts/eval/eval-baseline-vector.md`
- `artifacts/eval/eval-routed-vector.json`
- `artifacts/eval/eval-routed-vector.md`
- `artifacts/eval/comparison.md`
- `artifacts/eval/traces/routed-vector/trace-67fa1006210d44ca8c6b70742e7f2192.json`
- `artifacts/traces/trace-86887ad82e4f4eb88fe3588f5a2d93b4.json`

## Corpus At A Glance

The corpus is intentionally small and pinned so reviewers can inspect exactly what the system is allowed to know. The current manifest contains 27 local Markdown snapshots from Microsoft Learn, Microsoft Generative AI for Beginners, OpenAI Cookbook, OpenAI API docs, OWASP Top 10 for LLM Applications, NIST, TREC, Wikipedia, and Hugging Face Evaluate.

The corpus started from a single-source idea, but the five-category taxonomy needed broader coverage than one prompt-engineering source could provide. The final curation uses a small multi-source set so each category has enough substance for routing, retrieval, no-answer checks, and golden-set evaluation while staying manually reviewable.

Every source record in `corpus/manifest.json` includes:

- `source_slug`: stable ID used in chunks, traces, and evaluation expectations.
- `category`: one of the five allowed knowledge categories.
- `url`: canonical upstream location for audit.
- `license`: license or reuse note copied into corpus inspection output.
- `pinned_version`: commit, publication identifier, or snapshot label.
- `local_ref`: repository-relative path under `corpus/sources/`.
- `sections`: expected section headings used by deterministic chunking.

License rationale:

- Prefer sources with explicit permissive or documentation-friendly terms: MIT, Apache-2.0, CC BY 4.0, and CC BY-SA 4.0.
- Include public/government materials from NIST and TREC when they materially improve evaluation and risk coverage.
- Keep license and reuse uncertainty visible instead of hiding it. OpenAI API docs and some public/government sources are marked with `reuse metadata pending snapshot verification` where the local snapshot still needs final reuse review.
- Store normalized local snapshots rather than scraping live pages during ingestion, so reviewers can inspect the exact text being embedded.

Pinned provenance is part of the runtime contract. GitHub-backed sources use commit or short commit references such as `openai-cookbook@8730772`, `owasp-llm-top-10@0205957`, and `microsoft-generative-ai-for-beginners@75d89e41403186a1e3613297b1c5483c7d087e5f`. Documentation sources without a repo commit use explicit snapshot labels such as `nist-ai-600-1@2024-07`, `trec-common-evaluation-measures-2006`, `wikipedia@current-snapshot`, or provider documentation snapshot labels. Ingestion validates local references before writing vectors, and chunk provenance carries the source URL, license, pinned version, and local file path forward into Qdrant payloads and traces.

The five categories are deliberately coarse enough for deterministic embedding routing but specific enough for evaluation:

- `prompting techniques` (5 sources): instruction design, prompt patterns, structured outputs, model-specific prompting guidance, and examples.
- `RAG and context handling` (5 sources): chunking, embeddings, vector search, context assembly, grounding, and retrieval architecture.
- `RAG evaluation and quality` (6 sources): golden sets, retrieval metrics, answer evaluation, groundedness, metric selection, and diagnostic reporting.
- `LLM security and risks` (6 sources): prompt injection, sensitive information disclosure, data/model poisoning, excessive agency, vector/embedding weaknesses, and generative AI risk management.
- `LLM settings, cost, and tokens` (5 sources): token counting, latency, rate limits, prompt caching, request shape, and operational budget tradeoffs.

## Retrieval, Tracing, And Evaluation

The MVP runtime supports exactly two retrieval modes:

- `baseline-vector`: embeds the question and searches the full Qdrant collection without a category filter. This is the control mode for comparison.
- `routed-vector`: embeds the question, routes it against the five category description embeddings, and searches Qdrant with a `category` payload filter when routing confidence is high enough. The filter is soft: it includes the winning category plus categories whose route score is close to the winner.

Routing is deterministic and non-LLM. The router embeds the question, compares it with the five category description embeddings using cosine similarity, records all category scores, and selects the top category only when its confidence is at or above the configured threshold. The default threshold is `0.18` from `RuntimeConfig`. If confidence is below the threshold, `fallback_all_categories` is recorded as `true`, `selected_category` is empty, and `routed-vector` searches all categories instead of applying a weak filter. When confidence is high enough, the retriever includes the selected category plus any category within `RAGLAB_ROUTER_CATEGORY_MARGIN` of the selected category score; the default margin is `0.15`.

Context budgeting is also deterministic. Retrieved chunks are sorted by retrieval rank and considered in order. A chunk is included only if its estimated token count fits within `max_context_tokens`; otherwise it is recorded under `excluded_chunks` with reason `budget_exceeded`. The trace records `final_estimated_context_tokens`, `max_context_tokens`, `output_token_limit`, included chunks, and excluded chunks. The CLI defaults are `--top-k 6`, `--max-context-tokens 2500`, and `--output-token-limit 500` for ad hoc queries. Evaluation runs default to `--output-token-limit 800` to reduce max-output truncation during golden-set reporting. Each value can be overridden per command.

Each `raglab query` run writes a trace under `artifacts/traces/` by default. A trace contains:

- `schema_version`, `trace_id`, and `created_at`.
- `question` with the original query text.
- `retrieval_mode`.
- `route_decision` with selected category, fallback flag, confidence, threshold, and all five category scores.
- `retrieval_results` with rank, chunk ID, source slug, category, section path, score, estimated tokens, and content when returned for context assembly.
- `context_build` with included chunks, excluded chunks, final estimated context tokens, maximum context tokens, and output token limit.
- `answer_result` with answer text, no-answer flag, citations, validation status, and validation errors.
- `citation_validation` with cited chunk IDs, invalid citations, and validation errors.
- `model_usage` when the chat model returns token accounting.

Evaluation runs execute the same traced query pipeline over `golden/questions.json` for one retrieval mode at a time. `raglab eval run` writes a machine-readable JSON artifact and a Markdown report; `raglab eval compare` reads one or more evaluation artifacts and writes a mode-by-mode comparison table.

The required evaluation metrics are:

- `routing_accuracy`: share of golden questions with an expected category where the selected category matches.
- `fallback_rate`: share of traces that fell back to all-category retrieval.
- `recall_at_k`: share of answerable golden questions where any expected source slug or chunk ID appears in retrieved results.
- `mrr`: mean reciprocal rank of the first expected source or chunk in retrieved results.
- `citation_source_match`: share of answerable golden questions where a cited included chunk matches an expected source slug or chunk ID.
- `no_answer_accuracy`: share of golden questions where answer/no-answer behavior matches the golden label.
- `average_context_tokens`: average `final_estimated_context_tokens` across traces.
- `average_included_chunks`: average number of included context chunks across traces.

For comparison reports, higher is better for quality metrics except `fallback_rate`; lower is better for token-budget diagnostics and fallback rate. Metrics that are not applicable for a run are kept as `null`/`n/a` rather than removed from artifacts.

## Scope Boundaries

This is a portfolio-quality lab, not a production RAG platform. The MVP is intentionally narrow so the retrieval, routing, context, citation, trace, and evaluation behavior stays inspectable.

Citation validation is a context-membership check. Generation prompts expose short citation labels such as `[C1]` instead of long chunk IDs; validation resolves those labels back to full chunk IDs in `answer_result.citations` and `citation_validation.cited_chunk_ids`. It proves that every cited label or chunk ID in the answer maps to selected context and records missing, malformed, or out-of-context citations as validation failures. It does not prove claim-level factual correctness, judge whether the cited passage fully supports a claim, detect paraphrase errors, or verify facts against sources outside the selected context.

No-answer behavior is evidence-gated. If no chunks fit the selected context, the system returns `There is not enough evidence in the selected context to answer.` without calling the chat model. If chunks are present, the prompt instructs the LangChain chat model to answer only from selected context and to return the same no-answer statement when evidence is insufficient. No-answer traces still preserve the route decision, retrieved evidence, context budget, and validation status so reviewers can inspect why the answer was withheld.

MVP exclusions:

- No web UI, chatbot session state, agent loop, LangGraph workflow, or tool-calling agent.
- No production deployment, authentication, authorization, multi-tenant storage, monitoring stack, or SLA behavior.
- No live internet crawling or open-ended ingestion at query time.
- No multi-corpus management; the lab uses one curated, pinned corpus manifest.
- No alternate model providers; runtime embeddings and generation use the configured Azure/OpenAI-compatible Foundry boundary.
- No alternate vector stores; Qdrant is the required runtime vector store.
- No reranker, query rewriting, answer grading model, or claim-level verifier.
- No large evaluation framework such as RAGAS; the harness is intentionally lightweight and local.
- No hybrid lexical/vector retrieval in the MVP runtime contract.

Future extensions that would fit the design:

- Hybrid lexical/vector retrieval with BM25 or rank fusion for exact-term-sensitive questions.
- Optional reranking after vector retrieval, with trace fields that show rank changes.
- Claim-level citation support checks or judge-based groundedness evaluation.
- Additional corpus manifests selected by name while preserving pinned provenance.
- More retrieval diagnostics, such as per-category recall, score distribution summaries, and chunk-overlap analysis.
- CI-generated sample artifacts after live Qdrant and model credentials are available.

## Current Status

The core CLI and library implementation for corpus inspection and ingestion, traced single-query execution, trace inspection, evaluation runs, and evaluation comparison is present. Live end-to-end commands require configured Azure OpenAI deployments and a reachable Qdrant instance. Representative sample command outputs and artifact paths are documented above, with final artifact refresh and redaction checks tracked as polish tasks.

Implemented foundations include:

- Python package metadata and the `raglab` console script.
- Environment/configuration handling.
- Azure OpenAI embedding provider and LangChain Azure chat-model factory.
- Pydantic schemas for corpus, trace, evaluation, retrieval, and artifacts.
- Curated corpus manifest, five categories, local source snapshots, and golden question set.
- Qdrant-backed ingestion and retrieval boundaries.
- Deterministic category routing, bounded context selection, generation, citation validation, trace persistence, and evaluation reports.
- Unit, contract, and integration tests using fakes where external services are not required.

See [tasks.md](specs/001-rag-quality-lab/tasks.md) for the implementation checklist and [quickstart.md](specs/001-rag-quality-lab/quickstart.md) for the end-to-end validation flow.
