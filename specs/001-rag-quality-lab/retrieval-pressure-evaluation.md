# Retrieval Pressure Evaluation Notes

Last updated: 2026-07-10

This note summarizes the evaluation exercise where the golden set was expanded with ambiguous cross-category questions and the retrieval defaults were tightened to make differences between `baseline-vector` and `routed-vector` observable on the included cases. It reports a small, manually curated benchmark over the pinned corpus, not a general comparison of retrieval strategies.

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

| Metric | baseline-vector | routed-vector | Included-benchmark observation |
| --- | ---: | ---: | --- |
| `routing_accuracy` | n/a | 7/12 eligible questions, 58.3% | only routed retrieval uses route filtering |
| `fallback_rate` | 0/16 questions, 0.0% | 0/16 questions, 0.0% | same observed value |
| `hit_rate_at_k` | 12/14 questions, 85.7% | 13/14 questions, 92.9% | routed value higher by one question |
| `mrr` | 0.6071 | 0.6786 | routed value higher |
| `citation_source_match` | 12/14 questions, 85.7% | 13/14 questions, 92.9% | routed value higher by one question |
| `no_answer_accuracy` | 16/16 questions, 100.0% | 16/16 questions, 100.0% | same observed value |
| `average_context_tokens` | 609.7 | 597.8 | routed value lower by 11.9 tokens |
| `average_included_chunks` | 2.938 | 2.812 | routed value lower by 0.126 chunks |

Routed retrieval achieved a higher hit rate on the included curated benchmark: 13/14 questions (92.9%) versus 12/14 (85.7%) for baseline retrieval. This one-question difference is useful evidence that category filtering can help under the included corpus, questions, and tight retrieval settings; it is not evidence of general superiority. Routing accuracy is not compared with `baseline-vector`, because baseline global vector search does not use route filtering.

The top-category result also illustrates why route accuracy and retrieval hit rate should be read separately. The routed mode selected the expected top category for 7/12 eligible questions (58.3%), while soft multi-category routing searched an average of 2.312 categories and could recover relevant evidence when the expected category was not first.

## Why The Earlier Runs Were Inconclusive

The corpus is intentionally small. With `top_k=6` and `max_context_tokens=2500`, baseline vector search often had enough room to include both noisy matches and useful matches. That made the difference between filtered and unfiltered retrieval hard to see.

This is a saturation problem, not necessarily proof that routing is unnecessary. If the retriever can return many chunks and the context builder can include most of them, the downstream model receives enough evidence despite imperfect ranking. In this evaluation design, routing has more opportunity to affect the measured result when:

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

These results apply only to the pinned corpus and included golden questions. The benchmark is small and manually curated, so differences may reflect one changed question, as the hit-rate result does here. They should not be generalized to other corpora or query distributions. The fallback threshold and category margin are heuristic, and retrieval pressure and routing configuration were adjusted while inspecting this same benchmark rather than against a separate holdout set.

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
