# Source snapshot

Source metadata:
- source_slug: microsoft-foundry-rag-evaluators
- category: RAG evaluation and quality
- upstream_url: https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rag-evaluators
- source_markdown: https://github.com/MicrosoftDocs/azure-ai-docs/blob/main/articles/foundry/concepts/evaluation-evaluators/rag-evaluators.md
- license: CC BY 4.0 content / MIT code examples
- pinned_version: microsoft-azure-ai-docs@main
- snapshot_type: normalized documentation digest from Microsoft Learn source markdown
- normalization: removed Microsoft Learn page chrome, feedback controls, sample links lists, and footer content; retained evaluator taxonomy, required data mappings, context format guidance, threshold semantics, document retrieval metrics, parameter-sweep guidance, and compact configuration examples

---
# Process and system evaluation taxonomy

The source defines Retrieval-Augmented Generation evaluation around the full RAG workflow. A user query triggers retrieval from a corpus of grounding documents, and the retrieved context is used by a model to generate a response. Evaluation therefore has two related surfaces: the retrieval process that selects context, and the final system response that uses that context.

Microsoft Foundry separates RAG evaluators into process evaluation and system evaluation.

Process evaluation focuses on the retrieval step before answer generation:

- `Retrieval` evaluates how relevant retrieved context chunks are to the query when there is no ground-truth relevance label set. It uses an LLM judge and returns pass or fail based on a 1-to-5 scoring scale and threshold.
- `Document Retrieval` evaluates whether retrieved documents match query relevance labels, also known as ground truth or qrels. It returns a composite set of search-quality metrics such as Fidelity, NDCG, XDCG, Max Relevance, and Holes.

System evaluation focuses on the generated response after retrieval:

- `Groundedness` evaluates whether a response aligns with the provided context and avoids fabricating content. It is framed as the precision side of grounded answering: the response should not include material outside the grounding context.
- `Groundedness Pro` is a preview evaluator that uses the Azure AI Content Safety service to test strict consistency between response and context. It returns a boolean result rather than a 1-to-5 numeric score.
- `Relevance` evaluates whether the response directly addresses the user's query, including accuracy, completeness, and direct relevance, without requiring ground truth.
- `Response Completeness` is a preview evaluator that checks whether the response covers expected information from ground truth. It is framed as the recall side of response quality: the response should not miss critical expected information.

The source explicitly contrasts groundedness and response completeness. Groundedness checks whether the response avoids unsupported content outside the context. Response completeness checks whether the response includes the important information expected from the ground truth. A response can be grounded but incomplete if it only says true things from context while omitting key facts. A response can be complete-looking but ungrounded if it includes expected facts that are not supported by the supplied context.

The evaluator selection can be summarized as follows:

| Evaluator | Evaluation surface | Use when | Primary output |
| --- | --- | --- | --- |
| Document Retrieval | Process | Retrieval quality is a bottleneck and query relevance labels are available | Composite retrieval metrics with pass/fail labels |
| Retrieval | Process | Retrieved context quality must be judged without ground-truth labels | Pass/fail from a 1-to-5 LLM-judge score |
| Groundedness | System | The response should be checked against provided context using an LLM judge | Pass/fail from a 1-to-5 score |
| Groundedness Pro | System | Strict context consistency should be checked with Azure AI Content Safety | Boolean pass/fail |
| Relevance | System | Response quality relative to the query should be judged without ground truth | Pass/fail from a 1-to-5 score |
| Response Completeness | System | The response should be checked for missing expected information | Pass/fail from a 1-to-5 score |

This taxonomy is useful for RAG quality work because it avoids treating "answer quality" as a single metric. A poor answer might come from weak retrieval, irrelevant context, unsupported generation, incomplete synthesis, or a response that is grounded but does not answer the question. The right evaluator depends on which failure surface is being investigated and what labels are available.

## Required inputs and mappings

Each evaluator requires specific input fields and, for LLM-judge evaluators, model deployment configuration.

The source lists these required inputs:

- `Groundedness`: requires `response`; `context` is optional but recommended; `query` is optional and can improve scoring. For agent response mode, it can use `query`, `response`, and `tool_definitions`.
- `Groundedness Pro`: requires `query`, `response`, and `context`.
- `Relevance`: requires `query` and `response`.
- `Response Completeness`: requires `ground_truth` and `response`.
- `Retrieval`: requires `query` and `context`.
- `Document Retrieval`: requires `retrieval_ground_truth` and `retrieved_documents`.

The standard dataset shape for many RAG evaluators includes `query`, `context`, and `response`. The query is the user's question, the context is the retrieved text supplied to the model, and the response is the generated answer.

Compact example record:

```json
{
  "query": "What are the store hours?",
  "context": "Our store is open Monday-Friday 9am-6pm and Saturday 10am-4pm.",
  "response": "The store is open weekdays from 9am to 6pm and Saturdays from 10am to 4pm."
}
```

For multi-chunk retrieval, the `context` field is still a plain string. The source recommends concatenating chunks with a separator such as a blank line. This keeps evaluator input simple while allowing the context to represent multiple retrieved chunks.

Compact multi-chunk context example:

```json
{
  "query": "What is the return policy?",
  "context": "Items can be returned within 30 days with receipt.\n\nGift items are eligible for store credit only.",
  "response": "You can return items within 30 days with your receipt."
}
```

For agent evaluation with `{{sample.output_items}}`, context can be optional if the response contains tool call messages. The evaluator can extract context from tool call results. For groundedness evaluation of tool-assisted responses, the source recommends supplying `tool_definitions` so the evaluator can better judge whether the response is grounded in retrieved tool output. If traces already include tool definitions, they can be used automatically.

Data mappings use template syntax:

- `{{item.field_name}}` references fields from the test dataset, such as `{{item.query}}`;
- `{{sample.output_items}}` references generated or retrieved agent responses during evaluation.

Compact configuration example:

```python
testing_criteria = [
    {
        "type": "azure_ai_evaluator",
        "name": "groundedness",
        "evaluator_name": "builtin.groundedness",
        "initialization_parameters": {"deployment_name": model_deployment},
        "data_mapping": {
            "context": "{{item.context}}",
            "response": "{{item.response}}",
        },
    },
    {
        "type": "azure_ai_evaluator",
        "name": "relevance",
        "evaluator_name": "builtin.relevance",
        "initialization_parameters": {"deployment_name": model_deployment},
        "data_mapping": {
            "query": "{{item.query}}",
            "response": "{{item.response}}",
        },
    },
    {
        "type": "azure_ai_evaluator",
        "name": "retrieval",
        "evaluator_name": "builtin.retrieval",
        "initialization_parameters": {"deployment_name": model_deployment},
        "data_mapping": {
            "query": "{{item.query}}",
            "context": "{{item.context}}",
        },
    },
]
```

The source advises providing `query`, `response`, and `context` for the strongest groundedness results. Even when `query` is optional for an evaluator, including it can improve scoring accuracy because the judge can understand both the user intent and the retrieved support.

# Retrieval quality, groundedness, relevance, and thresholds

Most RAG evaluators in the source return a score from 1 to 5, where 1 is very poor and 5 is excellent. The default passing threshold is 3. Scores greater than or equal to the threshold are labeled as passing. The output includes the evaluator type, evaluator name, metric name, score, pass/fail label, reason, threshold, and a boolean `passed` field.

Compact numeric output shape:

```json
{
  "type": "azure_ai_evaluator",
  "name": "Groundedness",
  "metric": "groundedness",
  "score": 4,
  "label": "pass",
  "reason": "The response is grounded in the provided context.",
  "threshold": 3,
  "passed": true
}
```

Groundedness Pro differs from the LLM-judge 1-to-5 evaluators. It uses Azure AI Content Safety and returns a boolean-style result rather than a numeric score. Its output still includes evaluator metadata, a metric name, a pass/fail label, a reason, and `passed`.

Compact Groundedness Pro output shape:

```json
{
  "type": "azure_ai_evaluator",
  "name": "Groundedness Pro",
  "metric": "groundedness_pro",
  "label": "pass",
  "reason": "The response is strictly consistent with the provided context.",
  "passed": true
}
```

Thresholds make evaluator results operational. A raw score can be useful for trend analysis, but pass/fail labels let a test suite or batch evaluation gate behavior. For RAG systems, thresholds should be chosen with representative datasets because evaluator strictness, model-judge behavior, corpus style, and answer format can affect scores.

## Retrieval evaluator without ground truth

The `Retrieval` evaluator measures how relevant retrieved context chunks are to a query when no ground-truth labels are available. It uses the `query` and `context` fields and requires a model deployment for the LLM judge.

This evaluator is useful when a team wants to test whether the retrieved text is plausibly useful for answering the question but has not built a qrels dataset. It does not measure whether the exact correct document was returned according to human labels. Instead, it judges the textual relevance of the provided context to the query.

The retrieval evaluator is therefore well suited to early development, regression checks, or qualitative corpus debugging. It is less precise than document retrieval metrics with ground truth because it depends on judge behavior and does not provide ranked-list metrics such as NDCG.

## Document retrieval evaluator with ground truth

The source emphasizes document retrieval quality because retrieval is upstream of answer generation. If retrieval is poor and the answer requires corpus-specific knowledge, the language model is less likely to produce a satisfactory answer. The `document_retrieval` evaluator is the most precise retrieval measurement in this source because it compares retrieved documents against human-labeled relevance data.

The evaluator expects two mapped fields:

- `retrieval_ground_truth`: a list of document IDs with human relevance labels for the query;
- `retrieved_documents`: a list of retrieved document IDs with relevance scores from the search system.

Compact configuration:

```python
testing_criteria = [
    {
        "type": "azure_ai_evaluator",
        "name": "document_retrieval",
        "evaluator_name": "builtin.document_retrieval",
        "initialization_parameters": {
            "ground_truth_label_min": 1,
            "ground_truth_label_max": 5,
        },
        "data_mapping": {
            "retrieval_ground_truth": "{{item.retrieval_ground_truth}}",
            "retrieved_documents": "{{item.retrieved_documents}}",
        },
    },
]
```

Compact data shape:

```python
retrieval_ground_truth = [
    {"document_id": "1", "query_relevance_label": 4},
    {"document_id": "2", "query_relevance_label": 2},
]

retrieved_documents = [
    {"document_id": "2", "relevance_score": 45.1},
    {"document_id": "6", "relevance_score": 35.8},
]
```

The document retrieval evaluator returns multiple search-quality metrics:

- `Fidelity`: how well the top retrieved chunks reflect known good documents for the query. The source describes it as the number of good documents returned out of the total number of known good documents in the dataset.
- `NDCG`: normalized discounted cumulative gain, measuring how good the ranking is relative to an ideal order where relevant items appear at the top.
- `XDCG`: a top-k ranking measure focused on how good results are within the top-k documents regardless of scores assigned to other index documents.
- `Max Relevance`: the maximum relevance found among the top-k chunks.
- `Holes`: a label sanity metric counting retrieved documents that are missing query relevance judgments.

The evaluator can also return metrics such as `ndcg@3`, `xdcg@3`, `top1_relevance`, `top3_max_relevance`, `holes`, and `holes_ratio`.

Compact output shape:

```json
[
  {
    "type": "azure_ai_evaluator",
    "name": "Document Retrieval",
    "metric": "ndcg@3",
    "score": 0.646,
    "label": "pass",
    "passed": true
  },
  {
    "type": "azure_ai_evaluator",
    "name": "Document Retrieval",
    "metric": "fidelity",
    "score": 0.019,
    "label": "fail",
    "passed": false
  }
]
```

The source recommends using document retrieval metrics for parameter sweeps. A team can generate retrieval results for different search settings, such as vector search, semantic search, `top_k`, or chunk size, then use `document_retrieval` to identify which settings produce the strongest retrieval quality. This fits RAG optimization because retrieval tuning often affects answer quality before the answer model sees any context.

## Groundedness, relevance, and completeness

Groundedness checks whether the generated answer stays supported by the context. It is not the same as answer relevance: a response can be grounded in the context but fail to answer the user's question directly. Relevance checks whether the response addresses the user's query. Response completeness checks whether the response includes critical expected information from ground truth.

A robust RAG evaluation set should therefore include multiple checks when possible:

- retrieval quality, to ensure the right evidence reaches the model;
- groundedness, to ensure the model does not fabricate beyond the evidence;
- relevance, to ensure the response answers the actual query;
- response completeness, when ground truth is available and missing critical information matters;
- document retrieval metrics, when ranked retrieval labels are available.

For this project's RAG corpus, the source is most useful as an evaluator map. It describes which quality questions belong to retrieval, which belong to final answer evaluation, how inputs should be mapped, how thresholds convert scores into pass/fail outcomes, and how document retrieval metrics can support systematic tuning of search mode, `top_k`, and chunking choices.
