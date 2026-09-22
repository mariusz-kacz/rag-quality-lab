# Implementation Plan: Ragas evaluation

Status: Task 1 authorized by explicit user request and completed on 2026-09-22. Tasks 2-8 remain unstarted. The planning-stage scope below is historical; implementation evidence is recorded in [todo.md](todo.md) and the [compatibility notes](../tests/integration/ragas_compatibility.md).

Input: [SPEC-ragas-evaluation.md](../SPEC-ragas-evaluation.md), especially sections 6–11 and AC-01–AC-18. Task checklist: [todo.md](todo.md). Inspected on 2026-09-21 at `15fabc588040bf302ce5e8651e90e97682167050`, matching the specification baseline.

## Overview

Replace the bespoke general evaluation path with capture followed by a Ragas experiment over saved inputs. Keep the existing golden set and query pipeline. Add Faithfulness and Answer Relevancy, use `ir-measures` for retrieval scores, and retain application diagnostics. Deliver unique v2 run bundles, replay-only rescoring, and comparison under matching conditions. Eight focused implementation tasks cover the change; live demonstration is a separate optional activity.

User clarification (2026-09-22): preserve the benchmark cases and labels in JSON, but treat the old evaluation implementation as disposable. Ragas is the only evaluation framework, using native execution, metrics, and persistence. Retained domain checks and `ir-measures` run inside that experiment. No legacy evaluation API, option/default, schema, report, score parity, or fallback compatibility is required. Delete superseded code and obsolete tests as replacements land; Task 7 is a final removal audit rather than a reason to keep old code alive. Core query/corpus/trace protections still apply.

Only this plan and its task checklist are produced now. No dependencies are installed, tests or provider calls run, or application files changed during planning. The existing untracked specification and `artifacts/eval/traces/` are left intact. No `tasks/plan.md` or `tasks/todo.md` existed. Existing Spec Kit artifacts are background context, not the task target for this request; no project tracker override was found.

## Repository evidence

Paths below are relative to the repository root.

| Evidence | Planning consequence |
| --- | --- |
| `pyproject.toml`: Python >=3.12, Hatchling, pytest and Ruff; no eval extra | Add a locked optional extra; prove installation on this Windows development environment before refactoring. |
| `eval/reports.py::run_evaluation` resolves config once, shares components, then builds legacy aggregates/reports | Reuse composition and ownership patterns, but replace orchestration rather than wrapping the old scorer inside Ragas. Paths in this table abbreviated under `src/rag_quality_lab/`. |
| `rag/pipeline.py::resolve_query_components` uses `ExitStack`; `run_query` returns a saved trace | Keep one scope per capture, borrow its components for each query, then close it before judging. |
| `retrieval/qdrant_store.py` stores `index_fingerprint` in each payload; has search/upsert but no inventory operation | Add a read-only paginated payload inventory; do not infer provenance from local corpus files or search results. |
| `schemas/eval.py::GoldenSet` requires 12–20 questions and required case types | Validate the complete dataset before selecting IDs; a smoke subset must not be revalidated as a full GoldenSet. |
| `eval/metrics.py` has source/chunk matching, citation/refusal/routing predicates, ID matching, and bespoke IR formulas | Keep only predicates needed by the new contracts; use verified library calculations without requiring legacy parity. |
| `schemas/artifacts.py::read_json_artifact` accepts `expected_schema_version`, default `1.0` | Explicitly request evaluation v2. Keep shared defaults and ordinary trace/corpus formats at v1. |
| `cli.py` eagerly imports report constants/errors despite lazy run wrappers | Keep ordinary commands dependency-light and guard optional imports. Design evaluation options/defaults for the new workflow; legacy defaults are not constraints. |
| `providers.py::_foundry_api_key` snapshots an Entra token; generation uses Responses | Evaluator clients need a separate supported adapter and refresh-capable authentication; do not assume the generator client is suitable. |
| `tests/integration/test_eval_execution_scope.py`, query/ingest workflows, citation/chat tests | Carry forward lifecycle, scope, exact refusal, index compatibility, and incomplete-output regressions. |
| `README.md`, `docs/architecture.md`, `specs/001-rag-quality-lab/contracts/{cli,artifacts}.md` describe legacy evaluation | Document the Ragas workflow and `.env.example`; any retained old reports are historical files, not a supported contract. |

## Architecture decisions

1. **Prove external boundaries first.** Task 1 selects tested pins and exercises the actual Ragas experiment, metric objects, and local result round-trip with fake external model responses. Use collections metrics as described in the [Ragas migration guide](https://docs.ragas.io/en/stable/howtos/migrations/migrate_from_v03_to_v04/); experiments support dataset execution and local storage in the [experiment documentation](https://docs.ragas.io/en/stable/concepts/experimentation/). These documents were checked during planning; they do not establish compatibility with a particular package build or Azure deployment. No version or backend filename is assumed.
2. **Keep a small evaluation boundary.** Use `eval/runner.py` for capture/evaluation composition and bundle handling, `eval/adapters.py` for metric mapping and IR conversion, and small `eval/config.py` / `eval/providers.py` modules for the distinct evaluator lifecycle. Retain `eval/metrics.py` only for plain application checks after migration; there is no need to rename it just to match the spec's suggested `checks.py`. Reduce `eval/reports.py` to summaries/comparison. Keep v2 contracts in `schemas/eval.py` without Ragas imports. Do not introduce a registry, engine selector, provider framework, or Ragas imports into the query path.
3. **Capture evidence before scoring.** Preflight full golden validation, selected IDs, effective config, and full index inventory before generation. Require one known index fingerprint and resolve every relevance label against the inventory. Acquire query components once; execute sequentially and persist every successful trace and replay row immediately, plus explicit failures. Query resources close before evaluator resources open. Preserve golden order by ID, independent of framework ordering.
4. **Use self-contained, versioned bundles.** Allocate a UTC timestamp plus collision-resistant run ID without overwriting. Write `running` manifest, `inputs.jsonl`, framework-owned result files, and `summary.json`; record actual relative paths. Contracts include Question/QueryTrace snapshots, frozen relevant IDs, sanitized errors, explicit statuses, and all provenance in spec section 10. Use a documented deterministic digest of input bytes, preserving those bytes on rescore, and canonical JSON digests for question content and non-secret configuration. Finalize as complete/partial/failed; interrupted runs remain running. No automatic resume.
5. **Separate immutable generation evidence from current evaluator provenance.** Record source revision and a deterministic digest of relevant source/configuration, prompt/category digests, active collection/fingerprint, deployment identities and parameters, package versions, adapter/eligibility versions, and effective evaluator settings. Define the source-file set explicitly, including dirty relevant files but excluding credentials, outputs, and unrelated documentation. Rescore copies generation provenance and input digest, assigns a new run ID and source reference, and records its current evaluator identity separately.
6. **Make eligibility and coverage explicit.** Apply spec section 6 before any metric call. Faithfulness receives the original answer with citation markers and only ordered included context. Expected no-answer rows exclude both quality metrics even on capture failure; unexpected refusals exclude Faithfulness but still attempt Answer Relevancy. Failed answerable queries remain `not_run`, not inferred exclusions. Empty context excludes Faithfulness; undefined/nonfinite output is an error. Preserve finite negative relevancy. Every selected ID gets one status per metric.
7. **Delegate IR calculations inside Ragas.** Resolve binary judgments over unique chunk IDs; keep repeated sources as distinct chunks and unjudged results in the ranking. Validate contiguous ranks, uniqueness, and at most K results, supplying strictly descending rank-derived scores if needed. Include successful empty-result questions. Use library Success@K and RR@K, with backend behavior proven early; do not retain parallel formulas. [ir-measures definitions](https://ir-measur.es/en/latest/measures.html) distinguish Success from document Recall and expose rank/cutoff semantics.
8. **Share one evaluation stage.** `eval run` calls it after capture; `eval rescore` validates a copied bundle and its digest before any judge request and invokes that same stage. Rescore must not load generation/Qdrant configuration, corpus files, or original source paths. Compare reads local bundles only and applies the strict compatibility fields from spec section 11. It allows different replay digests/answers and suppresses individual deltas when scored IDs differ or eligible outcomes are incomplete.

## Behavior that must remain unchanged

- Golden questions, labels, source snapshots, routing/category policy, retrieval ranking, chunking, context selection, prompts, and generation settings/behavior.
- Exact refusal recognition, rejection of incomplete Responses output, recorded `searched_categories` (unknown remains unknown), citation identifier validation, and incompatible-ingestion protection.
- Run-scoped query clients/category embedding reuse; owned clients close on success, failures, and partial setup; injected clients remain caller-owned.
- Ordinary corpus/query/trace commands, help, artifact versions, and environment precedence. The global `--env-file` still precedes subcommands. Core imports work without eval dependencies.
- In the new workflow, poor quality is a successful evaluation, while execution/configuration/artifact failures remain nonzero. Old evaluation interfaces, defaults, error payloads, and report formats have no compatibility guarantee.

Allowed changes: v2 evaluation schemas/outputs, `mrr` becoming `mrr_at_k`, addition of repeatable `--question-id` and `eval rescore`, stricter comparison, and removal of the legacy general evaluator. No v1 score migration or fallback engine.

## Task list and dependencies

| Task | Reviewable result | Depends on |
| --- | --- | --- |
| 1 | Locked framework compatibility fixture | None |
| 2 | Explicit evaluator configuration and owned provider lifecycle | 1 |
| 3 | Durable, provenance-bearing query capture | 1 |
| 4 | Fixed metric experiment with eligibility and diagnostics | 2, 3 |
| 5 | v2 `eval run` with summaries and failure reporting | 4 |
| 6 | Copied-bundle rescore and compatible-run comparison | 5 |
| 7 | Retirement of superseded evaluation machinery | 6 |
| 8 | Updated user/contracts documentation and final validation | 7 |

Checkpoints follow tasks 1–2, 3–4, 5–6, and 7–8. Tasks 2 and 3 could proceed independently after task 1; remaining shared runner/report/CLI changes should be sequential. Prefer one implementation stream for this repository's size. Remove replaced legacy evaluation paths within each relevant task; do not invest in keeping them working during the transition. Keep tests for the new evaluation contracts and ordinary application behavior passing. Task 7 audits remaining obsolete code and tests.

## Assumptions and implementation decisions still to verify

- The collection is stable during capture and the pinned corpus was fully ingested. No concurrent ingestion, locking system, or index repair is introduced. Reject mixed/missing fingerprints and unresolved labels.
- For an isolated query failure, preserve its failure row and continue independent questions. If setup or a fatal failure stops capture, finalize unattempted selected IDs as `not_run` when storage remains writable. An abrupt interruption may leave an incomplete `running` bundle, which rescore rejects. Never claim an artifact was saved if its write failed.
- Expected no-answer exclusions take precedence; for an answerable refusal with empty context, use `refusal` as the Faithfulness reason. Treat a successful but blank/non-substantive answer as a visible invalid-output error rather than inventing a quality score; confirm the existing generator normally rejects that state.
- Exact Ragas/provider versions, local backend serialization, supported IR backend on Windows, metric default identities, concurrency controls, and structured-output repair behavior are task 1 evidence, not settled by this plan. If compatibility fails, record the concrete blocker before a broad refactor.
- Evaluator settings resolve once: explicit judge and embedding models; recorded endpoint fallback only; timeout 120 seconds and one transient retry by default. Reuse application credentials only for the same normalized endpoint. A distinct endpoint needs explicit compatible authentication. Keep one transport retry owner and record framework repair attempts separately.
- No live credentials/deployment suitability are assumed. Offline test completion and a real portfolio demonstration are separate claims. No planning question blocks review; unresolved library choices are bounded by the first checkpoint.

## Risks and mitigations

| Risk | Impact | Mitigation / evidence |
| --- | --- | --- |
| Ragas/adapter API drift or unavailable IR wheel/backend on Windows | High | Lock and exercise actual runner, both metrics, persistence, and cutoff IR measures before migration. |
| Lost/null-coerced status columns or omitted empty-result queries | High | Round-trip explicit states and negative/zero values; validate result ID populations and coverage conservation. |
| Credential leakage, expired token, multiplied retries | High | Endpoint-aware auth tests, refresh-capable evaluator auth, sanitized failure payloads, bounded requests, ownership tests. |
| Partial runs look like high-quality complete runs | High | Status-driven counts, answerable refusal/abstention display, saved failure evidence, nonzero exit, population-aware deltas. |
| Provenance omits dirty code or rescoring rewrites generation identity | High | Explicit file/digest rules; mutate compatibility fields in parameterized tests; copied-bundle replay tests. |
| Optional dependency or v2 changes break core workflows | High | Lazy integration imports, separate clean no-extra environment, unchanged schema defaults, core regressions. |
| Hosted deployments change behind stable names; 16 cases overstate findings | Medium | Capture provider model metadata when available; document judge bias, nondeterminism, small sample, and absence of universal thresholds. |

## Validation strategy and completion boundary

Use a small number of parameterized suites over meaningful boundaries. The real Ragas compatibility test must fake only external LLM/embedding calls, not the experiment runner, metric implementations, or local backend. Other workflow tests may inject captured traces and use local Qdrant/fakes. No ordinary test needs credentials or asserts exact live model scores.

Validation matrix: framework/install (AC-01/02/16); mapping/eligibility/IR (AC-04/06/07/08/12); provider/lifetime/failures (AC-05/11/13); capture/replay/integrity/IDs (AC-03/09/10/14); comparison/CLI (AC-15/17); retirement/docs (AC-18). Detailed commands and acceptance conditions are in the checklist.

Implementation checks: `uv sync --locked --extra eval`, focused pytest suites, then `uv run --locked --extra eval pytest`, Ruff lint/format checks, and `uv build`. Establish lint/format baseline first; fix changed-file issues and report unrelated pre-existing failures without a repository-wide formatting detour. Verify no-extra installation in a separate clean environment, not the environment already containing Ragas. There is no configured type checker or CI workflow to invent for this change.

Offline completion requires AC-01–AC-18, no superseded general evaluator, preserved core regressions, and accurate docs. Optional live verification starts with a small subset and then both complete modes under matching settings, followed by copied-bundle rescore and comparison. Record whether it ran and which judgments were actually inspected; never fabricate evidence. Review these planning artifacts before beginning any implementation.
