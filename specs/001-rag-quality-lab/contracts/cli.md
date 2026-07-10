# CLI Contract: RAG Quality Lab

The CLI is the public interface for the MVP. Commands must support human-readable output by default and machine-readable JSON where noted.

## Global Behavior

- Commands return exit code `0` on success.
- Commands return non-zero exit codes for missing configuration, invalid corpus metadata, unavailable Qdrant, missing golden questions, unsupported retrieval modes, or failed citation validation when strict validation is requested.
- Errors must be written in a reviewer-readable form and include the failing stage.
- Commands that write artifacts must print the artifact path.

## `raglab corpus inspect`

Inspect the curated corpus manifest and local source snapshots.

**Options**

- `--json`: emit machine-readable corpus summary.

**Success Output**

- selected source count, with any corpus-size policy warning reported by inspection rather than manifest loading
- category counts
- license summary
- pinned version or commit
- local reference validation status

**Failure Cases**

- missing provenance or license metadata
- category outside the five allowed categories
- missing local source snapshot

## `raglab corpus ingest`

Validate, chunk, embed, and load the corpus into Qdrant.

**Options**

- `--collection <name>`: target Qdrant collection.
- `--recreate`: recreate the collection before ingestion.
- `--json`: emit machine-readable ingestion summary.

**Success Output**

- collection name
- source count
- chunk count
- category counts
- embedding model deployment label

**Failure Cases**

- invalid corpus manifest
- missing Azure OpenAI embedding configuration
- unavailable Qdrant
- chunk metadata validation failure

## `raglab query`

Run one question through the deterministic RAG workflow.

**Arguments**

- `QUESTION`: question text.

**Options**

- `--mode baseline-vector|routed-vector`
- `--top-k <n>`
- `--max-context-tokens <n>`
- `--output-token-limit <n>`
- `--trace-dir <path>`
- `--json`

**Success Output**

- answer or no-answer result
- citations
- route decision for routed mode or an explicit not-applicable value for baseline mode
- included and excluded chunk counts
- trace path

**Failure Cases**

- unsupported retrieval mode, including future-extension modes that are not part of the MVP runtime contract
- corpus not ingested
- missing generation configuration
- invalid citation output when strict mode is enabled

## `raglab trace inspect`

Inspect a persisted query trace.

**Arguments**

- `TRACE_PATH`: path to a machine-readable trace.

**Options**

- `--json`: emit the trace unchanged or normalized.

**Success Output**

- question
- route decision
- retrieval mode and ranked chunks
- context budget diagnostics
- citation validation result
- model usage when available

## `raglab eval run`

Run the golden question set for one retrieval mode.

**Options**

- `--mode baseline-vector|routed-vector`
- `--golden <path>`
- `--artifacts-dir <path>`
- `--top-k <n>`
- `--max-context-tokens <n>`
- `--output-token-limit <n>`
- `--json`

**Success Output**

- retrieval mode
- number of questions evaluated
- aggregate metrics
- raw counts alongside rate percentages where available
- benchmark-scope statement
- machine-readable artifact path
- Markdown report path

**Failure Cases**

- golden set outside 12-20 questions
- missing required case type
- unsupported retrieval mode, including future-extension modes that are not part of the MVP runtime contract
- one or more traces cannot be written

## `raglab eval compare`

Compare previously written evaluation artifacts.

**Arguments**

- one or more evaluation artifact paths.

**Options**

- `--markdown <path>`: write comparison table.
- `--json`: emit machine-readable comparison.

**Success Output**

- metric table by retrieval mode
- token-budget diagnostics by retrieval mode
- observed higher or lower value on the included benchmark per comparable metric
- benchmark-scope and interpretation notes
