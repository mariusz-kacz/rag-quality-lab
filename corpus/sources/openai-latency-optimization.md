# Source snapshot

Source metadata:
- source_slug: openai-latency-optimization
- category: LLM settings, cost, and tokens
- upstream_url: https://github.com/openai/openai-cookbook/blob/8730772/examples/data/oai_docs/latency-optimization.txt
- source_markdown: https://raw.githubusercontent.com/openai/openai-cookbook/8730772/examples/data/oai_docs/latency-optimization.txt
- license: MIT
- pinned_version: openai-cookbook@8730772
- snapshot_type: normalized documentation digest from OpenAI Cookbook documentation text
- normalization: removed page navigation assumptions, image-only diagram dependence, repeated prompt blocks, and long illustrative scaffolding; retained the seven latency principles, token and request tradeoffs, streaming and user-perceived latency tactics, RAG context trimming guidance, and the customer-service bot optimization sequence

---
# Latency and efficiency principles

The source presents latency optimization as a set of engineering principles for LLM applications. It applies to small workflow steps, multi-step agents, retrieval-augmented systems, and chatbots. The central message is that latency is not only model inference speed. It also comes from output length, input size, network round trips, sequential dependencies, user-interface choices, and using an LLM where a simpler method would be faster.

The guide organizes the topic into seven principles:

1. Process tokens faster.
2. Generate fewer tokens.
3. Use fewer input tokens.
4. Make fewer requests.
5. Parallelize independent work.
6. Make users wait less.
7. Do not default to an LLM when a faster deterministic method fits.

These principles often interact. Combining prompts can reduce round trips but may force a larger model to do work that a smaller model could handle. Splitting a prompt can let cheaper or faster models handle narrow classification fields, but the extra request may add latency. Parallelization can reduce wall-clock time only when dependencies allow it. The guide repeatedly treats measurement as the deciding factor: profile where latency comes from, test candidate changes against realistic examples, and keep the changes that improve the production workflow without unacceptable quality loss.

## Process tokens faster

Inference speed is the rate at which a model processes tokens. It is commonly measured as tokens per minute or tokens per second. Model size is the most practical application-level lever: smaller models are generally faster and less expensive, and a smaller model can sometimes match or outperform a larger one when the task is well constrained.

The source recommends several ways to preserve quality when moving a task to a smaller model:

- write a longer and more specific prompt for the smaller model;
- provide few-shot examples that demonstrate the target behavior;
- use fine-tuning or distillation for repeated narrow tasks.

This principle is useful when a workflow contains classification, query rewriting, routing, extraction, or formatting tasks that do not require the strongest model. A RAG system might use a smaller tuned model to classify whether retrieval is needed, choose a knowledge category, or produce compact metadata fields, while reserving a larger model for final answer synthesis where open-ended reasoning and language quality matter more.

The guide notes that hardware, saturation level, and inference-engine optimizations can also affect token processing speed. Many application teams cannot directly control those factors, but teams running their own infrastructure can sometimes improve throughput by using faster hardware, avoiding overloaded inference servers, or applying lower-level serving optimizations.

## Generate fewer tokens

The source treats output generation as the largest latency contributor in many LLM calls. A useful heuristic is that large reductions in generated output can produce roughly proportional latency reductions. If an application cuts output length in half, it may also cut a large share of response time.

For natural-language outputs, the simplest tactic is to ask for a concise answer. Instructions such as a maximum word count, a brief style, or a compact answer format can reduce generated tokens. Few-shot examples and fine-tuning can also teach the model to produce shorter responses consistently.

For structured outputs, the source recommends minimizing syntax when the structure is internal to the application. Long field names, repeated labels, verbose wrapper objects, and unnecessary natural-language explanations all increase generation time. Shorter field names, compact booleans, and lean schemas can save output tokens. The source cautions that extreme compression, such as single-character keys or array-only encodings, can harm quality or maintainability, so teams should test compact formats rather than assuming the shortest representation is best.

Generation can also be stopped early with request-level limits such as maximum token settings or stop sequences. These controls are blunt tools: they can reduce latency, but they can also truncate useful content if the limit is too aggressive. For corpus and RAG workflows, they are most appropriate when the output format has a predictable upper bound, such as a classification label, a small JSON object, or a short answer with citations.

## Use fewer input tokens

Input length affects latency, but the guide frames it as a smaller lever than output length for many common requests. The source gives the practical warning that cutting a prompt substantially may produce only a small latency gain unless the request uses very large context.

Input trimming becomes important when prompts contain long documents, chat history, images, or RAG context. The source identifies several techniques:

- fine-tune a model so the prompt no longer needs long instructions or many examples;
- filter context before sending it to the model;
- clean noisy text such as HTML or boilerplate;
- prune RAG results to the passages most likely to answer the question;
- put stable prompt text first and dynamic material later to make requests friendlier to provider-side key-value caching.

For RAG, the key lesson is that context should be intentionally selected. Retrieval systems should not pass every vaguely related chunk into the model. They should choose high-signal chunks, remove duplicate or boilerplate text, respect token budgets, and leave room for the answer. Input reduction may not always dominate latency, but it also improves relevance, lowers cost, and reduces the chance that the model attends to distracting context.

The source links the stable-prefix tactic to key-value caching. When repeated requests share a long prefix, a serving system can sometimes reuse cached computation for that prefix. To benefit from that pattern, applications should keep durable instructions, policies, schemas, and examples before per-request content such as conversation history, retrieved passages, and user-specific data.

## Make fewer requests

Every API call has round-trip latency. In multi-step LLM workflows, that overhead accumulates. If several sequential tasks can safely be performed by one model invocation, the source recommends combining them into one prompt and returning the pieces in a structured response.

One practical pattern is to enumerate the steps in the prompt and ask for named fields in JSON. For example, a single call can rewrite a contextual user query and decide whether retrieval is required:

```json
{
  "query": "How long does the return policy cover?",
  "retrieval": true
}
```

Combining requests can simplify pipelines and remove network round trips, but it is not automatically superior. A combined prompt may require a larger model, longer context, or more output tokens. The source's customer-service example uses this principle for two narrow retrieval-preparation tasks because they are straightforward and share dependencies.

For RAG systems, request reduction is especially relevant around query transformation, routing, retrieval gating, answerability checks, and final synthesis. If the same model can safely produce a rewritten query, a retrieval decision, and a route label in one compact object, the system can avoid multiple serial calls before retrieval begins.

## Parallelize independent work

Parallelization reduces wall-clock latency when subtasks do not depend on each other. The source distinguishes independent steps from strictly sequential steps. Independent LLM calls, retrieval calls, moderation calls, metadata classification, and tool calls can often run at the same time. Sequential steps cannot be parallelized unless the system uses speculation.

Speculative execution starts a likely next step before the prior step is fully known, then cancels or discards the result if the assumption was wrong. The source uses the pattern of starting input moderation and generation together when moderation is expected to pass. If moderation fails, generation can be canceled or ignored; if it passes, the generation completed with little or no additional wall-clock delay.

Speculation is useful only when the predicted path is common enough and the cost of wasted work is acceptable. It also requires careful safety and resource controls. In a RAG pipeline, an analogous pattern might start a likely retrieval route while a classifier confirms the route, or generate a draft for the most common branch while a validation step runs. The implementation must still prevent unsafe or unsupported output from reaching the user.

Parallelization can increase request volume, cost, and rate-limit pressure. It should be used when reducing user-visible latency is worth those tradeoffs and when observability can show which parallel branch actually determines the critical path.

## Make users wait less

The guide distinguishes actual latency from perceived latency. A user experiences a blank wait differently from visible progress. The source recommends several techniques:

- stream partial model output as soon as it is available;
- process long output in chunks when a backend must moderate, translate, or transform it before display;
- show meaningful progress for multi-step or tool-using workflows;
- use loading states for moments when no partial result can be displayed.

Streaming is the strongest user-experience lever because it can reduce time to first visible output even when total generation time is unchanged. Chunking can reduce end-to-end latency when a backend can process and forward partial output incrementally instead of waiting for the full response.

Progress indicators and step displays are partly psychological, but they still matter in production applications. A RAG assistant can show that it is searching sources, reading retrieved passages, checking evidence, or preparing a cited answer. The user sees work progressing instead of a stalled interface. This does not replace real optimization, but it can make unavoidable latency more tolerable.

## Do not default to an LLM

The source emphasizes that LLMs are powerful but not always the fastest or simplest tool. Some outputs are constrained enough that deterministic application logic is better. Examples include standard confirmations, refusal messages, requests for required input, and tightly controlled UI summaries.

The guide identifies several alternatives:

- hard-code highly constrained outputs;
- pre-compute responses for constrained inputs such as known categories;
- present metrics, reports, and search results with purpose-built UI components;
- use ordinary algorithmic optimizations such as caching, hash maps, binary search, and complexity reduction.

This principle matters for RAG quality because not every trace step should become a generation step. Category definitions, source metadata checks, citation validation, token counting, and chunk filtering are better handled with deterministic code when possible. The LLM should be reserved for tasks where language understanding or generation provides real value.

# Token reduction, fewer requests, streaming, and RAG trimming

The source's practical guidance can be translated into a latency playbook for RAG and retrieval-aware applications: reduce generated tokens first, avoid unnecessary serial calls, trim and order context, stream or chunk visible output, and replace LLM calls with deterministic logic where the behavior is constrained.

## Token reduction for natural language and JSON

Generated output is a direct latency lever. For natural-language answers, concise instructions should be concrete. Instead of asking for a generally short answer, specify the desired shape: a one-sentence answer, three bullets, a maximum word count, or a compact answer plus citations. Few-shot examples are useful when the model otherwise drifts into verbose explanations.

For structured output, shorten the parts the model must generate repeatedly. Internal field names can be compact when developers, not end users, consume the object. The source's example changes verbose reasoning fields into shorter names while keeping comments or prompt instructions available for interpretation.

Compact internal JSON example:

```json
{
  "cont": true,
  "n_msg": 1,
  "tone_in": "aggravated",
  "type": "hardware_issue",
  "tone_out": "validating_solution_oriented",
  "reqs": "propose repair or replacement options",
  "human": false
}
```

This object is complete enough for a downstream prompt or service to use, but it avoids repeatedly generating long keys such as `message_is_conversation_continuation` or `user_requesting_to_talk_to_human`. The source notes that shortening keys saved only a small number of tokens in the example, but the same technique can matter more for larger objects, repeated calls, or slower models.

There is a quality boundary. If compact keys make the model less accurate or make downstream debugging harder, the token savings may not be worth it. Teams should test compact schemas against representative cases.

## Fewer requests in retrieval preparation

The customer-service example starts with a multi-step architecture: contextualize the user's latest message, decide whether retrieval is needed, perform retrieval, and generate an answer from the conversation and retrieved information. The source identifies two consecutive LLM calls before retrieval as an inefficiency. The contextualized query is required for the retrieval decision, so the two tasks can be combined.

Combined retrieval-preparation output:

```json
{
  "query": "How long does the return policy cover?",
  "retrieval": true
}
```

The combined prompt asks the model to rewrite the latest user message so it contains necessary conversation context, then determine whether a live lookup is needed. This removes one serial request and gives the application both fields at once.

For a local RAG lab, the same pattern can combine:

- standalone query rewriting;
- category routing;
- answerability or retrieval-needed classification;
- compact metadata extraction for the retrieval step.

The tasks should be combined only when they share inputs and can be evaluated together. If combining tasks makes the output less reliable, the saved round trip may not be worth the quality regression.

## Smaller models for narrow subtasks

The source proposes using a smaller or fine-tuned model for well-defined subtasks. Query rewriting, retrieval gating, and structured classification are narrow enough that a smaller model can often handle them with a strong prompt or fine-tuning.

The customer-service example also considers splitting a large assistant prompt. The original prompt asks one model to produce many reasoning fields and the final response. Some fields are narrow classifications or metadata, while the final response benefits from stronger open-ended generation. The source describes a tradeoff:

- one larger-model request avoids an extra round trip;
- two requests may be faster if a smaller model can produce most fields quickly and the larger model only handles final response synthesis.

The correct choice depends on the proportion of output tokens assigned to each part, the actual speed difference between models, and the latency added by a second request. The guide recommends testing this with production-like examples rather than deciding from architecture alone.

For RAG, a common split is:

1. A small model or deterministic component classifies the query, decides whether retrieval is needed, and extracts routing metadata.
2. Retrieval runs with the selected route and filters.
3. A stronger model receives only the selected context and generates the final grounded answer.

This keeps the expensive generation step focused on evidence-backed response synthesis.

## Parallel retrieval, reasoning, and validation work

After splitting the assistant prompt, the source observes that some reasoning fields no longer depend on retrieved context. That creates a parallelization opportunity: retrieval-related work and context-independent reasoning can run at the same time. The final response waits for both branches, but the branches no longer stack sequentially.

This is directly applicable to RAG systems. Work that often can run in parallel includes:

- embedding or query-routing decisions that do not need generation output;
- retrieval from multiple indexes;
- lexical and vector searches for later fusion;
- source-access checks;
- deterministic token counting and context-budget planning;
- generation of context-independent classification fields.

Parallel work should still be bounded. Running every possible search and classifier for every request may reduce latency for a single user while increasing global cost, saturation, and rate-limit failures. The source's general rule is to test the critical path and make parallelism intentional.

## RAG input trimming and shared prompt prefixes

The source's input-token section is especially relevant for RAG. Retrieved context can become large, repetitive, or noisy. Filtering context input is named directly as a way to reduce input tokens. The source gives examples such as pruning RAG results and cleaning HTML.

Good RAG trimming keeps the most answer-relevant evidence while removing tokens that do not help the model answer:

- drop low-scoring or off-topic retrieved chunks;
- remove boilerplate, navigation, duplicated headers, and HTML artifacts;
- deduplicate near-identical passages;
- prefer passages that contain the asked attribute, not just the entity name;
- keep source identifiers and section labels needed for citations;
- leave enough output budget for the answer and citations.

The guide also recommends maximizing the shared prompt prefix. Put stable instructions, output schema, citation rules, and examples before dynamic content. Put conversation history, retrieved chunks, and user-specific data later. This layout helps with cache-friendly request structure and makes the dynamic part easier to trim without rewriting the whole prompt.

In a traced RAG system, this maps cleanly to prompt construction:

1. Developer instructions and no-answer policy.
2. Output schema and citation rules.
3. Stable examples if needed.
4. User question.
5. Selected retrieved context.
6. Optional trace metadata or route summary.

The exact order depends on the API and application design, but stable reusable text should remain stable across requests when possible.

## Streaming, chunking, and visible progress

The guide treats streaming as the fastest way to reduce user waiting time. The model can begin sending tokens while the rest of the response is still being generated. For an assistant answer, this reduces time to first visible content and lets the user start reading earlier.

Chunking extends this idea when the backend needs to process output before showing it. A service can stream generated text to the backend, process chunks for moderation, translation, formatting, or other transformations, and forward approved chunks to the frontend. This avoids waiting for the full answer before beginning post-processing.

For RAG, streaming needs to respect citation and grounding behavior. A system should avoid showing unsupported claims before evidence checks if those checks are required before display. Depending on risk, the application can stream only after retrieval and prompt assembly are complete, stream a source-reading progress state first, or buffer enough output to validate citation format before displaying it.

Meaningful progress states are also valuable. A retrieval-aware assistant can show that it is searching, ranking sources, reading context, or preparing the answer. Those states should reflect real work rather than decorative delays.

## Deterministic alternatives in RAG workflows

The source's final principle warns against using an LLM by default. In a RAG quality system, many operations should be deterministic:

- manifest validation;
- section heading checks;
- source license and pinned-version checks;
- chunk ID generation;
- content hashing;
- token estimation;
- retrieval result sorting and filtering;
- citation syntax validation;
- no-answer decision enforcement when no selected context exists.

Using code for these steps reduces latency, improves reproducibility, and makes evaluation easier. LLM calls should be reserved for semantic tasks such as query understanding, answer synthesis, or judgments that cannot be captured reliably with rules.

## Example optimization sequence

The source's customer-service bot example demonstrates how the principles fit together. The original workflow uses multiple consecutive model calls and a large assistant prompt. The optimization sequence is:

1. Combine query contextualization and retrieval-needed classification into one structured response.
2. Move the combined retrieval-preparation prompt to a smaller or fine-tuned model.
3. Split the assistant prompt so narrow reasoning fields can be produced separately from final response generation.
4. Run context-independent reasoning in parallel with retrieval-related work.
5. Shorten structured output field names to reduce generated tokens.

The example does not claim that every application should apply every technique. It shows how to inspect a workflow, find the critical path, and choose changes that reduce serial work or generated tokens while preserving answer quality. The durable lesson is to optimize the measured bottleneck, then retest. In RAG applications, the bottleneck may be final answer generation, retrieval latency, oversized context, too many serial routing calls, or user-interface waiting time.
