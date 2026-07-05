# Source snapshot

Source metadata:
- source_slug: microsoft-advanced-prompts
- category: prompting techniques
- upstream_url: https://github.com/microsoft/generative-ai-for-beginners/tree/main/05-advanced-prompts
- source_markdown: https://github.com/microsoft/generative-ai-for-beginners/blob/75d89e41403186a1e3613297b1c5483c7d087e5f/05-advanced-prompts/README.md
- license: MIT
- pinned_version: microsoft-generative-ai-for-beginners@75d89e41403186a1e3613297b1c5483c7d087e5f
- snapshot_type: normalized documentation digest from source README
- normalization: removed image banner, classroom assignment scaffolding, knowledge-check material, next-lesson links, duplicated/truncated code listings, and long fenced examples; retained reusable prompting techniques, tradeoffs, compact prompts, and output-variation guidance

---
# Advanced prompt patterns

Prompt engineering is the practice of guiding a model toward more useful responses by giving it clear instructions, relevant context, examples, constraints, and output expectations. A prompt usually has two phases of work:

- construction: deciding what context, instructions, examples, and constraints to include;
- optimization: iterating on the prompt after reviewing model failures.

A simple prompt such as `Generate 10 questions on geography` already contains two useful constraints: the topic is geography and the output count is limited to 10. It is still underspecified because geography is broad and the format is undefined. A stronger prompt narrows the topic, audience, difficulty, and response shape:

```text
Generate 10 geography quiz questions for middle-school students.
Focus on world capitals and major rivers.
Return a numbered list.
Include the answer after each question.
```

The core pattern is to reduce ambiguity. State the task, define the relevant context, constrain the output, and specify how the result should be formatted.

## Zero-shot prompting

Zero-shot prompting asks the model to perform a task without examples. It is the simplest approach and works best when the task is common, the desired format is obvious, or small variations are acceptable.

Example:

```text
Explain algebra in two paragraphs for a student who has just learned arithmetic.
```

Zero-shot prompts are fast to write, but they often leave too much room for interpretation. Add more constraints when you need a specific scope, tone, level of detail, or output format.

## Few-shot prompting

Few-shot prompting includes examples that demonstrate the desired behavior. Examples can show the expected style, format, reasoning pattern, label set, or level of detail.

Example:

```text
Classify each headline as Sports, Business, Technology, or Politics.

Headline: "Central bank leaves interest rates unchanged"
Category: Business

Headline: "New chip design improves mobile battery life"
Category: Technology

Headline: "Rookie scores twice in playoff win"
Category:
```

The examples act as a local pattern for the current request. They do not train the model permanently, but they help it infer the expected output for the current inference.

Use few-shot prompting when:

- the task has a specific label set or response format;
- the model is misinterpreting a zero-shot prompt;
- the difference between good and bad output is easier to show than explain;
- you need consistent style across many responses.

## Decomposition and worked examples

For multi-step tasks, prompts often work better when they decompose the problem into smaller steps. The original source describes this as chain-of-thought prompting and least-to-most prompting. In modern application prompts, the safer reusable pattern is to ask for the task to be solved through explicit intermediate outputs when those outputs are useful to the user or downstream system, rather than asking for hidden reasoning.

Simple decomposition prompt:

```text
Break the task into subtasks, solve each subtask, then provide the final answer.
Keep each subtask result to one sentence.

Task: Plan a five-step data science workflow for predicting customer churn.
```

Worked-example prompt:

```text
Use the example calculation pattern, then solve the final problem.

Example:
Lisa has 7 apples, throws away 1, gives 4 to Bart, and Bart gives 1 back.
7 - 1 = 6
6 - 4 = 2
2 + 1 = 3
Answer: 3

Problem:
Alice has 5 apples, throws away 3, gives 2 to Bob, and Bob gives 1 back.
Answer:
```

Use decomposition when:

- the task has dependencies between steps;
- the model is skipping important constraints;
- the output needs an audit trail;
- a large task can be made easier by solving smaller subtasks first.

Avoid making every answer verbose by default. If the final user experience only needs an answer, ask for a concise final answer and reserve intermediate details for diagnostics, tool calls, or explicit user requests.

## Generated knowledge and contextual templates

Generated-knowledge prompting enriches the prompt with relevant facts, data, or context before asking the model to decide or generate. In enterprise applications, this often appears as a prompt template whose variables are filled from trusted internal systems.

Template:

```text
Company: {{company_name}}
Available products:
{{products_list}}

User budget: {{budget}}
User requirements: {{requirements}}

Recommend products that satisfy the requirements and do not exceed the budget.
Return only products from the available list.
```

Filled prompt:

```text
Company: ACME Insurance
Available products:
- type: Car, tier: cheap, cost: 500 USD
- type: Car, tier: expensive, cost: 1100 USD
- type: Home, tier: cheap, cost: 600 USD
- type: Home, tier: expensive, cost: 1200 USD
- type: Life, tier: cheap, cost: 100 USD

User budget: 1000 USD
User requirements: Car and Home insurance

Recommend products that satisfy the requirements and do not exceed the budget.
Return only products from the available list.
```

This pattern is useful because it narrows the answer space to known data. It still needs explicit constraints. If the model recommends unavailable or over-budget products, strengthen the prompt with rules such as `Do not exceed the budget` and `Return "no valid package" if no combination satisfies all requirements`.

## Self-refine

Self-refine is an iterative prompting pattern: ask for an answer, critique the answer against criteria, then ask for an improved version. It is useful when the first output is plausible but incomplete.

Workflow:

1. Ask the model to produce an initial answer.
2. Ask it to critique the answer against explicit criteria.
3. Ask it to revise the answer using the critique.
4. Repeat only if the remaining issues are worth the extra cost and latency.

Example:

```text
Create a small Flask API with routes for products and customers.
```

Critique prompt:

```text
Review the code for correctness, maintainability, and production readiness.
List exactly three concrete improvements.
```

Revision prompt:

```text
Apply the three improvements.
Keep the API behavior the same.
Return the revised code only.
```

Self-refine does not remove the need for external validation. Generated code should still be run, tested, and reviewed by application-specific checks.

## Maieutic prompting

Maieutic prompting asks the model to explain or justify parts of an answer, then checks whether those explanations remain consistent. It is related to self-refine but focuses on surfacing contradictions.

Workflow:

1. Ask the model to answer a question.
2. Ask it to explain each important part of the answer.
3. Compare explanations for contradictions or unsupported claims.
4. Discard or revise inconsistent parts.

Example:

```text
Create a five-step crisis plan for pandemic response.
For each step, include the risk it addresses and the stakeholder responsible.
After the plan, list any assumptions that could change the recommendation.
```

This pattern is most useful for analysis, planning, policy review, and other cases where consistency matters. It should be paired with factual verification for high-stakes decisions.

## Prompt construction checklist

Use these checks before treating a prompt as ready:

- Define the task in one direct sentence.
- Provide only context that is relevant to the task.
- State required output format and length.
- Include examples when the desired pattern is not obvious.
- Add constraints for allowed sources, labels, tools, or products.
- Tell the model what to do when required information is missing.
- Keep dynamic data clearly separated from instructions.
- Test on failure cases, not only happy-path examples.

# Iterative prompting methods and tradeoffs

Prompt optimization is the process of improving a prompt after seeing model behavior. A prompt that works once may still fail on edge cases, ambiguous inputs, long contexts, or inputs with missing information. Treat prompt design as an empirical loop: write, test, inspect failures, revise, and test again.

## Common failure modes

Simple prompts often fail because they leave important assumptions implicit. Common issues include:

- topic scope is too broad;
- desired format is not specified;
- examples conflict with written instructions;
- the model is not told how to handle missing information;
- supplied context contains irrelevant or contradictory details;
- the prompt asks for a recommendation without constraints;
- the prompt relies on model knowledge where authoritative data is required.

When a prompt fails, revise the instruction that created the ambiguity. Do not only add more text; remove conflicting or distracting text when possible.

## Output variation and determinism

LLM outputs are nondeterministic. Re-running the same prompt can produce different wording, structure, examples, or code. Variation is acceptable for creative tasks, brainstorming, and open-ended drafting. It is a problem when downstream code, evaluation, or user workflows require stable output.

Use more deterministic prompts when:

- the output must be parsed by code;
- answers are evaluated against a golden set;
- the user expects a repeatable checklist or classification;
- the response controls a tool call or workflow decision.

Prompt-level controls for stability:

- specify a strict output schema or template;
- use a fixed label set;
- ask for no extra prose;
- limit the number of returned items;
- provide examples of the exact response shape;
- define fallback behavior such as `return "not found"`.

Model-parameter controls can also affect variation. Temperature is commonly used to make outputs more or less varied, but exact ranges and behavior are API/model dependent. Lower temperature generally favors more predictable completions; higher temperature generally allows more diverse outputs. Top-p and related sampling parameters can also affect variation, depending on the provider.

## Tradeoffs of prompt patterns

Different prompt patterns improve different failure modes and introduce different costs.

| Pattern | Best for | Tradeoff |
| --- | --- | --- |
| Zero-shot | Simple, common tasks | Can be underspecified |
| Few-shot | Consistent labels, style, or format | Adds prompt length and examples can bias outputs |
| Decomposition | Multi-step tasks and audit trails | More tokens and potentially verbose answers |
| Generated knowledge | Grounding answers in supplied data | Requires trusted context and clear constraints |
| Self-refine | Improving drafts or code | Extra latency and no guarantee of correctness |
| Maieutic prompting | Finding inconsistencies | Can be slow and still needs external verification |

Use the lightest pattern that solves the observed failure. A few precise constraints are often better than a long prompt that mixes rules, examples, and unrelated context.

## Iteration workflow

A practical prompt-iteration loop:

1. Start with the simplest prompt that expresses the task.
2. Run it against representative examples.
3. Record specific failures.
4. Add or revise one instruction to address the highest-impact failure.
5. Re-run the same examples.
6. Add edge cases for any newly discovered failure.

Example failure-driven revision:

```text
Initial prompt:
Suggest an insurance package for this budget and these requirements.

Observed failure:
The model recommends products outside the budget and includes product types the user did not request.

Revised prompt:
Suggest an insurance package using only products from the provided list.
The total monthly cost must be less than or equal to the budget.
Use only product types listed in the user's requirements.
If no package satisfies all constraints, return "No valid package".
```

This kind of targeted revision is easier to evaluate than broad rewrites because each change maps to a specific failure.

## Good practices

Reusable prompting practices from the source lesson:

- Specify context: domain, audience, task purpose, and relevant data.
- Limit output: number of items, length, or level of detail.
- Specify both what and how: task plus desired format or structure.
- Use templates for prompts that combine instructions with dynamic data.
- Use correct spelling and clear grammar to reduce avoidable ambiguity.

Additional practices for application prompts:

- Separate instructions from user-provided or retrieved content.
- Put hard constraints close to the task they constrain.
- Avoid conflicting rules and stale examples.
- Prefer structured outputs when downstream code consumes the result.
- Validate model output with code, tests, retrieval checks, or human review when correctness matters.

## When to stop iterating

Stop prompt iteration when remaining failures are better handled by another control. Examples:

- Use retrieval instead of prompting when the model lacks required facts.
- Use structured outputs instead of prose instructions when code must parse the result.
- Use validators when constraints are mechanical.
- Use tools or business logic when the task requires calculations, lookups, or side effects.
- Use evaluation data when subjective inspection is no longer enough.

Prompting is useful, but it is not a substitute for application design. Reliable LLM systems combine prompts with context management, schemas, validation, tests, and monitoring.
