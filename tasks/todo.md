# Tasks: Ragas evaluation

Status: Tasks 1-2 completed on 2026-09-22; tasks 3-8 remain unstarted.

**Authorized early retirement:** The user requested removal of all legacy evaluation code and automated tests, preserving only the benchmark cases/labels in `golden/questions.json`. Removed `eval/golden.py`, `eval/metrics.py`, `eval/reports.py`, `schemas/eval.py`, legacy CLI commands/helpers/defaults, seven dedicated test files (54 cases), obsolete golden fixtures, and legacy report artifacts/documentation. Existing query refusal/citation/trace assertions remain in `test_query_workflow.py`; only its legacy scoring assertion was removed. Core provider ownership, generation, routing, corpus, and trace suites remain. No replacement tests were added for retired evaluation behavior. New Ragas configuration/providers and their existing tests remain. Later task references to removed files describe historical starting points, not code to restore. Task 7 remains a final audit, and no replacement runner/CLI has been implemented.

Retirement validation: 175 remaining tests passed; Ruff lint, formatting of the seven modified existing Python files, `uv build`, root CLI help, and `git diff --check` passed. No source/test references to deleted evaluator APIs remain. Benchmark SHA-256 is unchanged: `6CC804358BDBB02651CBCA631064AC22FFCCCC3FF9ECA7968372B10863E2C68B`. This is intentional feature/test deletion, not behavior-preserving refactoring; no RED/GREEN or replacement tests were added. No Git commit was created.

Read [plan.md](plan.md) with [the specification](../SPEC-ragas-evaluation.md). Paths are repository-relative; new filenames are proposals. Each task includes its tests and should leave affected workflows working. Do not broaden scope to unrelated cleanup. Acceptance references use the specification's AC IDs.

- [x] User explicitly authorized Task 1. Authorization is limited to this task.
- [x] User subsequently authorized Task 2 only; completed without a Git commit.

Direction clarified on 2026-09-22: Ragas is the sole evaluation framework. Preserve benchmark cases/labels in JSON; old evaluation behavior, scores, options/defaults, schemas, and reports are not compatibility targets. Remove superseded implementation and obsolete tests as the Ragas workflow lands. Preserve tests only for meaningful new contracts or unchanged core query/corpus/trace behavior. Task 7 is a final audit, not a requirement to maintain a second evaluator until then. This planning update does not start another implementation task.

## Task 1: Prove the framework boundary

**Description:** Select compatible pinned eval dependencies and establish a tiny executable integration fixture before replacing application orchestration. Validate the actual package/backend behavior on the repository's Python/Windows environment. Record the chosen API, local storage format, and provider integration choice alongside the fixture for later documentation.

**Acceptance criteria:**
- [x] `eval` extra contains Ragas, `ir-measures`, and only required provider integration dependencies; `uv.lock` resolves with `uv sync --locked --extra eval`. Establish that the core package/help still imports in a clean no-extra environment (AC-01).
- [x] Real Ragas experiment execution invokes both collections metrics with substituted external LLM/embedding responses and round-trips a local result with question ID, diagnostic fields, and explicit null/error/not-applicable states. Record actual storage paths and metric result shape; no runner/metric mock substitutes for this proof (AC-02/16).
- [x] Real IR backend executes Success@K and RR@K, including an empty ranking, on this platform. Confirm evaluator concurrency of one, built-in defaults, retry/repair controls, and the supported endpoint adapter path; unresolved incompatibility blocks later integration rather than triggering a homegrown metric.

**Verification:**
- [x] `uv sync --locked --extra eval`
- [x] `uv run --locked --extra eval pytest tests/integration/test_ragas_compatibility.py`
- [x] `uv build`; clean no-extra package import and `raglab --help` smoke.
- [x] Establish current pytest/Ruff baselines. Keep eval-dependent tests discoverable without the extra using a narrow dependency guard, and verify they actually execute in the eval-enabled suite.

**Dependencies:** None.

**Files likely touched:** `pyproject.toml`, `uv.lock`, `tests/integration/test_ragas_compatibility.py` (new).

**Estimated scope:** Medium: 3 files; external compatibility is the main uncertainty.

**Completion evidence:** Verification path 5 (dependency configuration and executable compatibility proof; no application behavior change). Added one integration suite with five cases: real metric/experiment/JSONL serialization and sequential execution; a three-case transport retry matrix; and IR cutoff/empty-query scoring. Existing tests were unchanged. Ragas and IR are pinned at 0.4.3; required `langchain-community` is pinned at 0.4.1 after reproducing an import failure with 0.4.2. IR uses supported public dispatch, not a forced provider or custom formula. Detailed defaults, paths, result shape, failure handling caveats, and adapter decisions are in [compatibility notes](../tests/integration/ragas_compatibility.md).

Baseline: 195 tests passed, Ruff lint passed, 26 pre-existing formatting failures. Final eval-enabled suite: 200 passed. Separate clean no-extra environment: 195 passed, five optional cases skipped; package/query imports and root CLI help passed with Ragas, ir-measures, Instructor, and langchain-community absent. Locked sync, build, lint, and changed-file formatting passed. Sandbox cache/temp-directory restrictions were resolved by approved reruns. No production code changed, no live scoring performed, no Git commit created. Scope additions are this evidence note and task-progress updates; later tasks and their checkpoints remain open.

## Task 2: Configure and own evaluator clients

**Description:** Add a small evaluation-specific configuration/provider boundary using the supported adapters proven in task 1. Keep evaluator clients separate from generator clients and avoid changing ordinary generation authentication.

**Acceptance criteria:**
- [x] Require `RAGLAB_EVAL_MODEL` and `RAGLAB_EVAL_EMBEDDING_MODEL`; resolve endpoint fallback explicitly, preserve env-file precedence, validate timeout/retry settings, and expose only non-secret effective configuration. No implicit generator-model fallback (AC-05).
- [x] Same-endpoint credential reuse and different-endpoint authentication are tested; Entra uses refresh-capable auth. Defaults are 120-second request timeout and at most one transient retry with one transport retry owner; authentication/configuration failures stop subsequent judging (AC-11).
- [x] Owned clients/credentials close on success and partial setup/failure, borrowed clients remain open, and provider failures are sanitized (AC-13). Evaluator usage bookkeeping was subsequently removed at the user's request.

**Verification:**
- [x] `uv run --locked --extra eval pytest tests/unit/test_eval_providers.py tests/integration/test_ragas_compatibility.py tests/unit/test_config.py tests/unit/test_providers.py`
- [x] Inspect fake-provider call counts, refresh behavior, and error serialization for secret leakage; no live endpoint calls.

**Dependencies:** Task 1.

**Files likely touched:** `src/rag_quality_lab/eval/config.py` (new), `src/rag_quality_lab/eval/providers.py` (new), `tests/unit/test_eval_providers.py` (new), `tests/integration/test_ragas_compatibility.py`.

**Estimated scope:** Medium: 4 files.

**Completion evidence:** Verification path 1 (new observable behavior), implemented in tested increments. Added the canonical evaluator configuration/ownership suite with 25 cases; extended the existing real-Ragas fixture from five to nine cases rather than creating another adapter suite. New tests protect required evaluator identities, endpoint-specific credential isolation, safe configuration serialization, env-file precedence, numeric/URL validation, and resource ownership across setup/scoring/cleanup failures. The existing HTTP failure matrix now owns retry counts, sanitized failures/logs, timeout classification, and stopping after fatal errors. Two credential-lifetime cases prove real Azure bearer-provider refresh, borrowed-credential ownership, and stopping after token acquisition fails. The native experiment fixture now uses the production provider scope. One redundant borrowed-client setup case was replaced by the unique cleanup-failure case. Usage assertions were subsequently removed with the usage feature at the user's request.

The first new configuration/provider tests failed for the absent APIs; usage checks then failed on missing usage reporting, and the cleanup/log checks reproduced raw exception leakage before fixes. A real SDK timeout representation mismatch was diagnosed and fixed using the debugging workflow. Final full suite: 229 passed (including all 47 focused cases); no-extra environment: 220 passed, nine optional cases skipped. Core-only imports and CLI help, Ruff lint, all four changed Python files' formatting, `git diff --check`, and `uv build` passed. The 26 unrelated baseline formatting failures and existing Qdrant deprecation warnings remain. Sandbox cache/temp restrictions required approved reruns, with no application workaround.

The explicit different-endpoint authentication path is an evaluator API key; same-endpoint keyless auth uses Azure's async refresh-capable bearer provider. Borrowed SDK clients must match endpoint/timeout/retries. The user subsequently requested simpler evaluation without token/cost bookkeeping: `_Usage`, the SDK subclass, the usage property, and their assertions were removed. Clients now use `AsyncOpenAI` directly. The specification and provider notes reflect this authorized scope reduction. No new tests, CLI cutover, legacy removal, live scoring, Git commit, or later task was performed. See [provider notes](../tests/integration/ragas_compatibility.md#task-2-provider-boundary) for the interface and remaining integration obligations.

## Checkpoint: Framework and provider boundary (tasks 1–2)

- [x] Actual runner, metrics, local backend, and IR measures work with no external model traffic.
- [x] Locked installation/build and no-extra smoke pass; compatibility choices and any limitations are ready for review before broad integration.

## Task 3: Capture durable replay inputs

**Description:** Introduce the v2 contracts and capture composition. Reuse full golden validation and query component ownership, adding only the read-only inventory operation needed for frozen judgments/provenance. The legacy evaluator has no compatibility requirement; remove superseded pieces when they are replaced.

**Acceptance criteria:**
- [ ] Full dataset and requested IDs validate before external calls; subsets preserve golden order. Paginated full inventory rejects missing/mixed fingerprints and unresolved labels before generation; resolve source slugs or exact chunk IDs, including relevant chunks absent from search results (AC-03/08).
- [ ] Sequential capture uses one component scope and resolved runtime config. A unique run directory gets a running manifest, immediately persisted successful traces/snapshots, explicit failed/not-run rows, and exactly one row per selected question on orderly completion. Validate duplicate/missing/unexpected IDs and cross-check embedded question identity (AC-03/13/14).
- [ ] Bundle schemas support spec sections 5.2, 9, and 10: finite metric outcomes, input digest, all generation/evaluator provenance, relative paths, and final states. Preserve v1 shared artifact defaults; error/digest handling survives failure without claiming lost writes succeeded (AC-10/12).

**Verification:**
- [ ] `uv run --locked --extra eval pytest tests/integration/test_eval_capture.py tests/unit/test_qdrant_store.py tests/unit/test_golden.py tests/unit/test_artifacts.py`
- [ ] Test both modes with local Qdrant/fake query boundaries, multi-page inventory, invalid subset, empty search, mid-capture failure, and repeated run allocation; verify cleanup and saved rows.

**Dependencies:** Task 1; task 2 can proceed independently.

**Files likely touched:** `src/rag_quality_lab/schemas/eval.py`, `src/rag_quality_lab/eval/runner.py` (new), `src/rag_quality_lab/retrieval/qdrant_store.py`, `tests/integration/test_eval_capture.py` (new), `tests/unit/test_qdrant_store.py`.

**Estimated scope:** Medium: 5 files; focus on capture/bundle behavior, with no scoring or CLI cutover.

## Task 4: Evaluate snapshots with the fixed metric set

**Description:** Turn captured rows into one native Ragas dataset/experiment using the fixed metrics and useful domain predicates. Ragas owns evaluation execution and persistence; IR calculations and diagnostics run within the experiment. Remove superseded scoring code instead of maintaining the old evaluator.

**Acceptance criteria:**
- [ ] Faithfulness sees exact original answer text and only ordered selected context. Answer Relevancy uses the explicit judge/embedding pair. Parameterized no-answer/refusal/empty-context/failed-query cases obey status precedence; finite negative scores remain intact and nonfinite/malformed results are errors (AC-04/05/06/12).
- [ ] Real `ir-measures` agrees with relevant-first/later, no-hit, empty-result, exact-ID, and repeated-source/different-chunk fixtures. Reject duplicate/noncontiguous/over-K rankings; retain unjudged items, every eligible query, and binary full-inventory relevance. No new IR formulas (AC-07/08).
- [ ] Native results preserve ID-matched statuses/reasons and application routing, citation, refusal, search-scope, context, and existing generation usage diagnostics. Do not add evaluator token/cost bookkeeping. Concurrency stays one; timeout/malformed/auth failures preserve available results and distinguish unattempted metrics, while deterministic checks remain available (AC-11/13/16).

**Verification:**
- [ ] `uv run --locked --extra eval pytest tests/integration/test_ragas_compatibility.py tests/integration/test_eval_scoring.py tests/unit/test_metrics.py`
- [ ] Compare captured metric arguments and returned ID populations; assert no hidden retrieval/generation calls from scoring.
- [ ] Keep canonical tests for the new metric contracts and unchanged domain invariants. Delete tests that only protect obsolete evaluator behavior; do not recreate legacy coverage for its own sake.

**Dependencies:** Tasks 2 and 3.

**Files likely touched:** `src/rag_quality_lab/eval/runner.py`, `src/rag_quality_lab/eval/adapters.py` (new), `src/rag_quality_lab/eval/metrics.py`, `tests/integration/test_eval_scoring.py` (new), `tests/unit/test_metrics.py`.

**Estimated scope:** Medium: 5 files.

## Checkpoint: Saved-input evaluation (tasks 3–4)

- [ ] Capture through native persisted results works in both modes with fake services; coverage/status populations match selected IDs.
- [ ] Query ownership, exact refusal, and recorded scope remain protected; library IR definitions are verified. Inspect one successful row and one failure row before CLI cutover.

## Task 5: Expose v2 run results and failure coverage

**Description:** Switch `eval run` to capture then evaluate, add subset selection, and produce compact summaries and useful saved-artifact errors. Adapt existing CLI/lifecycle tests when changing the entry point.

**Acceptance criteria:**
- [ ] Evaluation options/defaults serve the Ragas workflow; repeatable `--question-id` works and labels subsets. No legacy option/default compatibility is required. Optional dependencies load lazily with an actionable `uv sync --locked --extra eval` error; ordinary command imports/help continue working (AC-01/03).
- [ ] Summary means use only `ok` values including zero, preserve binary numerators/denominators, show no-answer successes and unexpected answerable refusals, and enforce `eligible = scored + error + not_run` plus exclusions for every metric. Native paths and manifests finalize accurately; low scores and expected exclusions still yield complete runs (AC-06/11).
- [ ] Success JSON is one stdout object; progress goes to stderr. Partial/failure JSON has one structured error payload with saved manifest path and no preceding success/plain-text path. Distinguish provider from artifact/configuration failures without requiring old evaluation payloads or codes; ordinary command behavior stays unchanged (AC-17).

**Verification:**
- [ ] `uv run --locked --extra eval pytest tests/contract/test_cli_eval_run.py tests/integration/test_eval_execution_scope.py tests/unit/test_cli.py`
- [ ] Exercise complete, subset, partial, setup-failed, all-excluded, and all-refusing cases; parse stdout/stderr and verify referenced files actually exist.

**Dependencies:** Task 4.

**Files likely touched:** `src/rag_quality_lab/eval/runner.py`, `src/rag_quality_lab/eval/reports.py`, `src/rag_quality_lab/cli.py`, `tests/contract/test_cli_eval_run.py`, `tests/integration/test_eval_execution_scope.py`.

**Estimated scope:** Medium: 5 files.

## Task 6: Rescore portable evidence and compare modes

**Description:** Complete the CLI workflow with `eval rescore` and v2 `eval compare`. Both consume the same bundle contracts; rescore shares task 4's evaluation stage and comparison remains a local read-only operation.

**Acceptance criteria:**
- [ ] Rescore a copied bundle without original traces, corpus files, Qdrant, generation credentials, or checkout paths. Verify input digest/schema/IDs before judge calls; allocate a new run preserving bytes/digest and generation provenance with a source-run reference and new evaluator provenance. Assert zero retrieval, category-embedding, or generation calls (AC-09/10/14).
- [ ] Compare exactly one baseline and one routed v2 run without credentials/network. Parameterize spec section 11's required-match fields and report mismatches; allow different answers/replay digests/IDs/times/usage/locations. Reject v1 with regeneration guidance; accept complete/partial evidence for inspection (AC-15).
- [ ] JSON/human/optional compact Markdown expose values, counts, exclusions, and comparability notes. Emit a per-metric delta only for complete outcomes on identical scored IDs; suppress deltas with errors/unattempted outcomes or unequal populations. Separate resource diagnostics and do not declare a universal winner (AC-15/17).

**Verification:**
- [ ] `uv run --locked --extra eval pytest tests/integration/test_eval_workflow.py tests/contract/test_cli_eval_compare.py tests/contract/test_cli_eval_run.py`
- [ ] Extend workflow coverage to invoke rescore CLI with copied bundles, tampered inputs, and generation boundaries set to fail if called; test comparison with all provider/network boundaries prohibited.

**Dependencies:** Task 5.

**Files likely touched:** `src/rag_quality_lab/eval/runner.py`, `src/rag_quality_lab/eval/reports.py`, `src/rag_quality_lab/cli.py`, `tests/integration/test_eval_workflow.py`, `tests/contract/test_cli_eval_compare.py`.

**Estimated scope:** Medium: 5 files; reuse established capture/scoring contracts, no second runner.

## Checkpoint: End-to-end CLI (tasks 5–6)

- [ ] Offline run → native results → copied-bundle rescore → comparison works, including partial failures and digest rejection.
- [ ] `uv run --locked --extra eval pytest tests/integration tests/contract` passes; inspect native results and summaries before the final removal audit.

## Task 7: Retire superseded evaluation code

**Description:** Audit and remove any remaining legacy orchestration, schemas, aggregate IR formulas, and report construction not already removed in earlier tasks. No legacy parity gate applies. Keep JSON benchmark cases, useful deterministic predicates, and golden-data validation. Remove obsolete evaluation tests; retain unique coverage for new contracts and unchanged core behavior.

**Acceptance criteria:**
- [ ] Ragas is the sole general evaluation path; no legacy engine flag, duplicate hit/MRR formulas, stale schema exports, or unused report runner remains (AC-18).
- [ ] Remaining report/schema tests cover status counts, source matching, unknown scope, and comparison rules under v2; ordinary trace/corpus schema defaults and readers remain unchanged.
- [ ] JSON benchmark cases/labels and corpus content are preserved; test/import searches find no live references to removed evaluation APIs. Historical reports impose no compatibility or migration requirement.

**Verification:**
- [ ] `uv run --locked --extra eval pytest tests/unit tests/integration tests/contract`
- [ ] `rg -n 'calculate_hit_rate_at_k|calculate_mrr|calculate_evaluation_metrics|EvaluationRun|EvaluationMetrics' src tests` — inspect remaining hits for intentional v2 usage, not merely a renamed old path.

**Dependencies:** Task 6.

**Files likely touched:** `src/rag_quality_lab/eval/metrics.py`, `src/rag_quality_lab/eval/reports.py`, `src/rag_quality_lab/schemas/eval.py`, `src/rag_quality_lab/schemas/__init__.py`, `tests/unit/test_eval_reports.py`.

**Estimated scope:** Medium: 5 files; public caller/test migration belongs to tasks 4–6.

## Task 8: Document the workflow and verify completion

**Description:** Update the user guide, architecture, environment example, and affected contracts to match the verified v2 implementation. Record framework choices from task 1 and run final checks without broad unrelated code formatting.

**Acceptance criteria:**
- [ ] Document locked eval installation, explicit judge/embedding/auth settings, new CLI options/defaults, subset/full run, copied-bundle rescore, local comparison, actual native result locations, and structured partial-error output. Update architecture flows and CLI/artifact contracts (AC-18).
- [ ] Explain `mrr` → `mrr_at_k`, application checks vs Ragas scores, coverage/refusal interpretation, v1 historical evidence, model mutability, small-benchmark limits, and live rescore's judge calls. Remove README claims that conflict with the newly added bounded evaluation scope.
- [ ] AC-01–AC-18 map to passing evidence; full offline suite, changed-file quality checks, package build, and clean no-extra smoke pass. Report unrelated baseline check failures and whether live scoring remains unverified (AC-01/16/18).

**Verification:**
- [ ] `uv sync --locked --extra eval`; `uv run --locked --extra eval pytest`
- [ ] `uv run --locked --extra eval ruff check src tests`; `uv run --locked --extra eval ruff format --check src tests` — compare against pre-change baseline and require changed files clean.
- [ ] `uv build`; in a separate clean environment install core only and verify package/query imports, root/query/corpus/trace help, local corpus inspection, and actionable missing-extra evaluation behavior.
- [ ] Review documented command examples against CLI help and offline fixture bundles; no invented live results.

**Dependencies:** Task 7.

**Files likely touched:** `README.md`, `docs/architecture.md`, `.env.example`, `specs/001-rag-quality-lab/contracts/cli.md`, `specs/001-rag-quality-lab/contracts/artifacts.md`.

**Estimated scope:** Medium: 5 documentation/configuration-example files.

## Checkpoint: Offline implementation complete (tasks 7–8)

- [ ] All acceptance criteria have evidence, core behavior is preserved, and one supported evaluation path remains.
- [ ] Plan assumptions and external compatibility decisions have been resolved or explicitly reported; changes are ready for human review before merge/deploy.

## Optional follow-up: Live portfolio verification

**Dependencies:** Task 8 and available compatible evaluator/generation deployments, credentials, and indexed corpus. This is not a blocker for offline implementation completion and is not performed during planning.

- [ ] Run a small question selection first, including answerable and no-answer cases; inspect actual judge output.
- [ ] Run both full modes with matching settings, rescore a copied bundle, and produce a comparison in new artifact directories.
- [ ] Inspect selected individual judgments and any observed disagreement/error. Record measured outcomes and exactly what was reviewed; if unavailable, state “live scoring not run.” Never overwrite historical examples or fabricate evidence.
