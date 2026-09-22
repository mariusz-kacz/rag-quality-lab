# Specification: Ragas evaluation for RAG Quality Lab

Status: ready for implementation planning  
Date: 21 September 2026  
Repository: [mariusz-kacz/rag-quality-lab](https://github.com/mariusz-kacz/rag-quality-lab)  
Inspected baseline: [15fabc588040bf302ce5e8651e90e97682167050](https://github.com/mariusz-kacz/rag-quality-lab/tree/15fabc588040bf302ce5e8651e90e97682167050)

This specification defines the first implementation. “Must” denotes acceptance requirements. Suggested module names may change if the responsibilities and contracts remain clear. Check the actual implementation branch before editing; preserve fixes introduced after the inspected baseline.

User clarification (2026-09-22): Ragas is the only evaluation framework. Preserve the evaluation cases and labels in the existing JSON datasets. The old evaluator, its interfaces/defaults, reports, schemas, and scores are not compatibility targets. Use native Ragas execution, metrics, and persistence with only the adapters needed for this application's inputs and diagnostics. `ir-measures` is a metric library invoked inside that Ragas experiment, not a separate evaluation path. Ordinary query, retrieval, corpus, and trace behavior remains outside this replacement.

## 1. Objective

Replace the bespoke evaluation execution and general-purpose scoring in RAG Quality Lab with Ragas experiments and established metric implementations.

The completed feature must let a developer:

1. Run the existing baseline-vector and routed-vector pipelines against the existing golden questions.
2. Measure answer faithfulness and answer relevance using Ragas.
3. Preserve Hit@K and MRR using standard information-retrieval calculations.
4. Inspect routing, citation, refusal, and token diagnostics.
5. Re-evaluate saved answers without repeating retrieval or answer generation.
6. Compare two retrieval modes under matching experimental conditions.

The useful demonstration is a reproducible experiment with understandable failures and limitations. Introducing additional platforms is outside this change.

## 2. Decisions and scope

| Decision | Required implementation |
|---|---|
| Main evaluation framework | Ragas, using its supported experiment execution and local result storage |
| Initial Ragas metrics | Faithfulness and Answer Relevancy |
| Standard retrieval calculations | `ir-measures`: Success@K and mean RR@K |
| Application-specific checks | Small deterministic functions retained from the current implementation |
| Source dataset | Existing `golden/questions.json`; currently 16 questions, 14 answerable and two no-answer |
| Generation pipeline | Existing `run_query()`, with run-scoped component reuse and cleanup |
| Evaluation inputs | Saved snapshots of actual query execution |
| Result access | CLI, native Ragas local results, and a small machine-readable summary |
| Comparison scope | Baseline versus routed retrieval; retrieval mode is the sole intended experimental variable |
| Initial scheduling | Sequential query capture; evaluator concurrency of one |
| Quality gates | Scores and diagnostics only; no arbitrary universal passing threshold |

Out of scope:

- DeepEval, LangSmith, MLflow, hosted dashboards, or an additional tracking service.
- Synthetic dataset generation, automatic prompt optimization, or an enlarged benchmark.
- Reference-answer authoring and reference-based Context Precision, Context Recall, or Factual Correctness.
- Changes to routing policy, chunking policy, retrieval ranking, prompts, or answer-generation behavior.
- A custom metric plugin framework, configurable workflow engine, parallel query execution, or distributed jobs.
- Building a general compatibility layer across several Ragas API generations.
- Automatic live evaluation during ordinary unit tests.

The reference-based metrics are a possible follow-up. Source identifiers in the current golden set are relevance labels, not reference answers. Do not pass them to a metric's `reference` field.

## 3. Current integration points

The inspected repository provides the required execution evidence:

| Existing component | Treatment |
|---|---|
| `rag/pipeline.py::run_query` | Reuse for query capture |
| `resolve_query_components` | Reuse its context manager and resource ownership |
| `QueryTrace` | Reuse question, ordered retrieval results, selected context, answer, citations, and usage |
| `QueryTrace.searched_categories` | Preserve as an execution fact |
| `eval/golden.py` | Preserve golden-data loading and validation |
| `eval/metrics.py` | Retain only useful domain checks and ID matching needed by Ragas; remove superseded Hit@K/MRR calculations without legacy parity requirements |
| `eval/reports.py` | Replace the old evaluation runner and large report construction with a thin Ragas integration and summary/comparison functions |
| `schemas/eval.py` | Replace fixed legacy evaluation schemas with the small versioned contracts specified below |
| `cli.py` | Preserve the eval command group; add rescoring and adapt outputs |
| Qdrant index fingerprint | Reuse for provenance; obtain the fingerprint from the active index |

Keep the recent fixes: exact refusal recognition, recorded search scope, incompatible-ingestion protection, run-scoped clients, and rejection of incomplete provider output.

Ragas must not be imported into retrieval, routing, generation, or corpus policy code. The evaluation package adapts application outputs into framework inputs.

## 4. Dependency and API compatibility

### 4.1 Installation

Add a Python optional dependency extra named `eval`, containing Ragas, `ir-measures`, and any provider integration dependency actually required by the selected Ragas adapters. Commit the resolved `uv.lock`.

The documented installation command must be:

```bash
uv sync --locked --extra eval
```

Select and pin tested compatible package versions during implementation. Do not invent a version number from this specification. Record the versions in every evaluation manifest.

Core query/corpus commands and their help must remain usable without the extra. Evaluation commands should use lazy imports and produce an actionable installation error when it is missing.

### 4.2 Supported Ragas path

Use the supported `experiment`/dataset APIs for execution and local persistence. The current documentation recommends metrics from `ragas.metrics.collections`, including `Faithfulness` and `AnswerRelevancy`, with `score` or `ascore`. Prefer these over legacy sample-based wrappers. [Ragas migration guidance](https://docs.ragas.io/en/stable/howtos/migrations/migrate_from_v03_to_v04/).

Before a broad refactor, demonstrate with a tiny offline fixture that the selected version can:

- Execute the real Ragas experiment runner with substituted judge/embedding boundaries.
- Accept the intended row shape and return metric result objects.
- Persist one local result row and load it back.
- Preserve custom diagnostic columns and explicit missing/error states.

Keep this as an integration test. A test replacing the entire Ragas runner with a mock does not establish compatibility.

Do not rewrite a Ragas metric if a provider adapter fails. Resolve the adapter/version mismatch or report the concrete blocker.

## 5. Execution flow

### 5.1 Capture then evaluate

`eval run` has two stages.

**Capture stage**

1. Validate CLI/configuration, the full golden dataset, and index provenance before query generation.
2. Resolve effective runtime settings once.
3. Acquire query components once for the selected retrieval mode.
4. Execute the selected questions sequentially using `run_query()`.
5. Persist each successful trace and a replay input row immediately. Persist a failure row when query execution fails.
6. Close owned query components.

This is a small application-capture loop. Do not preserve the old scoring/reporting engine inside it.

**Evaluation stage**

1. Construct the Ragas dataset from the saved input rows.
2. Execute the per-row evaluation function through Ragas.
3. Score eligible rows with the fixed metric set, attach domain diagnostics, and preserve metric errors.
4. Let Ragas persist the detailed results.
5. Produce the small summary and finalize the manifest.

The same evaluation stage is used by `eval rescore`. It must not call `run_query()`.

### 5.2 Replay input contract

Each row in `inputs.jsonl` must contain:

| Field | Contract |
|---|---|
| `question_id` | Stable nonempty ID from the golden set |
| `question` | Snapshot of the existing Question model, including expected labels |
| `execution_status` | `succeeded`, `failed`, or `not_run` |
| `trace` | Complete QueryTrace snapshot for successful execution; otherwise null |
| `relevant_chunk_ids` | Frozen relevance judgments resolved for this question; empty for no-answer cases |
| `error` | Sanitized stage/type/message for a failed execution; otherwise null |

Trace paths may be included for convenience, but rescoring must be possible using the snapshot alone. It must not require the original Qdrant service, current corpus files, generation credentials, or the original checkout.

Validate exactly one row per selected golden question and restore golden order after framework execution. Reject duplicate, missing, and unexpected IDs. A failed execution is a present failure row, not a silently missing question.

Store an input digest in the manifest. Rescoring must verify it before making judge calls.

### 5.3 Mapping to Ragas

| Metric argument | Source |
|---|---|
| `user_input` | `trace.question.text` |
| `response` | `trace.answer_result.answer_text` |
| `retrieved_contexts` for Faithfulness | Ordered `content` values from `trace.context_build.included_chunks` |
| Judge model | Explicit evaluator configuration |
| Embedding model for Answer Relevancy | Explicit evaluator embedding configuration |

Faithfulness must see only the context supplied to generation. Do not pass excluded chunks, all corpus documents, golden relevance labels, or a fresh retrieval result. The provider must see the original generated answer, including citation markers; no answer rewriting is allowed in the adapter.

The original ranked retrieval results remain available separately for Hit@K/MRR. Preserve the distinction between retrieved candidates and selected generation context.

## 6. Metric and eligibility contracts

### 6.1 Required framework metrics

| Artifact name | Implementation | Eligible cases | Interpretation |
|---|---|---|---|
| `faithfulness` | Ragas Faithfulness | Successful answerable cases with nonempty selected context and a substantive answer | Estimated support of answer claims in the supplied context |
| `answer_relevancy` | Ragas AnswerRelevancy | All successful answerable cases, including unexpected refusals | Alignment of the response with the question |
| `hit_rate_at_k` | Mean `ir-measures Success@K` | Successful answerable cases with resolved relevance judgments | Fraction with at least one relevant chunk in the retrieved top K |
| `mrr_at_k` | Mean `ir-measures RR@K` | Same retrieval-eligible cases | Rank of the first relevant retrieved chunk |

Use built-in metric prompts and default metric parameters initially; record their effective identities/parameters. No custom LLM judge prompt is required.

Faithfulness does not establish real-world truth. Answer Relevancy does not establish factual correctness. Ragas Answer Relevancy uses an LLM and embeddings; its cosine-based score can be negative. Preserve the supported metric's finite raw score rather than applying the legacy all-metrics-`0..1` schema or clamping it. [Faithfulness](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/), [Answer Relevancy](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/answer_relevance/).

### 6.2 Refusals, empty context, and failed execution

- For the two expected no-answer questions, both Ragas metrics are `not_applicable`, regardless of the generated output. Score their abstention behavior separately.
- For an answerable question that receives a refusal, Faithfulness is `not_applicable` with reason `refusal`. Answer Relevancy is still attempted. The abstention diagnostic records an incorrect refusal.
- For empty selected context, Faithfulness is `not_applicable` with reason `empty_generation_context`. Do not invent a perfect score.
- An empty retrieved list on an otherwise successful query is a valid retrieval miss: Hit@K and RR@K are zero.
- Failed query execution makes otherwise eligible dependent metrics `not_run` with reason `query_failed`. Golden-label exclusions still take precedence: Ragas metrics for an expected no-answer case remain `not_applicable`. Do not fabricate an answer, score zero, or classify a failed call as a refusal.
- An undefined/nonfinite Ragas result is a metric `error` with the available reason. It is never silently converted to zero or one.

A model that refuses everything must not look successful because its remaining Faithfulness scores are high. Always display answerable refusal counts, per-metric coverage, and abstention accuracy next to the quality scores.

### 6.3 Standard retrieval adapter

Preserve the existing relevance definition: a retrieved chunk is relevant when its source slug or exact chunk ID occurs in `expected_relevant_sources`.

At capture preflight, obtain a read-only inventory of the active lab collection sufficient to identify every chunk ID, source slug, and index fingerprint. The collection must have one known fingerprint. Resolve golden relevance labels against this full inventory, not merely against the chunks returned for a question.

The lab assumes its pinned corpus has been completely indexed. If a relevance label cannot resolve to any indexed chunk, report an incomplete/incompatible benchmark setup before generation. Do not silently omit that question. This validation concerns the benchmark's indexed corpus; it does not change the treatment of a search that returns no relevant results.

Persist the resolved relevant chunk IDs in the input snapshot so rescoring is independent of Qdrant.

For `ir-measures`:

- Use unique chunk IDs as ranked item IDs. Do not collapse several chunks from one source into one ranked item.
- Use binary relevance judgments and keep unjudged returned items in the ranking.
- Preserve recorded order. If the API accepts scores rather than ranks, use a deterministic strictly descending score derived from rank.
- Validate ranks are contiguous from one, chunk IDs are unique, and result count is at most the effective K.
- Include every retrieval-eligible question in the calculation, including empty-result queries.
- Do not implement reciprocal-rank or hit-rate formulas in parallel with the library.

The mean of Success@K matches the lab's hit-rate definition. It is not the same as document Recall@K. The old `mrr` was calculated over the returned top K; name the new metric `mrr_at_k` and document the correspondence. [ir-measures definitions](https://ir-measur.es/en/latest/measures.html).

### 6.4 Retained domain checks and diagnostics

Keep these as plain deterministic functions consuming captured data:

| Item | Contract |
|---|---|
| `routing_accuracy` | Existing selected-category match for routed cases with an expected category; baseline is not applicable |
| `citation_source_match` | Existing match between actually cited included chunks and expected sources |
| Citation validity | Expose the recorded validation status and errors; no LLM judge replaces identifier validation |
| `no_answer_accuracy` | Existing answerability-versus-refusal classification across all successful questions |
| Abstention breakdown | Show expected-no-answer successes out of eligible cases, and unexpected refusals on answerable cases |
| Search scope | Use `trace.searched_categories`; unknown stays unknown |
| Context diagnostics | Selected chunk count and estimated context tokens |
| Generation usage | Preserve provider-reported token counts and model metadata when available |

Do not label these checks as Ragas metrics. Their predicates remain application-owned; the framework stores their results alongside the standard metrics.

## 7. Evaluator provider configuration

Configure the judge independently from the answer generator. Reusing the same deployment is permitted when explicitly selected, but must not happen through an undocumented fallback.

| Setting | Policy |
|---|---|
| `RAGLAB_EVAL_MODEL` | Required evaluator deployment/model identifier |
| `RAGLAB_EVAL_EMBEDDING_MODEL` | Required for Answer Relevancy; may be the same configured deployment used by retrieval |
| `RAGLAB_EVAL_BASE_URL` | Evaluator endpoint; explicit value preferred; may fall back to the existing Foundry base URL with that resolution recorded |
| `RAGLAB_EVAL_API_KEY` | Optional SecretStr; otherwise reuse the project's supported authentication mechanism for the resolved endpoint |
| `RAGLAB_EVAL_TIMEOUT_SECONDS` | Per-request limit, default 120 seconds |
| `RAGLAB_EVAL_MAX_RETRIES` | At most one retry by default for transient transport/provider failures |

Resolve evaluator settings once. CLI `--env-file` behavior and existing environment precedence remain consistent with the application.

Reuse existing application credentials only when the resolved evaluator endpoint is the same endpoint. A different endpoint requires explicit compatible authentication; do not forward the application's API key to an unrelated service.

Use supported Ragas LLM/embedding adapters for the configured Azure/OpenAI-compatible service. The application currently uses the Responses API for generation; this does not establish that its wrapper satisfies the evaluator's completion/structured-output requirements. Verify the evaluator endpoint and deployment separately. [Ragas model customization](https://docs.ragas.io/en/stable/howtos/customizations/customize_models/).

Prefer a native supported adapter. If a small provider shim is necessary, keep it restricted to request/response translation and test it. Do not reimplement judging, parsing workflows, or a general provider abstraction.

Use one retry owner for evaluator transport errors; avoid multiplying SDK, framework, and outer-loop retries. Record effective retry settings and distinguish any framework structured-output repair attempts. Non-retryable authentication or configuration failures should stop further judge calls.

Query and evaluator clients have distinct lifetimes. Close resources created by the integration; do not close borrowed clients. If Entra authentication is used, use a refresh-capable provider supported by the selected adapter for the run lifetime.

Never persist API keys, bearer tokens, or unsanitized provider exceptions. Separate generator usage from evaluator usage. Unknown token usage or cost remains null; a price-calculation subsystem is not required.

## 8. CLI behavior

Keep `raglab eval run` and `raglab eval compare`. Add `raglab eval rescore`. A documented v2 evaluation-artifact change is allowed; retaining legacy output schemas is not required.

### 8.1 Run

```bash
uv run --extra eval raglab --env-file .env.local eval run \
  --mode baseline-vector \
  --golden golden/questions.json \
  --artifacts-dir artifacts/eval \
  --top-k 3 --max-context-tokens 1000 --output-token-limit 500

uv run --extra eval raglab --env-file .env.local eval run \
  --mode routed-vector \
  --golden golden/questions.json \
  --artifacts-dir artifacts/eval \
  --top-k 3 --max-context-tokens 1000 --output-token-limit 500
```

Expose the inputs required by the Ragas workflow; old evaluation options and defaults need not be preserved. Add repeatable `--question-id` for a bounded smoke run; validate all requested IDs before external calls. No selection means the full golden set. Label subset runs as subsets.

Capture effective routing threshold and margin from the same resolved configuration used by execution.

### 8.2 Rescore

```bash
uv run --extra eval raglab --env-file .env.local eval rescore \
  --run "artifacts/eval/<source-run-id>/manifest.json" \
  --artifacts-dir artifacts/eval
```

This creates a new run ID, references the source run, preserves the captured input digest and generation provenance, and uses the current explicit evaluator configuration. It must issue zero retrieval, category-embedding, or answer-generation calls.

Rescoring does make evaluator LLM/embedding calls. It is not described as offline evaluation in the sense of having no network use.

### 8.3 Compare

```bash
uv run --extra eval raglab eval compare \
  "artifacts/eval/<baseline-run-id>/manifest.json" \
  "artifacts/eval/<routed-run-id>/manifest.json" \
  --markdown artifacts/eval/comparison-ragas.md
```

Comparison requires no provider credentials and performs no network calls. It accepts exactly one run for each retrieval mode and applies Section 11's compatibility rules.

Replace the angle-bracket run IDs in these examples with IDs printed by completed commands.

All evaluation commands support `--json`. Successful JSON mode emits one JSON object on stdout; diagnostics/progress go to stderr. Errors are structured and machine-readable; compatibility with old evaluation payloads is not required.

Poor quality scores are a successful evaluation execution, not a process failure. Invalid configuration, invalid artifacts, and execution/evaluator failures use nonzero exits with distinguishable error categories. Partial runs report the saved manifest path before reporting a nonzero exit. In JSON mode, put that path in the structured error payload; do not print an extra plain-text path or emit a success payload first.

## 9. Results and artifact ownership

Create a unique directory for each run, using a timestamp plus a collision-resistant suffix. Never overwrite an earlier run or the committed legacy examples.

| Artifact | Purpose |
|---|---|
| `manifest.json` | Evaluation schema v2, identities, configuration, provenance, status, artifact locations |
| `inputs.jsonl` | Replayable query snapshots and relevance judgments |
| Native Ragas result file(s) | Detailed per-question scores and diagnostics; use the framework's supported local backend |
| `summary.json` | Small aggregate view with counts and missing/error states |
| `traces/` | Existing query traces from capture; optional on rescored runs because snapshots are sufficient |

Native filenames may follow the pinned Ragas backend. Record the actual relative paths in the manifest rather than depending on an assumed naming convention.

Results and summaries must join by question ID, never completion order. Use an explicit fixed metric set; no dynamic plugin registry is needed.

### 9.1 Per-metric result

Represent every metric outcome with:

- `status`: `ok`, `not_applicable`, `error`, or `not_run`.
- `value`: finite numeric value for `ok`; null otherwise.
- `reason`: applicability reason, available evaluator explanation, or sanitized error information.

Ragas may persist flattened columns such as `faithfulness_value`, `faithfulness_status`, and `faithfulness_reason`. Use actual returned explanations when available; do not generate extra explanations or claim a metric provides them when it does not.

Maintain deterministic diagnostic columns separately. Validate the schema at the adapter boundary.

### 9.2 Aggregation

Calculate the arithmetic mean over `ok` values only. A zero value is included. A missing value is not a zero.

Each summary metric must include `mean`, `eligible_count`, `scored_count`, `error_count`, and `not_run_count`. Also list not-applicable counts by reason. For binary rates, preserve the numerator and scored denominator. When no value is scored, mean is null.

Eligibility follows Section 6; it must not be inferred merely from the presence of a numeric result. Framework failures must remain visible in coverage.

For each metric, every selected question must belong to exactly one status. `eligible_count = scored_count + error_count + not_run_count`; the remaining questions are `not_applicable`. Before a failed answerable query can reveal context/refusal details, keep its dependent quality metrics in `not_run` rather than assuming an exclusion.

Small aggregation and rendering functions are allowed. Do not preserve a second experiment runner or implement a custom Ragas-equivalent scoring engine.

### 9.3 Run states

- `running`: execution is underway; an interrupted run remains visibly unfinished.
- `complete`: capture and every applicable requested metric completed without execution errors.
- `partial`: usable evidence exists but some captures or eligible metrics failed or were not attempted.
- `failed`: setup or execution prevented useful evaluation results.

Expected not-applicable cases and low numeric scores do not make a run partial. Persist available rows on failure; do not synthesize successful rows. Automatic resume is outside this version.

## 10. Provenance requirements

The manifest must record enough information to identify the executed experiment:

- Run ID, optional source-run ID, UTC creation time, schema version, and run state.
- Selected question IDs and a canonical digest of their complete content and expected labels.
- Replay-input digest and actual artifact paths.
- Retrieval mode, K, context budget, output-token limit, routing threshold, and margin.
- Active Qdrant collection identifier and stored index fingerprint.
- Digest of routing category definitions and the answer prompt.
- Generator deployment/model identity, configured generation parameters, and retrieval embedding identity.
- Application revision plus a digest of relevant source/config files, so uncommitted relevant changes are identifiable.
- Ragas, `ir-measures`, and relevant provider package versions.
- Evaluator model/embedding identities, non-secret endpoint identity, effective settings, metric class names, and metric parameters.
- A version identifier for eligibility rules and the trace-to-metric adapter.

Capture the active collection fingerprint read-only from the collection itself; do not infer it solely from present local files. Reject an index with mixed or missing fingerprints for a new v2 capture.

Preserve generation provenance from the source run during rescoring. Record evaluator provenance for the new run separately.

Stable deployment names do not guarantee that a hosted model is immutable. Record provider-reported model versions when available and document this limitation.

## 11. Comparison rules

This version compares retrieval modes under otherwise fixed conditions.

Reject the comparison, listing the mismatched fields, when the runs differ in selected question content, index fingerprint, application source identity, prompt/category definitions, generator or embedding configuration, retrieval/context/output settings, evaluator configuration, metric definitions, or eligibility rules.

Allow differences in retrieval mode, run IDs/times, source-run IDs, observed answers/results, token usage, and generated artifact locations. Do not require identical replay-input digests across retrieval modes: different outputs are expected.

For matching runs:

1. Show each metric's values, counts, and exclusions for both modes.
2. Show a numeric delta only when both metric outcomes are complete for the same scored question IDs.
3. If scored populations differ or errors exist, show the values with a comparability note and suppress that metric's delta.
4. Never infer a universal winner from one average.
5. Keep quality metrics and resource diagnostics separate; fewer searched categories or fewer tokens is not automatically better.

Complete and partial runs may be inspected side by side, with the above restrictions. Reject legacy v1 artifacts with an instruction to generate v2 evidence. Do not infer missing historical settings or automatically migrate old scores.

An optional Markdown comparison contains one compact metric table, coverage notes, and the small-benchmark limitation. A dashboard and extensive generated narrative are unnecessary.

## 12. Suggested implementation structure

Use the existing evaluation package. A reasonable division is:

| Module/responsibility | Content |
|---|---|
| `eval/golden.py` | Existing dataset validation and selection |
| `eval/runner.py` | Capture composition and Ragas experiment entry points |
| `eval/adapters.py` | Snapshot validation, Ragas arguments, and IR relevance/ranking conversion |
| `eval/checks.py` | Retained application predicates and diagnostics |
| `eval/reports.py` | Small summaries, compatibility validation, and comparison rendering |
| `schemas/eval.py` | Manifest, replay row, metric outcome, and summary contracts |
| `config.py` or a small evaluation config module | Explicit evaluator settings |

Combining closely related responsibilities is acceptable. Do not create classes solely to match this table.

Reuse existing error types, serialization utilities, golden validators, and resource ownership patterns where they fit. Introduce an abstraction only at a real external boundary or to express a meaningful contract.

## 13. Migration and removal

- Make Ragas the sole evaluation framework. Do not retain a legacy engine, fallback, or compatibility facade.
- Delete superseded scoring, orchestration, schemas, and reports as their Ragas replacements land. Verify the new contracts; matching old evaluation behavior or scores is not a prerequisite.
- Preserve the existing golden questions and labels; do not tune them to improve the new scores.
- Old evaluation reports are not inputs or acceptance evidence for the new workflow. Any retained historical files must be labeled as such; no reader, migration, or report-format compatibility is required. Preserve JSON benchmark cases and labels.
- Update README commands and metric definitions, architecture documentation, example configuration, and affected CLI/artifact contracts.
- Document the v2 artifact change, `mrr` to `mrr_at_k` naming, and the separate role of retained domain checks.
- Existing ordinary corpus, query, and trace behavior must remain covered by the relevant regression suite.

## 14. Acceptance criteria

| ID | Acceptance requirement |
|---|---|
| AC-01 | Installing the eval extra resolves from the committed lock; core CLI help/query imports work without the extra. |
| AC-02 | A test executes the real pinned Ragas experiment runner and local persistence with substituted external model boundaries. |
| AC-03 | Both retrieval modes run the existing golden set and yield exactly one captured row per selected question, including explicit failure rows. |
| AC-04 | Faithfulness receives the exact answer and only selected generation-context text, in order. |
| AC-05 | Answer Relevancy uses the configured evaluator LLM and embeddings; no generator-model fallback occurs silently. |
| AC-06 | The prescribed no-answer, unexpected-refusal, empty-context, and failed-query policies produce explicit statuses and correct coverage counts. |
| AC-07 | Real `ir-measures` results implement Success@K and RR@K as defined in section 6 on relevant-first, relevant-later, no-hit, empty-result, and repeated-source/different-chunk fixtures. No comparison against the legacy evaluator is required. |
| AC-08 | Expected-source labels resolve against the full index inventory; search misses do not erase eligible questions. |
| AC-09 | Rescoring a copied v2 bundle works without Qdrant, corpus files, or generation credentials and makes zero generation/retrieval calls. |
| AC-10 | Modified replay inputs fail digest validation before judge calls. |
| AC-11 | Judge timeout, malformed/nonfinite output, and non-retryable authentication failure remain distinguishable from poor quality; available evidence is saved. |
| AC-12 | A finite negative Answer Relevancy score is preserved when supported by the pinned metric; it is not clamped or rejected by a generic 0..1 schema. |
| AC-13 | The default capture reuses query components, evaluator execution is bounded, and owned resources close on success and failure. |
| AC-14 | Two runs and a rescore have distinct IDs and preserve prior artifacts. |
| AC-15 | Comparison rejects incompatible datasets/indexes/settings, accepts differing retrieval outputs, and suppresses deltas for unequal or incomplete scored populations. |
| AC-16 | Ordinary tests make no live provider calls, require no cloud credentials, and do not assert exact LLM-generated scores. |
| AC-17 | CLI JSON success/error outputs are machine-readable, and partial failures include an accessible artifact path. |
| AC-18 | Legacy generic evaluation machinery is removed, affected documentation is updated, and the retained application checks are clearly identified. |

Prefer a small number of parameterized tests covering these distinct guarantees. Do not create a test for every wrapper or mirror each implementation function.

## 15. Implementation sequence

### Task 1 — Establish framework compatibility

Pin compatible dependencies; add the eval extra and configuration contract. Demonstrate the real Ragas runner/local storage and both metrics with substituted provider boundaries. Confirm the Azure endpoint integration path without changing the query pipeline.

Completion evidence: lockfile, supported API choice documented, one meaningful integration test.

### Task 2 — Capture reusable inputs

Build dataset selection, index inventory/provenance, stable relevance judgments, and replay rows. Reuse run-scoped query components. Persist complete and failed captures with unique run IDs.

Completion evidence: ordered snapshots, integrity validation, resource cleanup, unchanged query behavior.

### Task 3 — Integrate metrics and domain checks

Connect Ragas metrics and `ir-measures`, implement eligibility/status contracts, and carry over the small domain predicates. Use the fixed metric set.

Completion evidence: context mapping tests, library retrieval-metric fixtures, refusal/empty/failure cases, finite score preservation.

### Task 4 — Connect run, rescore, and compare

Wire CLI operations, native result paths, summaries, replay-only scoring, compatibility checks, and nonzero failure reporting.

Completion evidence: CLI contract tests and an offline end-to-end fixture for capture, scoring, copied-bundle rescore, and comparison.

### Task 5 — Remove superseded code and document

Delete redundant legacy paths; update README, architecture, configuration, and artifact examples. Run focused tests, affected regression tests, lint/format checks, and the package build.

Completion evidence: one supported evaluation implementation and accurate documentation.

### Task 6 — Optional live validation with available credentials

First run a small question selection, inspect the judge outputs, then run both modes over the full set with matching settings. Produce a comparison and inspect several individual judgments, including an error or disagreement if one occurs.

Live validation is separate from offline implementation completion. If credentials or compatible deployments are unavailable, finish the code and offline verification and state that live scoring was not run. Never fabricate results or mark unreviewed judgments as human-validated.

## 16. Definition of done

The implementation is complete when AC-01 through AC-18 hold, the old general evaluation path is removed, and a developer can follow documented commands to run and rescore experiments.

The portfolio demonstration is verified only after a real baseline/routed run has produced inspectable results. Its description must distinguish measured outcomes, evaluator judgments, and known limitations.

Do not claim that Ragas alone establishes factual correctness, eliminates judge bias, makes the hosted model deterministic, or validates conclusions on other query populations.

## 17. References

These sources establish framework capabilities. The application policies and acceptance criteria above are design decisions for this repository.

- [Ragas experiments and local results](https://docs.ragas.io/en/stable/concepts/experimentation/)
- [Ragas datasets](https://docs.ragas.io/en/stable/concepts/datasets/)
- [Ragas supported API migration guidance](https://docs.ragas.io/en/stable/howtos/migrations/migrate_from_v03_to_v04/)
- [Faithfulness](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/)
- [Answer Relevancy and embedding requirements](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/answer_relevance/)
- [Ragas model customization](https://docs.ragas.io/en/stable/howtos/customizations/customize_models/)
- [ir-measures Success and Reciprocal Rank definitions](https://ir-measur.es/en/latest/measures.html)
