# Evaluation comparison

## Compared artifacts

| Artifact |
| --- |
| artifacts\eval\eval-baseline-vector.json |
| artifacts\eval\eval-routed-vector.json |

## Metric comparison

| Metric | baseline-vector | routed-vector | Best mode |
| --- | --- | --- | --- |
| routing_accuracy | 0.7778 | 0.7778 | tie |
| fallback_rate | 0 | 0 | tie |
| recall_at_k | 0.7273 | 1 | routed-vector |
| mrr | 0.5909 | 0.6848 | routed-vector |
| citation_source_match | 0.7273 | 0.9091 | routed-vector |
| no_answer_accuracy | 1 | 1 | tie |

## Token-budget diagnostics

| Metric | baseline-vector | routed-vector | Best mode |
| --- | --- | --- | --- |
| average_context_tokens | 1277 | 1375 | baseline-vector |
| average_included_chunks | 6 | 6 | tie |
