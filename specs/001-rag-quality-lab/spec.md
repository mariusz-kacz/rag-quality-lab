# Feature Specification: RAG Quality Lab

**Feature Branch**: `[001-rag-quality-lab]`

**Created**: 2026-07-02

**Status**: Draft

**Input**: User description: "Build a focused Python portfolio project called RAG Quality Lab that demonstrates practical RAG engineering quality over a small, pinned, openly licensed LLM-engineering corpus. The project is CLI-first and must make retrieval, routing, context budgeting, citations, no-answer behavior, traces, and evaluation explicit, measurable, and reproducible."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Inspect and Ingest a Curated Corpus (Priority: P1)

As a portfolio reviewer, I want to inspect the pinned source corpus and ingest it into the required retrieval store so that I can verify the project starts from a controlled, reproducible knowledge base rather than arbitrary document ingestion.

**Why this priority**: A reproducible corpus with documented provenance is the foundation for all later retrieval, citation, and evaluation claims.

**Independent Test**: Can be tested by inspecting corpus metadata, running ingestion from a clean local state, and confirming that every chunk has stable metadata and is available for retrieval.

**Acceptance Scenarios**:

1. **Given** a clean local checkout and valid environment configuration, **When** the reviewer runs the corpus inspection command, **Then** the system lists all selected source pages with slug, category, URL, license metadata, pinned version or commit, and reproducible local reference.
2. **Given** the curated corpus contains 15-30 selected source pages across exactly five knowledge categories, **When** the reviewer runs ingestion, **Then** all chunks are loaded into Qdrant with stable chunk IDs, source slugs, categories, section metadata, content hashes, estimated token counts, and source provenance.
3. **Given** a source page has missing provenance, license, category, URL, pinned version, or local reference metadata, **When** the reviewer attempts ingestion, **Then** ingestion fails with a clear validation error and does not silently create incomplete chunks.

---

### User Story 2 - Run a Single Traced RAG Query (Priority: P1)

As a reviewer, I want to run an individual question through a deterministic RAG workflow so that I can inspect routing, retrieval, context-budget decisions, citations, no-answer behavior, and persisted traces for a single case.

**Why this priority**: The core portfolio value is showing that the RAG pipeline is controlled and inspectable rather than a black-box Q&A demo.

**Independent Test**: Can be tested by running one answerable query and one insufficient-evidence query, then verifying the answer or no-answer result, citations, citation validation outcome, and trace contents.

**Acceptance Scenarios**:

1. **Given** the corpus has been ingested, **When** the reviewer asks an answerable question using a selected retrieval mode, **Then** the system routes the question, retrieves evidence, builds a bounded context, generates an answer constrained to that context, validates citations against the selected context, and persists a trace.
2. **Given** retrieved evidence is insufficient to answer a question, **When** the reviewer runs the query, **Then** the system returns an explicit no-answer outcome with the retrieved evidence and trace data needed to understand why the answer was withheld.
3. **Given** a generated answer cites a chunk that was not included in the selected context, **When** citation validation runs, **Then** the answer is marked invalid and the trace records the invalid citation.
4. **Given** category-routing confidence is below the configured threshold, **When** a query is routed, **Then** retrieval falls back to all categories and the trace records the fallback decision and confidence score.

---

### User Story 3 - Compare Retrieval Strategies with a Golden Set (Priority: P2)

As a reviewer, I want to run a lightweight evaluation over a golden question set so that I can compare retrieval modes using clear quality and cost-related diagnostics.

**Why this priority**: Comparison across strategies demonstrates practical RAG engineering judgment and makes improvements measurable.

**Independent Test**: Can be tested by running evaluation for each supported retrieval mode and checking that machine-readable and Markdown artifacts contain the required metrics and per-question diagnostics.

**Acceptance Scenarios**:

1. **Given** a golden set with 12-15 cases, **When** the reviewer evaluates `baseline-vector`, **Then** the system reports routing accuracy where applicable, fallback rate, recall@k, MRR, citation source match, no-answer accuracy, average context tokens, and average included chunks.
2. **Given** the same golden set, **When** the reviewer evaluates `routed-vector`, **Then** the system reports the same comparable metrics and includes routing decisions for each question.
3. **Given** the optional Phase 1.5 hybrid retrieval feature is enabled, **When** the reviewer evaluates `routed-hybrid`, **Then** the system combines vector and lexical retrieval results, reports comparable metrics, and identifies the retrieval mode in all artifacts.
4. **Given** evaluation completes, **When** artifacts are written, **Then** reviewers can inspect both a machine-readable result and a human-readable Markdown report without rerunning the evaluation.

---

### User Story 4 - Understand Project Scope and Limitations (Priority: P3)

As a reviewer, I want clear documentation of the architecture, corpus choices, category design, evaluation method, limitations, and exclusions so that I can judge the project as a focused RAG quality engineering lab.

**Why this priority**: Strong documentation turns the implementation into a portfolio artifact that explains tradeoffs and avoids misrepresenting validation as full factual correctness.

**Independent Test**: Can be tested by reading the README and verifying that it explains the intended workflow, metrics, limitations, and future extensions without presenting the project as a chatbot, generic ingestion platform, or production system.

**Acceptance Scenarios**:

1. **Given** the reviewer opens the README, **When** they read the project overview, **Then** it positions the project as a CLI-first RAG quality lab and not as a chatbot, generic ingestion platform, or agentic system.
2. **Given** the reviewer reads the limitations section, **When** citation validation is described, **Then** the documentation clearly states that validation proves cited chunks were present in selected context but does not prove full claim-level factual correctness.
3. **Given** the reviewer reads the future extensions section, **When** optional or later features are listed, **Then** MVP exclusions remain clearly out of scope.

### Edge Cases

- The source corpus contains fewer than 15 or more than 30 selected pages.
- A source page cannot be mapped to exactly one of the five required categories.
- A chunk exceeds the maximum context budget by itself.
- Multiple chunks tie in retrieval score near the context budget boundary.
- Router confidence is close to the threshold for a category-boundary question.
- The golden set references an expected source slug or category that is missing from the ingested corpus.
- The answer generator omits citations, emits malformed citations, or cites retrieved-but-excluded chunks.
- Actual model usage metadata is unavailable for a query.
- Optional hybrid retrieval is not implemented in the MVP but evaluation is requested for `routed-hybrid`.
- Required environment configuration or the required retrieval store is unavailable.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a CLI-first product experience that supports corpus inspection, corpus ingestion, single-query execution, trace inspection, retrieval-mode evaluation, and writing evaluation artifacts.
- **FR-002**: The system MUST use a small curated corpus of 15-30 selected source pages from one pinned, openly licensed LLM-engineering source, with DAIR.AI Prompt Engineering Guide as the default source unless replaced by an equivalent openly licensed pinned source before planning.
- **FR-003**: Each selected source page MUST record provenance metadata including source slug, category, URL, license metadata, pinned version or commit, and reproducible local reference.
- **FR-004**: The corpus MUST use exactly five knowledge categories: prompting techniques; RAG and context handling; RAG evaluation and quality; LLM security and risks; LLM settings, cost, and tokens.
- **FR-005**: Every ingested chunk MUST include stable metadata: chunk ID, source slug, category, section metadata, content hash, estimated token count, and source provenance.
- **FR-006**: The query workflow MUST follow this deterministic sequence: question, route, retrieve, build bounded context, generate cited answer or no-answer, validate citations, persist trace.
- **FR-007**: Routing MUST be deterministic and embedding-based by comparing the user question against category description embeddings.
- **FR-008**: Routing MUST select one category when confidence is high enough and MUST fall back to all categories when confidence is insufficient.
- **FR-009**: The MVP router MUST NOT use an LLM.
- **FR-010**: Retrieval MUST support `baseline-vector`, which searches across all chunks without category filtering.
- **FR-011**: Retrieval MUST support `routed-vector`, which applies route-first category filtering before vector search in Qdrant.
- **FR-012**: Retrieval MAY support `routed-hybrid` as a Phase 1.5 feature that combines vector retrieval and BM25 with reciprocal rank fusion.
- **FR-013**: Qdrant MUST be the mandatory vector store for MVP runtime.
- **FR-014**: Azure OpenAI MUST be used for embeddings and answer generation, configured through environment variables.
- **FR-015**: LangChain MAY be used only as a thin integration boundary for Azure OpenAI, Qdrant, or prompt templates; core routing, retrieval orchestration, context budgeting, citation validation, trace persistence, and evaluation logic MUST remain plain Python application logic.
- **FR-016**: The context builder MUST enforce a maximum context token budget and include retrieved chunks in ranked order until adding another chunk would exceed the budget.
- **FR-017**: The context builder MUST record excluded chunks and the reason each chunk was excluded.
- **FR-018**: Every query trace MUST expose token-budget decisions, including estimated chunk tokens, included chunks, excluded chunks, final estimated context size, output-token limit, and actual model usage when available.
- **FR-019**: Answer generation MUST be constrained to retrieved context and MUST return either a cited answer or an explicit no-answer result.
- **FR-020**: Model output MUST be treated as untrusted until citation validation completes.
- **FR-021**: Citations MUST reference retrieved chunks only and MUST be validated against chunks present in the selected context.
- **FR-022**: The project documentation MUST state that citation validation proves cited chunks were present in the selected context, but does not prove full claim-level factual correctness.
- **FR-023**: The system MUST support no-answer behavior when retrieved evidence is insufficient.
- **FR-024**: The golden set MUST include answerable questions, no-answer questions, ambiguous category-boundary questions, and fallback-routing cases.
- **FR-025**: The evaluation harness MUST be lightweight and custom-built rather than based on a large evaluation framework such as RAGAS.
- **FR-026**: The evaluation harness MUST compare retrieval modes using a golden question set of 12-15 cases.
- **FR-027**: Evaluation metrics MUST include routing accuracy, fallback rate, recall@k, MRR, citation source match, no-answer accuracy, average context tokens, and average included chunks.
- **FR-028**: Evaluation MUST produce both machine-readable and Markdown artifacts.
- **FR-029**: The README MUST explain the architecture, corpus and license choices, category design, CLI workflow, evaluation metrics, sample results, limitations, and future extensions.
- **FR-030**: The MVP MUST explicitly exclude web UI, chatbot-style conversation, LangGraph or agents, multi-corpus ingestion, multiple vector stores, multiple model providers, reranking, production deployment, user authentication, full internet crawling, and large evaluation frameworks.
- **FR-031**: The CLI MUST fail clearly when required configuration, corpus files, retrieval store availability, or evaluation inputs are missing.
- **FR-032**: Repeated runs over the same pinned corpus, configuration, and retrieval mode MUST produce stable corpus identifiers, stable chunk identifiers, and comparable evaluation artifacts.

### Key Entities

- **Source Page**: A selected page from the pinned corpus source. Key attributes include source slug, title, category, URL, license metadata, pinned version or commit, local reference, and source-level provenance.
- **Knowledge Category**: One of the five allowed topical categories used by the deterministic router and by routed retrieval modes. Key attributes include category name, category description, and category description embedding reference.
- **Chunk**: A stable unit of retrieved text derived from a source page. Key attributes include chunk ID, source slug, category, section metadata, content hash, estimated token count, text, and provenance.
- **Question**: A user-supplied query or golden-set case. Key attributes include question text, expected category when applicable, expected relevant source or chunks when applicable, answerability label, and expected no-answer behavior when applicable.
- **Route Decision**: The deterministic routing result for a question. Key attributes include selected category or all-category fallback, confidence score, threshold comparison, and category similarity scores.
- **Retrieval Result**: A ranked set of candidate chunks returned by a retrieval mode. Key attributes include retrieval mode, rank, score, chunk ID, source slug, and category.
- **Context Build**: The bounded context selected for answer generation. Key attributes include included chunks, excluded chunks, exclusion reasons, estimated chunk tokens, final estimated context size, and output-token limit.
- **Answer Result**: The generated cited answer or explicit no-answer result. Key attributes include answer text, citation list, no-answer flag, and validation status.
- **Query Trace**: The persisted record of a full query run. Key attributes include question, route decision, retrieval results, context build, answer result, citation validation outcome, token-budget diagnostics, and model usage when available.
- **Evaluation Run**: A comparison run for a retrieval mode over the golden set. Key attributes include retrieval mode, per-question outcomes, aggregate metrics, token diagnostics, artifact paths, and run timestamp.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reviewer can complete a clean corpus inspection and ingestion walkthrough in 10 minutes or less using documented CLI commands.
- **SC-002**: The curated corpus contains 15-30 selected source pages and 100% of selected source pages have complete provenance, license, category, URL, pinned version or commit, and local reference metadata.
- **SC-003**: 100% of ingested chunks include stable chunk ID, source slug, category, section metadata, content hash, estimated token count, and source provenance.
- **SC-004**: For every single-query run, the persisted trace records route decision, retrieval results, context inclusion and exclusion decisions, citation validation outcome, and token-budget diagnostics.
- **SC-005**: On the golden question set, evaluation artifacts report all required metrics for each implemented retrieval mode with no manual post-processing.
- **SC-006**: At least 12 and no more than 15 golden-set cases are included, covering answerable, no-answer, ambiguous category-boundary, and fallback-routing scenarios.
- **SC-007**: 100% of answer outputs are either cited answers whose citations validate against selected context or explicit no-answer responses.
- **SC-008**: Re-running evaluation for the same pinned corpus and retrieval mode produces machine-readable artifacts with the same question identifiers, retrieval mode labels, metric names, and trace references.
- **SC-009**: A reviewer can identify, from the README alone, the project purpose, MVP scope, excluded features, corpus source and license rationale, category design, CLI workflow, metrics, limitations, and future extensions.
- **SC-010**: The README and trace artifacts make token-budget behavior visible by reporting average context tokens, average included chunks, and per-query included and excluded chunks.

## Assumptions

- The primary user is a technical portfolio reviewer or interviewer evaluating practical RAG engineering quality.
- The MVP prioritizes local reproducibility and traceability over production deployment concerns.
- The corpus source will be pinned before ingestion and will remain small enough for local inspection and evaluation.
- The default curated source is DAIR.AI Prompt Engineering Guide if its selected pages and license metadata satisfy the provenance requirements during planning.
- Required external service credentials and endpoints are provided by the reviewer through environment variables.
- The optional `routed-hybrid` mode is not required for the core MVP unless selected for Phase 1.5 implementation.
- Exact token counts may be estimated for budgeting, while actual model usage is recorded when available from the model provider.
- Stable outputs are expected for identifiers, traces, and evaluation schemas; natural-language answer wording may vary across model calls.
