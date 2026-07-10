# Source snapshot

Source metadata:
- source_slug: openai-gpt5-prompting-guide
- category: prompting techniques
- upstream_url: https://developers.openai.com/cookbook/examples/gpt-5/gpt-5_prompting_guide
- source_page: https://developers.openai.com/cookbook/examples/gpt-5/gpt-5_prompting_guide
- source_notebook: https://raw.githubusercontent.com/openai/openai-cookbook/main/examples/gpt-5/gpt-5_prompting_guide.ipynb
- license: MIT
- pinned_version: openai-cookbook@main-snapshot-2026-07-10
- snapshot_captured: 2026-07-10
- snapshot_type: normalized documentation digest from OpenAI Cookbook GPT-5 prompting guide
- normalization: removed page navigation, raw notebook JSON, long benchmark-specific prompt blocks, and large coding-agent examples; retained model behavior guidance, instruction tuning patterns, agentic persistence guidance, tool preamble guidance, verbosity controls, minimal-reasoning guidance, Markdown behavior, metaprompting, and migration implications

---
# GPT-5 prompt behavior and instruction tuning

The GPT-5 prompting guide focuses on model-specific behavior and migration from earlier GPT and reasoning-model prompt styles. The durable lesson is that GPT-5 benefits from clear, explicit instructions that describe the desired behavior, constraints, and completion criteria. Prompt changes should be tested because small wording differences can affect adherence, verbosity, tool behavior, and final answer format.

## Be explicit about the desired behavior

The guide repeatedly treats prompts as living documents that need review. If a model produces the wrong behavior, the fix is often a minimal prompt change that names the missing behavior or removes an ambiguous instruction.

Good instruction tuning starts with:

- the role or operating domain;
- the outcome the model must produce;
- workflow rules that matter for the task;
- constraints on what not to do;
- output format expectations;
- examples only where the behavior is hard to describe.

For a RAG answer prompt, an explicit GPT-5-style instruction might say:

```text
Answer using only the provided source excerpts.
Use a citation after every sentence that depends on source evidence.
If the excerpts do not answer the question, return the configured no-answer sentence.
Do not use background knowledge to fill missing facts.
```

This is stronger than a generic instruction such as "be accurate" because every rule is observable in a trace or evaluation.

## Review ambiguity and contradictions

The guide notes that prompt libraries can accumulate contradictory or poorly worded instructions. Cleaning these instructions can improve performance. In practice, prompt review should look for:

- two rules that point to different output styles;
- old model-specific workarounds that no longer apply;
- examples that imply behavior not stated in the instructions;
- instructions that are too broad, such as always using a tool;
- missing fallback behavior for ambiguous or incomplete input.

For evaluation, ambiguous prompts make failures harder to diagnose. A bad answer might come from retrieval, model behavior, output parsing, or conflict inside the prompt. Removing prompt ambiguity reduces that diagnostic noise.

## Prompt optimization loop

The guide supports an iterative workflow:

1. Identify the undesired behavior.
2. Inspect whether the current prompt lacks a rule, contains a conflict, or shows the wrong pattern in examples.
3. Make the smallest prompt edit likely to address the failure.
4. Re-run representative and edge-case tests.
5. Keep the edit only if it improves measured behavior.

This maps directly to a RAG quality lab. Prompt changes should be evaluated against golden questions, citation validation, no-answer behavior, token budgets, and trace inspection rather than judged from one successful answer.

## Markdown and response formatting

The guide says GPT-5 API responses do not necessarily default to Markdown formatting. Applications that need Markdown should ask for it and define what kind of Markdown is allowed.

Useful formatting guidance:

- use Markdown only where it carries meaning;
- use inline code for file paths, function names, commands, or identifiers;
- use lists and tables when they make comparisons clearer;
- avoid decorative formatting that makes parsing harder;
- repeat formatting reminders in long conversations if adherence degrades.

For a corpus-backed RAG answer, Markdown rules should not conflict with citation rules. If every claim needs a citation, examples should show citations in the same list or paragraph style the application expects.

# Agentic workflows, verbosity, and migration patterns

GPT-5 guidance is especially relevant for long-running agents and coding-style workflows, but the same patterns apply to RAG pipelines that perform routing, retrieval, evidence selection, answer synthesis, and verification.

## Agentic persistence

The guide recommends persistence reminders for tasks that should continue until completion. In an agentic workflow, the model should not stop after only part of the user's request is handled.

For RAG, persistence does not mean endless tool use. It means the prompt should define completion criteria:

- decide whether retrieval is needed;
- retrieve or receive the selected context;
- answer only when evidence is available;
- cite the evidence used;
- return the no-answer response when evidence is insufficient.

Compact persistence instruction:

```text
Complete the evidence check before answering.
If the selected context is insufficient, say so instead of producing a partial answer.
```

## Tool preambles and progress updates

The guide discusses tool-calling preambles: short updates that explain what the model is about to do or has found. These are useful when users need visibility into long-running work.

For RAG systems, preambles should be concise and tied to real work:

- searching selected sources;
- checking retrieved passages;
- validating citations;
- preparing the final answer.

Avoid vague progress text that is not connected to actual pipeline state. In automated evaluation, progress messages may be unnecessary and can add output tokens or complicate parsing.

## Verbosity controls

GPT-5 can be steered toward shorter or more detailed outputs. Verbosity should be controlled by task need, not by a generic preference for long answers.

Examples:

- a router explanation should be compact;
- a cited answer may need enough detail to connect each claim to evidence;
- an audit trace summary should include route, context budget, citations, and failures;
- a user-facing answer should avoid internal diagnostic detail unless requested.

Prompt designers should define output length and content. For example:

```text
Answer in 2-4 bullets.
Each bullet must include at least one citation.
Do not include implementation details unless the question asks for them.
```

This kind of instruction manages quality, latency, and token cost together.

## Minimal reasoning mode

The guide introduces minimal reasoning as a low-latency option that still uses the reasoning-model paradigm. It notes that prompt wording can matter more at minimal reasoning than at higher reasoning levels.

For latency-sensitive RAG workflows, minimal reasoning is attractive for:

- classification;
- routing;
- short extraction;
- answerability checks;
- simple grounded answers over clear evidence.

The prompt should compensate by being explicit about workflow and completion criteria. If the model has fewer internal reasoning tokens, the prompt should make the required plan and constraints easier to follow.

## Migration from earlier prompts

When migrating to GPT-5, do not assume older prompt workarounds still help. Review prompts for:

- stale model names;
- instructions that were added to counter old failure modes;
- hidden assumptions about Markdown or verbosity;
- tool-use rules that are too broad;
- examples that are no longer representative.

Migration should be measured with the same evaluation suite before and after the change. For this project, that means comparing retrieval results, selected context, citation validity, no-answer behavior, and answer quality with the model and prompt version recorded in traces.

## Metaprompting

The guide suggests using GPT-5 as a prompt reviewer: provide the current prompt, describe the desired and undesired behavior, and ask for minimal edits. This is useful for finding contradictions or missing rules, but it should not replace human review and evaluation.

Metaprompting workflow:

1. Give the model the existing prompt.
2. State the behavior that should happen.
3. State the behavior that actually happened.
4. Ask for small edits that preserve most of the prompt.
5. Review the edits manually.
6. Test against golden examples.

For a RAG quality lab, metaprompting can suggest improvements to citation instructions, no-answer wording, and answer shape. The final decision should still come from trace inspection and evaluation metrics.
