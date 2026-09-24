# Simple Ragas evaluation

The evaluation keeps the sample's dataset -> experiment -> results workflow.
The primary question is whether the answer satisfies explicit grading notes
and stays supported by its generation context.

## Workflow

- Run golden questions through the existing query pipeline.
- Save answers, context, grading notes, labels, and essential settings in a native
  Ragas dataset, then score them with one `@experiment`.
- Print the metric means, scored/eligible counts, and refusal diagnostics.
- Inspect saved per-question answers, evidence, scores, and judge explanations.

Only `datasets/answers.jsonl` and `experiments/scores.jsonl` are needed.
Rows are ordinary dictionaries. GoldenDataset validates IDs, source labels, and
nonempty grading notes. No manifest, checksums, replay state machine, full trace
snapshots, or saved summary. Each invocation runs fresh questions; saved-run
loading, rescoring, and automatic comparison are outside the workflow.

## Metric meaning

- Primary: `answer_success`, a native Ragas DiscreteMetric pass/fail with a reason.
  The judge receives question, grading notes, answerability, answer, and exact
  ordered generation context. It checks completeness and factual support.
  Essential requirements match the user-visible question. Optional details and
  example lists are not mandatory; false or unsupported claims still fail.
  Prohibiting an overclaim does not require an explicit disclaimer.
- No-answer questions also receive an answer-success judgment. A semantic refusal
  can pass without the application's exact refusal phrase. For answerable
  questions, missing evidence does not excuse an incomplete answer or refusal.
- Supporting: native Ragas Faithfulness and ir-measures source Hit@K/MRR@K.
  Source labels expand to every chunk from that source. The metric names explicitly
  describe source coverage, not passage relevance or exhaustive retrieval recall.
- Expected no-answer cases exclude supporting metrics. Recognized refusals and
  empty context exclude faithfulness. Empty answerable rankings score zero.
- Routing, citation-source match, citation validation, refusal phrase detection,
  and original generation usage remain diagnostics.
- Query/judge failures are unscored, never converted into an answer failure.
  Fatal judge authentication/configuration errors stop later requests.
- Means accompany scored/eligible counts. Error and exclusion reasons remain in
  per-question results. No weighted composite score or comparison rules.

## Provider and CLI boundaries

Only an explicit evaluator judge deployment is needed. No evaluator embeddings.
Reuse/close query clients; close owned judge clients. Preserve endpoint/auth
isolation, sanitized errors, finite-score checks, and one transport retry owner.
Credentials never enter saved rows.

The CLI exposes `eval run` with text or JSON output. Low answer
success is a valid result; incomplete evaluation exits nonzero with available
file paths. Core commands and evaluation help work without Ragas installed.

## Validation and interpretation

Use real Ragas over simulated HTTP, in-memory Qdrant, exact judge-input tests,
workflow/failure tests, ordinary regressions, lint, build, and a core-only smoke.
These prove implementation behavior, not agreement between a live judge and humans.
Grading notes are draft success criteria. Review representative answers blindly,
record human pass/fail reasons, inspect disagreements, and validate revised notes
on held-out cases before using the pass rate as a decision rule.
