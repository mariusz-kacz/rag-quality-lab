# Source snapshot

Source metadata:
- source_slug: openai-api-prompt-engineering
- category: prompting techniques
- upstream_url: https://developers.openai.com/api/docs/guides/prompt-engineering
- source_page: https://developers.openai.com/api/docs/guides/prompt-engineering
- license: OpenAI API docs reuse terms pending snapshot verification
- pinned_version: openai-api-docs@current-snapshot
- snapshot_captured: 2026-07-10
- snapshot_type: normalized documentation digest from OpenAI API documentation page
- normalization: removed site navigation, duplicated SDK examples, long generated examples, and page chrome; retained message-role guidance, prompt organization, code-managed prompt versioning, Markdown/XML formatting, few-shot examples, context-window planning, GPT-series prompt pointers, prompt caching layout guidance, and testing/evaluation implications

---
# Message roles and instruction hierarchy

The OpenAI prompt engineering guide frames prompting as the process of writing instructions that reliably shape model output. The guide emphasizes that prompting is empirical: model outputs are non-deterministic, different model families may respond to different prompting patterns, and production teams should test prompt behavior as prompts or model versions change.

## Messages as application contracts

The guide distinguishes developer instructions from user input. Developer messages and the `instructions` parameter carry application rules, business logic, and behavior constraints. User messages carry the task-specific input to which those rules are applied.

For a RAG system, this authority split is important:

- citation rules, no-answer policy, source-use constraints, and output schema belong in developer-level instructions;
- the user question belongs in user input;
- retrieved passages should be clearly labeled as evidence, not as instructions;
- application code should not let retrieved text override developer rules.

Useful prompt layout:

```text
Developer instructions
- Answer only from selected context.
- Cite source ids for claims.
- If the evidence is insufficient, say so.

User input
Question: ...

Context
<source id="...">...</source>
```

The retrieved context is data. The developer instruction defines how the model may use that data.

## Prompt sections

The guide recommends using clear sections when prompts contain several kinds of information. Markdown headings and lists can show prompt hierarchy; XML tags can isolate examples, documents, or records and attach metadata.

Common sections include:

- identity or role;
- instructions;
- examples;
- context;
- final task or user query.

This structure makes prompts easier to review and test. It also gives the model clearer boundaries between durable rules, demonstration examples, supporting data, and the current task.

Compact example:

```text
# Identity
You answer questions from selected documentation.

# Instructions
- Use only the provided context.
- Cite document ids.
- Return the configured no-answer sentence when evidence is missing.

# Context
<doc id="A">Average precision rewards relevant results ranked early.</doc>

# Task
Which metric rewards relevant results ranked early?
```

## Examples and few-shot behavior

Few-shot examples can teach a task pattern without fine-tuning. They are most useful when the desired output is easier to show than describe, such as classification labels, tone, short extraction objects, or citation format.

Good examples should:

- cover a diverse range of expected inputs;
- include edge cases and negative cases, not only ideal cases;
- match the final output format exactly;
- avoid implying rules that contradict written instructions.

Examples should usually live in developer-level instructions so they define application behavior rather than becoming user-provided data. In RAG workflows, examples can demonstrate citation style and no-answer behavior before the dynamic question and retrieved context.

## Context window planning

The guide connects prompt engineering to context management. Adding extra context can give the model access to proprietary or selected data and is one way to implement retrieval-augmented generation. The same context window has to hold instructions, examples, user input, retrieved text, tool definitions, and room for the model's answer.

Practical RAG implications:

- reserve space for the answer and citations before adding retrieved passages;
- trim or rank context instead of passing every related chunk;
- keep delimiters and source identifiers compact but unambiguous;
- decide whether the model may use outside knowledge or only supplied context;
- test long-context behavior because more text can add distraction as well as evidence.

Prompt design and context budgeting should be evaluated together. A prompt with perfect instructions can still fail if the needed evidence is excluded, buried, mislabeled, or crowded out by noisy context.

# Prompt testing, model snapshots, and output control

The guide recommends treating prompts as application code. Prompts should be versioned, reviewed, tested, and deployed through the normal engineering process.

## Prompt behavior changes across models

Prompt behavior is model-specific. A prompt that works for one model family or snapshot may need adjustment after a model upgrade. The guide recommends pinning production applications to specific model snapshots when stable behavior matters and using tests or evaluation suites to monitor changes.

For this project, a prompt or model change should be recorded alongside:

- retrieval mode;
- prompt template version;
- model deployment or snapshot;
- selected context and token budget;
- answer text and citations;
- no-answer and citation-validation results.

That trace makes it possible to separate retrieval regressions from prompt or model-behavior regressions.

## Version prompts in code

The guide recommends storing production prompts in application code instead of relying on reusable prompt objects. Code-managed prompts support typed inputs, code review, tests, feature flags, and normal deployment review.

A maintainable prompt builder should:

- accept typed arguments for dynamic values;
- keep durable instructions near the feature they support;
- produce `instructions` and `input` directly for the Responses API;
- make prompt template changes visible in code review;
- include fixtures and evaluation cases for important behavior.

For a RAG lab, this means the prompt that enforces context-only answering and citation syntax should be a versioned artifact, not an invisible dashboard setting.

## Formatting and output control

Markdown and XML are useful for prompt readability and model comprehension. Markdown headings and lists establish section hierarchy. XML tags can mark where supporting documents, examples, or user-provided records begin and end.

Structured outputs remain a separate reliability mechanism when downstream code requires a strict JSON contract. Prompt engineering can request a format, but schemas and validators should enforce machine-readable response shape when the output drives code, tools, or evaluation.

Output-control checklist:

- define the expected answer shape;
- state whether Markdown is allowed or required;
- define citation syntax;
- define the no-answer response;
- use structured outputs for typed machine contracts;
- validate returned data before execution or scoring.

## Cost and caching implications

Prompt layout also affects cost and latency. Stable instructions, schemas, and examples should be placed early when they are reused across requests, while dynamic user input and retrieved context should appear later. That arrangement is friendlier to provider-side prompt caching and easier to trim when context budgets are tight.

For repeated RAG evaluations:

- keep stable developer instructions stable;
- avoid volatile IDs or timestamps near the prompt prefix;
- put retrieved chunks after stable instructions and schemas;
- record prompt-token and cached-token usage when available.

Prompt engineering is therefore not only about answer quality. It also affects reproducibility, latency, cost, cacheability, and the ability to audit RAG behavior.
