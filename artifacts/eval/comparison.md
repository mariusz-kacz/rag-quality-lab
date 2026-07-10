# Evaluation comparison

## Compared artifacts

| Artifact |
| --- |
| artifacts\eval\eval-baseline-vector.json |
| artifacts\eval\eval-routed-vector.json |

## Metric comparison

| Metric | baseline-vector | routed-vector | Best mode |
| --- | --- | --- | --- |
| routing_accuracy | n/a | 0.5833 | n/a |
| fallback_count | 0 | 0 | tie |
| fallback_rate | 0 | 0 | tie |
| average_searched_categories | 5 | 2.312 | routed-vector |
| hit_rate_at_k | 0.8571 | 0.9286 | routed-vector |
| mrr | 0.6071 | 0.6786 | routed-vector |
| citation_source_match | 0.8571 | 0.9286 | routed-vector |
| no_answer_accuracy | 1 | 1 | tie |

## Token-budget diagnostics

| Metric | baseline-vector | routed-vector | Best mode |
| --- | --- | --- | --- |
| average_context_tokens | 609.7 | 597.8 | routed-vector |
| average_included_chunks | 2.938 | 2.812 | routed-vector |

## Interpretation notes

- Routing accuracy is not applicable to baseline-vector because baseline retrieval does not use route filtering.
