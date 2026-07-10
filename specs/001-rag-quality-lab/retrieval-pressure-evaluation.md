# Retrieval Pressure Evaluation Notes

Last updated: 2026-07-10

This note summarizes the evaluation exercise where the golden set was expanded with ambiguous cross-category questions and the retrieval defaults were tightened to expose differences between `baseline-vector` and `routed-vector`.

## Purpose

The goal was not to create cases that prove routing wins. The goal was to model real retrieval problems that routing is supposed to help with:

- a user question uses terms that appear in multiple categories;
- the best evidence belongs to a narrower category than the most common vocabulary in the question;
- a generic vector search can spend limited `top_k` slots on semantically nearby but wrong documents;
- the context budget is small enough that wrong early chunks crowd out the evidence needed for a good answer;
- final answer quality depends on whether the retriever selected the right sources before generation begins.

With a small corpus and a generous retrieval budget, baseline retrieval often gets enough useful chunks anyway. In that setup, route-aware filtering has little room to show value because the context still includes the right evidence.

## Changes Made

Three additional ambiguous boundary cases were added to `golden/questions.json`:

| Question | Expected category | Main pressure point |
| --- | --- | --- |
| `q-cross-category-003` | LLM settings, cost, and tokens | The wording mentions RAG evaluation runs, but the expected evidence is about prompt caching and cost optimization. |
| `q-cross-category-004` | LLM security and risks | The wording mentions retrieved context, but the expected evidence is prompt injection and vector/embedding weakness guidance. |
| `q-cross-category-005` | RAG evaluation and quality | The wording mentions retrieved chunks, but the expected evidence is evaluation checks for evidence sufficiency rather than retrieval implementation. |

The default retrieval settings were also tightened:

| Setting | Previous default | Current default | Reason |
| --- | ---: | ---: | --- |
| `top_k` | 6 | 3 | Fewer returned chunks make each retrieval slot matter more. |
| `max_context_tokens` | 2500 | 1000 | A tighter context budget makes noisy or wrong chunks more costly. |

Evaluation output token limit remains higher for eval runs than for ad hoc queries so answer generation has enough room to produce citations and no-answer behavior.

## Observed Results

Latest comparison artifact: `artifacts/eval/comparison.md`

| Metric | baseline-vector | routed-vector | Result |
| --- | ---: | ---: | --- |
| `routing_accuracy` | n/a | 0.5833 | not comparable |
| `fallback_rate` | 0 | 0 | tie |
| `recall_at_k` | 0.8571 | 0.9286 | routed wins |
| `mrr` | 0.6071 | 0.6786 | routed wins |
| `citation_source_match` | 0.8571 | 0.9286 | routed wins |
| `no_answer_accuracy` | 1 | 1 | tie |
| `average_context_tokens` | 609.7 | 597.8 | routed wins |
| `average_included_chunks` | 2.938 | 2.812 | routed wins |

After tightening `top_k` and context budget, `routed-vector` became the clear winner on the retrieval-sensitive metrics: recall, first relevant rank, citation source match, and token/context efficiency. Routing accuracy is intentionally not compared against `baseline-vector`, because baseline global vector search does not use route filtering.

## Why The Earlier Runs Were Inconclusive

The corpus is intentionally small. With `top_k=6` and `max_context_tokens=2500`, baseline vector search often had enough room to include both noisy matches and useful matches. That made the difference between filtered and unfiltered retrieval hard to see.

This is a saturation problem, not necessarily proof that routing is unnecessary. If the retriever can return many chunks and the context builder can include most of them, the downstream model receives enough evidence despite imperfect ranking. Routing is most useful when:

- the corpus has overlapping concepts across categories;
- the result list is short;
- the context window is constrained;
- relevant chunks are easy to crowd out with adjacent but wrong material;
- citation source match matters, not just whether the model can produce a plausible answer.

## Remaining Diagnostic Case

`q-cross-category-003` remains useful because it still exposes a miss in both modes.

Expected sources:

- `openai-prompt-caching`
- `openai-cost-optimization`

Retrieved sources in the inspected run:

- `openai-gpt5-prompting-guide`
- `openai-api-prompt-engineering`
- `openai-evaluation-flywheel`

This case is valuable because it shows a real ambiguity: "RAG evaluation runs" pulls retrieval toward prompting and evaluation material, while the intended answer is about repeated static prompt prefixes, caching, and cost. That is the kind of failure a retrieval report should make visible.

## Reporting Improvement

The Markdown evaluation report originally showed expected and retrieved sources but did not mark retrieval expectation misses as row-level failures. The `Errors` column only represented runtime, answer validation, and citation validation errors.

A per-question `Status` column was added to the Markdown report. It can now surface:

- `pass`
- `route filter miss`
- `source retrieval miss`
- `citation source miss`
- `answerability miss`
- `runtime/citation error`

Route status is based on the effective routed category filter, not only the strict top category. If multi-category routing keeps the expected category in scope, the question is not marked as a route filter miss even when the top selected category differs. This makes cases like `q-cross-category-003` visible without requiring manual comparison between expected and retrieved source lists, while avoiding false route failures for recovered multi-route cases such as `q-security-boundary-001`.

## Interpretation

The current result supports this evaluation design:

- Ambiguous cross-category questions are necessary because simple category questions are too easy for both retrieval modes.
- Retrieval pressure is necessary because a small corpus with a generous context budget hides ranking problems.
- `routed-vector` should be evaluated on retrieval metrics and citation source match, not only on final answer plausibility.
- A failing ambiguous case is still useful if it points to a real retrieval weakness rather than an artificial benchmark trick.

The useful evaluation pattern is therefore:

1. Keep direct answerable questions to verify normal behavior.
2. Keep no-answer questions to verify unsupported-question handling.
3. Keep ambiguous boundary questions to stress route selection and source ranking.
4. Keep tight enough retrieval settings that wrong ranking has observable consequences.
5. Use per-question diagnostics to decide whether a failure is routing, retrieval, context budgeting, citation selection, or generation behavior.
