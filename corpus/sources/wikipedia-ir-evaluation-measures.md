# Source snapshot

Source metadata:
- source_slug: wikipedia-ir-evaluation-measures
- category: RAG evaluation and quality
- upstream_url: https://en.wikipedia.org/wiki/Evaluation_measures_(information_retrieval)
- source_page: https://en.wikipedia.org/wiki/Evaluation_measures_(information_retrieval)
- source_revision: https://en.wikipedia.org/w/index.php?oldid=1360656682&title=Evaluation_measures_%28information_retrieval%29
- license: CC BY-SA 4.0
- pinned_version: wikipedia@current-snapshot
- snapshot_type: normalized documentation digest from Wikipedia article
- normalization: removed Wikipedia navigation, edit controls, citation markup, formula image artifacts, reference list, and page chrome; retained IR evaluation context, offline and online metric definitions, formulas, caveats, and compact RAG-oriented interpretation

---
# Precision, recall, F-score, and precision at k

The Wikipedia article frames information retrieval evaluation as the assessment of how well an index, search engine, or database returns resources that satisfy a user's query. It distinguishes system effectiveness from broader product qualities such as latency, usability, satisfaction, reliability, and operational efficiency. For a RAG system, this distinction matters: retrieval metrics can show whether evidence was found and ranked well, but they do not by themselves prove that the generated answer is grounded, complete, or useful.

The article describes two broad evaluation settings:

- online evaluation, which uses user interactions such as clicks, abandoned sessions, success events, and zero-result sessions;
- offline evaluation, which uses a fixed collection, a set of queries, and relevance judgments for returned documents.

Offline metrics are the main fit for a reproducible RAG quality lab because the same questions, sources, and judgments can be reused across retrieval strategies. The article notes that relevance judgments can be binary or graded. It also calls out that real queries may be ambiguous. For example, a query such as "mars" can refer to a planet, a candy bar, a person, or a deity. This is directly relevant to RAG evaluation: a route, retrieval filter, or answer policy should handle ambiguous questions explicitly rather than treating every mismatch as a retriever failure.

## Precision

Precision is the fraction of retrieved documents that are relevant to the user's information need:

```text
precision = relevant retrieved / retrieved total
```

Equivalently, using set notation:

```text
precision = |relevant documents intersect retrieved documents| / |retrieved documents|
```

In binary classification terms, precision is analogous to positive predictive value. In retrieval terms, it asks how much of the returned result set is useful. High precision is important when users or downstream components inspect only a few results. For RAG, high precision means the model context is less likely to be crowded with irrelevant chunks that distract generation or cause unsupported citations.

The article cautions that information retrieval precision is not the same concept as "precision" in measurement science or general statistics. In IR, precision is about the relevance fraction among retrieved items.

## Recall

Recall is the fraction of relevant documents that the system successfully retrieves:

```text
recall = relevant retrieved / relevant total
```

Equivalently:

```text
recall = |relevant documents intersect retrieved documents| / |relevant documents|
```

In binary classification terms, recall is often called sensitivity. It asks whether the system found the relevant material that exists in the collection.

Recall alone is not enough. The article points out that a system can trivially reach perfect recall by returning every document. That behavior is usually not useful because it retrieves many nonrelevant documents as well. RAG systems have the same issue under a context window: returning too much evidence can make context selection noisy, expensive, and impossible to fit into the prompt. Recall should therefore be read with precision, cutoff size, and context budget.

## Fall-out

Fall-out measures the fraction of nonrelevant documents that are retrieved:

```text
fall-out = nonrelevant retrieved / nonrelevant total
```

In classification terms, fall-out is the complement of specificity. It can be interpreted as the probability that a nonrelevant document is retrieved by the query. The article notes that fall-out can be trivially reduced to zero by returning no documents, which again shows why single metrics can be misleading.

Fall-out is less commonly used in lightweight RAG evaluation than precision and recall, but the concept helps explain retrieval noise. A retriever with high fall-out may send many irrelevant chunks into reranking or context assembly, increasing latency and the chance of unsupported generation.

## F-score and F-measure

The F-score combines precision and recall using a harmonic mean. The balanced F1 score weights precision and recall equally:

```text
F1 = 2 * precision * recall / (precision + recall)
```

The more general F-beta measure lets the evaluator weight recall and precision differently:

```text
F_beta = (1 + beta^2) * precision * recall /
         ((beta^2 * precision) + recall)
```

The article explains that F2 weights recall more heavily than precision, while F0.5 weights precision more heavily than recall. This is useful when the evaluation target has a clear preference. A compliance or audit RAG workflow may prefer recall because missing a relevant policy clause is costly. A compact answer assistant may prefer precision because irrelevant retrieved chunks can contaminate short answers.

F-score is convenient as a single number, but it hides the tradeoff between precision and recall. A local report should still include the component values and the cutoff at which they were measured.

## Precision at k

Precision at k evaluates only the top `k` retrieved results:

```text
precision@k = relevant documents in top k / k
```

The article describes precision at k as especially useful in modern web-scale retrieval, where many queries can have thousands of relevant documents and users rarely inspect all of them. It gives P@10 as the common form: the number of relevant results among the first ten retrieved documents.

Precision at k is simple to score because judges only need to inspect the first `k` results. It is also operationally meaningful for RAG because context assembly usually passes a limited number of chunks to the model.

The article identifies two caveats:

- P@k does not account for the positions of relevant documents within the top `k`. A relevant result at rank 1 and a relevant result at rank 10 both count equally.
- If a query has fewer than `k` relevant results, even a perfect system can score below 1.0 because the denominator remains `k`.

For RAG evaluation, these caveats suggest pairing precision@k with first relevant rank, reciprocal rank, recall@k, or nDCG when ranking order and graded usefulness matter.

# MAP, DCG, nDCG, MRR, hit rate, and metric caveats

Ranked retrieval systems should be evaluated not only by whether they return relevant documents, but also by where those documents appear. The Wikipedia article covers several ranked-list measures that extend precision and recall.

## Average precision and MAP

Average precision evaluates ranking quality over a retrieved sequence. The article describes it as the area under the precision-recall curve and gives a finite-sum form used in practice:

```text
AveP = sum(P(k) * rel(k) for k in 1..n) / total relevant documents
```

Where:

- `k` is a rank in the retrieved list;
- `P(k)` is precision at cutoff `k`;
- `rel(k)` is 1 if the document at rank `k` is relevant and 0 otherwise;
- relevant documents that are not retrieved contribute zero through the denominator.

Average precision rewards systems that retrieve relevant documents early. It is more informative than set precision when rank order matters. For a RAG retriever, average precision can show whether evidence is generally near the top of the list, even beyond the final context cutoff.

Mean average precision is the mean of average precision across queries:

```text
MAP = sum(AveP(q) for q in queries) / number of queries
```

MAP is useful for comparing retrieval strategies across a fixed golden set. It should be interpreted with care when relevance judgments are incomplete. If the evaluator labels only one expected source but other sources are also valid, MAP can penalize reasonable alternate evidence.

## Interpolated average precision

The article notes that some evaluation methods interpolate precision-recall curves to reduce curve instability. One historical method averages interpolated precision across evenly spaced recall levels:

```text
interpolated_precision(r) =
    max(precision(r2) for recall level r2 >= r)
```

This mirrors traditional IR evaluation practice and helps produce smoother comparisons. It is less common in small RAG test sets than direct average precision, but it explains why different tools may report slightly different "average precision" values.

## R-precision

R-precision uses the number of known relevant documents as the cutoff. If a query has `R` relevant documents, evaluate precision after the top `R` retrieved results:

```text
R-precision = relevant documents in top R / R
```

The article's example says that if there are 15 relevant documents for a query, R-precision inspects the top 15 returned documents and computes the relevance fraction. R-precision is equivalent to both precision at rank `R` and recall at rank `R`, because the cutoff equals the number of relevant documents.

The article notes that R-precision is often highly correlated with MAP. In RAG evaluation, it is most useful when the relevant set size is known reasonably well. It is less useful when the golden labels are intentionally non-exhaustive.

## DCG and nDCG

Discounted cumulative gain is designed for graded relevance rather than only binary relevant/nonrelevant labels. It evaluates the usefulness, or gain, of documents by considering both their relevance grade and rank. The core idea is that highly relevant documents are less valuable when they appear lower in the ranking, so their gain is discounted logarithmically.

A common DCG form at rank `p` is:

```text
DCG_p = sum(rel_i / log2(i + 1) for i in 1..p)
```

Where `rel_i` is the relevance grade at rank `i`. Normalized DCG compares the observed ranking to the ideal ranking for the same result set:

```text
nDCG_p = DCG_p / IDCG_p
```

`IDCG_p` is the DCG for the ideal ordering, with the most relevant documents first. The article states that nDCG values are relative values from 0.0 to 1.0, making them comparable across queries.

nDCG is useful for RAG when relevance is not binary. For example:

- a chunk that directly answers the question could receive a high grade;
- a chunk that provides background but not the answer could receive a lower grade;
- a duplicate or stale chunk could receive little or no gain.

This lets a retriever receive more credit for ranking the strongest evidence before weaker support.

## MRR, bpref, GMAP, diversity, credibility, and hit rate

The article lists several additional measures. Mean reciprocal rank (MRR) focuses on the rank of the first relevant result:

```text
reciprocal_rank = 1 / rank_of_first_relevant_result
MRR = mean(reciprocal_rank over queries)
```

MRR is helpful when a task needs at least one useful evidence item quickly. It is less complete than recall-oriented measures for questions requiring multiple pieces of evidence.

The article also names bpref and GMAP. `bpref` is useful when judgments are incomplete because it compares judged relevant documents against judged irrelevant documents without treating every unjudged document as irrelevant. GMAP is the geometric mean of per-topic average precision and emphasizes weak topics more than arithmetic MAP.

The article mentions measures based on marginal relevance and document diversity, measures that combine relevance with credibility, and hit rate. Hit rate is commonly used as a top-k success measure:

```text
hit_rate@k = queries with at least one relevant result in top k / total queries
```

Hit rate is easy to understand, but it is coarse. It does not distinguish one relevant result from many, and it does not measure how much irrelevant material appears beside the hit.

## Online and operational measures

The article includes online measures derived from search logs:

- session abandonment rate, the share of sessions that do not result in a click;
- click-through rate, the share of impressions that receive a click;
- session success rate, the share of sessions that achieve a context-specific success event;
- zero result rate, the share of search result pages with no results;
- queries per unit time, an operational utilization measure.

These metrics are useful in production but are not direct substitutes for offline relevance metrics. Clicks and dwell time can be biased by presentation, user intent, and rank position. A RAG lab can still use them as secondary signals after deployment, especially to detect regressions or query classes that need new golden examples.

## Metric caveats for RAG systems

The article's broad warning is that evaluation measures should be validated against what they are meant to measure and against the system's intended use case. For RAG systems, that means retrieval metrics should be connected to answer outcomes and context constraints.

Important caveats include:

- Relevance judgments may be incomplete, ambiguous, binary, or graded.
- Precision and recall without a cutoff may not reflect what reaches the model.
- Precision@k ignores rank order within the top `k`.
- Recall alone can be maximized by returning too much content.
- MAP and R-precision assume that relevance judgments are meaningful across the ranked list.
- nDCG depends on consistent graded relevance labels.
- Hit rate is useful for quick success tracking but hides evidence quantity and ranking quality.
- Online behavior metrics can reflect interface effects rather than pure retrieval quality.

A reproducible RAG evaluation should name the query set, cutoff, relevance labels, averaging method, and any assumptions about unjudged sources. Retrieval metrics should be reported alongside generation checks such as groundedness, citation validity, answer relevance, and no-answer handling.
