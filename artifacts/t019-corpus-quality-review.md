# T019 Corpus Quality Review

Status: prompt, RAG/context, evaluation, and LLM settings replacements implemented
Created: 2026-07-10
Scope: prompt engineering, RAG/context handling, RAG evaluation, and LLM settings rows from `artifacts/t019-corpus-materials-proposal.md`

Implementation note: Prompting replacements were implemented in `corpus/manifest.json` and `corpus/sources/` on 2026-07-10. `azure-openai-prompt-engineering-techniques` was replaced by `openai-api-prompt-engineering`, and `microsoft-advanced-prompts` was replaced by `openai-gpt5-prompting-guide`.

Implementation note: RAG/context replacements were implemented in `corpus/manifest.json` and `corpus/sources/` on 2026-07-10. `openai-embedding-wikipedia-search` was replaced by `azure-ai-search-chunk-documents`, and `openai-file-search-responses` was replaced by `qdrant-hybrid-and-multistage-queries`.

Implementation note: RAG evaluation replacements were implemented in `corpus/manifest.json` and `corpus/sources/` on 2026-07-10. `wikipedia-ir-evaluation-measures` was replaced by `ragas-rag-metrics`, `huggingface-evaluate-choosing-metric` was replaced by `deepeval-rag-metrics`, and `huggingface-evaluate-considerations` was removed without replacement.

Implementation note: LLM settings replacements were implemented in `corpus/manifest.json` and `corpus/sources/` on 2026-07-10. `openai-text-generation` was replaced by `openai-cost-optimization`, `openai-handle-rate-limits` was replaced by `openai-rate-limits`, and `openai-prompt-caching` was refreshed for cache-write and breakpoint behavior.

## Summary

The current T019 proposal over-selects sources that are either too introductory, too generic, or only loosely aligned with the project's RAG quality goal. The generated corpus is still usable for plumbing, ingestion, routing, and trace validation, but the learning value of the prompt engineering and RAG evaluation categories is uneven.

The corpus should be reduced toward fewer, stronger documents rather than padded to keep five or six sources per category. The project only needs 15-30 source pages overall, so a leaner corpus with three high-signal sources per category is acceptable if the five required categories remain represented.

## Quality Bar

A source should stay in the corpus only if it satisfies most of these criteria:

- It directly supports expected questions in this lab, not just the broad category name.
- It remains useful after code, page chrome, classroom scaffolding, and product setup are removed.
- It has clear provenance and a reusable license or documented reuse terms.
- It contains enough substantive text to create retrievable chunks without synthetic filler.
- It has limited overlap with other selected sources.
- It teaches durable concepts, tradeoffs, metrics, or failure modes rather than only tool syntax.

## Prompt Engineering Review

| Current source | Recommendation | Reason |
| --- | --- | --- |
| `azure-openai-prompt-engineering-techniques` | Replace | The source is broad and partly legacy. The local snapshot even preserves a warning that the techniques are not recommended for reasoning models. It includes basic prompt components and old Completion/Chat Completion framing, so it is weak as a 2026 prompt-engineering source. |
| `microsoft-advanced-prompts` | Replace | Lesson-style material. The local snapshot is more of a rewritten digest than a close source snapshot, which weakens attribution and corpus credibility. |
| `openai-gpt41-prompting-guide` | Keep | Practical, model-specific, and useful for instruction following, agentic workflows, long-context behavior, and migration questions. |
| `openai-o-series-prompting-guide` | Keep | Useful because reasoning-model prompting differs from generic prompt engineering. It helps answer questions about concise instructions, constraints, and when not to over-prescribe reasoning. |
| `azure-openai-structured-outputs` | Keep or move | Strong document, but it is more "output control and schema reliability" than prompt engineering. Keep only if the category is treated as prompt and output control; otherwise move it to settings/cost/tokens or replace it. |

### Recommended Prompt Set

Prefer this set if the prompt category stays at five sources:

| Proposed source | Review link | Category role | Notes |
| --- | --- | --- | --- |
| `openai-api-prompt-engineering` | [OpenAI API prompt engineering guide](https://developers.openai.com/api/docs/guides/prompt-engineering) | Current general prompt practices | Use the OpenAI API prompt engineering guide as the general baseline. Capture snapshot metadata and reuse terms before ingest. |
| `openai-gpt5-prompting-guide` | [OpenAI Cookbook GPT-5 prompting guide](https://developers.openai.com/cookbook/examples/gpt-5/gpt-5_prompting_guide) | Current model-specific prompting | Replace older or weaker prompting material with the GPT-5 prompting guide if reuse terms and source pinning are acceptable. |
| `openai-gpt41-prompting-guide` | [OpenAI Cookbook GPT-4.1 prompting guide](https://github.com/openai/openai-cookbook/blob/8730772/examples/gpt4-1_prompting_guide.ipynb) | GPT-series instruction following and long context | Keep if the corpus wants contrast with GPT-5/reasoning guidance. |
| `openai-o-series-prompting-guide` | [OpenAI Cookbook o-series prompting guide](https://github.com/openai/openai-cookbook/blob/8730772/examples/o-series/o3o4-mini_prompting_guide.ipynb) | Reasoning-model prompt behavior | Keep as the reasoning-model counterpart. |
| `azure-openai-structured-outputs` | [Azure OpenAI structured outputs](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/structured-outputs) | Reliable structured responses | Keep as application-level output control, not as generic prompt technique material. |

If the category can shrink to three sources, keep only `openai-api-prompt-engineering`, `openai-gpt5-prompting-guide`, and `azure-openai-structured-outputs` or `openai-o-series-prompting-guide`.

## RAG Evaluation And Quality Review

| Current source | Recommendation | Reason |
| --- | --- | --- |
| `microsoft-foundry-rag-evaluators` | Keep | Directly maps RAG process evaluation, system evaluation, retrieval quality, groundedness, relevance, completeness, thresholds, and data mappings. This is one of the strongest sources in the category. |
| `openai-evaluation-flywheel` | Keep | Useful operational evaluation loop: failure discovery, annotation, graders, prompt/system improvement, and regression test expansion. |
| `trec-common-evaluation-measures` | Keep | Durable retrieval metric reference. Keep as the canonical IR metrics source if one generic IR source remains. |
| `wikipedia-ir-evaluation-measures` | Replace | Mostly duplicates TREC and adds license/attribution complexity. It is broad glossary material, not RAG-specific quality material. |
| `huggingface-evaluate-choosing-metric` | Replace | Generic metric-selection guidance. The local snapshot adds RAG interpretation, but the source itself is not RAG-specific enough. |
| `huggingface-evaluate-considerations` | Replace | Good ML evaluation hygiene, but too generic for the RAG evaluation category. Better as background reading than corpus material. |

### Recommended Evaluation Set

Prefer this set if the evaluation category stays at five or six sources:

| Proposed source | Review link | Category role | Notes |
| --- | --- | --- | --- |
| `microsoft-foundry-rag-evaluators` | [Microsoft Foundry RAG evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rag-evaluators) | RAG evaluator taxonomy | Keep. |
| `openai-evaluation-flywheel` | [OpenAI Cookbook evaluation flywheel](https://developers.openai.com/cookbook/examples/evaluation/building_resilient_prompts_using_an_evaluation_flywheel) | Evaluation process and regression loop | Keep. |
| `trec-common-evaluation-measures` | [TREC common evaluation measures PDF](https://trec.nist.gov/pubs/trec15/appendices/CE.MEASURES06.pdf) | Retrieval metrics | Keep as the single generic IR metrics source. |
| `ragas-rag-metrics` | [Ragas RAG metrics index](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/) | RAG-specific metrics | Candidate replacement for Wikipedia/Hugging Face rows. Review especially [faithfulness](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/), [context precision](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/context_precision/), [context recall](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/context_recall/), and [response relevancy](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/answer_relevance/). Repository license is Apache-2.0, but exact docs source paths and pin should be resolved before ingest. |
| `langsmith-evaluate-rag-application` | [LangSmith evaluate a RAG application](https://docs.langchain.com/langsmith/evaluate-rag-tutorial) | Evaluator surfaces and dataset workflow | Candidate replacement if documentation reuse terms are acceptable. It cleanly separates correctness, relevance, groundedness, and retrieval relevance for RAG applications. |

If reuse terms for LangSmith docs are not acceptable, do not snapshot it. Use it only as a design reference and select another license-clear RAG evaluation source instead.

## Proposed Corpus Direction

Do not keep weak documents just to maintain artificial category symmetry. A better corpus shape is:

| Category | Target count | Rationale |
| --- | ---: | --- |
| prompting techniques | 3-5 | Use current OpenAI/model-specific guidance and structured-output reliability. |
| RAG and context handling | 5 | Current set is mostly stronger than the prompt/eval rows; review separately before changing. |
| RAG evaluation and quality | 4-5 | Keep only one generic IR metric source, then prefer RAG-specific evaluator and process sources. |
| LLM security and risks | 5-6 | Current OWASP/NIST mix is likely fine. |
| LLM settings, cost, and tokens | 5 | Refined OpenAI token/cost/latency/rate-limit/prompt-caching set is implemented. |

This keeps the project within the 15-30 source-page requirement while improving density and reducing synthetic RAG-oriented interpretation inside generic source snapshots.

## Replacement Work Items

1. Decide whether to shrink categories or maintain five sources per category.
2. Verify reuse terms and source pins for current OpenAI API docs, Ragas docs, and any LangSmith candidate.
3. Update `artifacts/t019-corpus-materials-proposal.md` with accepted replacements and explicitly demote rejected rows.
4. Update `corpus/manifest.json` and remove replaced source files only after the replacement set is approved.
5. Regenerate local snapshots from source material, keeping them close to the source and avoiding synthetic filler.
6. Re-run corpus inspection and ingestion tests.
7. Re-run golden evals because changed source slugs and content will affect expected relevant sources and retrieval metrics.
