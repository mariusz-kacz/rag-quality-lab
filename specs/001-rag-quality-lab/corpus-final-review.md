# Final Corpus Review

Last updated: 2026-07-10

This document is the human review index for the current corpus state after the initial generation plan and all approved refinement tasks. Use this as the single review entry point for the final selected corpus.

Runtime source of truth remains `corpus/manifest.json`. This document mirrors the current manifest in a reviewer-friendly format and links each local snapshot to its upstream reference page.

## Review Checklist

For each row:

1. Open the local snapshot and confirm it is useful without page chrome, setup noise, or synthetic filler.
2. Open the upstream reference and confirm the local snapshot reflects the intended source.
3. Check the license or reuse note and pinned version.
4. Confirm the listed H1 sections match the local snapshot and manifest.
5. Confirm the source belongs in its category and does not duplicate a stronger source.

## Corpus Summary

| Category | Source count | Review status |
| --- | ---: | --- |
| prompting techniques | 5 | Final after prompting refinement |
| RAG and context handling | 5 | Final after RAG/context refinement |
| RAG evaluation and quality | 5 | Final after evaluation refinement |
| LLM security and risks | 6 | Kept without second-pass review by approved decision |
| LLM settings, cost, and tokens | 5 | Final after settings refinement |

Total sources: 26

## Prompting Techniques

| Source slug | Title | Local snapshot | Upstream reference | Pinned version | License / reuse note | Sections |
| --- | --- | --- | --- | --- | --- | --- |
| `openai-api-prompt-engineering` | Prompt engineering | [openai-api-prompt-engineering.md](../../corpus/sources/openai-api-prompt-engineering.md) | [OpenAI prompt engineering](https://developers.openai.com/api/docs/guides/prompt-engineering) | `openai-api-docs@current-snapshot` | OpenAI API docs reuse terms pending snapshot verification | Message roles and instruction hierarchy; Prompt testing, model snapshots, and output control |
| `openai-gpt5-prompting-guide` | GPT-5 prompting guide | [openai-gpt5-prompting-guide.md](../../corpus/sources/openai-gpt5-prompting-guide.md) | [OpenAI Cookbook GPT-5 prompting guide](https://developers.openai.com/cookbook/examples/gpt-5/gpt-5_prompting_guide) | `openai-cookbook@main-snapshot-2026-07-10` | MIT | GPT-5 prompt behavior and instruction tuning; Agentic workflows, verbosity, and migration patterns |
| `openai-gpt41-prompting-guide` | GPT-4.1 prompting guide | [openai-gpt41-prompting-guide.md](../../corpus/sources/openai-gpt41-prompting-guide.md) | [OpenAI Cookbook GPT-4.1 prompting guide](https://github.com/openai/openai-cookbook/blob/8730772/examples/gpt4-1_prompting_guide.ipynb) | `openai-cookbook@8730772` | MIT | Instruction following and agentic workflows; Long context guidance and prompt migration |
| `openai-o-series-prompting-guide` | o-series prompting guide | [openai-o-series-prompting-guide.md](../../corpus/sources/openai-o-series-prompting-guide.md) | [OpenAI Cookbook o-series prompting guide](https://github.com/openai/openai-cookbook/blob/8730772/examples/o-series/o3o4-mini_prompting_guide.ipynb) | `openai-cookbook@8730772` | MIT | Reasoning model instruction design; Concise instructions versus detailed constraints |
| `azure-openai-structured-outputs` | Structured outputs | [azure-openai-structured-outputs.md](../../corpus/sources/azure-openai-structured-outputs.md) | [Azure OpenAI structured outputs](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/structured-outputs) | `microsoft-azure-ai-docs@main` | CC BY 4.0 content / MIT code examples | Schema constrained outputs; Constraints, model support, and compact examples |

## RAG And Context Handling

| Source slug | Title | Local snapshot | Upstream reference | Pinned version | License / reuse note | Sections |
| --- | --- | --- | --- | --- | --- | --- |
| `azure-ai-search-rag-overview` | Retrieval-augmented generation in Azure AI Search | [azure-ai-search-rag-overview.md](../../corpus/sources/azure-ai-search-rag-overview.md) | [Azure AI Search RAG overview](https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview) | `microsoft-azure-docs@main` | CC BY 4.0 content / MIT code examples | RAG architecture and query understanding; Token constraints, security trimming, and retrieval patterns |
| `azure-ai-search-chunk-documents` | Chunk documents | [azure-ai-search-chunk-documents.md](../../corpus/sources/azure-ai-search-chunk-documents.md) | [Chunk documents in Azure AI Search](https://learn.microsoft.com/en-us/azure/search/vector-search-how-to-chunk-documents) | `microsoft-azure-docs@main-snapshot-2026-07-10` | CC BY 4.0 content / MIT code examples | Chunking workflow and strategy selection; Chunk size, overlap, token limits, and indexing implications |
| `openai-question-answering-embeddings` | Question answering using embeddings | [openai-question-answering-embeddings.md](../../corpus/sources/openai-question-answering-embeddings.md) | [OpenAI Cookbook question answering using embeddings](https://github.com/openai/openai-cookbook/blob/8730772/examples/Question_answering_using_embeddings.ipynb) | `openai-cookbook@8730772` | MIT | Search-Ask retrieval workflow; Context assembly, answer grounding, and no-answer behavior |
| `azure-ai-search-vector-relevance-ranking` | Relevance in vector search | [azure-ai-search-vector-relevance-ranking.md](../../corpus/sources/azure-ai-search-vector-relevance-ranking.md) | [Azure AI Search vector relevance ranking](https://learn.microsoft.com/en-us/azure/search/vector-search-ranking) | `microsoft-azure-docs@main` | CC BY 4.0 content / MIT code examples | KNN, ANN, and similarity metrics; Score interpretation, k selection, chunk tuning, and hybrid ranking |
| `qdrant-hybrid-and-multistage-queries` | Hybrid and multi-stage queries | [qdrant-hybrid-and-multistage-queries.md](../../corpus/sources/qdrant-hybrid-and-multistage-queries.md) | [Qdrant hybrid queries](https://qdrant.tech/documentation/search/hybrid-queries/) | `qdrant-landing-page@master-snapshot-2026-07-10` | Qdrant documentation reuse terms pending snapshot verification | Hybrid retrieval and dense-sparse fusion; Multi-stage retrieval, prefetch, and reranking patterns |

## RAG Evaluation And Quality

| Source slug | Title | Local snapshot | Upstream reference | Pinned version | License / reuse note | Sections |
| --- | --- | --- | --- | --- | --- | --- |
| `microsoft-foundry-rag-evaluators` | Retrieval-Augmented Generation evaluators | [microsoft-foundry-rag-evaluators.md](../../corpus/sources/microsoft-foundry-rag-evaluators.md) | [Microsoft Foundry RAG evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rag-evaluators) | `microsoft-azure-ai-docs@main` | CC BY 4.0 content / MIT code examples | Process and system evaluation taxonomy; Retrieval quality, groundedness, relevance, and thresholds |
| `openai-evaluation-flywheel` | Building resilient prompts using an evaluation flywheel | [openai-evaluation-flywheel.md](../../corpus/sources/openai-evaluation-flywheel.md) | [OpenAI evaluation flywheel](https://developers.openai.com/cookbook/examples/evaluation/building_resilient_prompts_using_an_evaluation_flywheel) | `openai-cookbook@8730772` | MIT | Failure-mode discovery and annotation; Automatic graders, prompt improvement, and test expansion |
| `trec-common-evaluation-measures` | Common evaluation measures | [trec-common-evaluation-measures.md](../../corpus/sources/trec-common-evaluation-measures.md) | [TREC common evaluation measures](https://trec.nist.gov/pubs/trec15/appendices/CE.MEASURES06.pdf) | `trec-common-evaluation-measures-2006` | Public/government documentation, reuse metadata pending snapshot verification | Recall, precision, and ranked-list evaluation; Average precision, R-precision, bpref, and GMAP |
| `ragas-rag-metrics` | Ragas RAG metrics | [ragas-rag-metrics.md](../../corpus/sources/ragas-rag-metrics.md) | [Ragas available metrics](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/) | `ragas@main-snapshot-2026-07-10` | Apache-2.0 | RAG metric surfaces and required inputs; Faithfulness, context quality, response relevancy, and noise sensitivity |
| `deepeval-rag-metrics` | DeepEval RAG metrics | [deepeval-rag-metrics.md](../../corpus/sources/deepeval-rag-metrics.md) | [DeepEval metrics introduction](https://deepeval.com/docs/metrics-introduction) | `deepeval@main-snapshot-2026-07-10` | Apache-2.0 | Retriever and generator metric taxonomy; Thresholds, scoring, and test-case requirements |

## LLM Security And Risks

| Source slug | Title | Local snapshot | Upstream reference | Pinned version | License / reuse note | Sections |
| --- | --- | --- | --- | --- | --- | --- |
| `owasp-llm01-prompt-injection` | LLM01 Prompt Injection | [owasp-llm01-prompt-injection.md](../../corpus/sources/owasp-llm01-prompt-injection.md) | [OWASP LLM01 Prompt Injection](https://github.com/OWASP/www-project-top-10-for-large-language-model-applications/blob/0205957/2_0_vulns/LLM01_PromptInjection.md) | `owasp-llm-top-10@0205957` | CC BY-SA 4.0 | Prompt injection risks; Examples, scenarios, and mitigations |
| `owasp-llm02-sensitive-information-disclosure` | LLM02 Sensitive Information Disclosure | [owasp-llm02-sensitive-information-disclosure.md](../../corpus/sources/owasp-llm02-sensitive-information-disclosure.md) | [OWASP LLM02 Sensitive Information Disclosure](https://github.com/OWASP/www-project-top-10-for-large-language-model-applications/blob/0205957/2_0_vulns/LLM02_SensitiveInformationDisclosure.md) | `owasp-llm-top-10@0205957` | CC BY-SA 4.0 | Sensitive information disclosure risks; Data leakage scenarios and mitigations |
| `owasp-llm04-data-model-poisoning` | LLM04 Data and Model Poisoning | [owasp-llm04-data-model-poisoning.md](../../corpus/sources/owasp-llm04-data-model-poisoning.md) | [OWASP LLM04 Data and Model Poisoning](https://github.com/OWASP/www-project-top-10-for-large-language-model-applications/blob/0205957/2_0_vulns/LLM04_DataModelPoisoning.md) | `owasp-llm-top-10@0205957` | CC BY-SA 4.0 | Data and model poisoning risks; Lifecycle, scenarios, and mitigation controls |
| `owasp-llm06-excessive-agency` | LLM06 Excessive Agency | [owasp-llm06-excessive-agency.md](../../corpus/sources/owasp-llm06-excessive-agency.md) | [OWASP LLM06 Excessive Agency](https://github.com/OWASP/www-project-top-10-for-large-language-model-applications/blob/0205957/2_0_vulns/LLM06_ExcessiveAgency.md) | `owasp-llm-top-10@0205957` | CC BY-SA 4.0 | Tool-use and excessive agency risks; Permission boundaries and mitigations |
| `owasp-llm08-vector-embedding-weaknesses` | LLM08 Vector and Embedding Weaknesses | [owasp-llm08-vector-embedding-weaknesses.md](../../corpus/sources/owasp-llm08-vector-embedding-weaknesses.md) | [OWASP LLM08 Vector and Embedding Weaknesses](https://github.com/OWASP/www-project-top-10-for-large-language-model-applications/blob/0205957/2_0_vulns/LLM08_VectorAndEmbeddingWeaknesses.md) | `owasp-llm-top-10@0205957` | CC BY-SA 4.0 | Vector and embedding weaknesses; Retrieval-specific risks and mitigations |
| `nist-generative-ai-risk-profile` | Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile | [nist-generative-ai-risk-profile.md](../../corpus/sources/nist-generative-ai-risk-profile.md) | [NIST AI 600-1](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf) | `nist-ai-600-1@2024-07` | Public NIST publication, reuse metadata pending snapshot verification | Generative AI risk taxonomy; Risk-management actions for LLM and RAG systems |

## LLM Settings, Cost, And Tokens

| Source slug | Title | Local snapshot | Upstream reference | Pinned version | License / reuse note | Sections |
| --- | --- | --- | --- | --- | --- | --- |
| `openai-cost-optimization` | Cost optimization | [openai-cost-optimization.md](../../corpus/sources/openai-cost-optimization.md) | [OpenAI cost optimization](https://developers.openai.com/api/docs/guides/cost-optimization) | `openai-api-docs@current-snapshot-2026-07-10` | OpenAI API docs reuse terms pending snapshot verification | Cost and latency reduction levers; Batch, flex processing, model choice, and token minimization |
| `openai-token-counting` | How to count tokens with tiktoken | [openai-token-counting.md](../../corpus/sources/openai-token-counting.md) | [OpenAI Cookbook token counting](https://github.com/openai/openai-cookbook/blob/8730772/examples/How_to_count_tokens_with_tiktoken.ipynb) | `openai-cookbook@8730772` | MIT | Token counting concepts; Prompt budgeting and model-specific token accounting |
| `openai-latency-optimization` | Latency optimization | [openai-latency-optimization.md](../../corpus/sources/openai-latency-optimization.md) | [OpenAI Cookbook latency optimization](https://github.com/openai/openai-cookbook/blob/8730772/examples/data/oai_docs/latency-optimization.txt) | `openai-cookbook@8730772` | MIT | Latency and efficiency principles; Token reduction, fewer requests, streaming, and RAG trimming |
| `openai-rate-limits` | Rate limits | [openai-rate-limits.md](../../corpus/sources/openai-rate-limits.md) | [OpenAI rate limits](https://developers.openai.com/api/docs/guides/rate-limits) | `openai-api-docs@current-snapshot-2026-07-10` | OpenAI API docs reuse terms pending snapshot verification | Rate-limit scope, usage tiers, and limit dimensions; Headers, shared limits, retries, batching, and ingestion limits |
| `openai-prompt-caching` | Prompt caching | [openai-prompt-caching.md](../../corpus/sources/openai-prompt-caching.md) | [OpenAI prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching) | `openai-api-docs@current-snapshot-2026-07-10` | OpenAI API docs reuse terms pending snapshot verification | Prompt caching mechanics; Static and dynamic prompt layout, cache keys, breakpoints, and usage observability |

## Related Planning Documents

- [Corpus generation plan](corpus-generation-plan.md): initial source-snapshot execution plan.
- [Corpus refinement plan](corpus-refinement-plan.md): approved review decisions and implementation tasks.
- [T019 corpus materials proposal](../../artifacts/t019-corpus-materials-proposal.md): historical proposal and external-search review.
- [T019 corpus quality review](../../artifacts/t019-corpus-quality-review.md): quality notes and replacement rationale.
