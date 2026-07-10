# Data Model: RAG Quality Lab

## SourcePage

Represents one selected page from the pinned corpus source.

**Fields**

- `source_slug`: stable unique slug within the corpus.
- `title`: human-readable source page title.
- `category`: one of the five required knowledge categories.
- `url`: canonical upstream URL.
- `license`: license identifier and attribution text.
- `pinned_version`: pinned upstream commit, tag, or version reference.
- `local_ref`: repository-relative path to the local source snapshot.
- `sections`: ordered source sections available for chunking.

**Validation Rules**

- `source_slug`, `category`, `url`, `license`, `pinned_version`, and `local_ref` are required.
- `category` must match exactly one known category.
- The MVP corpus target is 15-30 `SourcePage` records for manual reviewability and bounded local evaluation, but manifest loading must not fail solely because the count is outside that range.
- `local_ref` must resolve to a local readable file before ingestion.

## KnowledgeCategory

Represents one deterministic routing category.

**Fields**

- `name`: category name.
- `description`: text used to create the category description embedding.
- `embedding_ref`: reference to the stored category embedding or embedding cache key.

**Validation Rules**

- Exactly five categories must exist.
- Names must be exactly: `prompting techniques`, `RAG and context handling`, `RAG evaluation and quality`, `LLM security and risks`, `LLM settings, cost, and tokens`.
- Each category must have a non-empty description before routing can run.

## Chunk

Represents one stable retrievable text unit.

**Fields**

- `chunk_id`: stable chunk identifier.
- `source_slug`: parent source page slug.
- `category`: inherited knowledge category.
- `section_path`: ordered section headings or section metadata.
- `ordinal`: position within the source page or section.
- `content`: chunk text.
- `content_hash`: hash of normalized chunk content.
- `estimated_tokens`: estimated token count.
- `provenance`: source URL, license, pinned version, and local reference.

**Validation Rules**

- `chunk_id`, `source_slug`, `category`, `section_path`, `content_hash`, `estimated_tokens`, and `provenance` are required.
- `estimated_tokens` must be positive.
- `content_hash` must match normalized `content`.
- `chunk_id` must be stable for unchanged pinned source content.

## Question

Represents a user query or golden-set case.

**Fields**

- `question_id`: stable, required identifier for golden-set cases; optional for ad hoc queries.
- `text`: question text.
- `expected_category`: expected category for routing accuracy when applicable.
- `expected_relevant_sources`: source slugs or chunk IDs expected for retrieval metrics.
- `answerability`: `answerable` or `no_answer`.
- `case_type`: `answerable`, `no_answer`, `ambiguous_boundary`, or `fallback_routing`.

**Validation Rules**

- Golden set must contain 12-20 questions with unique, non-empty `question_id` values.
- Golden set must include all required case types.
- Answerable cases must include at least one expected relevant source or chunk.
- No-answer cases must define `answerability` as `no_answer`.

## RouteDecision

Represents deterministic routing output.

This record is present only for `routed-vector`. Baseline traces use `null` because global retrieval bypasses category routing.

**Fields**

- `selected_category`: category selected for routed retrieval, if any.
- `fallback_all_categories`: true when confidence is insufficient.
- `confidence`: top category confidence score.
- `threshold`: configured confidence threshold.
- `category_scores`: scores for all five categories.

**Validation Rules**

- `category_scores` must include all five categories.
- If `fallback_all_categories` is true, `selected_category` must be empty.
- If `fallback_all_categories` is false, `selected_category` must be one known category.

## RetrievalResult

Represents one ranked retrieved chunk.

**Fields**

- `mode`: retrieval mode label.
- `rank`: one-based rank.
- `chunk_id`: retrieved chunk identifier.
- `source_slug`: parent source slug.
- `category`: chunk category.
- `section_path`: ordered section headings or section metadata needed for downstream context selection.
- `score`: mode-specific retrieval score.

**Validation Rules**

- `mode` must be `baseline-vector` or `routed-vector`.
- Ranks must be unique and ordered within a query result.
- Routed vector results must match the selected category unless route fallback is active.

## SelectedContext

Represents the bounded context selected for answer generation.

**Fields**

- `max_context_tokens`: configured context budget.
- `output_token_limit`: configured generation limit.
- `included_chunks`: ordered chunks included in context.
- `excluded_chunks`: ordered chunks excluded from context.
- `final_estimated_context_tokens`: sum of included chunk estimates plus prompt overhead estimate.

**Validation Rules**

- Included chunks must preserve retrieval rank order.
- `final_estimated_context_tokens` must not exceed `max_context_tokens`.
- Every excluded chunk must include an exclusion reason, such as `budget_exceeded`.

## AnswerResult

Represents the generated answer or no-answer output.

**Fields**

- `answer_text`: generated response text or no-answer explanation.
- `is_no_answer`: true when evidence is insufficient.
- `citations`: cited chunk IDs.
- `validation_status`: `valid`, `invalid`, or `not_applicable`.
- `validation_errors`: citation validation failures.

**Validation Rules**

- Cited chunk IDs must exist in selected context.
- Missing, malformed, or out-of-context citations make the answer invalid.
- No-answer outputs may have no citations but must still be traceable to retrieval evidence.

## QueryTrace

Represents the persisted record of one full query workflow.

**Fields**

- `trace_id`: stable or timestamped trace identifier.
- `question`: question text and optional question ID.
- `route_decision`: `RouteDecision` for routed retrieval; `null` for baseline retrieval.
- `retrieval_results`: ranked `RetrievalResult` records.
- `context_build`: `SelectedContext`.
- `answer_result`: `AnswerResult`.
- `model_usage`: actual token usage when available.
- `created_at`: trace creation timestamp.

**Validation Rules**

- Query traces must include every applicable deterministic pipeline stage and explicitly serialize non-applicable routing as `null`.
- Evaluation traces must retain the originating golden `question_id`; result sets are matched and validated by ID before metrics are calculated.
- Model usage may be absent only when the LangChain chat model does not return usage metadata.
- Trace files must be machine-readable.

## EvaluationRun

Represents a golden-set evaluation for one retrieval mode.

**Fields**

- `run_id`: evaluation run identifier.
- `mode`: retrieval mode under evaluation.
- `questions`: per-question outcomes and trace references.
- `metrics`: aggregate metric values.
- `artifact_paths`: machine-readable and Markdown artifact paths.
- `created_at`: evaluation timestamp.

**Validation Rules**

- Each evaluation run covers one retrieval mode.
- Required metrics must be present for implemented modes.
- Every per-question outcome must reference a persisted query trace.

## State Transitions

**Corpus**

`not_inspected` -> `validated` -> `ingested` -> `queryable`

**Query**

`received` -> `routed` -> `retrieved` -> `context_built` -> `generated` -> `citations_validated` -> `trace_persisted`

**Evaluation**

`configured` -> `running` -> `traces_written` -> `metrics_computed` -> `artifacts_written`
