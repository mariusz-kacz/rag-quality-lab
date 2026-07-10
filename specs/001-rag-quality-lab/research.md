# Phase 0 Research: RAG Quality Lab

## Decision: Use DAIR.AI Prompt Engineering Guide as the default corpus candidate

**Rationale**: The feature asks for one small, pinned, openly licensed LLM-engineering source and names DAIR.AI Prompt Engineering Guide as the preferred example. The repository is public and its GitHub page identifies an MIT license. Implementation must pin an exact commit and store local snapshots of only the selected 15-30 pages.

**Alternatives considered**: Multiple sources were rejected because the MVP requires one corpus source. Live website crawling was rejected because reproducibility requires pinned local references. A synthetic corpus was rejected because reviewer value depends on real source provenance.

### Corpus sufficiency assessment

DAIR.AI Prompt Engineering Guide is not sufficient by itself for the unmodified five-category taxonomy. It is still a good primary source for prompting techniques and a useful supporting source for RAG, security, and LLM settings, but it does not fully cover `RAG evaluation and quality` or `LLM settings, cost, and tokens` at the depth needed for balanced golden questions and retrieval comparisons.

To keep the existing category names, the corpus should become a curated multi-source corpus rather than a single-source DAIR.AI corpus. This changes the earlier MVP constraint of "exactly one corpus source" and requires follow-up updates to the manifest task and validation rules. Recommended source set:

- `prompting techniques`: introduction, basics, prompt elements, general tips, examples, and technique pages.
- `RAG and context handling`: DAIR.AI RAG pages plus OpenAI Cookbook RAG examples and Microsoft Generative AI for Beginners RAG/vector-database lesson.
- `RAG evaluation and quality`: OpenAI Cookbook evaluation examples plus Microsoft Generative AI for Beginners lifecycle/metrics lesson.
- `LLM security and risks`: OWASP Top 10 for LLM Applications plus DAIR.AI adversarial prompting pages.
- `LLM settings, cost, and tokens`: Google Gemini API token counting, billing, rate limit, context caching, and optimization documentation plus OpenAI Cookbook token/cost examples.

Quality judgment: DAIR.AI remains useful but should not be presented as fully covering the selected categories. A better portfolio corpus is 20-30 pinned local snapshots from 3-4 openly licensed/documented sources: DAIR.AI Prompt Engineering Guide, OpenAI Cookbook, OWASP Top 10 for LLM Applications, and either Google Gemini API docs or Microsoft Generative AI for Beginners. The manifest should prefer substantive explanatory pages and avoid thin navigation, course-marketing, translation duplicates, and model-specific news pages unless they directly support a golden question.

## Decision: Represent corpus provenance with a manifest plus local snapshots

**Rationale**: A manifest makes license, URL, source slug, category, pinned commit, and local reference auditable before ingestion. Local snapshots make repeated runs reproducible even if the upstream website changes.

**Alternatives considered**: Pulling pages at ingestion time was rejected because it weakens reproducibility. Embedding provenance only in vector metadata was rejected because reviewers need to inspect the corpus before ingestion.

## Decision: Use deterministic content-derived chunk identifiers

**Rationale**: Stable chunk IDs should survive repeated ingestion of the same pinned corpus. IDs will derive from source slug, section path, chunk ordinal, and content hash so traces and evaluation artifacts remain comparable.

**Alternatives considered**: Random UUIDs were rejected because they break trace comparability. Sequential global IDs alone were rejected because they can shift when a source page changes.

## Decision: Use embedding similarity over five category descriptions for routing

**Rationale**: The router must be deterministic, embedding-based, and non-LLM. Category description embeddings provide a small, inspectable decision surface. A confidence threshold enables filtered retrieval when the top score is strong enough; a category margin can include several nearby categories. Only a top score below the threshold falls back to global retrieval.

**Alternatives considered**: LLM classification was rejected by the spec. Keyword-only routing was rejected because ambiguous phrasing in the golden set should exercise semantic category matching.

## Decision: Implement retrieval modes behind one retrieval interface

**Rationale**: `baseline-vector` and `routed-vector` must produce comparable ranked retrieval results. A shared interface keeps evaluation metrics independent from mode-specific implementation while avoiding extra architecture for low-value optional modes.

**Alternatives considered**: Separate command paths per mode were rejected because that would make metrics and trace schemas harder to compare.

## Decision: Use Qdrant as the only runtime vector store

**Rationale**: The MVP explicitly requires Qdrant. Qdrant supports vector search plus payload/category filtering for routed retrieval, which matches the route-first comparison goal.

**Alternatives considered**: Chroma, FAISS, or in-memory vector search were rejected because the MVP excludes multiple vector stores and mandates Qdrant.

## Decision: Use Azure OpenAI for embeddings and LangChain-backed answer generation through environment configuration

**Rationale**: The spec mandates Azure OpenAI and environment-based configuration. Embeddings use a narrow local provider boundary because retrieval needs vectors directly. Answer generation uses LangChain's chat model and prompt-template boundary so the application avoids raw chat completion calls while core routing, context budgeting, trace, and evaluation logic remains plain Python.

**Alternatives considered**: Multiple providers and local models were rejected by MVP scope. Hard-coded configuration was rejected because reviewers need portable local setup.

## Decision: Keep context budgeting deterministic and estimate-first

**Rationale**: The context builder must include retrieved chunks in ranked order until the configured estimated token budget is reached, then record excluded chunks and reasons. Estimated tokens are sufficient for pre-generation budgeting; actual model usage is recorded when available.

**Alternatives considered**: Letting the model decide context relevance was rejected because budget decisions must be inspectable. Truncating chunks silently was rejected because traceability requires explicit inclusion and exclusion.

## Decision: Treat generated answers as untrusted until citation validation

**Rationale**: The lab should show practical RAG failure controls. Validation will prove every citation references a chunk included in selected context, and traces will record invalid, missing, or malformed citations.

**Alternatives considered**: Trusting model-formatted citations was rejected because it hides failure modes. Claim-level factual verification was rejected as out of MVP scope and will be documented as a limitation.

## Decision: Use a custom lightweight evaluation harness

**Rationale**: Required metrics are straightforward and domain-specific: routing accuracy, fallback count and rate, average searched categories, hit rate at k, MRR, citation source match, no-answer accuracy, average context tokens, and average included chunks. A custom harness makes the formulas inspectable for a portfolio reviewer.

**Alternatives considered**: RAGAS or similar large frameworks were rejected by scope. Manual notebook evaluation was rejected because the CLI must write reproducible artifacts.

## Decision: Define CLI and artifact contracts as the public interface

**Rationale**: The product is CLI-first. Reviewers need stable commands, exit behavior, JSON outputs, trace files, and Markdown reports. Contracts should cover commands and file schemas rather than HTTP APIs.

**Alternatives considered**: REST or web UI contracts were rejected because the MVP explicitly excludes production deployment, authentication, web UI, and chatbot experiences.
