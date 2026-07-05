# Corpus Generation Plan for T021

## Purpose

T021 covers pinned local source snapshots for every manifest entry under `corpus/sources/`. This plan splits that work into independent document-level units so each source can be generated, reviewed, corrected, and accepted without blocking unrelated sources.

The goal is not to create loose summaries. Each local source file should be a credible normalized source snapshot or documentation digest that remains close to the original source while making it useful for this project's RAG quality corpus.

## Scope

For each manifest source with an upstream source document:

1. Create or update the local Markdown file at the manifest `local_ref`.
2. Preserve source metadata at the top of the file.
3. Normalize the content into the manifest's declared top-level sections.
4. Keep the document similar to the original source in substance, terminology, examples, and constraints.
5. Remove source-specific noise that hurts retrieval quality, such as page chrome, notebook execution output, classroom scaffolding, placeholder omissions, and broken/truncated examples.
6. Review the generated file against the quality checklist below.
7. Apply corrections raised during review before marking the source complete.

## Source File Template

Each generated file should use this shape unless the source already requires a stronger local convention:

```markdown
# Source snapshot

Source metadata:
- source_slug: <manifest source_slug>
- category: <manifest category>
- upstream_url: <manifest url>
- source_markdown/source_notebook/source_pdf/source_page: <specific source reference when available>
- license: <manifest license>
- pinned_version: <manifest pinned_version>
- snapshot_type: normalized documentation digest from <source type>
- normalization: <short description of what was removed and retained>

---
# <manifest section 1 heading>

...

# <manifest section 2 heading>

...
```

The top-level content headings after the metadata block should match `corpus/manifest.json` section headings exactly.

## Generation Workflow

For each source:

1. Read the manifest entry and identify expected section headings, upstream URL, pinned version, license, and local file path.
2. Retrieve or inspect the pinned source material when available locally or through an allowed source.
3. Build a normalized Markdown snapshot that preserves the source's substantive guidance.
4. Keep compact examples that improve retrieval and remove long examples only when they are too noisy; replace omissions with prose summaries rather than placeholder text.
5. Ensure examples are complete and not syntactically broken.
6. Avoid introducing headings inside fenced examples that a simple Markdown chunker could mistake for document sections.
7. Run the review checklist.
8. Correct all material review findings.
9. Mark the source complete in this plan and in `specs/001-rag-quality-lab/tasks.md`.

## Review Checklist

A source is complete only when all checks pass:

- Metadata matches the manifest: `source_slug`, category, URL, license, pinned version, and local path.
- The document's top-level content headings match the manifest section headings.
- Content is close enough to the original source to be credible and attributable.
- The text is useful for this project's corpus categories and likely RAG questions.
- Notebook/course/page scaffolding is removed unless it is genuinely useful content.
- No placeholder strings remain, such as `omitted`, `TODO`, or `TBD`, except when discussing those words as source content.
- Long examples are summarized or compacted without losing key technical guidance.
- Code or JSON examples are complete enough not to teach broken patterns.
- Links are preserved when they materially identify upstream concepts or provenance.
- The file is readable as standalone documentation for the source topic.

## Status

| T021 subtask | Status | Source slug | Local file | Manifest sections | Review status |
| --- | --- | --- | --- | --- | --- |
| T021.01 | Completed | `azure-openai-prompt-engineering-techniques` | `corpus/sources/azure-openai-prompt-engineering-techniques.md` | Prompt components and instruction design; Examples, separators, decomposition, and grounding cautions | Existing normalized source accepted as one of the first five completed files. |
| T021.02 | Completed | `microsoft-advanced-prompts` | `corpus/sources/microsoft-advanced-prompts.md` | Advanced prompt patterns; Iterative prompting methods and tradeoffs | Rewritten, reviewed, and corrected for corpus quality. |
| T021.03 | Completed | `openai-gpt41-prompting-guide` | `corpus/sources/openai-gpt41-prompting-guide.md` | Instruction following and agentic workflows; Long context guidance and prompt migration | Rewritten, reviewed, and corrected for corpus quality. |
| T021.04 | Completed | `openai-o-series-prompting-guide` | `corpus/sources/openai-o-series-prompting-guide.md` | Reasoning model instruction design; Concise instructions versus detailed constraints | Rewritten, reviewed, and corrected for corpus quality. |
| T021.05 | Completed | `azure-openai-structured-outputs` | `corpus/sources/azure-openai-structured-outputs.md` | Schema constrained outputs; Constraints, model support, and compact examples | Rewritten, reviewed, and corrected for corpus quality. |
| T021.06 | Completed | `azure-ai-search-rag-overview` | `corpus/sources/azure-ai-search-rag-overview.md` | RAG architecture and query understanding; Token constraints, security trimming, and retrieval patterns | Generated, reviewed, and corrected for corpus quality. |
| T021.07 | Completed | `openai-embedding-wikipedia-search` | `corpus/sources/openai-embedding-wikipedia-search.md` | Document collection and cleaning; Token-budget chunking, embedding, and storage | Generated, reviewed, and corrected for corpus quality. |
| T021.08 | Completed | `openai-question-answering-embeddings` | `corpus/sources/openai-question-answering-embeddings.md` | Search-Ask retrieval workflow; Context assembly, answer grounding, and no-answer behavior | Generated, reviewed, and corrected for corpus quality. |
| T021.09 | Completed | `azure-ai-search-vector-relevance-ranking` | `corpus/sources/azure-ai-search-vector-relevance-ranking.md` | KNN, ANN, and similarity metrics; Score interpretation, k selection, chunk tuning, and hybrid ranking | Generated, reviewed, and corrected for corpus quality. |
| T021.10 | Completed | `openai-file-search-responses` | `corpus/sources/openai-file-search-responses.md` | Managed file-search workflow; Vector-store retrieval and context delivery | Generated, reviewed, and corrected for corpus quality. |
| T021.11 | Completed | `microsoft-foundry-rag-evaluators` | `corpus/sources/microsoft-foundry-rag-evaluators.md` | Process and system evaluation taxonomy; Retrieval quality, groundedness, relevance, and thresholds | Generated, reviewed, and corrected for corpus quality. |
| T021.12 | Completed | `openai-evaluation-flywheel` | `corpus/sources/openai-evaluation-flywheel.md` | Failure-mode discovery and annotation; Automatic graders, prompt improvement, and test expansion | Generated, reviewed, and corrected for corpus quality. |
| T021.13 | Completed | `trec-common-evaluation-measures` | `corpus/sources/trec-common-evaluation-measures.md` | Recall, precision, and ranked-list evaluation; Average precision, R-precision, bpref, and GMAP | Generated, reviewed, and corrected for corpus quality. |
| T021.14 | Completed | `wikipedia-ir-evaluation-measures` | `corpus/sources/wikipedia-ir-evaluation-measures.md` | Precision, recall, F-score, and precision at k; MAP, DCG, nDCG, MRR, hit rate, and metric caveats | Generated, reviewed, and corrected for corpus quality. |
| T021.15 | Completed | `huggingface-evaluate-choosing-metric` | `corpus/sources/huggingface-evaluate-choosing-metric.md` | Generic, task-specific, and dataset-specific metrics; Selecting retrieval, answer, benchmark, and custom checks | Generated, reviewed, and corrected for corpus quality. |
| T021.16 | Completed | `huggingface-evaluate-considerations` | `corpus/sources/huggingface-evaluate-considerations.md` | Evaluation splits, imbalance, and metric combinations; Offline evaluation, interpretability, resource tradeoffs, and limitations | Generated, reviewed, and corrected for corpus quality. |
| T021.17 | Completed | `owasp-llm01-prompt-injection` | `corpus/sources/owasp-llm01-prompt-injection.md` | Prompt injection risks; Examples, scenarios, and mitigations | Generated, reviewed, and corrected for corpus quality. |
| T021.18 | Completed | `owasp-llm02-sensitive-information-disclosure` | `corpus/sources/owasp-llm02-sensitive-information-disclosure.md` | Sensitive information disclosure risks; Data leakage scenarios and mitigations | Generated, reviewed, and corrected for corpus quality. |
| T021.19 | Completed | `owasp-llm06-excessive-agency` | `corpus/sources/owasp-llm06-excessive-agency.md` | Tool-use and excessive agency risks; Permission boundaries and mitigations | Generated, reviewed, and corrected for corpus quality. |
| T021.20 | Completed | `owasp-llm08-vector-embedding-weaknesses` | `corpus/sources/owasp-llm08-vector-embedding-weaknesses.md` | Vector and embedding weaknesses; Retrieval-specific risks and mitigations | Generated, reviewed, and corrected for corpus quality. |
| T021.21 | Completed | `nist-generative-ai-risk-profile` | `corpus/sources/nist-generative-ai-risk-profile.md` | Generative AI risk taxonomy; Risk-management actions for LLM and RAG systems | Generated, reviewed, and corrected for corpus quality. |
| T021.22 | Completed | `openai-text-generation` | `corpus/sources/openai-text-generation.md` | Request shape and message roles; Instruction guidance and context-management implications | Generated, reviewed, and corrected for corpus quality. |
| T021.23 | Completed | `openai-token-counting` | `corpus/sources/openai-token-counting.md` | Token counting concepts; Prompt budgeting and model-specific token accounting | Generated, reviewed, and corrected for corpus quality. |
| T021.24 | Completed | `openai-latency-optimization` | `corpus/sources/openai-latency-optimization.md` | Latency and efficiency principles; Token reduction, fewer requests, streaming, and RAG trimming | Generated, reviewed, and corrected for corpus quality. |
| T021.25 | Completed | `openai-handle-rate-limits` | `corpus/sources/openai-handle-rate-limits.md` | Rate-limit causes and backoff strategies; RPM, TPM, fallback models, max tokens, and throughput | Generated, reviewed, and corrected for corpus quality. |
| T021.26 | Completed | `openai-prompt-caching` | `corpus/sources/openai-prompt-caching.md` | Prompt caching mechanics; Static and dynamic prompt layout, cache keys, and usage observability | Generated, reviewed, and corrected for corpus quality. |
| T021.27 | Completed | `owasp-llm04-data-model-poisoning` | `corpus/sources/owasp-llm04-data-model-poisoning.md` | Data and model poisoning risks; Lifecycle, scenarios, and mitigation controls | Added as sixth security source, generated, reviewed, and corrected for corpus quality. |

## Completion Rule

T021 is complete when every source above is marked `Completed`, every corresponding file exists under `corpus/sources/`, and each file has passed the review checklist after any corrections.
