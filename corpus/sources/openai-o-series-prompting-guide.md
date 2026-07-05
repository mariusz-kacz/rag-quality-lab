# Source snapshot

Source metadata:
- source_slug: openai-o-series-prompting-guide
- category: prompting techniques
- upstream_url: https://github.com/openai/openai-cookbook/blob/8730772/examples/o-series/o3o4-mini_prompting_guide.ipynb
- source_notebook: https://github.com/openai/openai-cookbook/blob/8730772/examples/o-series/o3o4-mini_prompting_guide.ipynb
- license: MIT
- pinned_version: openai-cookbook@8730772
- snapshot_type: normalized documentation digest from notebook markdown cells
- normalization: extracted reusable guidance from markdown cells; removed raw notebook JSON, execution outputs, long examples, duplicated prose, and notebook-specific transitions; retained reasoning-model instruction guidance, function-calling guidance, tool-boundary examples, hallucination mitigations, Responses API notes, hosted-tool guidance, MCP considerations, and FAQ-derived tradeoffs

---
# Reasoning model instruction design

The o-series prompting guide focuses on reasoning models such as o3 and o4-mini, especially when they are used with function calling and agentic tool workflows. These models are trained to reason internally before responding and before calling tools. Prompting should therefore emphasize task goals, tool boundaries, argument requirements, and completion criteria rather than asking the model to produce extra hidden reasoning.

## Developer messages and function descriptions

For o-series models, developer instructions are the durable place for application-level behavior. The source guide notes that system messages supplied by the developer are treated as developer messages internally, so application prompts should be written as developer guidance.

Use developer messages for:

- the agent's role and scope;
- allowed and disallowed actions;
- tool-use boundaries;
- workflow order for common tasks;
- fallback behavior when a task cannot be completed;
- instructions about not inventing tool calls or future work.

Use function descriptions for:

- what the function does;
- when the function should be invoked;
- when it should not be invoked;
- how arguments should be constructed;
- special formatting rules for arguments;
- required preconditions.

The developer prompt guides the agent across tools. The function description defines each tool's interface contract.

## Context setting

A reasoning-model developer prompt should establish the operating domain and the set of actions the agent can take.

Example:

```text
You are a retail support agent.
You can help users modify pending orders, return delivered orders, update saved addresses, and answer questions about their own orders.
Stay within this retail-support role.
```

This context helps the model decide which requests are in scope, which tools may be relevant, and when to respond without a tool.

## Tool ordering

Reasoning models can plan tool use, but they can still call tools in the wrong order. For common workflows, write the expected sequence explicitly.

Example:

```text
To process a refund for a delivered order:
1. Confirm delivery status with `order_status_check`.
2. Check refund eligibility with `refund_policy_check`.
3. Create the refund request with `refund_create`.
4. Notify the user with `user_notify`.
```

For file or code agents, precondition rules can be enough:

```text
Check that a directory exists before creating files inside it.
Do not overwrite an existing file unless the user explicitly requested replacement.
```

## Tool-use boundaries

Define when to use tools and when not to use them. This reduces both underuse and overuse.

Example:

```text
Use tools when the user asks to modify an order, return a product, update account details, or retrieve personalized order information.

Do not use tools for general policy questions, out-of-scope requests, or tasks that can be answered from static instructions.

If a requested action is impossible because of a real constraint, explain the constraint instead of calling tools blindly.
```

Boundaries can also define which tool should win when capabilities overlap:

```text
Use `calculate_shipping_cost` for shipping estimates because it applies business-specific live rates.
Do not estimate shipping with `python` unless the shipping tool is unavailable or fails.
```

## Function-description design

Function descriptions should put the most important rules first. Long descriptive prose can distract from invocation criteria and argument rules.

Focused description:

```text
Create a new file in an existing target directory.
- Call only after confirming the directory exists.
- Do not overwrite existing files.
- Use `file_update` for edits to an existing file.
- Ask for clarification if the target path is ambiguous.
```

Argument-format examples can be helpful when the model struggles to build valid arguments. For a regex-search tool, examples might show how to escape literal characters:

```text
Return a valid regex pattern.
Escape literal regex characters such as (, ), [, ], ., *, +, ?, and |.

Examples:
file.txt -> file\.txt
value[index] -> value\[index\]
user|admin -> user\|admin
```

Keep examples small and directly tied to the argument format.

## Avoid chain-of-thought prompting

The guide explicitly cautions against asking o-series reasoning models to produce additional chain-of-thought or to reason more before each function call. These models already produce internal reasoning. Asking for extra reasoning can hurt performance or increase latency.

Prefer instructions that define observable behavior:

- what task to complete;
- which tools to use;
- which arguments are valid;
- when to ask for clarification;
- what final response should contain.

Avoid instructions such as:

```text
Think step by step before every function call.
Explain your full reasoning before choosing a tool.
```

Use concise planning summaries only when they are part of the user experience or needed for auditability.

## Responses API and reasoning items

The source guide recommends the Responses API for reasoning-model tool workflows because reasoning items can persist between tool calls within a turn. Preserving this state can improve decisions about when and how tools are called.

Practical implication:

- prefer Responses API for multi-tool reasoning workflows;
- preserve prior response state or reasoning items when the API supports it;
- avoid dropping relevant tool-call state between steps;
- summarize or trim irrelevant old tool outputs when context becomes noisy.

## Hosted tools, custom tools, and MCP

Responses API can combine hosted tools, custom tools, and MCP tools. The more tools are available, the more important routing rules become.

Guidance:

- define which tool should be used for each capability;
- resolve overlap between hosted and custom tools;
- filter MCP tools to the subset needed for the task;
- cache or pass back tool lists when possible to reduce latency;
- reserve reasoning models for tasks that need reasoning depth.

Example:

```text
Use `python` for data analysis, code execution, and multistep math.
Use `calculator` only for simple one-step arithmetic.
Use `fetch_customer_record` for personalized account data.
Do not answer personalized account questions from memory.
```

# Concise instructions versus detailed constraints

Reasoning models often perform well with concise instructions, but tool workflows need enough specificity to prevent wrong calls, missing preconditions, invalid arguments, and speculative promises. The right level of detail depends on task risk, tool overlap, and observed failures.

## When concise instructions are enough

Use concise instructions when:

- the task is low risk;
- the tool set is small and non-overlapping;
- function names and schemas are self-explanatory;
- the model only needs a role, scope, and output format;
- evals show reliable behavior.

Concise example:

```text
You are a support agent.
Answer general policy questions directly.
Use account tools only for personalized order or profile information.
Ask for clarification when required account identifiers are missing.
```

This is enough when tool boundaries are obvious and the workflow has few branches.

## When detailed constraints are needed

Add detailed constraints when:

- multiple tools can satisfy similar requests;
- a workflow requires a fixed order;
- a tool has side effects;
- invalid arguments are costly;
- the model has hallucinated tool calls or future actions;
- the domain has policy, compliance, or safety constraints.

Detailed example:

```text
For cancellation requests:
1. Use `order_status_check`.
2. If the order is pending, use `order_cancel`.
3. If the order has shipped or been delivered, do not call `order_cancel`.
4. Explain the status and offer return options when applicable.
```

Detailed constraints should be specific and testable. Avoid long background prose that does not change behavior.

## Guarding against function-calling hallucinations

The guide calls out hallucination patterns such as promising to call a tool later, claiming background work was started, or inventing future follow-up. Add explicit rules to prevent these behaviors.

Useful rules:

```text
Do not promise to call a function later.
If a function call is required, emit it now.
If required arguments are missing, ask for clarification.
Do not claim background work has started unless a tool call was actually made.
```

Use strict schemas when possible:

```text
Validate tool arguments against the schema and required format before calling.
If unsure, ask for clarification instead of guessing.
```

Strict schemas reduce malformed arguments, but they do not replace application validation or business-rule checks.

## Managing lazy or incomplete behavior

The source guide notes rare cases where reasoning models may give terse or incomplete answers, say they lack time, or promise future follow-up. Mitigations include:

- start a new conversation for unrelated tasks;
- remove irrelevant old tool calls from context;
- summarize only the relevant prior state;
- state completion criteria clearly;
- ask for the full requested output when completeness matters.

Example:

```text
Complete the requested analysis in this response.
Do not defer work to a future message.
If information is missing, list the missing information explicitly.
```

## Tool count and schema complexity

There is no universal maximum number of functions, but larger tool sets increase ambiguity, latency, and the need for clear descriptions. The source guide notes that fewer than about 100 tools and fewer than about 20 arguments per tool was considered in-distribution for the referenced o3/o4-mini guidance, but reliability still depends on task complexity, descriptions, schemas, and evals.

Practical guidance:

- keep only relevant tools available for the task;
- make tool names and descriptions distinct;
- put invocation criteria early in descriptions;
- avoid overlapping tools unless routing rules explain priority;
- build evals for common and edge-case tool decisions.

Deeply nested parameters can also reduce reliability. Prefer flatter schemas when the domain allows it. Use nesting only when it reflects meaningful structure, and add descriptions or discriminators for ambiguous fields.

## Custom tool formats

The guidance assumes standard API tool schemas passed through the `tools` parameter. If tools are described in free text inside a prompt, the model is no longer relying on the same schema-native interface. Argument construction and tool selection may become less reliable.

Use standard tool schemas when possible. If a custom tool protocol is unavoidable:

- define the protocol explicitly;
- include small examples;
- validate outputs before execution;
- test tool selection and argument construction separately;
- expect more prompt maintenance.

## Practical decision checklist

Use concise instructions first, then add constraints based on failures.

Add detail when the model:

- calls the wrong tool;
- calls tools in the wrong order;
- guesses missing arguments;
- emits invalid argument formats;
- promises future or background tool calls;
- answers directly when a tool is required;
- uses a general tool where a business-specific tool is required.

Do not add detail merely for completeness. Every rule should prevent a known failure, clarify a real ambiguity, or encode a business requirement.
