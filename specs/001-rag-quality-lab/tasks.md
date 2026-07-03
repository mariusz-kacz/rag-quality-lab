# Tasks: RAG Quality Lab

**Input**: Design documents from `/specs/001-rag-quality-lab/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included because the feature specification and plan explicitly require pytest unit, integration, and contract coverage.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and does not depend on incomplete tasks
- **[Story]**: User story label, present only for story-phase tasks
- Each task includes exact file paths

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize the Python CLI project, package layout, durable input/output directories, and local developer defaults.

- [X] T001 Create Python project metadata with Typer, Pydantic, qdrant-client, openai, tiktoken, rank-bm25, pytest, and console script `raglab` in pyproject.toml
- [X] T002 Create package and test directory structure in src/rag_quality_lab/__init__.py and tests/
- [X] T003 [P] Create domain package directories with __init__.py files in src/rag_quality_lab/corpus/, src/rag_quality_lab/routing/, src/rag_quality_lab/retrieval/, src/rag_quality_lab/rag/, src/rag_quality_lab/eval/, and src/rag_quality_lab/schemas/
- [X] T004 [P] Create durable input and artifact directories with placeholder files in corpus/sources/, golden/, artifacts/traces/, and artifacts/eval/
- [X] T005 [P] Add local environment example for Azure OpenAI and Qdrant settings in .env.example
- [X] T006 [P] Configure pytest defaults and test discovery in pyproject.toml

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared configuration, schema, CLI, artifact, and provider boundaries that must exist before story implementation.

**CRITICAL**: No user story work can begin until this phase is complete.

- [X] T007 Implement environment and runtime configuration loading with clear missing-setting errors in src/rag_quality_lab/config.py
- [X] T008 [P] Implement shared corpus, routing, retrieval, context, answer, trace, and evaluation Pydantic schemas in src/rag_quality_lab/schemas/corpus.py, src/rag_quality_lab/schemas/trace.py, src/rag_quality_lab/schemas/eval.py, and src/rag_quality_lab/schemas/artifacts.py
- [X] T009 [P] Define the five required knowledge categories and descriptions in src/rag_quality_lab/routing/categories.py
- [X] T010 [P] Implement artifact JSON write/read helpers with schema_version support in src/rag_quality_lab/schemas/artifacts.py
- [X] T011 [P] Implement Azure OpenAI embedding and chat provider wrappers in src/rag_quality_lab/providers.py
- [X] T012 Implement base Typer application, shared options, and error-to-exit-code handling in src/rag_quality_lab/cli.py
- [X] T013 [P] Add pytest fixtures for temporary corpus, golden data, traces, and fake provider clients in tests/conftest.py

**Checkpoint**: Foundation ready - user story implementation can now begin according to dependencies below.

---

## Phase 3: User Story 1 - Inspect and Ingest a Curated Corpus (Priority: P1) MVP

**Goal**: A reviewer can inspect the pinned corpus metadata and ingest validated chunks into Qdrant with stable provenance.

**Independent Test**: Run `raglab corpus inspect --json`, then `raglab corpus ingest --collection rag_quality_lab --recreate --json` from a clean local state and confirm all source and chunk metadata is complete and stable.

### Tests for User Story 1

- [X] T014 [P] [US1] Add contract tests for `raglab corpus inspect` JSON and failure output in tests/contract/test_cli_corpus_inspect.py
- [X] T015 [P] [US1] Add contract tests for `raglab corpus ingest` JSON and failure output in tests/contract/test_cli_corpus_ingest.py
- [X] T016 [P] [US1] Add unit tests for manifest source count, category, provenance, license, URL, pinned version, and local_ref validation in tests/unit/test_manifest.py
- [X] T017 [P] [US1] Add unit tests for deterministic chunk IDs, content hashes, section metadata, and token estimates in tests/unit/test_chunking.py
- [ ] T018 [P] [US1] Add integration test for clean corpus inspection and Qdrant-backed ingestion using fake embeddings in tests/integration/test_corpus_ingest_workflow.py

### Implementation for User Story 1

- [ ] T019 [P] [US1] Create curated corpus manifest with 15-30 DAIR.AI Prompt Engineering Guide source pages, one pinned version, five categories, license metadata, URLs, and local references in corpus/manifest.json
- [ ] T020 [P] [US1] Create category definitions matching the five required categories in corpus/categories.json
- [ ] T021 [US1] Add pinned local source snapshots for every manifest entry under corpus/sources/
- [ ] T022 [US1] Implement manifest loading and validation for SourcePage and KnowledgeCategory records in src/rag_quality_lab/corpus/manifest.py
- [ ] T023 [US1] Implement corpus inspection summaries and JSON artifact shape in src/rag_quality_lab/corpus/inspect.py
- [ ] T024 [US1] Implement deterministic section-aware chunking, normalized content hashing, chunk IDs, and token estimates in src/rag_quality_lab/corpus/chunking.py
- [ ] T025 [US1] Implement Qdrant collection creation, payload mapping, vector upsert, and availability checks in src/rag_quality_lab/retrieval/qdrant_store.py
- [ ] T026 [US1] Implement corpus ingestion orchestration with validation-before-write behavior in src/rag_quality_lab/corpus/ingest.py
- [ ] T027 [US1] Wire `raglab corpus inspect` and `raglab corpus ingest` commands with human and JSON output in src/rag_quality_lab/cli.py

**Checkpoint**: User Story 1 is fully functional and testable independently.

---

## Phase 4: User Story 2 - Run a Single Traced RAG Query (Priority: P1)

**Goal**: A reviewer can run one answerable or insufficient-evidence question through deterministic routing, retrieval, bounded context selection, cited generation or no-answer behavior, citation validation, and trace persistence.

**Independent Test**: With the corpus ingested, run one answerable `raglab query` and one no-answer `raglab query`, then inspect the trace with `raglab trace inspect` and verify route decisions, retrieval results, context budget decisions, citations, validation status, and model usage fields.

### Tests for User Story 2

- [ ] T028 [P] [US2] Add contract tests for `raglab query` JSON output, unsupported mode errors, and trace path reporting in tests/contract/test_cli_query.py
- [ ] T029 [P] [US2] Add contract tests for `raglab trace inspect` JSON output and trace schema fields in tests/contract/test_cli_trace.py
- [ ] T030 [P] [US2] Add unit tests for embedding category routing confidence, fallback decisions, and all-category scores in tests/unit/test_embedding_router.py
- [ ] T031 [P] [US2] Add unit tests for baseline-vector and routed-vector retrieval filtering and ranked result normalization in tests/unit/test_retrieval_modes.py
- [ ] T032 [P] [US2] Add unit tests for context budget inclusion order, excluded chunk reasons, and single oversized chunk handling in tests/unit/test_context.py
- [ ] T033 [P] [US2] Add unit tests for citation parsing, malformed citations, missing citations, and out-of-context citation invalidation in tests/unit/test_citations.py
- [ ] T034 [P] [US2] Add integration tests for answerable and no-answer query workflows with persisted traces in tests/integration/test_query_workflow.py

### Implementation for User Story 2

- [ ] T035 [US2] Implement deterministic category embedding router with threshold fallback in src/rag_quality_lab/routing/embedding_router.py
- [ ] T036 [US2] Implement retrieval mode interface and supported mode validation in src/rag_quality_lab/retrieval/modes.py
- [ ] T037 [US2] Implement baseline-vector and routed-vector search over Qdrant with route-aware filters in src/rag_quality_lab/retrieval/qdrant_store.py
- [ ] T038 [US2] Implement optional routed-hybrid interface that clearly reports not implemented until Phase 1.5 is enabled in src/rag_quality_lab/retrieval/hybrid.py
- [ ] T039 [US2] Implement bounded context builder with included chunks, excluded chunks, estimated token totals, and output token limits in src/rag_quality_lab/rag/context.py
- [ ] T040 [US2] Implement context-constrained answer generation and explicit no-answer prompt handling in src/rag_quality_lab/rag/generation.py
- [ ] T041 [US2] Implement citation extraction and validation against selected context chunks in src/rag_quality_lab/rag/citations.py
- [ ] T042 [US2] Implement query trace creation, schema validation, persistence, and trace loading in src/rag_quality_lab/rag/traces.py
- [ ] T043 [US2] Implement end-to-end query pipeline sequence question -> route -> retrieve -> context -> generate/no-answer -> validate -> trace in src/rag_quality_lab/rag/pipeline.py
- [ ] T044 [US2] Wire `raglab query` and `raglab trace inspect` commands with human and JSON output in src/rag_quality_lab/cli.py

**Checkpoint**: User Stories 1 and 2 both work, with a traceable single-query RAG workflow.

---

## Phase 5: User Story 3 - Compare Retrieval Strategies with a Golden Set (Priority: P2)

**Goal**: A reviewer can run lightweight golden-set evaluations for supported retrieval modes and inspect comparable JSON and Markdown artifacts.

**Independent Test**: Run `raglab eval run` for `baseline-vector` and `routed-vector`, then run `raglab eval compare` and verify required metrics, per-question diagnostics, trace references, and Markdown reports are present.

### Tests for User Story 3

- [ ] T045 [P] [US3] Add contract tests for `raglab eval run` JSON output, metric names, artifact paths, and unsupported optional modes in tests/contract/test_cli_eval_run.py
- [ ] T046 [P] [US3] Add contract tests for `raglab eval compare` JSON and Markdown output in tests/contract/test_cli_eval_compare.py
- [ ] T047 [P] [US3] Add unit tests for golden question validation, required case types, answerability labels, and expected relevant sources in tests/unit/test_golden.py
- [ ] T048 [P] [US3] Add unit tests for routing accuracy, fallback rate, recall@k, MRR, citation source match, no-answer accuracy, and token averages in tests/unit/test_metrics.py
- [ ] T049 [P] [US3] Add integration tests for baseline-vector and routed-vector evaluation artifact generation in tests/integration/test_eval_workflow.py

### Implementation for User Story 3

- [ ] T050 [US3] Create 12-15 golden questions covering answerable, no-answer, ambiguous boundary, and fallback-routing cases in golden/questions.json
- [ ] T051 [US3] Implement golden question loading and validation in src/rag_quality_lab/eval/golden.py
- [ ] T052 [US3] Implement metric calculations for all required evaluation metrics in src/rag_quality_lab/eval/metrics.py
- [ ] T053 [US3] Implement evaluation run orchestration that executes query traces per golden case and mode in src/rag_quality_lab/eval/reports.py
- [ ] T054 [US3] Implement machine-readable evaluation artifact writing with required schema fields in src/rag_quality_lab/eval/reports.py
- [ ] T055 [US3] Implement Markdown evaluation report sections for summary, metrics, per-question diagnostics, token budgets, no-answer cases, failures, and limitations in src/rag_quality_lab/eval/reports.py
- [ ] T056 [US3] Implement evaluation comparison table generation for one or more artifact paths in src/rag_quality_lab/eval/reports.py
- [ ] T057 [US3] Wire `raglab eval run` and `raglab eval compare` commands with human and JSON output in src/rag_quality_lab/cli.py

**Checkpoint**: Retrieval strategy evaluation is runnable and produces comparable artifacts.

---

## Phase 6: User Story 4 - Understand Project Scope and Limitations (Priority: P3)

**Goal**: A reviewer can understand architecture, corpus choices, categories, CLI workflow, evaluation method, limitations, exclusions, and future extensions from documentation alone.

**Independent Test**: Read the README and confirm it positions the project as a CLI-first RAG quality lab, documents citation validation limits, and keeps MVP exclusions clearly out of scope.

### Tests for User Story 4

- [ ] T058 [P] [US4] Add documentation contract test that checks README coverage for purpose, scope, corpus, categories, workflow, metrics, limitations, and exclusions in tests/contract/test_readme_contract.py

### Implementation for User Story 4

- [ ] T059 [US4] Write README project overview, architecture, and CLI-first workflow in README.md
- [ ] T060 [US4] Document corpus source, license rationale, pinned provenance, and five-category design in README.md
- [ ] T061 [US4] Document retrieval modes, routing fallback behavior, context budgeting, trace contents, and evaluation metrics in README.md
- [ ] T062 [US4] Document citation validation limitations, no-answer behavior, MVP exclusions, and future extensions in README.md
- [ ] T063 [US4] Add sample command outputs and sample artifact paths from quickstart validation in README.md

**Checkpoint**: Documentation frames the project accurately as a focused portfolio artifact.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, sample artifacts, cleanup, and reproducibility checks across all stories.

- [ ] T064 [P] Run full pytest suite and record any intentional external-service skips in README.md
- [ ] T065 [P] Run corpus inspection quickstart command and save representative JSON output in artifacts/corpus-summary.sample.json
- [ ] T066 [P] Run ingestion quickstart command against the configured Qdrant collection and save representative JSON output in artifacts/ingestion-summary.sample.json
- [ ] T067 Run answerable query, no-answer query, trace inspect, baseline evaluation, routed evaluation, and comparison commands from specs/001-rag-quality-lab/quickstart.md
- [ ] T068 Review generated traces and evaluation artifacts for stable schema fields and redact any environment-specific secrets in artifacts/traces/ and artifacts/eval/
- [ ] T069 Update README.md with final sample metrics and command transcript references after quickstart validation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion - blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational and is the MVP slice.
- **User Story 2 (Phase 4)**: Depends on Foundational and requires an ingested corpus from User Story 1 for end-to-end manual validation.
- **User Story 3 (Phase 5)**: Depends on User Story 2 because evaluation reuses query pipeline and traces.
- **User Story 4 (Phase 6)**: Can start after Foundational, but final examples depend on User Stories 1-3.
- **Polish (Phase 7)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **US1 (P1)**: Starts after Foundational; no dependency on other stories.
- **US2 (P1)**: Starts after Foundational for unit work; end-to-end validation depends on US1 ingestion.
- **US3 (P2)**: Depends on US2 query pipeline and trace persistence.
- **US4 (P3)**: Documentation can begin once architecture is known; final sample results depend on US1-US3.

### Within Each User Story

- Tests should be written first and fail before implementation.
- Schema and model tasks precede services.
- Services precede CLI wiring.
- CLI wiring precedes integration workflow validation.
- Each story reaches its checkpoint before moving to the next priority unless parallel staffing is available.

### Parallel Opportunities

- Setup tasks T003-T006 can run in parallel after T001-T002 are understood.
- Foundational tasks T008-T011 and T013 can run in parallel.
- US1 tests T014-T018 can run in parallel, and corpus file tasks T019-T020 can run in parallel.
- US2 tests T028-T034 can run in parallel before implementation.
- US3 tests T045-T049 can run in parallel before implementation.
- US4 documentation test T058 can run in parallel with README drafting tasks T059-T062.
- Polish sampling tasks T064-T066 can run in parallel when the environment is configured.

---

## Parallel Example: User Story 1

```bash
Task: "T014 [P] [US1] Add contract tests for `raglab corpus inspect` JSON and failure output in tests/contract/test_cli_corpus_inspect.py"
Task: "T015 [P] [US1] Add contract tests for `raglab corpus ingest` JSON and failure output in tests/contract/test_cli_corpus_ingest.py"
Task: "T016 [P] [US1] Add unit tests for manifest source count, category, provenance, license, URL, pinned version, and local_ref validation in tests/unit/test_manifest.py"
Task: "T017 [P] [US1] Add unit tests for deterministic chunk IDs, content hashes, section metadata, and token estimates in tests/unit/test_chunking.py"
Task: "T018 [P] [US1] Add integration test for clean corpus inspection and Qdrant-backed ingestion using fake embeddings in tests/integration/test_corpus_ingest_workflow.py"
```

## Parallel Example: User Story 2

```bash
Task: "T030 [P] [US2] Add unit tests for embedding category routing confidence, fallback decisions, and all-category scores in tests/unit/test_embedding_router.py"
Task: "T031 [P] [US2] Add unit tests for baseline-vector and routed-vector retrieval filtering and ranked result normalization in tests/unit/test_retrieval_modes.py"
Task: "T032 [P] [US2] Add unit tests for context budget inclusion order, excluded chunk reasons, and single oversized chunk handling in tests/unit/test_context.py"
Task: "T033 [P] [US2] Add unit tests for citation parsing, malformed citations, missing citations, and out-of-context citation invalidation in tests/unit/test_citations.py"
```

## Parallel Example: User Story 3

```bash
Task: "T045 [P] [US3] Add contract tests for `raglab eval run` JSON output, metric names, artifact paths, and unsupported optional modes in tests/contract/test_cli_eval_run.py"
Task: "T046 [P] [US3] Add contract tests for `raglab eval compare` JSON and Markdown output in tests/contract/test_cli_eval_compare.py"
Task: "T047 [P] [US3] Add unit tests for golden question validation, required case types, answerability labels, and expected relevant sources in tests/unit/test_golden.py"
Task: "T048 [P] [US3] Add unit tests for routing accuracy, fallback rate, recall@k, MRR, citation source match, no-answer accuracy, and token averages in tests/unit/test_metrics.py"
```

## Parallel Example: User Story 4

```bash
Task: "T058 [P] [US4] Add documentation contract test that checks README coverage for purpose, scope, corpus, categories, workflow, metrics, limitations, and exclusions in tests/contract/test_readme_contract.py"
Task: "T059 [US4] Write README project overview, architecture, and CLI-first workflow in README.md"
Task: "T060 [US4] Document corpus source, license rationale, pinned provenance, and five-category design in README.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: User Story 1.
4. Stop and validate corpus inspection and ingestion independently.
5. Demo reproducible corpus provenance and Qdrant ingestion.

### Core Portfolio Flow

1. Complete MVP first: Setup -> Foundational -> US1.
2. Add US2 to demonstrate deterministic traced single-query RAG.
3. Add US3 to make retrieval strategy comparison measurable.
4. Add US4 documentation to explain tradeoffs, limits, and reproducibility.
5. Complete Phase 7 quickstart validation and sample artifacts.

### Parallel Team Strategy

1. Complete Setup and Foundational together.
2. Implement US1 corpus tasks while US2 unit tests are drafted against schemas and interfaces.
3. Start US3 metric and artifact tests after US2 trace schemas stabilize.
4. Draft US4 documentation throughout, then refresh examples after quickstart validation.

---

## Notes

- The optional `routed-hybrid` mode is represented as a clear unsupported-mode path for MVP unless Phase 1.5 is explicitly selected.
- Qdrant and Azure OpenAI are mandatory runtime integrations; tests should use fakes where possible and reserve live-service checks for integration validation.
- Citation validation proves cited chunks were included in selected context; claim-level factual correctness remains a documented limitation.
