# Answer-focused evaluation verification

## Current evaluator: run only

- [x] Removed `eval rescore`, `eval compare`, saved-row loading/validation, and
  experiment compatibility/delta rules. Deleted `eval/reports.py` entirely.
- [x] Kept one summary helper in the runner: means, scored/eligible counts, and
  refusal diagnostics. Per-question results retain scores and judge reasons.
- [x] Preserved all four metrics, grading notes, finite-score validation, failure
  reporting, client cleanup, and the native Ragas dataset/experiment workflow.
- [x] Updated CLI help, documentation, and tests for the reduced feature scope.
  Removed tests specific to deleted saved-file/compare features; retained run,
  query/judge failure, no-answer, and provider-isolation coverage.
- [x] Verified 205 tests, Ruff lint/format, and package builds. The smaller summary
  reproduces all four means and coverage counts from run
  `d8987727ed8f458c96b868bbad60b1a9` exactly without new model calls.

The records below describe earlier implementation stages, including capabilities
subsequently removed at the user's request.

## Earlier verification

- [x] Added grading notes to all 16 existing questions without changing IDs,
  text, source labels, or routing expectations.
- [x] Primary native Ragas answer_success: pass/fail with a reason.
- [x] Semantic no-answer judgment; completeness and evidence in the rubric.
- [x] Faithfulness and source Hit/MRR retained as supporting metrics.
- [x] Routing/citation/refusal detection separated into diagnostics.
- [x] Removed evaluator embeddings and Answer Relevancy.
- [x] Retained the two-file native dataset/experiment workflow.
- [x] Grading notes required for saved inputs and compared across runs.
- [x] Documented blinded human review and held-out judge validation.
- [x] Full regression suite, lint/format, build, and core-only smoke.

Verification: **201 tests passed**. Ruff lint and changed-file formatting passed.
Wheel and source distribution builds passed. The isolated core-only environment
passed imports, seven CLI help paths, golden validation, and the missing-extra
check. Seven existing Qdrant deprecation warnings remain.

Tests cover real DiscreteMetric structured output, reasons, exact judge inputs,
alternate refusal detection, quality failures versus provider failures, changed
grading-note comparisons, and preventing rubric leakage into generation prompts.
Live Azure scoring and human judge validation have not been run; grading notes
remain draft criteria.

## Live index preflight fix

The live collection contained 316 chunks from 26 sources, all missing
`index_fingerprint`. The evaluator rejected this legacy index but hid the reason
behind `Evaluation failed (QdrantStoreError)`.

Index validation now reports missing fields and rebuild guidance, distinguishes
empty/mixed/duplicate indexes, and retains sanitized remote errors. Regression
tests cover CLI text/JSON, no model calls before preflight passes, and cleanup.
The live CLI now shows the actionable message. The collection was not modified.

Verification after the fix: 205 tests passed, Ruff lint and changed-file formatting
passed, and package builds passed. Live scoring remains blocked until the legacy
index is rebuilt or replaced with a newly ingested collection.

## Grading criteria aligned with the questions

- [x] Reviewed all 16 questions against the rubric audit; revised the 14 answerable
  notes while preserving both no-answer criteria and every question/label field.
- [x] Made unrequested examples, caveats, cost explanations, and extra controls
  optional; retained essential completeness and factual-support requirements.
- [x] Clarified judge instructions for optional detail, equivalent explanations,
  and actual overclaims versus missing disclaimers; recorded metric version 3.
- [x] Documented that rescore uses saved notes, not the current golden file.
- [x] Verified 205 tests, Ruff lint/format, package builds, and an exact comparison
  of all question fields other than grading notes against the pre-change file.

The original live baseline/routed results were available for the rubric audit;
the earlier index blocker above is historical. Revised criteria have not been
rescored or validated against human judgments. Existing results retain their
original scores. Next: review/rescore copied answers with the revised notes.

## Corpus preparation and live verification

- [x] Exclude the snapshots' four exact administrative heading names from chunking.
  Keep substantive provenance guidance and all source files/metadata intact.
- [x] Embed each passage with its manifest title and section path. Preserve the
  passage body and token accounting used for generation.
- [x] Include exact embedding input in the index fingerprint; test title changes,
  heading changes, and rejection of the previous body-only index format.
- [x] Verify 209 tests, Ruff lint/format, package builds, and local corpus coverage.
  Ten warnings come from the existing Qdrant recreation deprecation.
- [x] Ingest 285 searchable chunks from all 26 sources into
  `raglab_prepared_20260923_0c7790b2`; verify the original `rag_quality_lab`
  collection is unchanged. Only the collection setting in `.env.local` was
  changed to activate the prepared index.
- [x] Run all 16 baseline questions with unchanged questions, labels, rubric,
  evaluator configuration, models, and runtime settings.

Prior run: `artifacts/eval/787cb4b601524b31b5f28f1b8d6f3cc3/experiments/scores.jsonl`.
Prepared-corpus run: `artifacts/eval/77948028815047f39ce916c2dfa8b751/experiments/scores.jsonl`.
This is a manual before/after review of different indexes, not a baseline/routed
comparison through `eval compare`. Each run generated fresh answers.

| Metric | Prior corpus | Prepared corpus |
| --- | --- | --- |
| answer_success | 12/16 (0.75) | 14/16 (0.875) |
| faithfulness | 0.9184 | 0.8980 |
| source_hit_at_k | 12/14 (0.8571) | 11/14 (0.7857) |
| source_mrr_at_k | 0.6071 | 0.6667 |

No administrative passages appeared in the selected contexts. The injection
mitigation summary now ranks first for q-answerable-004; that answer provides
concrete mitigations and passes. The context/latency answer also now passes.
Both expected no-answer cases still refuse appropriately.

Remaining failures are q-cross-category-005 (evidence coverage/relevance checks)
and q-multi-category-002 (prompt guidance and tradeoff). The security-boundary
answer deserves judge review: answer_success passes it, but faithfulness is 1/3,
and its selected passages do not establish the retrieved-instruction boundary.
The source-hit decline includes valid alternative sources missing from current
labels as well as that security retrieval miss. These mixed results from one run
do not establish a general improvement or resolve judge calibration.
