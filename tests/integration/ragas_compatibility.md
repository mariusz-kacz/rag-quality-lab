# Evaluation framework compatibility

Task 1 evidence for [the Ragas evaluation plan](../../tasks/plan.md).
The executable owner is [test_ragas_compatibility.py](test_ragas_compatibility.py).
Verified on Windows x64, Python 3.12.10. No live provider calls or credentials are
used; HTTPX substitutes only HTTP responses. Ragas execution, metric calculation,
Instructor parsing, OpenAI clients, persistence, and IR providers are real.

## Dependency selection

The optional `eval` extra pins `ragas==0.4.3`, `ir-measures==0.4.3`, and
`langchain-community==0.4.1`. Ragas imports `ChatVertexAI` eagerly; the resolved
0.4.2 community package removed that module and failed at import. The explicit
community pin is required even though this fixture uses the OpenAI adapter.
Instructor 1.17.0 and pytrec-eval-terrier 0.5.10 are locked transitive dependencies;
OpenAI 2.44.0 is already a core dependency. No additional provider SDK is needed.

## Selected API and local storage

Use `ragas.Dataset`, `@ragas.experiment()`, and `await experiment.arun(dataset)`
with `backend="local/jsonl"` and an explicit `root_dir`. The fixture produces:

```text
<pytest tmp_path>/datasets/compatibility.jsonl
<pytest tmp_path>/experiments/compatibility-result.jsonl
```

`Experiment.load(name, backend="local/jsonl", root_dir=...)` reloads the native
result. Each UTF-8 JSONL line is a returned row dictionary. The fixture proves
preservation of question IDs, nested metric states/reasons, explicit JSON nulls,
integer/boolean diagnostics, zero Faithfulness, and negative Answer Relevancy.
The error, not-applicable, and not-run rows are serialization probes, not an
implementation of application eligibility or failure handling.

Collections `Faithfulness.ascore(user_input, response, retrieved_contexts)` and
`AnswerRelevancy.ascore(user_input, response)` return `MetricResult` objects with
numeric `.value`; `.reason` and `.traces` are `None` in this path. Persist explicit
primitive fields, not the objects. The fixture's exact scores follow from canned
verdicts and vectors; they are not assertions about live LLM judgments.

The experiment runner schedules rows concurrently using `asyncio.as_completed`.
An `asyncio.Semaphore(1)` around each scoring row, with sequential metric awaits,
enforces concurrency one; the fixture verifies peak active rows under contention.
Result ordering is completion ordering: match by question ID in later tasks.

## Provider path, defaults, and retries

The tested path is `AsyncOpenAI(base_url=<Foundry OpenAI v1 URL>, ...)`,
`llm_factory(<explicit judge deployment>, client=client, max_retries=0)`, and
`OpenAIEmbeddings(model=<explicit embedding deployment>, client=client)`.
It sends Chat Completions in Instructor JSON mode (`response_format=json_object`)
and embeddings requests. It does not use the application's Responses generator.
The endpoint/deployment must support these APIs and parameters. Actual Azure
deployment suitability and refresh-capable authentication remain Task 2/live
verification work.

Observed built-in defaults: metric names `faithfulness` / `answer_relevancy`;
Answer Relevancy strictness 3 (three generated questions); judge temperature
0.01, top_p 0.1, max_tokens 1024. Faithfulness makes a statement-generation call
then a verdict call. No generated statements/verdicts can produce NaN; later
adapters must reject nonfinite values, and must preserve finite negative relevancy.

The fixture explicitly uses OpenAI `timeout=120` and `max_retries=1`. Instructor
1.17.0 interprets integer `max_retries` as retries after the initial attempt;
its default is 3, so `llm_factory(..., max_retries=0)` disables repair/retry calls.
The SDK is the sole transport retry owner. The parameterized probe confirms:

| Response | Total HTTP attempts | Outcome |
| --- | ---: | --- |
| HTTP 401 | 1 | Exception |
| HTTP 503 | 2 | Exception |
| Malformed JSON | 1 | Exception, no structured-output repair |

Failures are wrapped in `InstructorRetryException`; later provider code must
classify and sanitize the underlying failure instead of persisting its raw text.
The fixture disables Ragas telemetry with `RAGAS_DO_NOT_TRACK=true` before import.

## IR provider choice

Use public `ir_measures.evaluator(...)` dispatch for `Success@K` and `RR@K`.
The installed pipeline selects pytrec_eval for Success and the bundled MS MARCO
provider for cutoff RR. Directly forcing both through `PytrecEvalProvider` was
an invalid probe: its advertised RR support excludes cutoffs, and bypassing
dispatch silently gave incorrect results. No package patch or custom formula
was introduced.

One scenario matrix verifies relevant-first, relevant-later, unjudged-ranked
documents, cutoff exclusion, a query with no ranking, and an entirely empty run.
Both per-query values and aggregate denominators are checked. Keep every eligible
query in qrels, even with no returned documents. Supply strictly descending
rank-derived scores and use unique chunk IDs in later adapters.

## Integration cautions for later tasks

- Ragas catches unhandled row exceptions, prints a warning to stdout, and omits
  the failed row. Later scoring must return explicit failure outcomes and verify
  the ID population; CLI JSON output must stay clean.
- Native JSONL is written at the end of the experiment, overwriting the named
  file. Unique run directories and durable input capture belong to later tasks.
- Native loading skips malformed JSON lines with a warning and interprets some
  date-like strings. It is not a strict artifact-integrity validator. Replay
  input validation must use the application's strict artifact boundary.
- This fixture proves library compatibility, not application v2 run/rescore,
  eligibility, provider lifecycle/authentication, or quality of a live judge.

## Validation

```console
uv sync --locked --extra eval
uv run --locked --extra eval pytest tests/integration/test_ragas_compatibility.py
uv run --locked --extra eval pytest
uv run --locked --extra eval ruff check .
uv run --locked --extra eval ruff format --check tests/integration/test_ragas_compatibility.py
uv build
```

Baseline: 195 tests passed; Ruff lint passed. Repository-wide format checking
already reported 26 unrelated files. Changed Python formatting passes.
The eval-enabled suite passes all 200 cases, including five compatibility cases.
The no-extra guard skips only when a top-level optional dependency is absent;
installed-but-broken dependencies fail visibly, as the community mismatch did.

A separate environment at `.cache/task1-core` was created with
`UV_PROJECT_ENVIRONMENT=.cache/task1-core uv sync --locked --no-extra eval`
(set the environment variable separately in PowerShell). Ragas, ir-measures,
Instructor, and langchain-community were confirmed absent. Package and query
pipeline imports and `raglab --help` passed; its full suite passed 195 cases and
skipped exactly the five optional cases. Initial sandbox cache/temp-directory
permission failures were resolved with approved reruns, without code changes.

Upstream references: [Ragas experiments](https://docs.ragas.io/en/stable/concepts/experimentation/),
[collections migration](https://docs.ragas.io/en/stable/howtos/migrations/migrate_from_v03_to_v04/),
[IR providers](https://ir-measur.es/en/latest/providers.html).
Version-specific conclusions above come from the locked installed source and
executable fixture, rather than assuming the rolling documentation matches.

## Task 2 provider boundary

`eval/config.py::load_eval_config` resolves the evaluator environment once without
loading generator or Qdrant configuration. Both evaluator model variables are
required. It records endpoint fallback and authentication source; `model_dump()`
excludes the API key entirely. Numeric errors omit supplied values. Endpoint
normalization handles API operation suffixes, host case and default ports, and
rejects URL credentials/query strings/fragments. Only an identical normalized
Foundry endpoint may reuse Foundry credentials. A different endpoint requires
`RAGLAB_EVAL_API_KEY`. Explicit evaluator credentials do not need Foundry settings.

Use `async with evaluator_scope(config) as evaluator`, construct native Ragas
metrics with `evaluator.llm` / `evaluator.embeddings`, then invoke each metric via
`await evaluator.call(metric.ascore, ...)`. This boundary serializes metric calls
and latches fatal authentication/configuration failures; later calls return a
sanitized `stopped` error without model traffic. Task 4 must map these outcomes to
metric statuses and keep deterministic diagnostics available. It must also retain
the experiment row gate because metric-call serialization alone does not promise
row execution order. This module does not capture queries or introduce a second
evaluation runner.

Owned clients use 120-second SDK timeouts and one SDK transport retry by default;
explicit nonnegative retry counts and positive finite timeouts are supported.
Instructor structured-output retries remain zero. Entra authentication uses the
[async Azure bearer-token provider](https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.aio?view=azure-python#azure-identity-aio-get-bearer-token-provider)
as the SDK's callable API key, retaining the credential until scope exit. Tests
use near-expiry fake tokens with the real Azure provider and real SDK to verify
refresh and rejection of later calls after token acquisition fails.

An `AsyncExitStack` closes owned clients and credentials on normal exits, partial
setup, and scoring failures, including continuing cleanup when client close fails.
Injected clients/credentials remain caller-owned. An injected SDK client must
match the resolved endpoint, timeout and retry policy; its authentication remains
the caller's responsibility. Ordinary generator authentication is unchanged.

`EvalProviderError.as_dict()` exposes only fixed safe fields. The extended real
HTTP failure matrix distinguishes authentication, invalid request configuration,
timeouts, unavailable providers and malformed structured output. Instructor
1.17.0 logs raw API exceptions at ERROR before the caller sees them; a temporary
context-local filter sanitizes its retry diagnostics and SDK request diagnostics
during evaluator calls. Logs from unrelated tasks are left alone. This was an
observed leakage regression, not a speculative logging feature.

Evaluator clients use `AsyncOpenAI` directly. Evaluator token/cost bookkeeping
was removed at the user's request to keep evaluation simple; there is no custom
SDK subclass, usage collector, or placeholder usage output.

Task 2 validation: 229 eval-enabled tests passed; the isolated no-extra environment
passed 220 tests with nine optional cases skipped, and core-only imports/help
passed. Build, Ruff lint and changed-file formatting passed. The original 26
repository formatting failures remain outside scope. Live deployment suitability,
run-level artifact/status mapping and CLI integration remain later work.
