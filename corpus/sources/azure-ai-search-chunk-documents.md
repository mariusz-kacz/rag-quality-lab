# Source snapshot

Source metadata:
- source_slug: azure-ai-search-chunk-documents
- category: RAG and context handling
- upstream_url: https://learn.microsoft.com/en-us/azure/search/vector-search-how-to-chunk-documents
- source_markdown: https://github.com/MicrosoftDocs/azure-ai-docs/blob/main/articles/search/vector-search-how-to-chunk-documents.md
- license: CC BY 4.0 content / MIT code examples
- pinned_version: microsoft-azure-docs@main-snapshot-2026-07-10
- observed_source_commit: main snapshot inspected 2026-07-10
- snapshot_captured: 2026-07-10
- snapshot_type: normalized documentation digest from Microsoft Learn source markdown
- normalization: removed Microsoft Learn page chrome, feedback controls, long output excerpts, repeated navigation links, and setup-only details; retained chunking rationale, strategy taxonomy, overlap guidance, token and character limit notes, indexing workflow placement, and compact examples that materially explain chunk sizing

---
# Chunking workflow and strategy selection

The Azure AI Search chunking article frames document chunking as a prerequisite for reliable RAG and vector search when source documents are too large or too broad to be represented as a single retrievable unit. Chunking helps a system stay below embedding-model and chat-model input limits, prevents silent truncation, and gives retrieval smaller units that can match a user's question more precisely than an entire document.

The source uses Azure OpenAI `text-embedding-3-small` as a concrete example of a model with an 8,191-token input limit. It also notes the practical rule of thumb that one token is roughly four characters for common OpenAI models, which makes model limits relevant even when a chunking tool is configured in characters. The article applies the same constraint to chat completion and RAG workflows: the retrieved passages ultimately need to fit into the model request, so indexing-time chunking and answer-time context budgeting are connected.

Azure AI Search supports built-in chunking and vectorization through indexers and skillsets. In an integrated vectorization pipeline, the service can split content and generate embeddings during indexing. If a team cannot use integrated vectorization, the same article describes alternative chunking approaches and external libraries. For agentic retrieval, some knowledge sources can generate an indexer pipeline that includes chunking and optional vectorization from the knowledge source definition.

The source distinguishes several common chunking techniques:

- Fixed-size chunks define a target length, such as a number of words or characters, with some overlap. This can work well when the chosen size is large enough to contain semantically meaningful paragraphs.
- Variable-sized chunks use content characteristics, such as sentence endings, line breaks, document structure, HTML headings, or Markdown headings, to preserve natural section boundaries.
- Semantic chunks preserve meaning and relationships across sentences and paragraphs, producing chunks that better maintain semantic coherence and can cross page boundaries when the document structure calls for it.
- Custom combinations mix fixed and variable strategies. One example is appending the document title to chunks from the middle of a long document so retrieved text does not lose source context.
- Document parsing can sometimes achieve a similar effect by converting large source files into smaller search documents for indexing.

The article emphasizes that chunking is not only about avoiding hard input limits. A document might be small enough to embed as one vector but still be a poor retrieval unit if it covers many unrelated subtopics. In that case, finer-grained chunking can improve retrieval because each vector represents a narrower semantic unit.

For this project, the key workflow is:

1. Decide whether each source document is too large or too semantically broad to index as one unit.
2. Choose fixed, variable, semantic, or custom chunking based on document shape and likely user questions.
3. Preserve enough local metadata, such as title and section path, so a retrieved chunk is understandable alone.
4. Add chunking to the indexing workflow before embedding and vector storage.
5. Measure whether retrieved chunks fit the answer model's context budget and contain enough evidence for grounding.

Chunking also affects evaluation. If a relevant answer spans a boundary, an evaluation run might show poor recall even when the source document is in the corpus. If chunks are too large, retrieval can return broad passages that fit poorly into context and dilute citations. A RAG quality review should therefore record chunk size, overlap, title handling, token estimates, and whether the selected chunks are self-contained enough for answer generation.

Relevant upstream concepts:

- Azure AI Search integrated vectorization: `vector-search-integrated-vectorization.md`
- Text Split skill: `cognitive-search-skill-textsplit.md`
- Azure Content Understanding skill: `cognitive-search-skill-content-understanding.md`
- Custom skill workflow: `cognitive-search-custom-skill-web-api.md`

# Chunk size, overlap, token limits, and indexing implications

The article gives practical guidance for fixed-size chunking and overlap. When splitting by fixed size, a small overlap between adjacent chunks can maintain continuity and context at boundaries. The documented starting point is a 512-token chunk, approximately 2,000 characters, with 25 percent overlap, or 128 tokens. The source warns that the optimal overlap depends on the content type and use case: highly structured content might need less overlap, while narrative or conversational text can benefit from more continuity.

The article also highlights factors that should shape chunking choices:

- Shape and density of documents. If intact passages are important, larger chunks or variable chunking that preserves sentence structure can work better.
- User query patterns. Larger chunks and overlap can preserve context for questions that target specific information inside longer passages.
- Model constraints. Chunk size should work for every model in the workflow, such as both the embedding model and any summarization or chat model that consumes the retrieved text.

These factors turn chunking into a testable retrieval parameter. A system should not choose a size only because it is convenient for the splitter. It should choose a size that produces retrievable units that fit the embedding model, are meaningful to retrieve, and still leave enough answer budget after the selected context is assembled.

The Text Split skill example gives concrete parameters:

- `textSplitMode` can split content as `pages`, where chunks contain multiple sentences, or as `sentences`, where chunks contain single sentences.
- `maximumPageLength` defines the maximum size of each page or chunk. Depending on API version and parameters, this can be character-oriented or token-oriented.
- `pageOverlapLength` defines how much text from the end of the previous chunk appears at the start of the next chunk. When set, it must be less than half of `maximumPageLength`.
- `maximumPagesToTake` can limit how many chunks are taken from a document; the default means all chunks.

The article explicitly warns that characters do not align with tokens. A fixed character size measured by the splitter can produce different token lengths when the LLM tokenizer counts the same text. This matters for RAG because the answer model's context budget is token-based. The source notes token chunking support in newer preview APIs, including tokenizer parameters and tokens that should not be split.

In the Earth at Night example, changing split length and overlap changes the number of produced chunks. With smaller lengths or added overlap, the index receives more chunks. With larger lengths and no overlap, the index receives fewer chunks. The article recommends starting with `textSplitMode` set to `pages`, `maximumPageLength` set to 2,000 characters, and `pageOverlapLength` set to 500 characters when using character counts. This is a starting point, not a universal rule.

The LangChain example shows why token counts should be inspected before choosing chunk size. The source loads PDF pages, calculates token counts with TikToken, and uses the observed minimum, average, and maximum token counts to inform a splitter configuration. In the example, a standard 2,000-character chunk with 500-character overlap is not the best fit because the pages are already relatively small in token terms. The lesson is to inspect actual document lengths rather than assume defaults are appropriate.

Compact form of the token-inspection pattern:

```python
import tiktoken

tokenizer = tiktoken.get_encoding("cl100k_base")

def token_count(text: str) -> int:
    return len(tokenizer.encode(text, disallowed_special=()))

counts = [token_count(page.page_content) for page in pages]
summary = {
    "min_tokens": min(counts),
    "avg_tokens": int(sum(counts) / len(counts)),
    "max_tokens": max(counts),
}
```

The article's examples also show the indexing implication of overlap. Consecutive chunks can share text so that context from the first chunk appears at the beginning of the second. This improves boundary continuity but can increase duplicate text in the index and repeated evidence in retrieved context. Too much overlap can waste storage, embedding cost, retrieval slots, and prompt tokens.

A practical RAG chunking checklist from the source is:

1. Verify source documents and target models before selecting a splitter.
2. Keep every chunk below embedding-model input limits.
3. Keep retrieved chunks small enough for answer-time context budgets.
4. Prefer sentence, paragraph, heading, or semantic boundaries when those preserve meaning.
5. Add limited overlap when boundary cuts would otherwise lose context.
6. Inspect actual token counts because character size and token size diverge.
7. Treat chunk count, duplicate overlap, retrieval recall, and answer quality as connected metrics.

For this project's corpus, this source replaces a dataset-specific Wikipedia ingestion notebook with a focused chunking reference. It is most useful for questions about why RAG needs chunking, how chunk size and overlap affect retrieval, how token limits shape context handling, and where chunking belongs in an indexing and vectorization workflow.
