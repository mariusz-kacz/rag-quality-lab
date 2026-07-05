# Source snapshot

Source metadata:
- source_slug: openai-gpt41-prompting-guide
- category: prompting techniques
- upstream_url: https://github.com/openai/openai-cookbook/blob/8730772/examples/gpt4-1_prompting_guide.ipynb
- source_notebook: https://github.com/openai/openai-cookbook/blob/8730772/examples/gpt4-1_prompting_guide.ipynb
- license: MIT
- pinned_version: openai-cookbook@8730772
- snapshot_type: normalized documentation digest from notebook markdown cells
- normalization: extracted reusable guidance from markdown cells; removed raw notebook JSON, execution outputs, long sample prompts, appendix implementation details, and notebook-specific instructions; retained agentic workflow guidance, tool-use guidance, instruction-following advice, long-context guidance, delimiters, caveats, and compact examples

---
# Instruction following and agentic workflows

GPT-4.1 is described as more literal and more steerable than earlier GPT-4o-era models. Prompts that relied on implicit intent may need migration because the model follows written instructions closely. When behavior is not what the application expects, add a direct clarifying rule rather than assuming the model will infer it.

The practical workflow is:

1. State the role and objective.
2. Add high-level response rules.
3. Add detailed rules only where behavior needs tighter control.
4. Provide examples when the desired behavior is easier to show than describe.
5. Evaluate prompts against representative and adversarial cases.

## Agentic reminders

For agentic workflows, the source guide highlights three kinds of reminders that can improve persistence and tool use.

Persistence reminder:

```text
Keep working until the user's request is fully resolved.
Only stop when the task is complete or when required information is missing.
```

Tool-use reminder:

```text
If the answer depends on files, tools, or current workspace state, inspect those sources before answering.
Do not guess about unavailable state.
```

Planning reminder:

```text
Before taking major actions, briefly state the next step and why it is needed.
After tool results, update the plan if the evidence changes.
```

Use planning reminders when intermediate reasoning is useful for the task or for auditability. For simple tasks, extra planning can add unnecessary tokens and latency.

## Tool calls

The guide recommends passing tools through the API's structured `tools` field rather than manually describing tools inside the prompt and building a custom parser. Native tool definitions keep the model closer to its expected tool-calling format and reduce parsing errors.

Good tool definitions should include:

- a clear tool name;
- a concise description of when the tool should be used;
- parameter names that reflect domain meaning;
- parameter descriptions for ambiguous values;
- examples in the prompt only when the tool behavior is hard to infer from the schema.

If a tool is complicated, keep the tool description focused and put larger examples in an `Examples` section of the developer or system prompt. Tool descriptions should remain durable interface contracts, not long tutorials.

## Prompt-induced planning

GPT-4.1 is not a reasoning model in the same sense as o-series models, so prompts can ask it to produce visible planning or decomposition when that helps the task. This can be useful for agents, retrieval planning, document selection, and complex coding tasks.

Use visible planning when:

- the task spans several tool calls;
- the model must select relevant documents before answering;
- the user benefits from seeing the strategy;
- the plan can be checked against tool results.

Avoid exposing long reasoning by default. Prefer concise, task-relevant planning artifacts such as selected document IDs, subtask lists, assumptions, or verification steps.

Example retrieval planning instruction:

```text
First identify which provided documents are needed to answer the query.
Return the selected document titles and IDs.
Then answer using only those selected documents.
```

## Instruction-following workflow

GPT-4.1 is sensitive to exact instructions and prompt ordering. The guide recommends building prompts with clear sections and resolving conflicts explicitly.

Recommended workflow:

1. Start with a short `Instructions` or `Response Rules` section.
2. Add subsections for specialized behavior, such as tone, tool use, refusals, or output format.
3. Use ordered steps when the model should follow a fixed workflow.
4. If behavior fails, check for conflicts, missing constraints, and examples that imply a different rule.
5. Add examples that demonstrate the intended behavior, and make sure written rules cover what the examples show.

Common failure modes:

- A broad rule such as `always call a tool` can cause unnecessary or invalid tool calls.
- Sample phrases can be copied too literally and make responses repetitive.
- Missing output-format rules can lead to extra prose, extra formatting, or omitted fields.
- Conflicting rules may be resolved based on recency or salience rather than developer intent.

Example mitigation for over-eager tool use:

```text
Call a tool only when the required input values are available.
If required values are missing, ask one concise clarification question instead of guessing tool arguments.
```

## General prompt structure

A reusable prompt structure from the guide:

```text
Role and Objective

Instructions

Detailed Rules

Reasoning or Workflow Steps

Output Format

Examples

Context

Final Task
```

This structure should be adapted to the task. Short tasks may need only role, instructions, context, and output format.

## Delimiters and examples

The guide recommends Markdown as a strong default delimiter format. Markdown headings, bullets, numbered lists, inline code, and fenced blocks are easy to read and generally easy for models to follow.

XML can be useful when the prompt contains many nested records or examples:

```xml
<examples>
  <example type="abbreviation">
    <input>San Francisco</input>
    <output>SF</output>
  </example>
</examples>
```

For large sets of documents, XML-style records or compact pipe-delimited records can be more efficient and easier to distinguish than verbose JSON.

```text
ID: 1 | TITLE: Refund Policy | CONTENT: Refunds are available within 30 days.
```

JSON is useful when the task is code-oriented or when the model must produce structured data, but it can add escaping and token overhead in long prompts.

# Long context guidance and prompt migration

GPT-4.1 supports very long input contexts and can be useful for document parsing, re-ranking, retrieval selection, structured extraction, and multi-hop tasks. Long context does not remove the need for prompt design. Performance can degrade when the task requires finding many scattered items, reasoning over global state, or separating relevant from irrelevant material.

## Context reliance

A long-context prompt should clearly state whether the model may use outside knowledge or must rely only on supplied context.

Strict context-only instruction:

```text
Use only the provided context to answer.
If the context does not contain the answer, respond: "I don't have the information needed to answer that."
```

Hybrid context instruction:

```text
Use the provided context as the primary source.
You may use basic background knowledge only to connect concepts, not to introduce unsupported facts.
```

This distinction matters for RAG systems. A context-only rule improves grounding and no-answer behavior. A hybrid rule can improve helpfulness when the context is incomplete but increases the risk of unsupported claims.

## Prompt organization for long context

Instruction placement matters more as context grows. The guide recommends putting instructions before long context, and for very long prompts, repeating the most important instructions after the context.

Recommended layout:

```text
Task
Answer the user question using the provided context.

Rules
- Cite document IDs.
- If the answer is not present, say so.
- Do not use unsupported facts.

Context
...long context...

Final Reminder
Use only the context above. Cite document IDs.

User Question
...
```

This layout keeps the task visible before and after the high-token context block.

## Prompt migration for GPT-4.1

When migrating prompts from earlier models, expect more literal instruction following. Prompts that previously worked through implication may need explicit behavior rules.

Migration checklist:

- Remove stale or conflicting instructions.
- Replace vague preferences with testable rules.
- Specify what to do when information is missing.
- Define tool-use boundaries and required tool inputs.
- Add examples for edge cases, not only ideal cases.
- Check whether output formatting needs stricter constraints.
- Evaluate against the same examples before and after migration.

If a model follows an instruction too strongly, soften or qualify the rule. For example, replace `Always call a tool before answering` with `Call a tool when the answer depends on external state or unavailable information`.

## Long-context retrieval prompts

For retrieval-heavy workflows, ask the model to identify relevant documents before answering when document selection itself matters.

Example:

```text
Review the provided documents.
Select all documents needed to answer the question.
Return the selected document IDs.
Then answer using only those selected documents.
```

This pattern can improve auditability because the answer is tied to a selected evidence set. It also helps evaluate retrieval and context-building quality.

## Caveats

The source guide notes several practical caveats:

- Very long repetitive outputs may require stronger instructions or task decomposition.
- Parallel tool calls can occasionally be incorrect; test them before relying on them.
- Prompt behavior is empirical, so evals are necessary for production use.
- More detailed prompts can improve adherence but also increase latency and maintenance cost.

Use prompt changes as part of an engineering loop: update the prompt, run evaluations, inspect failures, and keep only changes that improve measured behavior.
