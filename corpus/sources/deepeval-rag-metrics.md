# Source snapshot

Source metadata:
- source_slug: deepeval-rag-metrics
- category: RAG evaluation and quality
- upstream_url: https://deepeval.com/docs/metrics-introduction
- source_markdown: https://github.com/confident-ai/deepeval/tree/main/docs/docs
- license: Apache-2.0
- pinned_version: deepeval@main-snapshot-2026-07-10
- observed_source_commit: main snapshot inspected 2026-07-10
- snapshot_captured: 2026-07-10
- snapshot_type: normalized documentation digest from DeepEval documentation pages
- normalization: removed website navigation, marketing chrome, install/setup repetition, platform-specific report notes, and long code variants; retained metric selection guidance, RAG retriever and generator metric split, required test-case fields, thresholds, scoring behavior, LLM-as-judge customization notes, and compact examples

---
# Retriever and generator metric taxonomy

DeepEval frames metric choice around the system component being evaluated. Custom metrics can be written for use-case-specific criteria, while generic metrics evaluate recurring system patterns such as RAG, agents, and multi-turn conversations. For RAG, DeepEval explicitly separates retriever metrics from generator metrics so the evaluation can identify whether a failure came from missing or noisy context or from the answer generation step.

The metrics introduction recommends limiting an evaluation suite to a small number of prioritized metrics rather than collecting many loosely defined numbers. For a RAG system, DeepEval suggests focusing on metrics such as `AnswerRelevancyMetric` and `FaithfulnessMetric`, while the RAG metric set also includes contextual precision, contextual recall, and contextual relevancy.

The main RAG metric surfaces are:

- Contextual precision: evaluates whether relevant retrieval nodes are ranked higher in the retrieval context.
- Contextual recall: evaluates whether the retrieval context contains the information needed to support the expected output.
- Contextual relevancy: evaluates signal-to-noise in retrieved context by checking whether context statements are relevant to the input.
- Faithfulness: evaluates whether the generated answer is supported by the retrieval context and avoids hallucination.
- Answer relevancy: evaluates whether the generated answer aligns with the input.

This taxonomy is useful because retriever and generator failures can look similar in the final answer. A wrong answer can result from missing evidence, irrelevant context, poor context order, unsupported generation, or an answer that is faithful but off target. DeepEval's split makes those failure surfaces visible.

Contextual relevancy measures the relevance of statements inside the retrieval context to the input. The documentation explains that the metric first uses an LLM to extract statements from `retrieval_context`, then classifies whether each statement is relevant to the `input`. Its score is the share of relevant statements among all extracted context statements:

```text
contextual_relevancy =
  number of relevant statements
  / total number of statements
```

This metric measures signal-to-noise, not merely whether the answer passage is somewhere in the context. A context can contain the right answer but still score poorly if the right passage is buried in irrelevant text. For a RAG pipeline, a low contextual relevancy score usually points toward noisy retrieval, overly large chunks, weak filters, poor reranking, or redundant context.

Contextual precision measures ranking quality within the retrieval context. DeepEval uses an LLM to judge whether each node is relevant to the input based on the expected output, then computes a weighted cumulative precision score. The score emphasizes top-ranked results because generators tend to give more attention to earlier context nodes. A higher contextual precision score means the retriever places relevant nodes higher.

Contextual recall measures whether the retrieval context captures information needed for the expected output. DeepEval first extracts statements from `expected_output`, then checks whether each statement can be attributed to the retrieval context:

```text
contextual_recall =
  attributable statements
  / total statements
```

The documentation uses `expected_output` rather than `actual_output` for contextual recall because the metric is measuring retriever quality for an ideal answer, not whether the generator happened to use the retrieved context. A higher score indicates the retriever found more of the relevant information available in the knowledge base.

Faithfulness and answer relevancy evaluate the generator side:

- Faithfulness checks whether the actual answer is supported by retrieved context. It is a hallucination or groundedness control.
- Answer relevancy checks whether the actual answer addresses the input. It is a query-answer alignment control.

A compact RAG diagnosis matrix is:

| Symptom | Likely metric signal | Likely fix area |
| --- | --- | --- |
| Relevant evidence missing from context | Low contextual recall | chunking, embeddings, retrieval mode, `top_k`, filters |
| Evidence appears late or under noisy chunks | Low contextual precision or relevancy | reranking, thresholds, source diversity, chunk size |
| Answer adds unsupported facts | Low faithfulness | prompt grounding, no-answer behavior, citation checks |
| Answer is grounded but does not answer the question | Low answer relevancy | prompt instructions, answer format, query understanding |

# Thresholds, scoring, and test-case requirements

DeepEval metrics use test cases with explicit fields. RAG metrics typically use `LLMTestCase` fields such as:

- `input`: the user question or request.
- `actual_output`: the answer generated by the system.
- `expected_output`: the reference answer, when a metric requires ground truth.
- `retrieval_context`: the retrieved context nodes supplied to the model or evaluator.

Different metrics require different fields:

- Contextual precision uses `input`, `expected_output`, and `retrieval_context` because it judges whether retrieved nodes are relevant for producing the expected answer and whether relevant nodes are ordered well.
- Contextual recall uses `expected_output` and `retrieval_context` because it checks whether expected-answer statements are attributable to retrieved context.
- Contextual relevancy uses `input` and `retrieval_context` because it checks whether context statements are relevant to the user input.
- Faithfulness uses `actual_output` and `retrieval_context` because it checks generated claims against retrieved evidence.
- Answer relevancy uses `input` and `actual_output` because it checks whether the answer aligns with the user request.

DeepEval metric constructors include common controls:

- `threshold`: the minimum passing score. The default shown for several metrics is 0.5.
- `model`: the LLM judge to use, either a named model or a custom `DeepEvalBaseLLM`.
- `include_reason`: whether the metric should include a natural-language reason for the score.
- `strict_mode`: when enabled, enforces a binary perfect-or-fail score and sets the threshold to 1.
- `async_mode`: whether metric measurement can run concurrently.
- `verbose_mode`: whether intermediate calculation steps are printed.
- `evaluation_template`: an overridable prompt template for LLM-as-judge behavior.

Thresholds make metrics operational. A score is useful for trend analysis, but a threshold defines pass/fail behavior for tests and review gates. A threshold should be calibrated against representative examples because LLM-as-judge metrics can vary with prompt templates, judge model choice, answer style, and corpus domain.

DeepEval also emphasizes reference versus referenceless metrics. Reference-based metrics need ground truth, such as contextual recall or tool correctness. Referenceless metrics can run without labeled data and are more practical for production monitoring where no reference answer exists. This distinction maps cleanly to RAG lab workflows: golden-set evaluation can use expected outputs and expected sources, while ad hoc trace review may rely on referenceless checks such as contextual relevancy or faithfulness against selected context.

The documentation notes that LLM-as-judge metrics can be customized by overriding evaluation templates. This is important for smaller judge models, domain-specific criteria, or stricter expectations around evidence. A RAG evaluator should document when it uses default prompts versus customized judge prompts, because template changes can change the meaning of scores.

DeepEval supports standalone metric measurement for one test case and evaluation runs over datasets or traced components. Standalone measurement is useful for debugging a single failing trace. Dataset evaluation is better for reporting because it produces consistent reports and can reuse optimizations such as caching and concurrent execution.

For this project's corpus, DeepEval is useful because it gives a concrete RAG evaluation vocabulary that maps to local artifacts:

1. Use `input` from the golden question text.
2. Use `retrieval_context` from retrieved or included chunks.
3. Use `actual_output` from the generated answer.
4. Use `expected_output` or expected source labels when available.
5. Report thresholds and pass/fail labels rather than raw scores alone.
6. Keep retriever metrics and generator metrics separate in diagnostics.

This replaces generic metric-selection guidance with RAG-specific evaluator framing. It helps reviewers understand which metrics need ground truth, which can run without labels, how thresholds affect pass/fail behavior, and why the same final answer failure can require different fixes depending on whether retrieval, context noise, faithfulness, or answer relevancy is the root cause.
