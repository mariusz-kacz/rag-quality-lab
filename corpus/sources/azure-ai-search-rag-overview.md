# Source snapshot

Source metadata:
- source_slug: azure-ai-search-rag-overview
- category: RAG and context handling
- upstream_url: https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview
- source_markdown: https://github.com/MicrosoftDocs/azure-ai-docs/blob/main/articles/search/retrieval-augmented-generation-overview.md
- license: CC BY 4.0 content / MIT code examples
- pinned_version: microsoft-azure-docs@main
- snapshot_type: normalized documentation digest from Microsoft Learn source markdown
- normalization: removed Microsoft Learn page chrome, tab scaffolding, feedback controls, and long resource lists; retained RAG challenges, Azure AI Search retrieval patterns, token and relevance controls, security trimming, and links that materially identify upstream concepts

---
# RAG architecture and query understanding

Retrieval-augmented generation extends a language model by grounding responses in content supplied at query time. In Azure AI Search, the retrieval system is responsible for finding compact, relevant grounding data from proprietary or enterprise content before the application or agent asks a model to formulate an answer. The documentation frames RAG as a simple pattern with difficult operational requirements: queries are conversational, data often comes from multiple systems, model context windows are finite, users expect low latency, and private content must remain governed.

Azure AI Search addresses these requirements through two RAG approaches:

- Agentic retrieval: a specialized, preview RAG pipeline that uses an LLM to plan retrieval, split complex requests into targeted subqueries, search across knowledge sources, and return structured grounding data for agents or chat completion models.
- Classic RAG: a simpler architecture where the application sends a single search request to Azure AI Search, receives a flattened result set, and separately orchestrates the model call that uses those results as grounding context.

The query understanding problem is central. A user might ask a natural-language question whose wording does not match source documents. Agentic retrieval handles this by analyzing the user question, using conversation history, decomposing the request into focused searches, and running those subqueries in parallel across knowledge sources. Classic RAG handles the same problem with search-time ranking features: hybrid search combines keyword and vector retrieval, semantic ranking re-scores results by meaning, and vector similarity can match related concepts even when exact terms differ.

For multi-source content, agentic retrieval introduces knowledge sources and knowledge bases. A knowledge base can unify multiple data sources, query remote SharePoint and Bing without indexing when appropriate, use retrieval instructions to steer source selection, and auto-generate indexing pipelines for supported sources such as Azure Blob, OneLake, SharePoint ingestion, and other external content. Classic RAG relies on the traditional Azure AI Search indexing model: indexers can pull from Azure data sources, skillsets can perform chunking, vectorization, image verbalization, and analysis, and incremental indexing keeps indexed content fresh while the application controls what is indexed and how.

Agentic retrieval changes the classic single-query flow into a multi-query retrieval flow. It provides context-aware query planning, parallel execution, structured responses with grounding data and citations, execution metadata, built-in semantic ranking, and optional answer synthesis in the retrieval response. To use this path, the application works with knowledge sources, a knowledge base, and a retrieve action that can be invoked from application code or an agent tool. The documentation recommends agentic retrieval for new RAG implementations, especially when the client is an agent or chatbot, the questions are complex or conversational, or structured responses with citations and query details are needed.

Classic RAG remains useful when general availability, speed, simplicity, or fine-grained application control are more important than the extra query-planning layer. In this architecture, the application sends a search query, receives ranked search results, selects or formats the returned fields, and then passes those results to the LLM. Because no LLM participates in query planning, classic RAG has fewer moving parts and can be faster for simpler workloads.

Content preparation affects both architectures. Azure AI Search supports built-in and skill-based chunking for large documents, language analyzers and multilingual vectors for multilingual text, OCR and image analysis for images and PDFs, integrated vectorization through Azure OpenAI or other vectorizers, and synonym maps or semantic ranking for terminology mismatches. For agentic retrieval, knowledge sources can auto-generate chunking and vectorization pipelines. For classic RAG, teams can use indexers and skillsets or push preprocessed content through the indexing APIs.

Relevant upstream concepts:

- Agentic retrieval overview: `agentic-retrieval-overview.md`
- Query planning and retrieval reasoning effort: `agentic-retrieval-how-to-set-retrieval-reasoning-effort.md`
- Knowledge source overview: `agentic-knowledge-source-overview.md`
- Classic Azure AI Search architecture: `search-what-is-azure-search.md`
- Classic RAG sample repository: https://github.com/Azure-Samples/azure-search-classic-rag/blob/main/README.md

# Token constraints, security trimming, and retrieval patterns

The source emphasizes that RAG retrieval should return highly relevant, concise grounding data rather than large document dumps. Even large-context models cannot accept every page in an enterprise corpus, and sending too much text wastes tokens and can reduce answer quality. Azure AI Search therefore treats relevance, result shaping, and context size as first-class RAG concerns.

Agentic retrieval reduces token pressure by returning only the most relevant chunks in a structured response. It includes citation tracking for provenance, a query activity log that shows what was searched, and optional answer synthesis that can further compress the retrieval response before final answer generation. Classic RAG exposes lower-level controls: semantic ranking can identify the strongest results, vector and text result counts can be configured, minimum thresholds can exclude weak matches, scoring profiles can boost important content, and select clauses can limit returned fields to what the model actually needs.

A useful retrieval pipeline starts during indexing. Large documents should be split into chunks so that relevant passages can be matched independently. Chunks that are too large are hard to fit into a prompt and may contain unrelated text; chunks that are too small can lose context. When vector retrieval is needed, the indexing pipeline should create embeddings for the chunks that will be searched at query time.

At query time, Azure AI Search recommends combining multiple relevance signals when grounding quality matters:

- Hybrid search combines keyword search and vector similarity search. When the same user input is supplied as text and as a vector query, Azure AI Search can run the keyword and similarity searches in parallel and merge the strongest matches into a unified result set.
- Semantic ranking can improve ordering by evaluating meaning and intent, and is built into agentic retrieval while remaining optional in classic RAG.
- Scoring profiles can boost specific fields or business criteria when some content should rank higher than the base retrieval score would place it.
- Vector query parameters, including vector weighting and minimum thresholds, can tune how strongly vector matches contribute and can filter out low-quality results.
- Field selection controls how much text and metadata are returned to the model, which directly affects context budget and response latency.

Security and governance are also retrieval responsibilities. RAG systems must avoid surfacing private content to unauthorized users or agents. Agentic retrieval can apply access control at the knowledge-source level, inherit SharePoint permissions for remote SharePoint queries, inherit Microsoft Entra ID permission metadata for indexed Azure Storage content, apply filter-based security at query time for other sources, and use private endpoints for network isolation. Classic RAG supports document-level security trimming, inherited permission metadata for indexed content, filter-based security, and private endpoints. In both patterns, authorization must be enforced before retrieved content is made available to a model.

Latency is another constraint. Agentic retrieval improves complex retrieval latency by executing subqueries in parallel, using built-in semantic ranking, and allowing adjustable reasoning effort. Classic RAG can be faster for simpler scenarios because search responses are typically low-latency, the application can make a single-shot query, timeout and retry policy remain under application control, and the architecture has fewer failure points.

The source's selection guidance can be summarized as follows:

- Use agentic retrieval for new agent or chatbot RAG systems, complex conversational queries, high relevance requirements, and workflows that benefit from structured grounding data, citations, and query execution details.
- Use classic RAG when generally available features are required, simple low-latency retrieval is enough, existing orchestration should be preserved, or the application needs direct control over query construction and result handling.

Some Azure AI Search features are less relevant for RAG than for human search experiences. Autocomplete and suggestions can usually be skipped. Facets and ordering can be useful in specialized cases, but they are not common core requirements for grounding an LLM response.

Relevant upstream concepts:

- Hybrid search: `hybrid-search-overview.md`
- Semantic ranking: `semantic-ranking.md`
- Scoring profiles: `index-add-scoring-profiles.md`
- Vector query weighting and thresholds: `vector-search-how-to-query.md`
- Built-in security: `search-security-built-in.md`
- Indexing concepts and strategies: `search-what-is-an-index.md`
- Query syntax and requirements: `search-query-create.md`
