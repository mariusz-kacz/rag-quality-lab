# Source snapshot

Source metadata:
- source_slug: ragas-rag-metrics
- category: RAG evaluation and quality
- upstream_url: https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/
- source_markdown: https://github.com/vibrantlabsai/ragas/tree/main/docs/concepts/metrics/available_metrics
- license: Apache-2.0
- pinned_version: ragas@main-snapshot-2026-07-10
- observed_source_commit: main snapshot inspected 2026-07-10
- snapshot_captured: 2026-07-10
- snapshot_type: normalized documentation digest from Ragas documentation pages
- normalization: removed navigation, installation scaffolding, long API examples, page footer content, and repeated legacy API variants; retained RAG metric taxonomy, required input fields, formulas, metric interpretation, context quality concepts, faithfulness, response relevancy, and noise sensitivity guidance

---
# RAG metric surfaces and required inputs

Ragas organizes evaluation metrics by application type. For Retrieval Augmented Generation, the available metrics include context precision, context recall, context entities recall, noise sensitivity, response relevancy, and faithfulness. The central idea is that RAG quality has multiple surfaces: the retriever must select useful context, the generator must use that context faithfully, and the final response must address the user's question.

The Ragas metric list is useful because it separates retrieval quality from answer quality. A single "RAG score" can hide the failure mode. Low context recall means the retriever missed information needed for the reference answer. Low context precision means relevant context is ranked poorly or surrounded by irrelevant context. Low faithfulness means the answer makes claims that cannot be supported by the retrieved context. Low response relevancy means the answer does not address the input well even if the retrieved context is useful.

The common fields used by the RAG metrics are:

- `user_input`: the user's question or task.
- `retrieved_contexts`: the list of retrieved text chunks supplied to the model or evaluator.
- `response`: the generated answer.
- `reference`: the expected answer or reference answer, used by metrics that need a target answer.
- `reference_contexts`: labeled reference contexts, used by non-LLM context recall.
- `retrieved_context_ids` and `reference_context_ids`: IDs for direct recall calculation when a document ID system exists.

Metrics do not all need the same fields. This matters for evaluation design:

- Faithfulness needs `response` and `retrieved_contexts` because it checks whether generated claims are supported by context.
- Response relevancy needs `user_input` and `response` because it checks whether the answer addresses the question.
- LLM-based context recall needs `reference` and `retrieved_contexts` because it breaks the reference answer into claims and checks which claims are supported by retrieved context.
- Non-LLM context recall needs `retrieved_contexts` and `reference_contexts` because it compares retrieved context against labeled reference context.
- ID-based context recall needs `retrieved_context_ids` and `reference_context_ids` because it evaluates retrieval by stable identifiers.
- Noise sensitivity needs `user_input`, `response`, `reference`, and `retrieved_contexts` because it checks how incorrect answer claims relate to relevant or irrelevant retrieved context.

Context recall measures whether important information was retrieved. The LLM-based form uses the reference answer as a proxy when annotating reference contexts is too expensive. It breaks the reference into claims and checks whether each claim can be attributed to retrieved context:

```text
context_recall =
  claims in the reference supported by retrieved context
  / total claims in the reference
```

The non-LLM form compares retrieved contexts with reference contexts:

```text
context_recall =
  relevant contexts retrieved
  / total reference contexts
```

The ID-based form compares retrieved context IDs with reference context IDs:

```text
id_context_recall =
  reference context IDs found in retrieved context IDs
  / total reference context IDs
```

The distinction is useful for this project. Golden questions currently name expected source slugs rather than exhaustive qrels. That makes ID-like recall useful for lightweight checks, while LLM-based recall is useful when the expected answer can be decomposed into claims. Both approaches require clear judgment assumptions: expected sources might be non-exhaustive, and unlisted sources may still support an answer.

Context precision evaluates whether retrieved contexts are useful and well ordered. Ragas includes variants such as LLM-based context precision, non-LLM context precision, and ID-based context precision. Precision is about the quality and rank of what was retrieved, not just whether any relevant item appears. In a RAG workflow with a small context budget, the highest-ranked chunks matter most because they are most likely to be included in the prompt and cited by the generator.

The practical evaluation contract from Ragas is:

1. Decide which field labels are available: answer references, reference contexts, IDs, or only query/context/response triples.
2. Select retrieval metrics for context quality and generator metrics for answer quality.
3. Keep retrieval metrics separate from answer metrics so failures can be attributed.
4. Record whether a metric is LLM-based, non-LLM, or ID-based.
5. Treat context quality as a prerequisite for grounded answer quality, not as a substitute for answer evaluation.

# Faithfulness, context quality, response relevancy, and noise sensitivity

Faithfulness measures whether the generated response is supported by the retrieved context. Ragas calculates faithfulness by examining claims in the answer and checking whether those claims can be inferred from the context. A high-faithfulness answer states only information supported by the retrieved passages. A low-faithfulness answer can be fluent and relevant but still include an unsupported or contradictory claim.

The metric is especially important for RAG because retrieved context is supposed to reduce unsupported generation. If the answer adds details outside the retrieved evidence, the RAG pipeline has failed even when the answer sounds plausible. Faithfulness is therefore closer to a groundedness check than a relevance check.

Response relevancy measures how well the generated response addresses the user's input. It is different from faithfulness. An answer can be faithful to the provided context but fail to answer the question directly. An answer can also be relevant to the question while being unfaithful to the retrieved evidence. A robust RAG evaluation should check both when possible.

Context precision and context recall represent two sides of context quality:

- Context precision asks whether the retrieved contexts are relevant and well ordered. It penalizes noisy retrieval because irrelevant chunks can distract the generator, consume context budget, and create citation noise.
- Context recall asks whether the retrieved contexts include the information needed to support the reference answer. It penalizes missing evidence.

This split mirrors practical RAG debugging. If recall is low, increase retriever coverage, improve chunking, change embeddings, add hybrid retrieval, or adjust `top_k`. If precision is low, reduce noisy chunks, improve reranking, tune thresholds, remove duplicates, or tighten source filters. If recall and precision are both acceptable but the answer is poor, the failure may be in generation, prompt design, citation handling, or answer format.

Noise sensitivity measures how often incorrect claims in the response are associated with retrieved context. The Ragas documentation describes modes for relevant and irrelevant context. The metric examines answer claims, checks correctness against the reference, and analyzes whether claims can be attributed to relevant or irrelevant retrieved context.

For relevant-context noise sensitivity, the core ratio is:

```text
noise_sensitivity_relevant =
  incorrect claims in the response
  / total claims in the response
```

The metric is useful because RAG systems can fail by overreacting to retrieved context. A model may copy misleading context, combine context incorrectly, or let irrelevant retrieved passages influence the answer. A low noise sensitivity score is desirable because it means fewer answer claims are incorrect under the retrieved-context conditions.

For this project's evaluation category, Ragas is most valuable as a RAG-specific metric taxonomy. It gives the corpus direct language for context precision, context recall, faithfulness, response relevancy, and noise sensitivity. It also reinforces that metrics require explicit inputs and judgment assumptions. This is stronger corpus material than a generic information retrieval glossary because it maps directly to RAG traces: user question, retrieved chunks, selected context, answer, citations, expected sources, and no-answer behavior.
