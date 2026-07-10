# T019 Corpus Materials Proposal

Status: superseded by approved corpus refinement
Created: 2026-07-03
Purpose: approval gate before creating `corpus/manifest.json` and local snapshots under `corpus/sources/`.

## Selection Rationale

`T019` still names a DAIR.AI-only manifest, but `specs/001-rag-quality-lab/research.md` updates the corpus strategy: DAIR.AI is useful but not sufficient for balanced coverage of the five required categories. This proposal selects a 27-document curated corpus from multiple openly licensed, pinnable or source-backed documentation sets.

The proposed corpus keeps the 15-30 source-page requirement and balances the five required categories with five materials each, plus one additional security/risk material because data and model poisoning is directly relevant to RAG corpus integrity. Each selected material should become one `SourcePage` record after approval.

## Pin Candidates

Use these repository versions as the initial pin targets. Resolve the full commit SHA during snapshot creation if the manifest should store more than the short SHA shown by GitHub.

| Source | Proposed pinned_version | License | Role |
| --- | --- | --- | --- |
| Microsoft Learn Foundry/Azure OpenAI docs | `microsoft-azure-ai-docs@main` (resolve source commit before snapshot) | CC BY 4.0 content / MIT code examples | Curated Azure/OpenAI prompt engineering, structured-output, and RAG evaluator documentation |
| Microsoft Learn Azure Search docs | `microsoft-azure-docs@main` (resolve source commit before snapshot) | CC BY 4.0 content / MIT code examples | Curated RAG architecture, vector search, and relevance/ranking documentation |
| OpenAI Cookbook / Developers Cookbook | `openai-cookbook@8730772` | MIT | Prompting guides, embeddings, vector search, RAG/evaluation workflow, token counting, rate limits |
| OpenAI API docs | `openai-api-docs@current-snapshot` and `openai-api-docs@current-snapshot-2026-07-10` (verify reuse terms before snapshot) | Verify documentation reuse terms before snapshot | Current prompt engineering, cost optimization, rate limits, prompt caching, and context-management guidance |
| Qdrant documentation | `qdrant-landing-page@master-snapshot-2026-07-10` | Reuse terms pending snapshot verification | Qdrant hybrid retrieval, dense-sparse fusion, prefetch, and multistage retrieval guidance |
| OWASP Top 10 for LLM Applications | `owasp-llm-top-10@0205957` | CC BY-SA 4.0 | LLM security and risk taxonomy |
| NIST AI Risk Management Framework: Generative AI Profile | `nist-ai-600-1@2024-07` | Public NIST publication, verify reuse metadata before snapshot | Cross-sector generative AI risk taxonomy and risk-management actions |
| NIST TREC evaluation material | `trec-common-evaluation-measures-2006` | Public/government documentation, verify reuse metadata before snapshot | General retrieval evaluation measures and reporting conventions |
| Ragas docs | `ragas@main-snapshot-2026-07-10` | Apache-2.0 | RAG-specific metric surfaces for faithfulness, context quality, response relevancy, and noise sensitivity |
| DeepEval docs | `deepeval@main-snapshot-2026-07-10` | Apache-2.0 | RAG-specific retriever and generator metric taxonomy, thresholds, and test-case requirements |

## Category Coverage

| Category | Count | Main sources |
| --- | ---: | --- |
| prompting techniques | 5 | OpenAI API docs, OpenAI Cookbook, Microsoft Learn |
| RAG and context handling | 5 | Microsoft Learn, OpenAI Cookbook, Qdrant docs |
| RAG evaluation and quality | 5 | Microsoft Learn, OpenAI Cookbook, TREC, Ragas, DeepEval |
| LLM security and risks | 6 | OWASP, NIST |
| LLM settings, cost, and tokens | 5 | OpenAI API docs, OpenAI Cookbook |

## Selected Materials

| # | Proposed slug | Category | Source | Upstream reference | Local snapshot target | Short description |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | `openai-api-prompt-engineering` | prompting techniques | OpenAI API docs | [`Prompt engineering`](https://developers.openai.com/api/docs/guides/prompt-engineering) | `corpus/sources/openai-api-prompt-engineering.md` | Current prompt-engineering guidance covering message roles, instruction hierarchy, prompt sectioning, few-shot examples, context-window planning, prompt versioning in code, prompt testing, and output-control implications. Snapshot should keep documentation text and compact examples, excluding page chrome and repeated SDK snippets. |
| 2 | `openai-gpt5-prompting-guide` | prompting techniques | OpenAI Cookbook | [`GPT-5 prompting guide`](https://developers.openai.com/cookbook/examples/gpt-5/gpt-5_prompting_guide) | `corpus/sources/openai-gpt5-prompting-guide.md` | Current GPT-5 prompting guidance covering explicit instruction tuning, ambiguity review, agentic persistence, verbosity, minimal reasoning, Markdown behavior, metaprompting, and migration from earlier prompt styles. Snapshot should keep guidance and compact prompt examples, excluding raw notebook structure and long benchmark prompts. |
| 3 | `openai-gpt41-prompting-guide` | prompting techniques | OpenAI Cookbook | [`examples/gpt4-1_prompting_guide.ipynb`](https://github.com/openai/openai-cookbook/blob/8730772/examples/gpt4-1_prompting_guide.ipynb) | `corpus/sources/openai-gpt41-prompting-guide.md` | Practical model-specific prompting guidance for instruction following, agentic workflows, long context, and prompt migration. Snapshot should extract narrative guidance and compact prompt examples, excluding raw notebook JSON, execution outputs, and long code cells. |
| 4 | `openai-o-series-prompting-guide` | prompting techniques | OpenAI Cookbook | [`examples/o-series/o3o4-mini_prompting_guide.ipynb`](https://github.com/openai/openai-cookbook/blob/8730772/examples/o-series/o3o4-mini_prompting_guide.ipynb) | `corpus/sources/openai-o-series-prompting-guide.md` | Reasoning-model prompting guidance, including when to give concise instructions versus detailed constraints. Snapshot should keep the guidance and illustrative prompt snippets, not raw notebook structure or generated outputs. |
| 5 | `azure-openai-structured-outputs` | prompting techniques | Microsoft Learn Azure OpenAI docs | [`Structured outputs`](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/structured-outputs) | `corpus/sources/azure-openai-structured-outputs.md` | Curated documentation for schema-constrained model outputs, useful for reliable formatting and machine-readable answer, trace, and evaluation shapes. Snapshot should keep concepts, constraints, supported-model notes, and compact schema examples, excluding repeated SDK boilerplate. |
| 6 | `azure-ai-search-rag-overview` | RAG and context handling | Microsoft Learn Azure Search docs | [`Retrieval-augmented generation in Azure AI Search`](https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview) | `corpus/sources/azure-ai-search-rag-overview.md` | Curated RAG architecture documentation covering query understanding, multi-source data access, token constraints, latency, security trimming, agentic retrieval, and classic RAG retrieval patterns. Snapshot should keep documentation text and decision framing, excluding page chrome. |
| 7 | `azure-ai-search-chunk-documents` | RAG and context handling | Microsoft Learn Azure Search docs | [`Chunk documents in Azure AI Search`](https://learn.microsoft.com/en-us/azure/search/vector-search-how-to-chunk-documents) | `corpus/sources/azure-ai-search-chunk-documents.md` | Focused chunking guidance covering strategy selection, chunk size, overlap, token/character mismatch, sentence boundaries, indexing workflow, and model input constraints. Snapshot should keep conceptual guidance and compact examples, excluding page chrome and long output excerpts. |
| 8 | `openai-question-answering-embeddings` | RAG and context handling | OpenAI Cookbook | [`examples/Question_answering_using_embeddings.ipynb`](https://github.com/openai/openai-cookbook/blob/8730772/examples/Question_answering_using_embeddings.ipynb) | `corpus/sources/openai-question-answering-embeddings.md` | Search-Ask pattern covering retrieval over reference text, prompt context assembly, answer grounding, no-answer behavior, and cost tradeoffs. |
| 9 | `azure-ai-search-vector-relevance-ranking` | RAG and context handling | Microsoft Learn Azure Search docs | [`Relevance in vector search`](https://learn.microsoft.com/en-us/azure/search/vector-search-ranking) | `corpus/sources/azure-ai-search-vector-relevance-ranking.md` | Curated documentation on exhaustive KNN, HNSW/ANN tradeoffs, similarity metrics, score interpretation, `k` selection, chunk-size relevance tuning, and hybrid semantic ranking. Snapshot should keep conceptual guidance and compact tables, excluding code snippets and page chrome. |
| 10 | `qdrant-hybrid-and-multistage-queries` | RAG and context handling | Qdrant documentation | [`Hybrid and multi-stage queries`](https://qdrant.tech/documentation/search/hybrid-queries/) | `corpus/sources/qdrant-hybrid-and-multistage-queries.md` | Qdrant-specific retrieval guidance covering dense+sparse fusion, prefetch, Reciprocal Rank Fusion, score fusion, multistage retrieval, reranking, formula scoring, and grouping. Snapshot should keep retrieval architecture guidance and compact examples, excluding repeated SDK variants and navigation chrome. |
| 11 | `microsoft-foundry-rag-evaluators` | RAG evaluation and quality | Microsoft Learn Foundry docs | [`Retrieval-Augmented Generation (RAG) evaluators`](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rag-evaluators) | `corpus/sources/microsoft-foundry-rag-evaluators.md` | High-signal RAG evaluator taxonomy covering process versus system evaluation, retrieval quality, groundedness, relevance, response completeness, data mappings, thresholds, and search metrics such as NDCG, XDCG, max relevance, and holes. Snapshot should preserve evaluator definitions and metric framing while excluding SDK boilerplate and Azure-only execution steps. |
| 12 | `openai-evaluation-flywheel` | RAG evaluation and quality | OpenAI Developers Cookbook | [`Building resilient prompts using an evaluation flywheel`](https://developers.openai.com/cookbook/examples/evaluation/building_resilient_prompts_using_an_evaluation_flywheel) | `corpus/sources/openai-evaluation-flywheel.md` | Practical evaluation-process guide covering failure-mode discovery, annotation, automatic graders, prompt improvement, model comparison, and synthetic test-data expansion. Useful for turning RAG failures into repeatable regression tests. Snapshot should keep process guidance and compact examples, excluding UI chrome and product-specific workflow details. |
| 13 | `trec-common-evaluation-measures` | RAG evaluation and quality | NIST TREC | [`Common Evaluation Measures`](https://trec.nist.gov/pubs/trec15/appendices/CE.MEASURES06.pdf) | `corpus/sources/trec-common-evaluation-measures.md` | Durable retrieval-evaluation reference covering recall, precision, ranked-list evaluation, average precision, R-precision, recall-precision curves, bpref, and GMAP. Useful for judging retriever quality independently from generation. Snapshot should keep formulas, metric explanations, and compact examples, excluding report boilerplate and graph rendering artifacts. |
| 14 | `ragas-rag-metrics` | RAG evaluation and quality | Ragas docs | [`Ragas available metrics`](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/) | `corpus/sources/ragas-rag-metrics.md` | RAG-specific metric guidance covering required inputs, context precision, context recall, faithfulness, response relevancy, and noise sensitivity. Snapshot should keep metric definitions and compact formulas, excluding navigation and long API examples. |
| 15 | `deepeval-rag-metrics` | RAG evaluation and quality | DeepEval docs | [`DeepEval metrics introduction`](https://deepeval.com/docs/metrics-introduction) | `corpus/sources/deepeval-rag-metrics.md` | RAG-specific evaluator framing covering retriever metrics, generator metrics, thresholds, test-case fields, referenceless versus reference-based checks, and LLM-as-judge customization. Snapshot should keep conceptual guidance and compact examples, excluding product chrome and repeated setup code. |
| 17 | `owasp-llm01-prompt-injection` | LLM security and risks | OWASP | [`2_0_vulns/LLM01_PromptInjection.md`](https://github.com/OWASP/www-project-top-10-for-large-language-model-applications/blob/0205957/2_0_vulns/LLM01_PromptInjection.md) | `corpus/sources/owasp-llm01-prompt-injection.md` | Canonical prompt injection risk and mitigations. |
| 18 | `owasp-llm02-sensitive-information-disclosure` | LLM security and risks | OWASP | [`2_0_vulns/LLM02_SensitiveInformationDisclosure.md`](https://github.com/OWASP/www-project-top-10-for-large-language-model-applications/blob/0205957/2_0_vulns/LLM02_SensitiveInformationDisclosure.md) | `corpus/sources/owasp-llm02-sensitive-information-disclosure.md` | Data leakage and sensitive information disclosure risks. |
| 18a | `owasp-llm04-data-model-poisoning` | LLM security and risks | OWASP | [`2_0_vulns/LLM04_DataModelPoisoning.md`](https://github.com/OWASP/www-project-top-10-for-large-language-model-applications/blob/0205957/2_0_vulns/LLM04_DataModelPoisoning.md) | `corpus/sources/owasp-llm04-data-model-poisoning.md` | Data, model artifact, and ingestion poisoning risks relevant to RAG corpus integrity and lifecycle controls. |
| 19 | `owasp-llm06-excessive-agency` | LLM security and risks | OWASP | [`2_0_vulns/LLM06_ExcessiveAgency.md`](https://github.com/OWASP/www-project-top-10-for-large-language-model-applications/blob/0205957/2_0_vulns/LLM06_ExcessiveAgency.md) | `corpus/sources/owasp-llm06-excessive-agency.md` | Tool-use and excessive permission risks relevant to agentic boundaries. |
| 20 | `owasp-llm08-vector-embedding-weaknesses` | LLM security and risks | OWASP | [`2_0_vulns/LLM08_VectorAndEmbeddingWeaknesses.md`](https://github.com/OWASP/www-project-top-10-for-large-language-model-applications/blob/0205957/2_0_vulns/LLM08_VectorAndEmbeddingWeaknesses.md) | `corpus/sources/owasp-llm08-vector-embedding-weaknesses.md` | Retrieval/vector-specific weaknesses that connect security to RAG architecture. |
| 21 | `nist-generative-ai-risk-profile` | LLM security and risks | NIST | [`Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile`](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf) | `corpus/sources/nist-generative-ai-risk-profile.md` | Authoritative cross-sector generative AI risk profile covering information security, data privacy, value-chain risks, confabulation, misuse, governance, measurement, and risk-management actions. Snapshot should keep the overview of risks, mappings, and suggested actions relevant to LLM/RAG systems, excluding federal front matter and long reference lists. |
| 22 | `openai-cost-optimization` | LLM settings, cost, and tokens | OpenAI API docs | [`Cost optimization`](https://developers.openai.com/api/docs/guides/cost-optimization) | `corpus/sources/openai-cost-optimization.md` | Current cost guidance covering request reduction, token minimization, smaller-model selection, Batch API, flex processing, and offline evaluation workload tradeoffs. Snapshot should keep cost/latency levers and asynchronous-processing guidance, excluding page chrome. |
| 24 | `openai-latency-optimization` | LLM settings, cost, and tokens | OpenAI Cookbook | [`examples/data/oai_docs/latency-optimization.txt`](https://github.com/openai/openai-cookbook/blob/8730772/examples/data/oai_docs/latency-optimization.txt) | `corpus/sources/openai-latency-optimization.md` | Source-backed latency and efficiency guide covering token generation cost, reducing input tokens, reducing output tokens, making fewer requests, parallelization, streaming, model-size tradeoffs, and RAG prompt/context trimming. Snapshot should keep the seven-principle taxonomy and RAG-relevant examples, excluding duplicated navigation fragments. |
| 25 | `openai-rate-limits` | LLM settings, cost, and tokens | OpenAI API docs | [`Rate limits`](https://developers.openai.com/api/docs/guides/rate-limits) | `corpus/sources/openai-rate-limits.md` | Current rate-limit guidance covering RPM/RPD/TPM/TPD dimensions, usage tiers, shared model limits, response headers, retries, batching, Batch API, and ingestion/vector-store limits. Snapshot should keep operational guidance and RAG/evaluation implications, excluding page chrome and long code blocks. |
| 26 | `openai-prompt-caching` | LLM settings, cost, and tokens | OpenAI API docs | [`Prompt caching`](https://developers.openai.com/api/docs/guides/prompt-caching) | `corpus/sources/openai-prompt-caching.md` | Current prompt-caching guide covering repeated prompt prefixes, cache-write accounting, `cached_tokens`, `cache_write_tokens`, `prompt_cache_key`, explicit breakpoints, cacheable-prefix design, and observability through usage metadata. Snapshot should keep caching mechanics and RAG prompt-structure implications, excluding page chrome and repetitive API examples. |

## Excluded Candidate

The original DAIR.AI prompting candidates are intentionally excluded from the prompting category after review because they are broad, introductory, and thin compared with the Microsoft and OpenAI Cookbook materials now selected. Microsoft `04-prompt-engineering-fundamentals` is also excluded because it overlaps heavily with the selected OpenAI prompting guides while adding less practical depth. `dair-chain-of-thought` ([`pages/techniques/cot.en.mdx`](https://github.com/dair-ai/Prompt-Engineering-Guide/blob/5767372/pages/techniques/cot.en.mdx)) remains excluded because the prompting category already has stronger OpenAI/Microsoft coverage.

DAIR.AI `pages/techniques/rag.en.mdx` is excluded from RAG/context handling because it is a short overview and citation list rather than a useful source for chunking, retrieval, or context-budget questions. OpenAI Cookbook `examples/vector_databases/README.md` is also excluded because it is mostly a navigation page, not substantive corpus material. Microsoft `15-rag-and-vector-databases` is excluded from the selected RAG rows because it is lesson-style and partially code-driven; the Azure AI Search documentation is more curated and remains useful after code removal.

## Rows 1-10 External Search Review

After a broader internet review, rows 1-10 remain the recommended selection with the Anthropic lesson-style materials removed.

Post-refinement prompting materials stay focused on OpenAI API docs, OpenAI Cookbook, and Microsoft Learn because they are aligned with the Azure/OpenAI runtime constraint and cover complementary patterns: current prompt-engineering guidance, GPT-5 prompt behavior, GPT-4.1 instruction following and long context, reasoning-model prompting, and schema-constrained outputs.

Rejected prompting alternatives:

- Anthropic Prompt Engineering Interactive Tutorial: excluded after review. The `AmazonBedrock/` edition has a folder-scoped MIT No Attribution license, but the materials read as lessons/exercises rather than curated documentation, and the Claude/Bedrock-specific framing is less aligned with the Azure/OpenAI corpus target.
- DAIR.AI prompting pages: license-compatible but too introductory or thin compared with the selected rows.
- Prompt-engineering survey/pattern papers from arXiv: useful background, but not selected for the corpus because licensing and snapshot reuse are less straightforward than the current MIT-licensed repository materials.

Post-refinement RAG/context materials remain balanced across curated RAG architecture, focused chunking guidance, Search-Ask context assembly, vector relevance/ranking, and Qdrant hybrid or multistage retrieval patterns.

Rejected RAG/context alternatives:

- LlamaIndex RAG documentation: useful and MIT-licensed through the repository, but more framework-specific than the current project-owned plain-Python/Qdrant design.
- Haystack documentation: useful and Apache-2.0 licensed, but also framework-specific and less aligned with the MVP's plain-Python orchestration constraint.
- OpenAI Cookbook Qdrant notebook: license-compatible, but excluded after markdown-only review because it becomes too thin once setup and Python code are stripped. The surviving prose mainly introduces Qdrant collections, payloads, and local search flow.
- Qdrant filtering/search pages beyond hybrid queries: still useful operationally, but not selected for this pass because the approved Qdrant hybrid and multistage query page gives the strongest match to this project's retrieval roadmap.

## Rows 11-16 External Search Review

After refinement, rows 11-15 give the evaluation category five stronger materials. The generic Wikipedia and Hugging Face evaluation rows are superseded by RAG-specific Ragas and DeepEval materials.

Accepted evaluation materials cover complementary quality concerns:

- Microsoft Foundry RAG evaluators: selected despite Azure specificity because it is the most direct RAG evaluator taxonomy in the set, separating process evaluation from system evaluation and mapping retrieval, groundedness, relevance, response completeness, thresholds, and required inputs.
- OpenAI evaluation flywheel: selected because it covers the operational loop missing from metric glossaries: failure analysis, annotation, graders, prompt/system iteration, model comparison, and synthetic test expansion.
- TREC common evaluation measures: selected as a durable retrieval-evaluation reference for precision, recall, average precision, R-precision, bpref, and report interpretation.
- Ragas RAG metrics: selected as RAG-specific metric material for faithfulness, context quality, response relevancy, required inputs, and noise sensitivity.
- DeepEval RAG metrics: selected for retriever versus generator metric framing, contextual precision/recall/relevancy, answer relevancy, faithfulness, thresholds, and test-case requirements.

Rejected evaluation alternatives:

- OpenAI Cookbook `Evaluate_RAG_with_LlamaIndex.ipynb`: useful, but excluded after review because it is framework-specific and largely a LlamaIndex walkthrough.
- OpenAI Cookbook `Getting_Started_with_OpenAI_Evals.ipynb`: license-compatible and prose-rich, but excluded because it targets the older OpenAI Evals framework and explicitly points readers toward the newer hosted evals product.
- Wikipedia information-retrieval metrics: removed during refinement because it duplicates TREC and is less RAG-specific.
- Hugging Face `Choosing a metric` and `Considerations for model evaluation`: removed during refinement because they are generic ML evaluation guidance and weaker than RAG-specific metric material.
- TruLens RAG Triad: conceptually useful, but excluded from the selected evaluation rows because the selected page is short and tool-specific.
- OpenAI Cookbook `Custom-LLM-as-a-Judge.ipynb`: useful for judge-design failure modes, but excluded from the selected evaluation rows because the OpenAI evaluation flywheel and Microsoft RAG evaluator page provide stronger coverage for this lab's immediate evaluation workflow.
- DAIR.AI `pages/prompts/evaluation.en.mdx`: excluded because the pinned page is only a very short evaluation stub and does not provide enough useful corpus text after normalization.

## Rows 17-21 External Search Review

Rows 17-20 remain selected from OWASP because they are substantive, authoritative, and directly relevant to a RAG lab: prompt injection, sensitive information disclosure, excessive agency, and vector/embedding weaknesses. The pages include risk descriptions, examples, scenarios, and mitigation guidance that should survive snapshot normalization well.

Row 21 is replaced with NIST AI 600-1. DAIR.AI `pages/risks/adversarial.en.mdx` is long enough to ingest, but it mixes dated jailbreak examples, prompt snippets, and uneven attack descriptions. NIST AI 600-1 is a stronger fifth security/risk source because it gives a cross-sector generative AI risk taxonomy and risk-management actions covering information security, data privacy, value-chain risk, confabulation, misuse, governance, measurement, and lifecycle controls. It complements OWASP instead of duplicating another prompt-injection example set.

Post-review addendum: OWASP `LLM04_DataModelPoisoning.md` is added as a sixth security/risk source because it covers poisoned data, model artifacts, backdoors, and lifecycle integrity controls directly relevant to RAG ingestion and corpus governance. It complements LLM08 by focusing on how unsafe data enters the system before retrieval, while LLM08 focuses on vector-store and embedding retrieval weaknesses.

## Rows 22-26 External Search Review

Rows 23, 24, and 26 remain selected. OpenAI Cookbook token counting has enough explanatory markdown to support context budgeting and cost diagnostics. OpenAI Cookbook latency optimization remains useful because it covers reducing generated tokens, reducing input tokens, making fewer requests, parallelizing work, streaming, model-size tradeoffs, and RAG prompt/context trimming. OpenAI prompt caching is refreshed from current docs because it adds practical cost/latency guidance for repeated RAG prefixes, cache-write accounting, explicit breakpoints, cache-key routing, and usage observability.

Rows 22 and 25 are replaced after settings review. DAIR.AI `settings.en.mdx` is excluded because it is basic and overlaps with stronger OpenAI/Microsoft prompt and generation material. OpenAI Cookbook `Embedding_long_inputs.ipynb` remains excluded because it is a narrow embedding notebook and overlaps with the selected RAG chunking/context materials. OpenAI text generation is superseded by OpenAI cost optimization because direct cost levers are a better fit for this category than request-shape coverage. OpenAI Cookbook rate-limit handling is superseded by current OpenAI rate-limit documentation because the live guide covers current limit dimensions, headers, shared limits, batching, and ingestion-related constraints. Because OpenAI API docs are not pinned like GitHub sources, snapshot creation should verify documentation reuse terms and capture the retrieval date/version metadata before ingest.

## Post-Approval Work

After approval, create `corpus/manifest.json` and local snapshots only for the approved rows. Do not crawl the live websites at ingest time. The local snapshots should include source title, upstream URL, license/reuse metadata, and either a pinned repository reference or captured documentation snapshot metadata. For repository-backed materials, normalize content from the pinned files.
