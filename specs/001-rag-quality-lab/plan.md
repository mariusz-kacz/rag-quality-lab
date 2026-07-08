# Implementation Plan: RAG Quality Lab

**Branch**: `[001-rag-quality-lab]` | **Date**: 2026-07-02 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-rag-quality-lab/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Build a CLI-first RAG quality engineering lab over a small pinned LLM-engineering corpus. The MVP will make corpus provenance, deterministic category routing, Qdrant-backed retrieval, bounded context selection, cited answer generation, citation validation, no-answer behavior, trace persistence, and lightweight golden-set evaluation explicit and reproducible. Core orchestration remains plain Python; integrations are limited to the required embedding, generation, and vector-store boundaries.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: Typer for CLI commands; Pydantic for validated schemas; qdrant-client for vector-store access; openai Azure client for embeddings; LangChain/langchain-openai for chat model invocation and prompt templates; tiktoken for token estimates; pytest for tests. Core routing, retrieval orchestration, context budgeting, citation validation, trace persistence, and evaluation remain plain Python application logic.

**Storage**: Qdrant for vector chunks; repository files for pinned corpus manifests, local source snapshots, golden questions, traces, evaluation artifacts, and README sample outputs.

**Testing**: pytest unit tests for routing, chunk metadata validation, context budgeting, citation validation, no-answer handling, and metrics; integration tests for CLI workflows and Qdrant-backed ingestion/retrieval; contract tests for CLI outputs and artifact schemas.

**Target Platform**: Local developer workstation, with Windows PowerShell support as first-class because this repository is being authored on Windows; commands should also be portable to Unix shells where practical.

**Project Type**: Single Python CLI application and supporting library modules.

**Performance Goals**: Corpus inspection completes in under 5 seconds for the curated corpus; ingestion completes in under 5 minutes for 15-30 source pages; single-query traces complete in under 60 seconds excluding external service latency spikes; golden-set evaluation over 12-15 cases completes in under 20 minutes.

**Constraints**: CLI-first only; no web UI or chatbot session state; exactly one corpus source for MVP; exactly five knowledge categories; Qdrant is mandatory; Azure OpenAI is the only model provider; deterministic non-LLM routing; bounded context builder must never exceed configured estimated context budget; every answer is invalid until citation validation completes.

**Scale/Scope**: 15-30 source pages, expected tens to low hundreds of chunks, 12-15 golden questions, and two retrieval mode labels: `baseline-vector` and `routed-vector`.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The repository constitution is still the stock placeholder template and defines no active project principles, gates, or governance rules. No constitution violations are present.

Post-design re-check: PASS. The design remains CLI-first, bounded to the MVP scope, and no active constitution rule is violated.

## Project Structure

### Documentation (this feature)

```text
specs/001-rag-quality-lab/
|-- plan.md              # This file (/speckit-plan command output)
|-- research.md          # Phase 0 output (/speckit-plan command)
|-- data-model.md        # Phase 1 output (/speckit-plan command)
|-- quickstart.md        # Phase 1 output (/speckit-plan command)
|-- contracts/           # Phase 1 output (/speckit-plan command)
`-- tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
src/
`-- rag_quality_lab/
    |-- __init__.py
    |-- cli.py
    |-- config.py
    |-- corpus/
    |   |-- inspect.py
    |   |-- ingest.py
    |   |-- manifest.py
    |   `-- chunking.py
    |-- routing/
    |   |-- categories.py
    |   `-- embedding_router.py
    |-- retrieval/
    |   |-- modes.py
    |   `-- qdrant_store.py
    |-- rag/
    |   |-- pipeline.py
    |   |-- context.py
    |   |-- generation.py
    |   |-- citations.py
    |   `-- traces.py
    |-- eval/
    |   |-- golden.py
    |   |-- metrics.py
    |   `-- reports.py
    `-- schemas/
        |-- artifacts.py
        |-- base.py
        |-- categories.py
        |-- corpus.py
        |-- eval.py
        |-- query.py
        |-- retrieval.py
        `-- trace.py              # compatibility import for QueryTrace

corpus/
|-- manifest.json
|-- categories.json
`-- sources/

golden/
`-- questions.json

artifacts/
|-- traces/
`-- eval/

tests/
|-- contract/
|-- integration/
`-- unit/
```

**Structure Decision**: Use a single Python package with CLI entrypoint and plain-Python domain modules. Keep durable portfolio inputs (`corpus/`, `golden/`) and generated outputs (`artifacts/`) outside package code so reviewers can inspect provenance, traces, and evaluation results directly.

## Complexity Tracking

No constitution violations require complexity tracking.
