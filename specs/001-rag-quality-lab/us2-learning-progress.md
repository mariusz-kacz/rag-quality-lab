# User Story 2 Learning Progress

Goal: implement User Story 2 in a learning-first way, using AI as a reviewer/tutor rather than the primary coder.

## Progress

| Status | Step | Module | Python Focus | RAG/System Focus |
|--------|---:|---|---|---|
| [X]    | 1 | `src/rag_quality_lab/retrieval/modes.py` | literals, validation, small exception types | supported retrieval mode contract |
| [X]    | 2 | `src/rag_quality_lab/rag/context.py` | pure functions, sorting, immutable Pydantic models, list transformations | token budgeting and context inclusion/exclusion |
| [X]    | 3 | `src/rag_quality_lab/rag/citations.py` | regex, parsing edge cases, validation result modeling | citation extraction and selected-context validation |
| [X]    | 4 | `src/rag_quality_lab/routing/embedding_router.py` | dependency injection, vector math, protocol-by-convention style | deterministic category routing |
| [X]    | 5 | `src/rag_quality_lab/retrieval/qdrant_store.py` | adapter pattern around SDKs, payload normalization | baseline and routed vector search |
| [X]    | 6 | `src/rag_quality_lab/rag/generation.py` | provider abstraction, prompt construction, simple orchestration | grounded answer and no-answer generation |
| [X]    | 7 | `src/rag_quality_lab/rag/traces.py` | `pathlib.Path`, JSON persistence, Pydantic serialization/deserialization | trace persistence and loading |
| [ ]    | 8 | `src/rag_quality_lab/rag/pipeline.py` | composition, dependency injection, error boundaries | full query flow: route -> retrieve -> context -> generate -> validate -> trace |
| [ ]    | 9 | `src/rag_quality_lab/cli.py` | Typer commands, JSON/human output split | reviewer-facing `query` and `trace inspect` workflows |

## Suggested Workflow

1. Read the failing tests for the current step.
2. Write down the API the tests imply before coding.
3. Implement the smallest useful version yourself.
4. Run the focused tests for that step.
5. Use AI for explanation, review, or minimal fix suggestions after you have a first pass.
6. Mark the row complete when the focused tests pass and the code feels understandable.

## AI Usage Rule

Prefer prompts such as:

- "Explain what this failing test implies the API should be."
- "Review my implementation for Python idioms."
- "What would be the C# equivalent of this pattern?"
- "Is this Pythonic, or am I writing C# in Python syntax?"

Avoid asking AI to generate whole files before you have attempted the first pass.

## Time Expectation

| Mode | Estimate |
|---|---:|
| Learning-first with AI as coach/reviewer | 3-4 days |
| Balanced learning and delivery | 2-3 days |
| AI-heavy implementation | 1-2 days |

## Python Concepts To Watch

- Duck typing and protocols instead of explicit interfaces everywhere.
- Small modules and functions over class-heavy service layers.
- Pydantic models as schema/contracts, not business objects.
- Exceptions and validation style.
- `pathlib.Path`, JSON serialization, and pytest fixtures.
- Dependency injection by passing objects/functions directly, without a container.
