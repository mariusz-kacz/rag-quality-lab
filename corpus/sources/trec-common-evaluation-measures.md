# Source snapshot

Source metadata:
- source_slug: trec-common-evaluation-measures
- category: RAG evaluation and quality
- upstream_url: https://trec.nist.gov/pubs/trec15/appendices/CE.MEASURES06.pdf
- source_pdf: https://trec.nist.gov/pubs/trec15/appendices/CE.MEASURES06.pdf
- license: Public/government documentation, reuse metadata pending snapshot verification
- pinned_version: trec-common-evaluation-measures-2006
- snapshot_type: normalized documentation digest from TREC PDF
- normalization: removed PDF graph axes, sample report layout noise, page breaks, and table-rendering artifacts; retained retrieval metric definitions, formulas, compact examples, trec_eval report interpretation, and cautions about incomplete judgments

---
# Recall, precision, and ranked-list evaluation

The TREC common evaluation measures document defines a compact set of retrieval metrics for evaluating systems that return documents for information needs. The metrics are framed around relevance judgments: a document is either relevant or not relevant to a topic, and a retrieval run returns some ordered or unordered set of documents.

Recall measures how much of the relevant material the system retrieved:

```text
recall = relevant retrieved / relevant in collection
```

Precision measures how much of the retrieved material is relevant:

```text
precision = relevant retrieved / retrieved total
```

As set-based metrics, recall and precision evaluate the quality of a retrieved set without considering rank order. That is useful when the question is whether a system found relevant documents at all. It is incomplete for search and RAG systems where the position of evidence matters. A retriever that puts relevant passages at ranks 1 and 2 is more useful than one that hides them at ranks 50 and 80, even if both retrieve the same relevant items somewhere in the result list.

For ranked retrieval, TREC evaluates precision after each retrieved document and then relates those values to recall. The result can be plotted as a recall-precision curve. Because different topics can have different numbers of relevant documents, TREC normalizes comparison by interpolating precision at standard recall levels from 0.0 through 1.0 in increments of 0.1.

Interpolated precision at a standard recall level is the maximum precision reached at any actual recall point greater than or equal to that level. This rule smooths the curve and lets runs be averaged across topics. It also defines a value at recall 0.0 even though ordinary precision is not defined at zero retrieved relevant documents.

The source example uses a collection with 20 documents and four relevant documents. If a system ranks those relevant documents at positions 1, 2, 4, and 15, the actual recall points are 0.25, 0.50, 0.75, and 1.00. The corresponding precision values at those relevant ranks are:

```text
rank 1:  relevant retrieved 1 / retrieved 1  = 1.00, recall 0.25
rank 2:  relevant retrieved 2 / retrieved 2  = 1.00, recall 0.50
rank 4:  relevant retrieved 3 / retrieved 4  = 0.75, recall 0.75
rank 15: relevant retrieved 4 / retrieved 15 = 0.27, recall 1.00
```

Using the interpolation rule, precision is 1.00 for standard recall levels up to 0.50, 0.75 for levels 0.60 and 0.70, and 0.27 for 0.80 through 1.00. The important retrieval lesson is that late relevant documents increase recall but can reduce precision sharply because many nonrelevant documents have been retrieved first.

## TREC evaluation reports

TREC ranked-list tasks can be evaluated with `trec_eval`, the evaluation program associated with TREC runs. A report for a run contains summary statistics, recall-level precision averages, document-level averages, and graphs. For a local RAG quality corpus, the tabular concepts are more useful than the original PDF formatting.

The summary statistics report:

- the run identifier and information such as whether queries were produced manually or automatically;
- the number of topics searched;
- the total number of submitted documents;
- the total number of relevant documents known from judgments;
- the number of relevant documents retrieved by the run.

These fields let a reviewer distinguish a weak retrieval run from a run evaluated under a sparse or difficult judgment set. In a RAG workflow, analogous summary fields would include number of evaluation questions, number of expected relevant source chunks, retrieved chunk count, and relevant retrieved chunk count.

The recall-level precision averages table reports interpolated precision at 11 standard recall levels:

```text
0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0
```

For each recall cutoff, the per-topic interpolated precision values are summed and divided by the number of topics. The result is a cross-topic average that can be plotted as a recall-precision curve. The curve is commonly used to compare systems. Curves closer to the upper-right corner represent stronger combined recall and precision.

The source recommends comparing systems in separate recall ranges rather than relying on a single visual impression:

- 0.0 to 0.2 characterizes high-precision behavior near the top of the ranking;
- 0.2 to 0.8 characterizes middle-recall behavior;
- 0.8 to 1.0 characterizes high-recall behavior when the system attempts to retrieve most relevant material.

For RAG systems, the high-precision range is often most important when context budgets allow only a few chunks. The high-recall range becomes important for tasks that must gather many pieces of evidence, such as multi-document synthesis, policy comparison, or exhaustive audit questions.

## Precision at document cutoffs

Document-level averages include precision at fixed cutoff values such as 5, 10, 15, 20, 30, 100, 200, 500, and 1000 documents. Precision at a cutoff reflects what a user or downstream system sees after reading only the first `k` results:

```text
precision@k = relevant retrieved in top k / k
```

In RAG evaluation, small cutoffs such as precision@3, precision@5, or precision@10 are usually more actionable than deep cutoffs because only a limited number of chunks can fit into the model context. A retriever can have respectable deep recall while still being poor for RAG if the first few chunks do not contain answer evidence.

Precision at cutoff values should be interpreted with the retrieval budget and task design in mind. If the application always sends the top 5 chunks to the generator, precision@5 and recall@5 are more directly connected to answer quality than precision@100.

## Graphs and per-topic diagnostics

The recall-precision graph summarizes average run behavior across standard recall levels. Its typical shape slopes downward as recall rises, because retrieving more relevant material usually requires accepting more nonrelevant material.

The average precision histogram compares each topic's average precision for a run against the median average precision for corresponding runs on the same topic. Its purpose is diagnostic: it shows which topics a system handles unusually well or poorly. This matters because a mean score can hide topic-level failures. A RAG system may look strong on average while failing on a small set of important query types, such as no-answer questions, temporal questions, or questions requiring exact policy constraints.

Per-topic diagnostics should therefore accompany aggregate scores. Useful local diagnostics include:

- query or topic identifier;
- number of known relevant documents or chunks;
- relevant retrieved count;
- first relevant rank;
- precision and recall at the application's context cutoff;
- average precision for the topic;
- whether the generator cited retrieved evidence correctly.

# Average precision, R-precision, bpref, and GMAP

Average precision is a single-valued ranked retrieval measure that rewards systems for retrieving relevant documents early. It is not the mean of the 11 interpolated precision values used in a recall-precision plot. Instead, it averages the precision observed each time a relevant document is retrieved. Relevant documents that are never retrieved contribute zero.

For one topic:

```text
AP = sum(precision at each relevant retrieved rank) / relevant documents for the topic
```

The source example has four relevant documents retrieved at ranks 1, 2, 4, and 7. Precision at those ranks is 1.00, 1.00, 0.75, and approximately 0.57. Their mean is approximately 0.83, so average precision for the topic is 0.83.

Mean average precision (MAP) is the arithmetic mean of per-topic AP values:

```text
MAP = sum(AP for each topic) / number of topics
```

MAP is useful when the evaluator wants a single number that reflects both ranking quality and coverage of relevant documents. It is sensitive to the full ranked list and therefore can reward improvements beyond the first few retrieved documents. In RAG settings, MAP is often paired with recall@k or MRR because the generator usually sees a truncated context rather than the full ranking.

## R-precision

R-precision is precision after `R` documents have been retrieved, where `R` is the number of relevant documents for the topic:

```text
R-precision = relevant retrieved in top R / R
```

For example, suppose a run has two topics. The first topic has 50 relevant documents and the system retrieves 17 relevant documents in the top 50. The second topic has 10 relevant documents and the system retrieves 7 relevant documents in the top 10. The run's average R-precision is:

```text
((17 / 50) + (7 / 10)) / 2 = 0.52
```

R-precision de-emphasizes the exact positions of relevant documents inside the top `R` compared with measures like AP. The source notes that this can be useful in TREC tasks with large numbers of relevant documents. For RAG, R-precision is conceptually helpful when the relevant set size differs widely by question, but it may be less operational than metrics tied to the actual context cutoff.

## bpref for incomplete relevance judgments

The `bpref` measure is designed for collections where relevance judgments are far from complete. It was introduced for the TREC 2005 terabyte track and uses only judged documents. Instead of assuming unjudged documents are nonrelevant, it measures whether judged relevant documents are ranked ahead of judged irrelevant documents.

The source defines bpref as:

```text
bpref = (1 / R) * sum over judged relevant retrieved documents r of
        (1 - judged nonrelevant documents ranked higher than r / min(R, N))
```

Where:

- `R` is the number of judged relevant documents;
- `N` is the number of judged nonrelevant documents;
- `r` is a judged relevant retrieved document;
- the nonrelevant count considers the first `R` judged nonrelevant retrieved documents.

The document calls out that this definition follows the `trec_eval` version 8.0 implementation, which differs from some commonly cited descriptions. That detail matters when reproducing historical results or comparing local metric code with `trec_eval`.

Conceptually, bpref is the inverse of the fraction of judged irrelevant documents that appear before relevant ones. With complete judgments, bpref and MAP tend to be highly correlated. With incomplete judgments, bpref preserves system rankings better than MAP because it avoids treating every unjudged document as nonrelevant.

For RAG evaluations, incomplete judgments are common. A golden dataset may name one or two expected sources even though other chunks also support the answer. In that setting, metrics that assume exhaustive judgments can understate retriever quality or penalize plausible alternate evidence. bpref's lesson is to keep the judgment model explicit: know whether unlisted sources are truly wrong, merely unjudged, or acceptable alternate support.

## GMAP for low-performing topics

GMAP is the geometric mean of per-topic average precision values. It was introduced in the TREC 2004 robust track for cases where evaluators want to highlight improvements on low-performing topics.

For `n` topics:

```text
GMAP = nth_root(product(AP_i for i in topics))
```

Equivalently:

```text
GMAP = exp((1 / n) * sum(log(AP_i) for i in topics))
```

MAP uses the arithmetic mean, so gains on one topic can offset losses on another. GMAP is more sensitive to very low AP values. If a run doubles a weak topic's AP from 0.02 to 0.04 while slightly reducing a strong topic's AP from 0.40 to 0.38, MAP may barely move, but GMAP can show improvement because the worst-performing topic improved proportionally.

This property is useful for robust retrieval evaluation. A RAG system that fails completely on a small class of questions may still have a reasonable MAP if many easier questions perform well. GMAP makes those low-performing topics harder to hide, although it also requires care with zero AP values because the product or log expression can collapse. Implementations often need an explicit small floor or documented handling for zero-valued topics.

## Applying these measures to RAG quality

The TREC measures are retrieval measures, not answer-quality measures. They evaluate whether the retriever ranks judged relevant documents well. In a RAG system, those metrics should be combined with generation checks such as groundedness, citation validity, no-answer behavior, and answer relevance.

Useful metric combinations include:

- recall@k to ask whether enough expected evidence reaches the context window;
- precision@k to ask whether the selected context is mostly useful;
- MRR or first relevant rank to ask how quickly the first useful evidence appears;
- AP or MAP to evaluate ranking quality over more of the result list;
- bpref when the relevance judgments are incomplete;
- GMAP or per-question diagnostics when robustness across difficult questions matters.

Metric interpretation should always name the cutoff, judgment assumptions, and averaging method. A statement such as "retrieval improved" is ambiguous. A reproducible statement is closer to "recall@5 increased on the golden set while precision@5 stayed flat, using expected relevant source labels as non-exhaustive judgments."
