# Corpus Refinement Plan

## Purpose

This plan covers a second-pass corpus quality refinement after review of `artifacts/t019-corpus-materials-proposal.md` and `artifacts/t019-corpus-quality-review.md`.

The goal is to improve source quality without changing the project's architecture or ingestion behavior. The refinement should replace weak or generic corpus entries with stronger, reviewable, source-backed materials while preserving:

- the five required knowledge categories;
- the 15-30 source-page corpus size requirement;
- manifest provenance fields;
- local, pinned or snapshot-backed Markdown source files;
- deterministic chunking and evaluation workflows.

## Scope

For each approved replacement:

1. Update `corpus/manifest.json` with the approved source slug, title, category, upstream URL, license/reuse metadata, pinned version or snapshot metadata, local reference, and section headings.
2. Create or update the local Markdown file under `corpus/sources/`.
3. Keep the source snapshot close to the upstream material and avoid synthetic filler.
4. Remove replaced local source files only after the manifest no longer references them.
5. Update documentation references in `README.md` and proposal artifacts if source counts or source names change.
6. Update `specs/001-rag-quality-lab/corpus-generation-plan.md` or cross-reference this plan so the corpus history is understandable.
7. Re-run corpus inspection, ingestion tests, and golden evaluation after manifest/content changes.

## Refinement Rules

Refinement changes should follow these rules:

- Do not keep weak documents only to preserve category symmetry.
- Prefer fewer high-signal documents over broad but low-value pages.
- A selected source must be directly useful for expected lab questions.
- A selected source must remain useful after code, page chrome, notebook output, classroom scaffolding, and setup details are removed.
- A selected source must have direct review links in the plan before implementation.
- OpenAI API documentation and other live documentation pages require captured snapshot metadata and reuse-term review before ingest.
- Repository-backed sources should use a pinned commit when practical.
- Replaced files should not be deleted until the replacement source is generated, manifest validation passes, and golden question impact is understood.

## Source File Template

Each new or regenerated source should use this shape unless the source requires a stronger local convention:

```markdown
# Source snapshot

Source metadata:
- source_slug: <manifest source_slug>
- category: <manifest category>
- upstream_url: <manifest url>
- source_markdown/source_notebook/source_page: <specific source reference when available>
- license: <manifest license>
- pinned_version: <manifest pinned_version>
- observed_source_commit: <commit when available>
- snapshot_captured: <YYYY-MM-DD when source is not pinned by commit>
- snapshot_type: normalized documentation digest from <source type>
- normalization: <short description of what was removed and retained>

---
# <manifest section 1 heading>

...

# <manifest section 2 heading>

...
```

The top-level content headings after the metadata block must match the corresponding `corpus/manifest.json` section headings exactly.

## Review Checklist

A refined source is complete only when all checks pass:

- Metadata matches the manifest.
- The upstream review link is present in this plan or a linked proposal artifact.
- License/reuse terms are recorded clearly enough for portfolio review.
- Pinned version, source commit, or snapshot capture date is recorded.
- Top-level content headings match the manifest exactly.
- The local text remains close enough to the source to be credible and attributable.
- The local text is useful for the category's expected RAG questions.
- The local text avoids synthetic RAG-oriented filler when the upstream source is generic.
- Notebook/course/page scaffolding is removed unless it is substantive.
- Code and JSON examples are compact, complete, and not misleading.
- No placeholder strings remain, such as `TODO`, `TBD`, or `omitted`, except when discussing those words as source content.
- `uv run pytest tests/unit/test_manifest.py tests/unit/test_chunking.py tests/integration/test_corpus_ingest_workflow.py` passes or any failure is documented.

## Approved Prompting Refinement

Prompting replacements are approved. The refined prompt category should use the proposed five-source set from `artifacts/t019-corpus-quality-review.md`.

### Prompting Source Decisions

| Current source | Decision | Replacement / retained source | Review link | Notes |
| --- | --- | --- | --- | --- |
| `azure-openai-prompt-engineering-techniques` | Replace | `openai-api-prompt-engineering` | [OpenAI API prompt engineering guide](https://developers.openai.com/api/docs/guides/prompt-engineering) | Replaces broad/partly legacy Azure prompt-engineering material with current OpenAI prompt guidance. Requires snapshot metadata and reuse-term review. |
| `microsoft-advanced-prompts` | Replace | `openai-gpt5-prompting-guide` | [OpenAI Cookbook GPT-5 prompting guide](https://developers.openai.com/cookbook/examples/gpt-5/gpt-5_prompting_guide) | Replaces lesson-style content with current model-specific prompt guidance. Requires source pin or snapshot metadata. |
| `openai-gpt41-prompting-guide` | Keep | `openai-gpt41-prompting-guide` | [OpenAI Cookbook GPT-4.1 prompting guide](https://github.com/openai/openai-cookbook/blob/8730772/examples/gpt4-1_prompting_guide.ipynb) | Keep as practical GPT-series instruction-following, agentic workflow, and long-context guidance. |
| `openai-o-series-prompting-guide` | Keep | `openai-o-series-prompting-guide` | [OpenAI Cookbook o-series prompting guide](https://github.com/openai/openai-cookbook/blob/8730772/examples/o-series/o3o4-mini_prompting_guide.ipynb) | Keep as reasoning-model prompt behavior guidance. |
| `azure-openai-structured-outputs` | Keep | `azure-openai-structured-outputs` | [Azure OpenAI structured outputs](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/structured-outputs) | Keep as prompt-adjacent output reliability and schema-control material. |

### Prompting Implementation Tasks

| Task | Status | Source slug | Local file | Manifest sections | Notes |
| --- | --- | --- | --- | --- | --- |
| CRP-P01 | Pending | `openai-api-prompt-engineering` | `corpus/sources/openai-api-prompt-engineering.md` | Message roles and instruction hierarchy; Prompt testing, model snapshots, and output control | Add manifest entry replacing `azure-openai-prompt-engineering-techniques`. Capture current snapshot metadata and reuse terms. |
| CRP-P02 | Pending | `openai-gpt5-prompting-guide` | `corpus/sources/openai-gpt5-prompting-guide.md` | GPT-5 prompt behavior and instruction tuning; Agentic workflows, verbosity, and migration patterns | Add manifest entry replacing `microsoft-advanced-prompts`. Capture source pin or snapshot metadata. |
| CRP-P03 | Pending | `openai-gpt41-prompting-guide` | `corpus/sources/openai-gpt41-prompting-guide.md` | Instruction following and agentic workflows; Long context guidance and prompt migration | Review existing local source against the stricter checklist; update only if needed. |
| CRP-P04 | Pending | `openai-o-series-prompting-guide` | `corpus/sources/openai-o-series-prompting-guide.md` | Reasoning model instruction design; Concise instructions versus detailed constraints | Review existing local source against the stricter checklist; update only if needed. |
| CRP-P05 | Pending | `azure-openai-structured-outputs` | `corpus/sources/azure-openai-structured-outputs.md` | Schema constrained outputs; Constraints, model support, and compact examples | Keep in prompting category unless a later taxonomy change moves schema control elsewhere. |
| CRP-P06 | Pending | Prompting category | `corpus/manifest.json` | n/a | Remove manifest references to `azure-openai-prompt-engineering-techniques` and `microsoft-advanced-prompts` after replacements are generated. |
| CRP-P07 | Pending | Prompting category | `README.md` and proposal artifacts | n/a | Update source list/counts and rationale. |
| CRP-P08 | Pending | Prompting category | `golden/questions.json` | n/a | Review expected sources for prompt-related golden questions after content changes. |

## Approved RAG And Context Handling Refinement

RAG and context handling source decisions are approved. The current category is stronger than the original Prompting and RAG Evaluation sets, but it still has two weak spots:

- `openai-embedding-wikipedia-search` is concrete and useful, but it is tightly coupled to a Wikipedia-specific notebook and overlaps with `openai-question-answering-embeddings`.
- `openai-file-search-responses` is current enough to be useful as a managed retrieval contrast, but it overlaps with evaluation and is less aligned with the project-owned Qdrant retrieval pipeline than a Qdrant retrieval source would be.

The approved direction is to keep the strongest architecture, retrieval, and Search-Ask sources, replace the Wikipedia-ingestion notebook with a focused chunking source, and replace managed file search with a Qdrant retrieval source aligned with the project retrieval stack.

### RAG And Context Source Decisions

| Current source | Decision | Replacement / retained source | Review link | Notes |
| --- | --- | --- | --- | --- |
| `azure-ai-search-rag-overview` | Keep | `azure-ai-search-rag-overview` | [Retrieval-augmented generation in Azure AI Search](https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview) | Strong architecture source covering query understanding, agentic versus classic RAG, multi-source retrieval, concise grounding data, token pressure, security trimming, latency, and retrieval-pattern selection. |
| `openai-embedding-wikipedia-search` | Replace | `azure-ai-search-chunk-documents` | [Chunk documents in Azure AI Search](https://learn.microsoft.com/en-us/azure/search/vector-search-how-to-chunk-documents) | Replaces a dataset-specific Wikipedia ingestion notebook with a focused source on chunking strategy, chunk size, overlap, token/character mismatch, sentence boundaries, and indexing workflow. Microsoft Learn content is CC BY 4.0 / MIT examples; resolve source commit before ingest. |
| `openai-question-answering-embeddings` | Keep | `openai-question-answering-embeddings` | [OpenAI Cookbook Question answering using embeddings](https://github.com/openai/openai-cookbook/blob/8730772/examples/Question_answering_using_embeddings.ipynb) | Keep as the clearest baseline Search-Ask source for semantic retrieval, ranked context assembly, token budgeting, answer grounding, no-answer behavior, and retrieval debugging. |
| `azure-ai-search-vector-relevance-ranking` | Keep | `azure-ai-search-vector-relevance-ranking` | [Relevance in vector search](https://learn.microsoft.com/en-us/azure/search/vector-search-ranking) | Keep as the strongest vector retrieval relevance source: exact versus approximate KNN, HNSW tuning, similarity metrics, score interpretation, `k`, chunk tuning, and hybrid ranking. |
| `openai-file-search-responses` | Replace | `qdrant-hybrid-and-multistage-queries` | [Qdrant hybrid and multi-stage queries](https://qdrant.tech/documentation/search/hybrid-queries/) | Approved replacement because the project uses Qdrant and the source covers dense+sparse retrieval, prefetch, Reciprocal Rank Fusion, score fusion, and multi-stage query patterns. |

### Alternative Candidates

| Candidate | Review link | Recommendation | Reason |
| --- | --- | --- | --- |
| `openai-retrieval-guide` | [OpenAI Retrieval guide](https://developers.openai.com/api/docs/guides/retrieval) | Backup replacement for `openai-file-search-responses` | Strong current OpenAI source for semantic search, vector stores, metadata filtering, ranking options, hybrid search weights, vector store operations, and chunking strategies. Use if Qdrant docs reuse terms are unclear. Requires OpenAI docs reuse-term review and snapshot metadata. |
| `openai-file-search-guide` | [OpenAI File search guide](https://developers.openai.com/api/docs/guides/tools-file-search) | Design reference or backup source | Better than the notebook for current managed file-search behavior, but still less aligned with the project-owned Qdrant pipeline. Requires OpenAI docs reuse-term review and snapshot metadata. |
| `openai-file-search-responses` | [OpenAI Cookbook File Search Responses notebook](https://github.com/openai/openai-cookbook/blob/8730772/examples/File_Search_Responses.ipynb) | Keep only if managed retrieval contrast remains important | The existing source is useful, but it mixes managed retrieval, annotations, and evaluation methodology. It is weaker than a Qdrant-specific source for this project. |
| `openai-embedding-wikipedia-search` | [OpenAI Cookbook Embedding Wikipedia articles for search](https://github.com/openai/openai-cookbook/blob/8730772/examples/Embedding_Wikipedia_articles_for_search.ipynb) | Keep only if we want a concrete ingestion walkthrough | The source is still useful, but the Wikipedia-specific cleaning and recursive splitting are less directly reusable than a focused chunking source. |

### RAG And Context Implementation Tasks

| Task | Status | Source slug | Local file | Manifest sections | Notes |
| --- | --- | --- | --- | --- | --- |
| CRP-RC01 | Pending | `azure-ai-search-rag-overview` | `corpus/sources/azure-ai-search-rag-overview.md` | RAG architecture and query understanding; Token constraints, security trimming, and retrieval patterns | Review existing local source against the stricter checklist; update only if needed. |
| CRP-RC02 | Pending | `azure-ai-search-chunk-documents` | `corpus/sources/azure-ai-search-chunk-documents.md` | Chunking workflow and strategy selection; Chunk size, overlap, token limits, and indexing implications | Add manifest entry replacing `openai-embedding-wikipedia-search`. Resolve Microsoft Learn source commit before ingest. |
| CRP-RC03 | Pending | `openai-question-answering-embeddings` | `corpus/sources/openai-question-answering-embeddings.md` | Search-Ask retrieval workflow; Context assembly, answer grounding, and no-answer behavior | Review existing local source against the stricter checklist; update only if needed. |
| CRP-RC04 | Pending | `azure-ai-search-vector-relevance-ranking` | `corpus/sources/azure-ai-search-vector-relevance-ranking.md` | KNN, ANN, and similarity metrics; Score interpretation, k selection, chunk tuning, and hybrid ranking | Review existing local source against the stricter checklist; update only if needed. |
| CRP-RC05 | Pending | `qdrant-hybrid-and-multistage-queries` | `corpus/sources/qdrant-hybrid-and-multistage-queries.md` | Hybrid retrieval and dense-sparse fusion; Multi-stage retrieval, prefetch, and reranking patterns | Add manifest entry replacing `openai-file-search-responses`. |
| CRP-RC06 | Pending | RAG and context category | `corpus/manifest.json` | n/a | Remove manifest references to replaced sources after replacement snapshots are generated. |
| CRP-RC07 | Pending | RAG and context category | `README.md` and proposal artifacts | n/a | Update source list/counts and rationale. |
| CRP-RC08 | Pending | RAG and context category | `golden/questions.json` | n/a | Review expected relevant sources for RAG/context golden questions after content changes. |

## Approved RAG Evaluation Refinement

RAG evaluation source decisions are approved. The refined evaluation category should keep the strongest current sources and replace generic or duplicative metric pages with RAG-specific metric material.

The approved refined category should use five sources instead of six. This removes weak padding while keeping the overall corpus within the 15-30 source-page requirement.

### Evaluation Source Decisions

| Current source | Decision | Replacement / retained source | Review link | Notes |
| --- | --- | --- | --- | --- |
| `microsoft-foundry-rag-evaluators` | Keep | `microsoft-foundry-rag-evaluators` | [Microsoft Foundry RAG evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rag-evaluators) | Strong direct RAG evaluator taxonomy covering process evaluation, system evaluation, retrieval quality, groundedness, relevance, response completeness, thresholds, and data mappings. |
| `openai-evaluation-flywheel` | Keep | `openai-evaluation-flywheel` | [OpenAI Cookbook evaluation flywheel](https://developers.openai.com/cookbook/examples/evaluation/building_resilient_prompts_using_an_evaluation_flywheel) | Strong evaluation process and regression-loop source: failure discovery, annotation, graders, prompt improvement, model comparison, and test expansion. |
| `trec-common-evaluation-measures` | Keep | `trec-common-evaluation-measures` | [TREC common evaluation measures PDF](https://trec.nist.gov/pubs/trec15/appendices/CE.MEASURES06.pdf) | Keep as the single generic retrieval-metric reference for precision, recall, ranked retrieval, average precision, R-precision, bpref, and GMAP. |
| `wikipedia-ir-evaluation-measures` | Replace | `ragas-rag-metrics` | [Ragas RAG metrics index](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/) | Replaces the duplicative Wikipedia IR glossary with RAG-specific metrics. Review especially [faithfulness](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/), [context precision](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/context_precision/), [context recall](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/context_recall/), [noise sensitivity](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/noise_sensitivity/), and [response relevancy](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/answer_relevance/). Ragas repository license is Apache-2.0; resolve docs source paths and commit before ingest. |
| `huggingface-evaluate-choosing-metric` | Replace | `deepeval-rag-metrics` | [DeepEval metrics introduction](https://deepeval.com/docs/metrics-introduction) | Replaces generic metric-selection guidance with RAG-specific evaluator framing. DeepEval explicitly splits RAG metrics into retriever metrics, such as contextual relevancy, contextual precision, and contextual recall, and generator metrics, such as answer relevancy and faithfulness. Repository license is Apache-2.0; resolve docs source paths and commit before ingest. |
| `huggingface-evaluate-considerations` | Remove | n/a | n/a | Remove rather than replace one-for-one. The refined evaluation category should have five high-signal sources, not six padded sources. |

### Rejected Evaluation Candidates

| Candidate | Review link | Reason |
| --- | --- | --- |
| `langsmith-evaluate-rag-application` | [LangSmith evaluate a RAG application](https://docs.langchain.com/langsmith/evaluate-rag-tutorial) | Useful design reference for correctness, relevance, groundedness, and retrieval relevance, but not selected for corpus snapshot until documentation reuse terms are clearer. |
| `wikipedia-ir-evaluation-measures` | [Wikipedia IR evaluation measures](https://en.wikipedia.org/wiki/Evaluation_measures_(information_retrieval)) | Duplicates TREC coverage and is less RAG-specific. |
| `huggingface-evaluate-choosing-metric` | [Hugging Face choosing a metric](https://huggingface.co/docs/evaluate/main/en/choosing_a_metric) | Generic metric-selection guidance; useful background but weak corpus material for RAG quality. |
| `huggingface-evaluate-considerations` | [Hugging Face evaluation considerations](https://huggingface.co/docs/evaluate/main/en/considerations) | Generic ML evaluation hygiene; useful background but weak corpus material for RAG quality. |

### Evaluation Implementation Tasks

| Task | Status | Source slug | Local file | Manifest sections | Notes |
| --- | --- | --- | --- | --- | --- |
| CRP-E01 | Pending | `microsoft-foundry-rag-evaluators` | `corpus/sources/microsoft-foundry-rag-evaluators.md` | Process and system evaluation taxonomy; Retrieval quality, groundedness, relevance, and thresholds | Review existing local source against the stricter checklist; update only if needed. |
| CRP-E02 | Pending | `openai-evaluation-flywheel` | `corpus/sources/openai-evaluation-flywheel.md` | Failure-mode discovery and annotation; Automatic graders, prompt improvement, and test expansion | Review existing local source against the stricter checklist; update only if needed. |
| CRP-E03 | Pending | `trec-common-evaluation-measures` | `corpus/sources/trec-common-evaluation-measures.md` | Recall, precision, and ranked-list evaluation; Average precision, R-precision, bpref, and GMAP | Keep as the only generic retrieval-metric source; review existing snapshot for source closeness. |
| CRP-E04 | Pending | `ragas-rag-metrics` | `corpus/sources/ragas-rag-metrics.md` | RAG metric surfaces and required inputs; Faithfulness, context quality, response relevancy, and noise sensitivity | Add manifest entry replacing `wikipedia-ir-evaluation-measures`. Build from Ragas docs pages after resolving source paths and commit. |
| CRP-E05 | Pending | `deepeval-rag-metrics` | `corpus/sources/deepeval-rag-metrics.md` | Retriever and generator metric taxonomy; Thresholds, scoring, and test-case requirements | Add manifest entry replacing `huggingface-evaluate-choosing-metric`. Build from DeepEval docs after resolving source paths and commit. |
| CRP-E06 | Pending | Evaluation category | `corpus/manifest.json` | n/a | Remove manifest references to `wikipedia-ir-evaluation-measures`, `huggingface-evaluate-choosing-metric`, and `huggingface-evaluate-considerations` after replacements are generated. |
| CRP-E07 | Pending | Evaluation category | `README.md` and proposal artifacts | n/a | Update source list/counts and rationale from six evaluation sources to five. |
| CRP-E08 | Pending | Evaluation category | `golden/questions.json` | n/a | Review expected relevant sources for evaluation-category golden questions after content changes. |

## Approved LLM Settings, Cost, And Tokens Refinement

LLM settings, cost, and tokens source decisions are approved. The current category is usable and stronger than the original weak proposal rows, but it has two quality issues:

- `openai-text-generation` is a good current API-basics source, but in this category it overlaps heavily with Prompting and request-shape material.
- `openai-handle-rate-limits` is practical and source-backed, but it is a cookbook notebook centered on retry examples; current rate-limit docs are a better fit for RPM, TPM, usage tiers, headers, project limits, long-context limits, and vector-store ingestion limits.

The approved direction is to keep the strong token-counting, latency, and prompt-caching sources, replace generic text-generation coverage with direct cost-optimization guidance, and replace the rate-limit notebook with current rate-limit documentation.

### LLM Settings Source Decisions

| Current source | Decision | Replacement / retained source | Review link | Notes |
| --- | --- | --- | --- | --- |
| `openai-text-generation` | Replace | `openai-cost-optimization` | [OpenAI cost optimization guide](https://developers.openai.com/api/docs/guides/cost-optimization) | Replaces broad request-shape and prompt-overlap material with direct cost guidance: reduce requests, minimize tokens, select smaller models, use Batch API for asynchronous jobs, and use flex processing for lower-priority workloads. Requires OpenAI docs reuse-term review and snapshot metadata. |
| `openai-token-counting` | Keep | `openai-token-counting` | [OpenAI Cookbook token counting with tiktoken](https://github.com/openai/openai-cookbook/blob/8730772/examples/How_to_count_tokens_with_tiktoken.ipynb) | Keep because it supports this project's deterministic local token budgeting and explains tokenizer encodings, context limits, cost estimation, message overhead, and tool-schema token overhead. Review against current model names, but do not replace unless we want API-based token counting instead of local estimation guidance. |
| `openai-latency-optimization` | Keep | `openai-latency-optimization` | [OpenAI latency optimization guide](https://developers.openai.com/api/docs/guides/latency-optimization) | Keep as the strongest latency/efficiency source. It covers fewer output tokens, fewer input tokens, fewer requests, parallelization, streaming, smaller models, deterministic alternatives, and RAG context trimming. Review the existing snapshot against the current documentation page. |
| `openai-handle-rate-limits` | Replace | `openai-rate-limits` | [OpenAI rate limits guide](https://developers.openai.com/api/docs/guides/rate-limits) | Replaces retry-example-centered notebook material with current operational limits: RPM, RPD, TPM, TPD, usage tiers, organization/project scope, long-context limits, shared model limits, rate-limit response headers, and vector-store ingestion limits. |
| `openai-prompt-caching` | Keep | `openai-prompt-caching` | [OpenAI prompt caching guide](https://developers.openai.com/api/docs/guides/prompt-caching) | Keep, but refresh the snapshot because current docs include cache-write accounting, `cached_tokens`, `cache_write_tokens`, `prompt_cache_key`, explicit cache breakpoints, and cacheable-prefix design. This is directly useful for repeated RAG prefixes and evaluation runs. |

### Alternative Candidates

| Candidate | Review link | Recommendation | Reason |
| --- | --- | --- | --- |
| `openai-token-counting-api` | [OpenAI token counting guide](https://developers.openai.com/api/docs/guides/token-counting) | Backup replacement or supplemental source | More current than the tiktoken notebook for exact request-token counting because it counts the same payload shape sent to Responses, including messages, tools, images, files, and request-structure tokens. Use if the category should prioritize exact API accounting over local deterministic estimation. |
| `openai-api-pricing` | [OpenAI API pricing](https://developers.openai.com/api/docs/pricing) | Review reference, not recommended as a corpus snapshot | Pricing is highly volatile and table-heavy. Use it to verify current cost fields and pricing dimensions, but prefer `openai-cost-optimization` for durable corpus text. |
| `azure-openai-quotas-limits` | [Azure OpenAI quotas and limits](https://learn.microsoft.com/en-us/azure/foundry/openai/quotas-limits) | Azure-specific backup candidate | Strong fit for the Azure runtime boundary: quota is scoped by subscription, region, model, and deployment type; TPM/RPM pools and quota tiers are operationally relevant. The page is table-heavy and changes often, so it is better as a backup unless Azure quota behavior becomes a core corpus question. |
| `openai-text-generation` | [OpenAI text generation guide](https://developers.openai.com/api/docs/guides/text-generation) | Keep only if request-shape coverage is still needed in this category | Useful API basics source, but it overlaps Prompting and is less directly tied to cost, tokens, and operational budget than the cost-optimization guide. |
| `openai-handle-rate-limits` | [OpenAI Cookbook rate limits notebook](https://github.com/openai/openai-cookbook/blob/8730772/examples/How_to_handle_rate_limits.ipynb) | Keep only if retry examples are more important than current limit semantics | The notebook remains useful for backoff and batching patterns, but current docs are a cleaner source for RPM/TPM, headers, usage tiers, and model/project limit behavior. |

### LLM Settings Implementation Tasks

| Task | Status | Source slug | Local file | Manifest sections | Notes |
| --- | --- | --- | --- | --- | --- |
| CRP-LS01 | Pending | `openai-cost-optimization` | `corpus/sources/openai-cost-optimization.md` | Cost and latency reduction levers; Batch, flex processing, model choice, and token minimization | Add manifest entry replacing `openai-text-generation`. Capture snapshot metadata and OpenAI docs reuse terms. |
| CRP-LS02 | Pending | `openai-token-counting` | `corpus/sources/openai-token-counting.md` | Token counting concepts; Prompt budgeting and model-specific token accounting | Keep and review existing local source against current model names and the stricter checklist. |
| CRP-LS03 | Pending | `openai-latency-optimization` | `corpus/sources/openai-latency-optimization.md` | Latency and efficiency principles; Token reduction, fewer requests, streaming, and RAG trimming | Keep and refresh only if the current docs materially differ from the pinned local snapshot. |
| CRP-LS04 | Pending | `openai-rate-limits` | `corpus/sources/openai-rate-limits.md` | Rate-limit scope, usage tiers, and limit dimensions; Headers, shared limits, retries, batching, and ingestion limits | Add manifest entry replacing `openai-handle-rate-limits`. |
| CRP-LS05 | Pending | `openai-prompt-caching` | `corpus/sources/openai-prompt-caching.md` | Prompt caching mechanics; Static and dynamic prompt layout, cache keys, breakpoints, and usage observability | Keep but refresh to current docs, especially cache-write and breakpoint behavior. |
| CRP-LS06 | Pending | LLM settings category | `corpus/manifest.json` | n/a | Remove manifest references to replaced sources after replacement snapshots are generated. |
| CRP-LS07 | Pending | LLM settings category | `README.md` and proposal artifacts | n/a | Update source list/counts and rationale. |
| CRP-LS08 | Pending | LLM settings category | `golden/questions.json` | n/a | Review expected relevant sources for settings/cost/token questions after content changes. |

## Categories Not Requiring Refinement

LLM security and risks does not require a second-pass source review for this refinement cycle. Keep the existing category sources unchanged unless implementation work later reveals a manifest, snapshot, or ingestion defect.

## Validation Workflow

After approved refinement edits are implemented:

1. Run manifest and chunking tests:

   ```powershell
   uv run pytest tests/unit/test_manifest.py tests/unit/test_chunking.py
   ```

2. Run corpus inspection:

   ```powershell
   uv run raglab corpus inspect --json
   ```

3. Run ingestion workflow tests:

   ```powershell
   uv run pytest tests/integration/test_corpus_ingest_workflow.py
   ```

4. If source slugs or content changed, re-run baseline and routed evaluation after re-ingesting the corpus in the configured environment.

5. Review traces for prompt-category, RAG/context, LLM settings/cost/token, and evaluation-category questions before updating final sample artifacts.

## Completion Rule

This refinement is complete when:

- all approved Prompting tasks are marked complete;
- all approved RAG and Context Handling tasks are marked complete or explicitly deferred with rationale;
- all approved RAG Evaluation tasks are marked complete or explicitly deferred with rationale;
- all approved LLM settings, cost, and tokens tasks are marked complete or explicitly deferred with rationale;
- LLM security and risks remains unchanged unless a concrete implementation defect is found;
- `corpus/manifest.json` references only existing local source files;
- replaced local files are removed only after they are no longer referenced;
- corpus inspection and relevant tests pass;
- README and proposal artifacts describe the refined corpus accurately.
