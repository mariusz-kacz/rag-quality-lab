# T019 Corpus Materials Proposal

Status: pending approval
Created: 2026-07-03
Purpose: approval gate before creating `corpus/manifest.json` and local snapshots under `corpus/sources/`.

## Selection Rationale

`T019` still names a DAIR.AI-only manifest, but `specs/001-rag-quality-lab/research.md` updates the corpus strategy: DAIR.AI is useful but not sufficient for balanced coverage of the five required categories. This proposal selects a 27-document curated corpus from multiple openly licensed, pinnable or source-backed documentation sets.

The proposed corpus keeps the 15-30 source-page requirement and balances the five required categories with five materials each, plus one additional RAG evaluation material because evaluation is a core lab concern. Each selected material should become one `SourcePage` record after approval.

## Pin Candidates

Use these repository versions as the initial pin targets. Resolve the full commit SHA during snapshot creation if the manifest should store more than the short SHA shown by GitHub.

| Source | Proposed pinned_version | License | Role |
| --- | --- | --- | --- |
| Microsoft Learn Foundry/Azure OpenAI docs | `microsoft-azure-ai-docs@main` (resolve source commit before snapshot) | CC BY 4.0 content / MIT code examples | Curated Azure/OpenAI prompt engineering, structured-output, and RAG evaluator documentation |
| Microsoft Learn Azure Search docs | `microsoft-azure-docs@main` (resolve source commit before snapshot) | CC BY 4.0 content / MIT code examples | Curated RAG architecture, vector search, and relevance/ranking documentation |
| OpenAI Cookbook / Developers Cookbook | `openai-cookbook@8730772` | MIT | Prompting guides, embeddings, vector search, RAG/evaluation workflow, token counting, rate limits |
| OpenAI API docs | `openai-api-docs@current-snapshot` (verify reuse terms before snapshot) | Verify documentation reuse terms before snapshot | Current text generation, prompt caching, and cost/context-management guidance |
| OWASP Top 10 for LLM Applications | `owasp-llm-top-10@0205957` | CC BY-SA 4.0 | LLM security and risk taxonomy |
| NIST AI Risk Management Framework: Generative AI Profile | `nist-ai-600-1@2024-07` | Public NIST publication, verify reuse metadata before snapshot | Cross-sector generative AI risk taxonomy and risk-management actions |
| Microsoft Generative AI for Beginners | `microsoft-generative-ai-for-beginners@61a1240` | MIT | Advanced prompting and lifecycle-oriented explanatory lessons |
| NIST TREC evaluation material | `trec-common-evaluation-measures-2006` | Public/government documentation, verify reuse metadata before snapshot | General retrieval evaluation measures and reporting conventions |
| Wikipedia | `wikipedia@current-snapshot` (capture revision during snapshot) | CC BY-SA 4.0 | General information-retrieval metric definitions |
| Hugging Face Evaluate docs | `huggingface-evaluate@main` (resolve source commit before snapshot) | Apache-2.0 | General metric selection and evaluation-design guidance |

## Category Coverage

| Category | Count | Main sources |
| --- | ---: | --- |
| prompting techniques | 5 | Microsoft Learn, OpenAI Cookbook, Microsoft |
| RAG and context handling | 5 | Microsoft Learn, OpenAI Cookbook |
| RAG evaluation and quality | 6 | Microsoft Learn, OpenAI Cookbook, TREC, Wikipedia, Hugging Face Evaluate |
| LLM security and risks | 6 | OWASP, NIST |
| LLM settings, cost, and tokens | 5 | OpenAI API docs, OpenAI Cookbook |

## Selected Materials

| # | Proposed slug | Category | Source | Upstream reference | Local snapshot target | Short description |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | `azure-openai-prompt-engineering-techniques` | prompting techniques | Microsoft Learn Azure OpenAI docs | [`Prompt engineering techniques`](https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/prompt-engineering) | `corpus/sources/azure-openai-prompt-engineering-techniques.md` | Curated Azure/OpenAI prompt-engineering guidance covering prompt components, instructions, primary/supporting content, few-shot examples, cues, syntax separators, task decomposition, recency effects, and grounding/validation cautions. Snapshot should keep documentation text and compact examples, excluding page chrome. |
| 2 | `microsoft-advanced-prompts` | prompting techniques | Microsoft Generative AI for Beginners | [`05-advanced-prompts/`](https://github.com/microsoft/generative-ai-for-beginners/tree/main/05-advanced-prompts) | `corpus/sources/microsoft-advanced-prompts.md` | Advanced prompt patterns and iterative methods that provide stronger material for technique and tradeoff questions. |
| 3 | `openai-gpt41-prompting-guide` | prompting techniques | OpenAI Cookbook | [`examples/gpt4-1_prompting_guide.ipynb`](https://github.com/openai/openai-cookbook/blob/8730772/examples/gpt4-1_prompting_guide.ipynb) | `corpus/sources/openai-gpt41-prompting-guide.md` | Practical model-specific prompting guidance for instruction following, agentic workflows, long context, and prompt migration. Snapshot should extract narrative guidance and compact prompt examples, excluding raw notebook JSON, execution outputs, and long code cells. |
| 4 | `openai-o-series-prompting-guide` | prompting techniques | OpenAI Cookbook | [`examples/o-series/o3o4-mini_prompting_guide.ipynb`](https://github.com/openai/openai-cookbook/blob/8730772/examples/o-series/o3o4-mini_prompting_guide.ipynb) | `corpus/sources/openai-o-series-prompting-guide.md` | Reasoning-model prompting guidance, including when to give concise instructions versus detailed constraints. Snapshot should keep the guidance and illustrative prompt snippets, not raw notebook structure or generated outputs. |
| 5 | `azure-openai-structured-outputs` | prompting techniques | Microsoft Learn Azure OpenAI docs | [`Structured outputs`](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/structured-outputs) | `corpus/sources/azure-openai-structured-outputs.md` | Curated documentation for schema-constrained model outputs, useful for reliable formatting and machine-readable answer, trace, and evaluation shapes. Snapshot should keep concepts, constraints, supported-model notes, and compact schema examples, excluding repeated SDK boilerplate. |
| 6 | `azure-ai-search-rag-overview` | RAG and context handling | Microsoft Learn Azure Search docs | [`Retrieval-augmented generation in Azure AI Search`](https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview) | `corpus/sources/azure-ai-search-rag-overview.md` | Curated RAG architecture documentation covering query understanding, multi-source data access, token constraints, latency, security trimming, agentic retrieval, and classic RAG retrieval patterns. Snapshot should keep documentation text and decision framing, excluding page chrome. |
| 7 | `openai-embedding-wikipedia-search` | RAG and context handling | OpenAI Cookbook | [`examples/Embedding_Wikipedia_articles_for_search.ipynb`](https://github.com/openai/openai-cookbook/blob/8730772/examples/Embedding_Wikipedia_articles_for_search.ipynb) | `corpus/sources/openai-embedding-wikipedia-search.md` | Concrete ingestion-side workflow for collecting documents, cleaning sections, chunking by token budget, embedding, and storing retrievable text. Snapshot should keep explanatory markdown and only minimal illustrative code, not raw notebook outputs or full setup code. |
| 8 | `openai-question-answering-embeddings` | RAG and context handling | OpenAI Cookbook | [`examples/Question_answering_using_embeddings.ipynb`](https://github.com/openai/openai-cookbook/blob/8730772/examples/Question_answering_using_embeddings.ipynb) | `corpus/sources/openai-question-answering-embeddings.md` | Search-Ask pattern covering retrieval over reference text, prompt context assembly, answer grounding, no-answer behavior, and cost tradeoffs. |
| 9 | `azure-ai-search-vector-relevance-ranking` | RAG and context handling | Microsoft Learn Azure Search docs | [`Relevance in vector search`](https://learn.microsoft.com/en-us/azure/search/vector-search-ranking) | `corpus/sources/azure-ai-search-vector-relevance-ranking.md` | Curated documentation on exhaustive KNN, HNSW/ANN tradeoffs, similarity metrics, score interpretation, `k` selection, chunk-size relevance tuning, and hybrid semantic ranking. Snapshot should keep conceptual guidance and compact tables, excluding code snippets and page chrome. |
| 10 | `openai-file-search-responses` | RAG and context handling | OpenAI Cookbook | [`examples/File_Search_Responses.ipynb`](https://github.com/openai/openai-cookbook/blob/8730772/examples/File_Search_Responses.ipynb) | `corpus/sources/openai-file-search-responses.md` | Managed file-search workflow that provides a useful contrast to the project-owned Qdrant pipeline and covers vector-store retrieval plus context delivery to responses. |
| 11 | `microsoft-foundry-rag-evaluators` | RAG evaluation and quality | Microsoft Learn Foundry docs | [`Retrieval-Augmented Generation (RAG) evaluators`](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rag-evaluators) | `corpus/sources/microsoft-foundry-rag-evaluators.md` | High-signal RAG evaluator taxonomy covering process versus system evaluation, retrieval quality, groundedness, relevance, response completeness, data mappings, thresholds, and search metrics such as NDCG, XDCG, max relevance, and holes. Snapshot should preserve evaluator definitions and metric framing while excluding SDK boilerplate and Azure-only execution steps. |
| 12 | `openai-evaluation-flywheel` | RAG evaluation and quality | OpenAI Developers Cookbook | [`Building resilient prompts using an evaluation flywheel`](https://developers.openai.com/cookbook/examples/evaluation/building_resilient_prompts_using_an_evaluation_flywheel) | `corpus/sources/openai-evaluation-flywheel.md` | Practical evaluation-process guide covering failure-mode discovery, annotation, automatic graders, prompt improvement, model comparison, and synthetic test-data expansion. Useful for turning RAG failures into repeatable regression tests. Snapshot should keep process guidance and compact examples, excluding UI chrome and product-specific workflow details. |
| 13 | `trec-common-evaluation-measures` | RAG evaluation and quality | NIST TREC | [`Common Evaluation Measures`](https://trec.nist.gov/pubs/trec15/appendices/CE.MEASURES06.pdf) | `corpus/sources/trec-common-evaluation-measures.md` | Durable retrieval-evaluation reference covering recall, precision, ranked-list evaluation, average precision, R-precision, recall-precision curves, bpref, and GMAP. Useful for judging retriever quality independently from generation. Snapshot should keep formulas, metric explanations, and compact examples, excluding report boilerplate and graph rendering artifacts. |
| 14 | `wikipedia-ir-evaluation-measures` | RAG evaluation and quality | Wikipedia | [`Evaluation measures (information retrieval)`](https://en.wikipedia.org/wiki/Evaluation_measures_(information_retrieval)) | `corpus/sources/wikipedia-ir-evaluation-measures.md` | Broad information-retrieval metric reference covering precision, recall, F-score, precision@k, R-precision, MAP, DCG/nDCG, MRR, hit rate, and metric caveats. Useful as a general retrieval metric glossary for RAG quality questions. Snapshot should capture the current revision and preserve attribution/license metadata. |
| 15 | `huggingface-evaluate-choosing-metric` | RAG evaluation and quality | Hugging Face Evaluate docs | [`Choosing a metric for your task`](https://huggingface.co/docs/evaluate/main/en/choosing_a_metric) | `corpus/sources/huggingface-evaluate-choosing-metric.md` | General evaluator-design guidance explaining generic, task-specific, and dataset-specific metric choice. Useful for deciding whether a RAG lab question needs retrieval metrics, answer metrics, benchmark metrics, or custom checks. Snapshot should keep conceptual guidance, excluding installation and code snippets. |
| 16 | `huggingface-evaluate-considerations` | RAG evaluation and quality | Hugging Face Evaluate docs | [`Considerations for model evaluation`](https://huggingface.co/docs/evaluate/main/en/considerations) | `corpus/sources/huggingface-evaluate-considerations.md` | General evaluation-quality guidance covering train/validation/test splits, class imbalance, combining metrics, offline versus online evaluation, interpretability, latency/resource tradeoffs, and metric limitations. Useful for lab methodology and interpreting RAG quality results. Snapshot should keep conceptual guidance, excluding navigation and page chrome. |
| 17 | `owasp-llm01-prompt-injection` | LLM security and risks | OWASP | [`2_0_vulns/LLM01_PromptInjection.md`](https://github.com/OWASP/www-project-top-10-for-large-language-model-applications/blob/0205957/2_0_vulns/LLM01_PromptInjection.md) | `corpus/sources/owasp-llm01-prompt-injection.md` | Canonical prompt injection risk and mitigations. |
| 18 | `owasp-llm02-sensitive-information-disclosure` | LLM security and risks | OWASP | [`2_0_vulns/LLM02_SensitiveInformationDisclosure.md`](https://github.com/OWASP/www-project-top-10-for-large-language-model-applications/blob/0205957/2_0_vulns/LLM02_SensitiveInformationDisclosure.md) | `corpus/sources/owasp-llm02-sensitive-information-disclosure.md` | Data leakage and sensitive information disclosure risks. |
| 18a | `owasp-llm04-data-model-poisoning` | LLM security and risks | OWASP | [`2_0_vulns/LLM04_DataModelPoisoning.md`](https://github.com/OWASP/www-project-top-10-for-large-language-model-applications/blob/0205957/2_0_vulns/LLM04_DataModelPoisoning.md) | `corpus/sources/owasp-llm04-data-model-poisoning.md` | Data, model artifact, and ingestion poisoning risks relevant to RAG corpus integrity and lifecycle controls. |
| 19 | `owasp-llm06-excessive-agency` | LLM security and risks | OWASP | [`2_0_vulns/LLM06_ExcessiveAgency.md`](https://github.com/OWASP/www-project-top-10-for-large-language-model-applications/blob/0205957/2_0_vulns/LLM06_ExcessiveAgency.md) | `corpus/sources/owasp-llm06-excessive-agency.md` | Tool-use and excessive permission risks relevant to agentic boundaries. |
| 20 | `owasp-llm08-vector-embedding-weaknesses` | LLM security and risks | OWASP | [`2_0_vulns/LLM08_VectorAndEmbeddingWeaknesses.md`](https://github.com/OWASP/www-project-top-10-for-large-language-model-applications/blob/0205957/2_0_vulns/LLM08_VectorAndEmbeddingWeaknesses.md) | `corpus/sources/owasp-llm08-vector-embedding-weaknesses.md` | Retrieval/vector-specific weaknesses that connect security to RAG architecture. |
| 21 | `nist-generative-ai-risk-profile` | LLM security and risks | NIST | [`Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile`](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf) | `corpus/sources/nist-generative-ai-risk-profile.md` | Authoritative cross-sector generative AI risk profile covering information security, data privacy, value-chain risks, confabulation, misuse, governance, measurement, and risk-management actions. Snapshot should keep the overview of risks, mappings, and suggested actions relevant to LLM/RAG systems, excluding federal front matter and long reference lists. |
| 22 | `dair-llm-settings` | LLM settings, cost, and tokens | DAIR.AI | [`pages/introduction/settings.en.mdx`](https://github.com/dair-ai/Prompt-Engineering-Guide/blob/5767372/pages/introduction/settings.en.mdx) | `corpus/sources/dair-llm-settings.md` | Temperature, sampling, and generation settings in prompt-engineering terms. |
| 24 | `openai-latency-optimization` | LLM settings, cost, and tokens | OpenAI Cookbook | [`examples/data/oai_docs/latency-optimization.txt`](https://github.com/openai/openai-cookbook/blob/8730772/examples/data/oai_docs/latency-optimization.txt) | `corpus/sources/openai-latency-optimization.md` | Source-backed latency and efficiency guide covering token generation cost, reducing input tokens, reducing output tokens, making fewer requests, parallelization, streaming, model-size tradeoffs, and RAG prompt/context trimming. Snapshot should keep the seven-principle taxonomy and RAG-relevant examples, excluding duplicated navigation fragments. |
| 25 | `openai-handle-rate-limits` | LLM settings, cost, and tokens | OpenAI Cookbook | [`examples/How_to_handle_rate_limits.ipynb`](https://github.com/openai/openai-cookbook/blob/8730772/examples/How_to_handle_rate_limits.ipynb) | `corpus/sources/openai-handle-rate-limits.md` | Operational rate-limit handling that supports latency/cost/budget discussion. |
| 26 | `openai-prompt-caching` | LLM settings, cost, and tokens | OpenAI API docs | [`Prompt caching`](https://developers.openai.com/api/docs/guides/prompt-caching) | `corpus/sources/openai-prompt-caching.md` | Current prompt-caching guide covering how repeated prompt prefixes reduce latency and input-token cost, cache-eligible prompt structure, static-versus-dynamic prompt layout, cache routing, cache-key use, and observability through usage metadata. Snapshot should keep caching mechanics and RAG prompt-structure implications, excluding page chrome and repetitive API examples. |

## Excluded Candidate

The original DAIR.AI prompting candidates are intentionally excluded from the prompting category after review because they are broad, introductory, and thin compared with the Microsoft and OpenAI Cookbook materials now selected. Microsoft `04-prompt-engineering-fundamentals` is also excluded because it overlaps heavily with the selected OpenAI prompting guides while adding less practical depth. `dair-chain-of-thought` ([`pages/techniques/cot.en.mdx`](https://github.com/dair-ai/Prompt-Engineering-Guide/blob/5767372/pages/techniques/cot.en.mdx)) remains excluded because the prompting category already has stronger OpenAI/Microsoft coverage.

DAIR.AI `pages/techniques/rag.en.mdx` is excluded from RAG/context handling because it is a short overview and citation list rather than a useful source for chunking, retrieval, or context-budget questions. OpenAI Cookbook `examples/vector_databases/README.md` is also excluded because it is mostly a navigation page, not substantive corpus material. Microsoft `15-rag-and-vector-databases` is excluded from the selected RAG rows because it is lesson-style and partially code-driven; the Azure AI Search documentation is more curated and remains useful after code removal.

## Rows 1-10 External Search Review

After a broader internet review, rows 1-10 remain the recommended selection with the Anthropic lesson-style materials removed.

Accepted prompting materials stay focused on Microsoft Learn, OpenAI Cookbook, and Microsoft Generative AI content because they are license-compatible or source-backed, aligned with the Azure/OpenAI runtime constraint, and cover complementary patterns: curated prompt-construction guidance, advanced prompting, model-specific instruction following, reasoning-model prompting, and schema-constrained outputs.

Rejected prompting alternatives:

- Anthropic Prompt Engineering Interactive Tutorial: excluded after review. The `AmazonBedrock/` edition has a folder-scoped MIT No Attribution license, but the materials read as lessons/exercises rather than curated documentation, and the Claude/Bedrock-specific framing is less aligned with the Azure/OpenAI corpus target.
- DAIR.AI prompting pages: license-compatible but too introductory or thin compared with the selected rows.
- Prompt-engineering survey/pattern papers from arXiv: useful background, but not selected for the corpus because licensing and snapshot reuse are less straightforward than the current MIT-licensed repository materials.

Accepted RAG/context materials remain balanced across curated RAG architecture, ingestion/chunking, Search-Ask context assembly, vector relevance/ranking, and managed file-search contrast.

Rejected RAG/context alternatives:

- LlamaIndex RAG documentation: useful and MIT-licensed through the repository, but more framework-specific than the current project-owned plain-Python/Qdrant design.
- Haystack documentation: useful and Apache-2.0 licensed, but also framework-specific and less aligned with the MVP's plain-Python orchestration constraint.
- OpenAI Cookbook Qdrant notebook: license-compatible, but excluded after markdown-only review because it becomes too thin once setup and Python code are stripped. The surviving prose mainly introduces Qdrant collections, payloads, and local search flow.
- Qdrant documentation pages for filtering/search: highly relevant operationally, but not selected for corpus snapshots until reusable content licensing and source pinning are clearer. Qdrant docs remain good implementation references for later `qdrant_store.py` work.

## Rows 11-16 External Search Review

After review, rows 11-16 intentionally give the evaluation category six materials. All six are valuable and complementary enough to keep because RAG evaluation is one of the lab's highest-value topics.

Accepted evaluation materials cover complementary quality concerns:

- Microsoft Foundry RAG evaluators: selected despite Azure specificity because it is the most direct RAG evaluator taxonomy in the set, separating process evaluation from system evaluation and mapping retrieval, groundedness, relevance, response completeness, thresholds, and required inputs.
- OpenAI evaluation flywheel: selected because it covers the operational loop missing from metric glossaries: failure analysis, annotation, graders, prompt/system iteration, model comparison, and synthetic test expansion.
- TREC common evaluation measures: selected as a durable retrieval-evaluation reference for precision, recall, average precision, R-precision, bpref, and report interpretation.
- Wikipedia information-retrieval metrics: selected as a broader glossary for precision@k, MAP, DCG/nDCG, MRR, hit rate, and metric caveats; it overlaps with TREC, but is broader and easier for ad hoc metric lookup.
- Hugging Face `Choosing a metric`: selected for general metric-choice framing across generic, task-specific, and dataset-specific metrics.
- Hugging Face `Considerations for model evaluation`: selected for evaluation hygiene: data splits, imbalance, combining metrics, offline versus online evaluation, interpretability, resource tradeoffs, and limitations.

Rejected evaluation alternatives:

- OpenAI Cookbook `Evaluate_RAG_with_LlamaIndex.ipynb`: useful, but excluded after review because it is framework-specific and largely a LlamaIndex walkthrough.
- OpenAI Cookbook `Getting_Started_with_OpenAI_Evals.ipynb`: license-compatible and prose-rich, but excluded because it targets the older OpenAI Evals framework and explicitly points readers toward the newer hosted evals product.
- Ragas metric pages: open-source and useful, but excluded from the selected evaluation rows because the individual selected pages are short and framework-specific.
- TruLens RAG Triad: conceptually useful, but excluded from the selected evaluation rows because the selected page is short and tool-specific.
- DeepEval metrics introduction: useful and broad, but excluded after the latest review because the accepted six already cover evaluator taxonomy, retrieval metrics, metric choice, and evaluation methodology without adding another framework-specific document.
- OpenAI Cookbook `Custom-LLM-as-a-Judge.ipynb`: useful for judge-design failure modes, but excluded from the selected evaluation rows because the OpenAI evaluation flywheel and Microsoft RAG evaluator page provide stronger coverage for this lab's immediate evaluation workflow.
- DAIR.AI `pages/prompts/evaluation.en.mdx`: excluded because the pinned page is only a very short evaluation stub and does not provide enough useful corpus text after normalization.

## Rows 17-21 External Search Review

Rows 17-20 remain selected from OWASP because they are substantive, authoritative, and directly relevant to a RAG lab: prompt injection, sensitive information disclosure, excessive agency, and vector/embedding weaknesses. The pages include risk descriptions, examples, scenarios, and mitigation guidance that should survive snapshot normalization well.

Row 21 is replaced with NIST AI 600-1. DAIR.AI `pages/risks/adversarial.en.mdx` is long enough to ingest, but it mixes dated jailbreak examples, prompt snippets, and uneven attack descriptions. NIST AI 600-1 is a stronger fifth security/risk source because it gives a cross-sector generative AI risk taxonomy and risk-management actions covering information security, data privacy, value-chain risk, confabulation, misuse, governance, measurement, and lifecycle controls. It complements OWASP instead of duplicating another prompt-injection example set.

Post-review addendum: OWASP `LLM04_DataModelPoisoning.md` is added as a sixth security/risk source because it covers poisoned data, model artifacts, backdoors, and lifecycle integrity controls directly relevant to RAG ingestion and corpus governance. It complements LLM08 by focusing on how unsafe data enters the system before retrieval, while LLM08 focuses on vector-store and embedding retrieval weaknesses.

## Rows 22-26 External Search Review

Rows 23, 24, and 25 remain selected. OpenAI Cookbook token counting has enough explanatory markdown to support context budgeting and cost diagnostics. OpenAI Cookbook latency optimization is a strong source-backed replacement for older API-formatting material because it covers reducing generated tokens, reducing input tokens, making fewer requests, parallelizing work, streaming, model-size tradeoffs, and RAG prompt/context trimming. OpenAI Cookbook rate-limit handling is still useful after code stripping because it explains why rate limits exist, exponential backoff, fallback model tradeoffs, `max_tokens` effects on rate accounting, batching, RPM/TPM distinctions, and throughput strategies.

Rows 22 and 26 are replaced after review. DAIR.AI `settings.en.mdx` is excluded because it is basic and overlaps with stronger OpenAI/Microsoft prompt and generation material. OpenAI Cookbook `Embedding_long_inputs.ipynb` is excluded because it is a narrow embedding notebook and overlaps with the already selected RAG chunking/context materials. The replacements are OpenAI text generation and prompt caching docs: text generation gives current request-shape and instruction/message-role guidance, while prompt caching adds practical cost/latency guidance for repeated RAG prefixes, static-versus-dynamic prompt layout, cache-key routing, and usage observability. Because OpenAI API docs are not pinned like GitHub sources, snapshot creation should verify documentation reuse terms and capture the retrieval date/version metadata before ingest.

## Post-Approval Work

After approval, create `corpus/manifest.json` and local snapshots only for the approved rows. Do not crawl the live websites at ingest time. The local snapshots should include source title, upstream URL, license/reuse metadata, and either a pinned repository reference or captured documentation snapshot metadata. For repository-backed materials, normalize content from the pinned files.
