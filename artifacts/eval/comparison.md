# Evaluation comparison

These results are evidence from a small, manually curated benchmark over the pinned corpus and included golden questions; they should not be generalized to other corpora or query distributions.

## Compared artifacts

| Artifact |
| --- |
| artifacts\eval\eval-baseline-vector.json |
| artifacts\eval\eval-routed-vector.json |

## Metric comparison

| Metric | baseline-vector | routed-vector | Observed value on included benchmark |
| --- | --- | --- | --- |
| routing_accuracy | n/a | 7/12 questions, 58.3% | n/a |
| fallback_count | 0 | 0 | tie |
| fallback_rate | 0/16 questions, 0.0% | 0/16 questions, 0.0% | tie |
| average_searched_categories | 5 | 2.312 | routed-vector |
| hit_rate_at_k | 12/14 questions, 85.7% | 13/14 questions, 92.9% | routed-vector |
| mrr | 0.6071 | 0.6786 | routed-vector |
| citation_source_match | 12/14 questions, 85.7% | 13/14 questions, 92.9% | routed-vector |
| no_answer_accuracy | 16/16 questions, 100.0% | 16/16 questions, 100.0% | tie |

## Token-budget diagnostics

| Metric | baseline-vector | routed-vector | Observed value on included benchmark |
| --- | --- | --- | --- |
| average_context_tokens | 609.7 | 597.8 | routed-vector |
| average_included_chunks | 2.938 | 2.812 | routed-vector |

## Interpretation notes

- These results are evidence from a small, manually curated benchmark over the pinned corpus and included golden questions; they should not be generalized to other corpora or query distributions.
- With 14 retrieval-scored questions, a one-question change moves hit rate by 7.1 percentage points.
- Top-category routing accuracy and retrieval hit rate measure different behavior: soft multi-category routing can retain the expected category and recover a hit even when the top category is incorrect.
- Fallback thresholds and category margins are heuristic, and configuration was adjusted while inspecting this same small benchmark.
- Routing accuracy is not applicable to baseline-vector because baseline retrieval does not use route filtering.
