# Source snapshot

Source metadata:
- source_slug: huggingface-evaluate-choosing-metric
- category: RAG evaluation and quality
- upstream_url: https://huggingface.co/docs/evaluate/main/en/choosing_a_metric
- source_markdown: https://github.com/huggingface/evaluate/blob/main/docs/source/choosing_a_metric.mdx
- license: Apache-2.0
- pinned_version: huggingface-evaluate@main
- snapshot_type: normalized documentation digest from Hugging Face Evaluate MDX documentation
- normalization: removed Hugging Face site navigation, version switcher, GitHub page chrome, copied-code labels, admonition rendering, and footer material; retained metric-category guidance, metric-card usage, compact code examples, benchmark-format constraints, and RAG evaluation interpretation

---
# Generic, task-specific, and dataset-specific metrics

The Hugging Face Evaluate guide starts from a practical evaluation question: after training a model, how should a user decide which metric to use on a dataset? Its central guidance is that there is no one-size-fits-all metric. A metric should be selected according to the task, dataset, benchmark convention, input format, and intended use of the evaluation result.

The guide groups metrics into three high-level categories:

1. Generic metrics that can be applied to many situations and datasets, such as accuracy and precision.
2. Task-specific metrics that are tied to a particular task, such as BLEU or ROUGE for machine translation and text generation, or seqeval for named entity recognition.
3. Dataset-specific metrics that are designed for a particular benchmark, such as the dedicated evaluation metrics used by GLUE or SQuAD.

This classification is useful for RAG systems because RAG quality spans multiple evaluation surfaces. Retrieval metrics such as precision, recall, and ranking metrics are generic or retrieval-specific. Answer metrics such as exact match, F1, ROUGE, or semantic similarity may be task-specific. Benchmark-style datasets may require a precise answer schema, matching rule, or aggregation method. A credible RAG report should say which category each metric belongs to and why it was chosen.

## Generic metrics

Generic metrics are broadly reusable across tasks and datasets. The guide names accuracy and precision as examples for labeled supervised datasets, and perplexity as an example for unsupervised generative tasks.

The Evaluate workflow encourages users to inspect a metric card before using a metric. A metric card describes the required input structure, expected values, limitations, ranges, and examples. This matters because metrics that sound simple can require specific field names, label formats, or averaging behavior.

The source gives a compact precision example:

```python
import evaluate

precision_metric = evaluate.load("precision")
results = precision_metric.compute(
    references=[0, 1],
    predictions=[0, 1],
)
print(results)
```

Expected result:

```python
{"precision": 1.0}
```

For a RAG lab, generic metrics can be used for simple classified outcomes:

- whether the route selected the expected knowledge category;
- whether an answerable question received an answer;
- whether an insufficient-evidence question produced a no-answer response;
- whether a cited source matches an expected source;
- whether at least one relevant chunk was retrieved in the top `k`.

Generic metrics are easy to compare across experiments, but they can be too coarse. A single accuracy score might hide whether failures come from retrieval, context selection, answer generation, citation validation, or no-answer behavior.

## Task-specific metrics

Task-specific metrics are used when a task has established measurement conventions. The guide names machine translation and named entity recognition as examples, with BLEU, GoogleBLEU, GLEU, ROUGE, MAUVE, and seqeval as representative metrics.

The guide recommends several ways to find the right task-specific metric:

- Look at task pages to see which metrics are used for models on that task.
- Check leaderboards such as Papers With Code, searching by task and dataset.
- Read metric cards for candidate metrics to understand fit, input format, limitations, and examples.
- Look at recent papers and blog posts to see what metrics are reported, since metric choices can change over time.

For RAG systems, task-specific metrics depend on the application's answer shape. A factoid QA task may use exact match and token-level F1. A summarization task may use ROUGE or a model-graded rubric. A retrieval-focused task may use recall@k, MRR, nDCG, or MAP. A safety-sensitive task may require categorical checks for refusal, sensitive-data disclosure, or unsupported claims.

The guide's emphasis on reading metric cards is important because task-specific metrics often encode assumptions. For example:

- BLEU and ROUGE compare generated text against references and may reward lexical overlap more than factual grounding.
- seqeval expects token or span labels in a task-specific structure.
- retrieval metrics need relevance judgments and a cutoff.
- model-graded checks need a rubric and validation against human judgments.

Task-specific metrics should therefore be selected for what they actually measure, not only because they are popular.

## Dataset-specific metrics

Dataset-specific metrics are associated with benchmark datasets. The guide highlights GLUE and SQuAD as examples.

The source warns that GLUE is a collection of different subsets covering different tasks. A user first needs to choose the subset that corresponds to the task, such as `mnli` for natural language inference. The metric and data format depend on that selected subset.

Dataset-specific evaluation requires following the benchmark's expected format. For SQuAD, the guide explains that the model receives `question` and `context`, and returns `prediction_text`. That prediction is compared with references by matching the question `id`.

The source gives this compact SQuAD example:

```python
from evaluate import load

squad_metric = load("squad")
predictions = [
    {
        "prediction_text": "1976",
        "id": "56e10a3be3433e1400422b22",
    }
]
references = [
    {
        "answers": {
            "answer_start": [97],
            "text": ["1976"],
        },
        "id": "56e10a3be3433e1400422b22",
    }
]
results = squad_metric.compute(
    predictions=predictions,
    references=references,
)
print(results)
```

Expected result:

```python
{"exact_match": 100.0, "f1": 100.0}
```

The guide recommends using the dataset preview or dataset card to inspect example structures, then using the metric card to understand the dedicated evaluation function.

For a local RAG benchmark, the same discipline applies. If the golden set defines expected relevant sources, answerability labels, and accepted answer text, the evaluator must preserve those fields and compare outputs using the intended schema. A metric implementation should not silently reinterpret the benchmark format.

# Selecting retrieval, answer, benchmark, and custom checks

The Evaluate guide is short, but its metric-selection principles translate directly into a practical RAG evaluation design. The evaluator should choose metrics by mapping each system behavior to the metric category that fits it best.

## Retrieval metrics

Retrieval metrics evaluate whether the retriever finds and ranks relevant evidence. They are not answer-quality metrics, but they determine what evidence is available to the generator.

Useful retrieval checks include:

- recall@k for whether expected evidence appears within the context candidate set;
- precision@k for whether the top results are mostly useful;
- MRR for whether the first relevant result appears early;
- nDCG when relevance is graded rather than binary;
- MAP when ranking quality across more of the retrieved list matters;
- category-routing accuracy when the retriever filters by predicted knowledge category.

These metrics are generic or retrieval-task-specific. They require a judgment set that identifies relevant documents, chunks, source slugs, or categories. The cutoff `k` should match the application context budget. A report should not claim strong RAG quality from retrieval metrics alone.

## Answer metrics

Answer metrics evaluate the generated response. The right metric depends on answer style.

For short factual answers, exact match and F1 may be appropriate, especially when the accepted answer has a known form. For generated explanations or summaries, lexical overlap metrics such as ROUGE may be useful but incomplete because a semantically correct answer can use different wording. For open-ended answers, rubric-based human review or validated model-graded checks may be more suitable.

RAG answer evaluation often needs checks that are not captured by generic text similarity:

- groundedness: whether claims are supported by retrieved context;
- citation validity: whether cited chunks were actually included in selected context;
- answer relevance: whether the response addresses the question;
- no-answer correctness: whether the system refuses or abstains when evidence is insufficient;
- completeness: whether all required answer parts are covered.

These are task-specific or custom metrics. Their cards or local documentation should define inputs, outputs, thresholds, and limitations.

## Benchmark metrics

Benchmark metrics should be used when evaluating against a known dataset with a dedicated scoring convention. The guide's SQuAD example illustrates the main rule: follow the benchmark's input and output schema exactly.

In a RAG benchmark, the benchmark schema might include:

- `question_id` for stable matching;
- `question` and optional `context` or source constraints;
- expected answer text or answer aliases;
- expected relevant source slugs or chunk ids;
- answerability labels;
- route or category expectations;
- case type, such as answerable, no-answer, ambiguous, or fallback-routing.

Metrics should preserve those fields through the evaluation pipeline. If predictions and references are matched by id, the id must be stable. If source relevance is non-exhaustive, the report should say so because it affects precision, MAP, and false-positive interpretation.

## Custom checks

The guide's "no one size fits all" principle leaves room for custom metrics when generic, task-specific, or dataset-specific metrics do not measure the behavior that matters. Custom checks are often necessary for RAG systems because the product risk may be tied to citation use, unsupported claims, latency, token budget, or security boundaries.

Examples of custom RAG checks:

- every cited source must be among selected context chunks;
- answer text must not cite a source when the response is a no-answer;
- total selected context must stay under a token budget;
- routed retrieval must fall back to all categories when confidence is below a threshold;
- answer generation must include an explicit insufficient-evidence response when context lacks support;
- generated answer must not include sensitive fields that are absent from approved context.

Custom checks should be documented like metric cards. At minimum, define:

- purpose: what behavior the check measures;
- inputs: prediction fields, reference fields, trace fields, and context fields;
- output: score type, boolean result, label, or numeric range;
- aggregation: mean, count, rate, per-case table, or threshold;
- limitation: what the metric does not prove.

## Practical selection pattern

A compact RAG evaluation suite can combine metrics from all three source categories:

1. Use generic metrics for binary or categorical outcomes, such as routing accuracy and no-answer accuracy.
2. Use retrieval-specific metrics for ranked evidence, such as recall@k, precision@k, MRR, and nDCG.
3. Use task-specific answer metrics for generated responses, such as exact match, F1, ROUGE, or rubric scores.
4. Use benchmark-specific metrics when the dataset prescribes a schema or scorer.
5. Add custom checks for trace-level guarantees such as citation validity, context-budget compliance, and source grounding.

This design follows the Hugging Face guide's main constraint: metric choice must fit the task and dataset. A metric report should explain why each metric is included, what input structure it uses, and which failure modes it can and cannot detect.
