# Evaluation comparison

## Compared artifacts

| Artifact |
| --- |
| artifacts\eval\eval-baseline-vector.json |
| artifacts\eval\eval-routed-vector.json |

## Metric comparison

| Metric | baseline-vector | routed-vector | Best mode |
| --- | --- | --- | --- |
| routing_accuracy | 0.7 | 0.7 | tie |
| fallback_rate | 0 | 0 | tie |
| recall_at_k | 0.7 | 0.9 | routed-vector |
| mrr | 0.55 | 0.61 | routed-vector |
| citation_source_match | 0.7 | 0.7 | tie |
| no_answer_accuracy | 1 | 1 | tie |

## Token-budget diagnostics

| Metric | baseline-vector | routed-vector | Best mode |
| --- | --- | --- | --- |
| average_context_tokens | 1328 | 1417 | baseline-vector |
| average_included_chunks | 6 | 6 | tie |
