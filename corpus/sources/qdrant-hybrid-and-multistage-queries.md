# Source snapshot

Source metadata:
- source_slug: qdrant-hybrid-and-multistage-queries
- category: RAG and context handling
- upstream_url: https://qdrant.tech/documentation/search/hybrid-queries/
- source_markdown: https://github.com/qdrant/landing_page/blob/master/qdrant-landing/content/documentation/search/hybrid-queries.md
- license: Qdrant documentation reuse terms pending snapshot verification
- pinned_version: qdrant-landing-page@master-snapshot-2026-07-10
- observed_source_commit: master snapshot inspected 2026-07-10
- snapshot_captured: 2026-07-10
- snapshot_type: normalized documentation digest from Qdrant documentation markdown
- normalization: removed navigation chrome, repeated SDK language variants, shortcode-only blocks, and long API examples; retained Query API structure, prefetch semantics, dense-sparse fusion, RRF and DBSF behavior, evaluation guidance for fusion weights, multi-stage rescoring, formula scoring, and grouping relevance

---
# Hybrid retrieval and dense-sparse fusion

The Qdrant hybrid queries documentation describes retrieval patterns that combine multiple vector representations or multiple search stages in one Query API request. This is directly relevant to a RAG system that stores chunks in Qdrant and may later need more than single-vector semantic search for exact terms, identifiers, or reranking.

The core mechanism is the `prefetch` parameter. When a query includes one or more prefetches, Qdrant first runs the prefetch query or queries, then applies the main query over the prefetch results. Prefetches can be nested, which allows a retrieval pipeline to collect candidates with one representation, refine them with another representation, and then apply a final fusion or scoring step. The documentation notes that `offset` affects only the main query, so each prefetch must request enough candidates to cover the final `limit + offset` or the main query can receive too small a candidate set.

Hybrid search addresses a common RAG problem: one representation rarely handles every query type well. Dense vectors capture semantic similarity and can match a natural-language question to a concept even when the exact words differ. Sparse vectors or lexical retrievers preserve exact word matching, which is often better for identifiers, product names, error codes, acronyms, and rare terms. Qdrant supports combining these result sets when the same point has multiple named vector representations.

The source describes two fusion methods:

- Reciprocal Rank Fusion, or RRF, uses the rank positions of results in each prefetch result set. A point receives a higher fused score when it appears near the top of one or more rankings. This avoids comparing raw dense and sparse score magnitudes directly.
- Distribution-Based Score Fusion, or DBSF, normalizes the score distribution from each retriever before summing normalized scores. This can work when raw scores carry useful magnitude information, but it depends on the returned top-k distribution for each query.

RRF is presented as a robust default because it fuses by rank rather than raw score. Qdrant uses zero-based rank positions, and its RRF query can also accept weights. Weighted RRF is useful when an evaluation set shows one retriever is stronger for the workload than another. For example, a dense retriever might be more reliable for natural-language questions, while a sparse retriever might be stronger for identifier-heavy questions. The documentation warns that weights should be measured on an evaluation set rather than hand-tuned arbitrarily.

The practical weighted-fusion guidance is:

- If there is an evaluation set with known-relevant documents, tune weights on one split and measure on another split so the same queries are not used for both tuning and reporting.
- If there is no evaluation set, keep equal weights instead of relying on unmeasured guesses.
- Retune when retrievers change, such as after a new embedding model, changed chunking strategy, changed corpus distribution, or scheduled evaluation refresh.

DBSF keeps raw score information but normalizes each retriever's returned scores. The documentation explains that dense and sparse scores live on different scales, so a fixed alpha over raw dense and sparse scores is unreliable unless scores are normalized first. DBSF can be appropriate when the raw scores are well calibrated and an evaluation set is not available, but the source notes caveats: the statistics come from the top-k prefetch sample, and an outlier can skew normalization for a query. Increasing the prefetch limit can help stabilize rankings when the top-k sample is too narrow.

The source's fusion-method decision table can be summarized as:

- Use weighted RRF when there is an evaluation set and the system can tune weights with a train/validation split.
- Use DBSF when raw retriever scores are trusted and there is no evaluation set.
- Use basic RRF when there is neither an evaluation set nor strong score calibration.

For a RAG quality lab, this source matters even when the current runtime supports only vector retrieval. It explains why future hybrid retrieval should be evaluated rather than guessed, why exact-term-sensitive questions may need sparse retrieval, why dense and sparse scores should not be naively averaged, and why traces should record retrieval mode, prefetch limits, fusion method, weights, and final rank.

Relevant upstream concepts:

- Qdrant Query API: https://api.qdrant.tech/
- Multiple named vectors per point: Qdrant vectors documentation
- RRF background: University of Waterloo Reciprocal Rank Fusion paper
- Qdrant search relevance reference: Qdrant documentation

# Multi-stage retrieval, prefetch, and reranking patterns

The documentation presents multi-stage retrieval as a way to balance retrieval quality and cost. Larger vector representations or late-interaction models can be more accurate, but they are more expensive to compute and compare across a whole collection. A two-stage architecture mitigates this by using a cheaper representation to collect a broad candidate set, then reranking that candidate set with a more accurate representation.

The source names several stage patterns:

- Use quantized vectors for the first stage and full-precision vectors for the second stage.
- Use Matryoshka Representation Learning to retrieve with shorter vectors and then refine with longer vectors.
- Use a regular dense vector to prefetch candidates and a multi-vector model such as ColBERT to rerank those candidates.

In Qdrant, this is expressed through nested prefetch queries. The early prefetch retrieves more candidates than the final answer needs. The main query or later stage then reranks those candidates and returns a smaller top-k. For example, a system can fetch 1,000 candidates with a short or quantized vector, rerank 100 with a full vector, and return the top 10 with a multi-vector reranker. The exact numbers are workload decisions, but the shape is stable: broad cheap recall first, narrower accurate ranking second.

The documentation also points out an index-memory optimization. If a vector is used only for rescoring and not for initial HNSW retrieval, its HNSW index can be disabled by setting `m=0` in that vector's HNSW configuration. Rescoring does not need the HNSW graph, so disabling it can free memory. This is an example of how retrieval architecture decisions affect storage and runtime cost, not just ranking.

A simplified Qdrant multistage retrieval shape is:

```json
{
  "prefetch": {
    "query": [0.01, 0.45, 0.67],
    "using": "small_dense",
    "limit": 100
  },
  "query": [0.02, 0.46, 0.69],
  "using": "full_dense",
  "limit": 10
}
```

This compact example keeps the important relationship from the source: prefetch produces candidates, the main query reranks those candidates, and the final limit controls the returned result count. A production request can extend this with named sparse vectors, dense vectors, multi-vectors, nested prefetches, and fusion queries.

The documentation also describes formula queries. A formula query composes a final score from the prefetch score, payload fields, and helper functions such as exponential or Gaussian decay. The typical pattern is to fuse retrievers with RRF or DBSF inside a prefetch, then wrap the fused result in a formula query that layers ranking logic on top. Examples include recency decay, popularity boosts, geographic decay, or category-specific multipliers.

Formula scoring has a calibration risk. RRF scores are small sums of rank-based terms, while decay functions often return values between 0 and 1. If a decay term is added without a smaller coefficient, it can dominate the fused score. The source recommends calibrating the decay weight against the scale of the fused score and tuning the coefficient for the workload.

Grouping is another retrieval-control feature. Qdrant can group results by a payload field so the final results avoid too many points from the same item. In RAG systems, grouping can reduce redundant chunks from the same document and improve source diversity before context assembly. Grouping is especially useful when documents have many chunks and the top-k could otherwise be filled by near-duplicate passages from one source.

The practical multi-stage RAG pattern from the source is:

1. Store multiple representations when different query types require different retrieval strengths.
2. Use prefetch to retrieve a broad candidate set cheaply.
3. Fuse dense and sparse candidate lists with RRF or DBSF when both semantic and lexical signals matter.
4. Rerank candidates with a stronger vector, multi-vector, or formula query.
5. Use payload-aware formula scoring only when its weight is calibrated.
6. Use grouping when redundant chunks from the same parent document crowd out useful evidence.
7. Trace every stage so evaluation can distinguish first-stage recall failures from reranking or fusion errors.

For this corpus, this source replaces a managed OpenAI file-search notebook with a Qdrant-specific retrieval reference aligned with the project's storage and retrieval boundary. It supports questions about hybrid retrieval, dense-sparse fusion, prefetching, multistage reranking, Qdrant scoring controls, and future extensions beyond the current MVP vector-only runtime.
