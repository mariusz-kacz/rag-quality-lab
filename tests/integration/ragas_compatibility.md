# Evaluation framework compatibility

The executable contract is [test_ragas_compatibility.py](test_ragas_compatibility.py).
Tests use real Ragas, Instructor, OpenAI clients, JSONL persistence, and IR
providers. HTTP responses are simulated; no live judge accuracy is implied.

## Pinned libraries

The optional eval extra pins Ragas 0.4.3, ir-measures 0.4.3, and
langchain-community 0.4.1. The community pin retains ChatVertexAI, eagerly imported
by this Ragas version. The locked environment uses Instructor 1.17.0.

## Native APIs

- `ragas.Dataset`, `@ragas.experiment()`, and `await experiment.arun(dataset)`
  use the local/jsonl backend and an explicit root directory.
- `DiscreteMetric(name="answer_success", prompt=..., allowed_values=["pass", "fail"])`
  accepts `ascore(llm=..., question=..., grading_notes=..., answerability=...,
  response=..., contexts=...)`. Ragas supplies structured value and reason.
  The lab maps pass/fail to 1/0 for summaries and preserves the reason.
- Collections `Faithfulness.ascore(user_input, response, retrieved_contexts)`
  returns a numeric MetricResult. This path has no reason or traces.
- JSONL preserves nested fields, explicit nulls, scores, and error states.
  Match result rows by question ID, not completion order.

The experiment schedules rows concurrently. A semaphore keeps one scoring row
active, and metrics are awaited sequentially. Unhandled row exceptions would be
omitted by Ragas, so the lab records explicit metric failures and checks returned
IDs. JSON output redirects progress to stderr.

## Provider boundary

Use AsyncOpenAI, Ragas llm_factory, and the configured judge deployment.
There is no evaluator embedding model or embedding request.
Instructor JSON mode uses Chat Completions, max_completion_tokens=4096, and no
temperature/top_p/max_tokens. Structured-output retries stay zero; the SDK owns
transport retries (one by default) and the 120-second timeout.

Compatibility tests cover authentication/configuration failure, timeout,
unavailable service, malformed output, no hidden repair retries, and credential
refresh. Fatal authentication/configuration errors stop later requests.
Context-local filters sanitize provider exception logs. Created clients and
credentials close on success and failure; borrowed resources remain caller-owned.
Borrowed clients must match endpoint, timeout and retry settings.

Evaluator configuration is independent of generator/Qdrant setup. Only a matching
normalized Foundry endpoint may reuse Foundry authentication. A different endpoint
requires an explicit evaluator API key. Keys never enter serialized configuration.

## Retrieval and persistence

Public ir-measures dispatch supports Success@K and cutoff RR@K; forcing both
through pytrec_eval does not. Tests cover ranks, cutoff, unjudged items, empty
queries, and empty runs. Rank-derived scores are strictly descending.
Lab source labels expand to chunk IDs: source_hit_at_k and source_mrr_at_k describe
expected-source coverage, not evidence completeness.

Ragas saves results at experiment completion. The lab saves the answers dataset
after each query. Saved files are inspection outputs and may be partial. The lab
does not reload them for scoring or comparison. There is no extra manifest,
checksum, or atomic publication layer.

## Verification

Run `uv run --locked --extra eval pytest`, `uv run --locked --extra eval ruff check .`,
changed-file formatting checks, and `uv build`. See
[verification record](../../tasks/todo.md) for this change's results.
Mock verdicts prove mapping, persistence, coverage and failure handling.
Human review of real answers is still needed to validate the rubric and judge.

References: [Ragas RAG evaluation](https://docs.ragas.io/en/stable/howtos/applications/evaluate-and-improve-rag/),
[experiments](https://docs.ragas.io/en/stable/concepts/experimentation/),
[IR providers](https://ir-measur.es/en/latest/providers.html).
Version-specific behavior is verified against installed source and executable tests.
