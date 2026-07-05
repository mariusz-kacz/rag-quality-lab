# Source snapshot

Source metadata:
- source_slug: huggingface-evaluate-considerations
- category: RAG evaluation and quality
- upstream_url: https://huggingface.co/docs/evaluate/main/en/considerations
- source_markdown: https://github.com/huggingface/evaluate/blob/main/docs/source/considerations.mdx
- license: Apache-2.0
- pinned_version: huggingface-evaluate@main
- snapshot_type: normalized documentation digest from Hugging Face Evaluate MDX documentation
- normalization: removed Hugging Face site navigation, version switcher, GitHub page chrome, image-only label diagrams, admonition rendering, footer material, and external discussion thread details; retained evaluation split guidance, class-imbalance cautions, offline versus online evaluation, interpretability and resource tradeoffs, limitation and bias guidance, and RAG-oriented interpretation

---
# Evaluation splits, imbalance, and metric combinations

The Hugging Face Evaluate guide presents model evaluation as an iterative part of machine learning development, not a final one-time check. Model work often involves architecture choices, hyperparameter tuning, and convergence toward a final candidate. Responsible evaluation is the process that keeps those choices honest.

The guide highlights two early evaluation design issues that affect whether reported metrics are meaningful: using the correct data split and accounting for class imbalance.

## Properly splitting data

The source recommends three dataset splits for a sound evaluation workflow:

- `train`: used to train the model;
- `validation`: used to validate model hyperparameters;
- `test`: used to evaluate the model.

Datasets on the Hugging Face Hub are not always split the same way. Some have `train` and `validation` only, some have `train`, `validation`, and `test`, and some have only a training split. The evaluator must use the right split for the right purpose.

If a dataset does not already define a train-test split, the user must decide which data will be used for training, hyperparameter tuning, and final evaluation. The source recommends keeping roughly 10-30% for evaluation depending on dataset size, while making the test set reflect production data as closely as possible.

The key warning is that training and evaluating on the same split can misrepresent results. A model that overfits training data can look strong on that same data while performing poorly on new data.

For a RAG quality lab, the same principle applies even when there is no model fine-tuning. Evaluation questions used to tune prompts, routing thresholds, chunking rules, rerankers, or retrieval filters should not be the only questions used for final reporting. A practical split can be:

- development questions for prompt and retrieval iteration;
- validation questions for threshold choices and metric-debugging;
- held-out test questions for final comparisons between retrieval modes.

If the dataset is too small for strict three-way splitting, the report should say so and avoid overstating generalization.

## Production-like test sets

The source explicitly recommends that the test set reflect production data. This is important because benchmark performance can diverge from real usage. A production-like RAG test set should include the question forms and failure modes expected in use:

- answerable questions with direct evidence;
- answerable questions requiring multiple chunks or sources;
- insufficient-evidence questions that should trigger no-answer behavior;
- ambiguous questions that should route conservatively or request clarification;
- category-boundary questions that test retrieval filters;
- stale, duplicate, or weakly related source material.

The test set should also preserve relevant metadata: expected category, expected sources, answerability label, case type, and any allowed answer aliases. Without those fields, metric interpretation becomes ambiguous.

## Class imbalance

The guide explains that many academic datasets are balanced, but real-world datasets often are not. A balanced dataset has labels represented equally. The source contrasts this with fraud detection, where non-fraud cases usually far outnumber fraud cases.

Class imbalance can skew metrics. The guide gives a simple example: a dataset with 99 non-fraud cases and 1 fraud case. A model that always predicts non-fraud gets 99% accuracy, but it never catches the fraud case. The high accuracy sounds good until the minority class is considered.

The source recommends using more than one metric to understand model performance from different points of view. Precision and recall can be used together, and F1 is their harmonic mean. Accuracy can reflect overall performance for balanced data, but F1 can be more representative when labels are imbalanced because it combines precision and recall.

In a RAG evaluation set, imbalance is common:

- most questions may be answerable, while no-answer cases are rare;
- one knowledge category may dominate the corpus;
- easy single-source questions may outnumber multi-source questions;
- successful retrieval cases may hide weak routing behavior;
- safe refusals may be underrepresented compared with normal answers.

A single aggregate metric can hide minority-case failure. For example, no-answer accuracy may be poor even when overall answer accuracy is high. Category routing may look acceptable while a small security category is never selected. Reports should include per-case-type or per-category metrics when the distribution is uneven.

## Combining metrics

The source's recommendation to combine precision, recall, and F1 generalizes to RAG evaluation. Different metrics expose different failures:

- recall@k asks whether expected evidence reached the candidate set;
- precision@k asks whether retrieved context is mostly relevant;
- MRR asks whether the first useful source appears early;
- no-answer accuracy asks whether the system abstains when evidence is missing;
- citation validity asks whether cited sources were actually included in context;
- groundedness checks whether answer claims are supported by context;
- latency and token metrics show operational cost.

Metric combinations should be intentional. If false negatives are expensive, emphasize recall. If unsupported answer generation is expensive, emphasize precision, citation validity, and groundedness. If the application must answer quickly, include latency and context-size metrics.

## Reporting distributions

Responsible evaluation should report dataset composition alongside metric scores. Useful distribution fields include:

- number of questions;
- counts by answerability label;
- counts by knowledge category;
- counts by case type;
- number of expected relevant sources per question;
- length or token distribution for queries and selected context;
- proportion of ambiguous or fallback-routing cases.

These fields make imbalance visible and help reviewers decide whether a metric is trustworthy for the intended use case.

# Offline evaluation, interpretability, resource tradeoffs, and limitations

The guide distinguishes offline and online evaluation, then discusses practical tradeoffs and limitations that should be communicated as part of model assessment.

## Offline versus online evaluation

Offline evaluation happens before deployment or before using model-generated insights. It uses static datasets and metrics. Offline evaluation can compare models against common benchmarks because every candidate is scored on the same data.

Online evaluation happens after deployment, while the model is used in production. It can measure production behavior such as latency, accuracy on live data, and the number of user queries the model successfully addresses.

The source notes that offline and online evaluation can use different metrics and measure different aspects of performance. Offline benchmark success does not guarantee production success. Online success metrics can be affected by traffic mix, user behavior, interface design, logging quality, and operational constraints.

For RAG systems:

- offline evaluation is appropriate for deterministic golden-set comparisons between retrieval modes, prompts, and context policies;
- online evaluation is appropriate for monitoring live answer success, no-answer rates, retrieval latency, token usage, citation errors, and user feedback;
- the two should be connected through error analysis so production failures become new offline test cases.

## Interpretability

The guide identifies interpretability as an important dimension of evaluation, especially for production deployments. Some metrics are easy to understand. Exact match has a clear range, such as 0 to 1 or 0% to 100%, and a clear rule: for a pair of strings, the score is 1 if they are exactly the same and 0 otherwise.

Other metrics are harder to interpret. The guide uses BLEU as an example: although BLEU also has a bounded range, scores can vary depending on parameters, tokenization, and normalization. A BLEU score is difficult to interpret without knowing the scoring procedure and limitations described in its metric card.

For RAG evaluation, interpretable reporting means metric names are not enough. A report should include:

- the metric formula or concise definition;
- the cutoff, such as `@5`;
- whether relevance labels are binary or graded;
- whether judgments are exhaustive or partial;
- the aggregation method;
- key threshold values;
- per-question diagnostics for failures.

Metrics that are hard to explain can still be useful, but they need procedure details. A model-graded groundedness score, for example, should include the rubric, score range, examples, and known limitations.

## Inference speed and memory footprint

The guide says that evaluating models in practice often requires tradeoffs. A model may be slightly less accurate but faster, or more accurate but require more memory, more GPUs, or more difficult deployment. Inference speed is the time required to make a prediction, and it depends on hardware and query mode, such as real-time API calls versus batch jobs. Memory footprint is the size of model weights and the hardware memory they occupy.

These resource concerns are especially important for online evaluation. The guide notes that online settings often require a tradeoff between inference speed and accuracy or precision, while the tradeoff is less central in offline evaluation.

RAG systems add resource tradeoffs beyond the generator model:

- embedding cost and latency;
- vector search latency;
- reranking latency;
- number of retrieved candidates;
- number of chunks selected for context;
- prompt token count;
- output token budget;
- citation validation cost;
- storage and index size.

A retrieval mode that improves recall but doubles latency may be inappropriate for an interactive assistant. A larger context window may improve answer completeness but increase cost and reduce throughput. Evaluation should therefore include both quality and resource metrics when the goal is production readiness.

## Accuracy, precision, and operational tradeoffs

The guide's example of choosing between a faster model and a more accurate, resource-intensive model maps to common RAG decisions:

- higher `top_k` can improve recall but increase reranking and context cost;
- stricter category filtering can improve precision but reduce recall when routing is wrong;
- larger chunks can preserve context but reduce retrieval specificity;
- smaller chunks can improve matching but require more context assembly;
- stronger no-answer thresholds can reduce hallucination but increase false abstentions.

These tradeoffs should be measured rather than guessed. A useful report compares quality metrics with latency, token totals, and failure modes.

## Limitations and bias

The source states that all models and metrics have limitations and biases. These depend on how models were trained, what data was used, and the intended uses. Limitations should be measured and communicated clearly to prevent misuse and unintended impacts. The guide points to model cards as a way to document training and evaluation.

It also describes ways to measure bias, including evaluating on bias-oriented datasets and using interactive error analysis to identify subsets of the evaluation data where the model performs poorly.

For RAG systems, limitations and bias can appear in several places:

- corpus coverage: the source collection may omit important viewpoints or policies;
- relevance judgments: expected sources may be incomplete or subjective;
- routing categories: categories may encode project assumptions;
- retrieval model: embeddings may underperform on certain terminology, languages, or formats;
- generation: the model may overstate evidence or smooth over uncertainty;
- evaluation set: golden questions may overrepresent easy or common cases.

The evaluation report should document these limitations explicitly. It should also include subset analysis where possible, such as performance by category, case type, answerability, source age, language, or question style.

## Error analysis and evaluation maintenance

The guide mentions interactive error analysis as a way to find poorly performing subsets. In a RAG lab, error analysis should feed evaluation maintenance:

1. Inspect failed or borderline traces.
2. Label the failure mode, such as routing error, retrieval miss, context omission, unsupported answer, bad citation, or incorrect no-answer.
3. Add representative cases to the development or validation set.
4. Keep a held-out test set for final comparisons.
5. Update documentation when metric definitions, thresholds, or known limitations change.

This keeps evaluation aligned with real system behavior rather than frozen around the easiest original benchmark cases.
