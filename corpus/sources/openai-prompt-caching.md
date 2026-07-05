# Source snapshot

Source metadata:
- source_slug: openai-prompt-caching
- category: LLM settings, cost, and tokens
- upstream_url: https://developers.openai.com/api/docs/guides/prompt-caching
- source_markdown: https://developers.openai.com/api/docs/guides/prompt-caching.md
- license: OpenAI API docs reuse terms pending snapshot verification
- pinned_version: openai-api-docs@current-snapshot
- snapshot_type: normalized documentation digest from OpenAI API documentation page
- normalization: removed page chrome and image-only explanation while retaining prompt caching purpose, automatic cache behavior, prompt structure requirements, cache routing and retention, cacheable inputs, prompt_cache_key guidance, usage observability, privacy notes, and rate-limit caveats

---
# Prompt caching mechanics

The OpenAI prompt caching guide explains how repeated prompt prefixes can reduce latency and input-token cost. LLM prompts often contain stable content such as developer instructions, system rules, schemas, tools, examples, or long shared context. OpenAI routes API requests to servers that recently processed the same prompt prefix, allowing matching prefixes to be reused instead of processed from scratch.

Prompt caching works automatically on API requests for supported recent models. The source says no code changes are required to enable the basic behavior and there are no additional fees for using prompt caching. The guide describes prompt caching as available for `gpt-4o` and newer models.

The practical benefit is lower latency and lower input-token cost when requests share a long exact prefix. The source states that prompt caching can reduce latency by up to 80 percent and input token costs by up to 90 percent. Those are potential reductions, not a guarantee for every request. Benefits depend on prompt length, prefix stability, routing, request rate, model support, and whether a matching prefix is present on the selected machine.

## Exact prefix matching

Cache hits are only possible for exact prefix matches. To increase cache hits, applications should place static or repeated content at the beginning of the prompt and variable content at the end. Static content can include instructions, examples, output schemas, and common context. Dynamic content can include the user's latest question, user-specific data, conversation tail, request-specific retrieved documents, and other per-request values.

This rule applies to text, images, and tools. Images and tool definitions must be identical between requests for the relevant prompt prefix to match. For images, the detail parameter must also be the same because it affects tokenization. Tool definitions and structured output schemas can contribute to the cacheable prompt prefix.

For RAG systems, this means durable instructions and schemas should be kept stable and placed before request-specific retrieved chunks. The prompt should avoid reordering static sections, changing whitespace or generated labels unnecessarily, or inserting dynamic request IDs near the beginning. Even harmless-looking differences can break exact prefix matching.

## Automatic eligibility and token threshold

Prompt caching is enabled automatically for prompts that are 1024 tokens or longer. Requests below that size still return cache usage details, but `cached_tokens` will be zero.

The source gives the usage field shape used to observe caching:

```json
{
  "usage": {
    "prompt_tokens": 2006,
    "completion_tokens": 300,
    "total_tokens": 2306,
    "prompt_tokens_details": {
      "cached_tokens": 1920
    },
    "completion_tokens_details": {
      "reasoning_tokens": 0,
      "accepted_prediction_tokens": 0,
      "rejected_prediction_tokens": 0
    }
  }
}
```

The important field is `usage.prompt_tokens_details.cached_tokens`. It reports how many prompt tokens were served from a cache hit. A value of zero means the request did not use cached prompt tokens, either because the prompt was too short, the prefix did not match, the relevant cache was not retained, routing overflow occurred, or no matching cached prefix was available.

## Cache routing

The guide describes the first step as cache routing. Requests are routed to a machine based on a hash of the initial prompt prefix. The source says the hash typically uses the first 256 tokens, although the exact length varies by model.

If the request includes `prompt_cache_key`, that key is combined with the prefix hash. This gives the application a way to influence routing and improve hit rates when many requests share long common prefixes. The source cautions that if requests for the same prefix and `prompt_cache_key` combination exceed a certain rate, approximately 15 requests per minute, some requests may overflow to additional machines. Overflow can reduce cache effectiveness because those machines may not already hold the desired prefix.

The durable design point is that cache routing is prefix-aware but capacity-bound. A good cache strategy should group requests that really share a prefix while avoiding a single excessively hot key.

## Cache lookup, hit, and miss

After routing, the system checks whether the selected machine has the initial prompt prefix in cache.

If there is a cache hit, the system uses cached intermediate computation for the matching prefix. This lowers latency and cost for the input tokens that were cached. The output is still generated for the current request.

If there is a cache miss, the system processes the full prompt and then caches the prefix on that machine for possible future requests. A cache miss can happen on the first request with a new prefix, after cache expiration, after routing to a different machine, or after a prompt-prefix change.

The source's FAQ states that prompt caching does not affect output token generation or the final response. The response is computed anew each time. The cache covers the prompt side, not a stored answer. Therefore, prompt caching should not be treated as answer caching or semantic memoization.

## Cache retention policies

The guide distinguishes in-memory prompt cache retention from extended prompt cache retention. Both policies use the same prompt cache pricing according to the source.

In-memory prompt cache retention is available for all models that support prompt caching except `gpt-5.5`, `gpt-5.5-pro`, and future models. In-memory cached prefixes generally remain active for 5 to 10 minutes of inactivity, up to a maximum of one hour. These prefixes are held in volatile GPU memory.

Extended prompt cache retention keeps cached prefixes active for longer, up to a maximum of 24 hours. The guide lists support for models including `gpt-5.5`, `gpt-5.5-pro`, `gpt-5.4`, `gpt-5.2`, `gpt-5.1` variants, `gpt-5`, `gpt-5-codex`, and `gpt-4.1`. Extended caching works by offloading key/value tensors to GPU-local storage when memory is full, increasing cache capacity.

The source clarifies that key/value tensors are intermediate representations from model attention layers produced during prefill. For extended caching, only those key/value tensors may be persisted in local storage. The original customer prompt text is retained only in memory.

## Per-request retention configuration

The retention policy can be configured on a Responses API request with `prompt_cache_retention`, or on `chat.completions.create` for Chat Completions.

For `gpt-5.5`, `gpt-5.5-pro`, and future models, only `24h` is supported. For older models that support both `in_memory` and `24h`, the default depends on the organization's data retention policy. Organizations without Zero Data Retention enabled default to `24h`; organizations with Zero Data Retention enabled default to `in_memory` when `prompt_cache_retention` is not specified.

Compact Responses API example:

```json
{
  "model": "gpt-5.5",
  "input": "Your prompt goes here...",
  "prompt_cache_retention": "24h"
}
```

Applications with privacy, residency, or compliance requirements should choose the retention policy intentionally rather than relying on implicit defaults.

## Cacheable request parts

The source lists several request components that can be cached:

- Messages: the complete messages array, including system, user, and assistant interactions.
- Images: images in user messages, whether links or base64-encoded data, including multiple images when the image inputs and detail settings match.
- Tool use: the messages array and list of available tools can be cached and can contribute to the 1024-token minimum.
- Structured outputs: the structured output schema serves as a prefix to the system message and can be cached.

For RAG, this means a stable structured-output schema and stable citation instructions can be good cache-prefix material. Retrieved passages are usually dynamic and should generally come later unless the same source context is intentionally reused across many requests.

## Privacy and data boundaries

The FAQ states that prompt caches are not shared between organizations. Only members of the same organization can access caches of identical prompts.

Prompt caching has no manual clear operation. Prompts that have not been encountered recently are cleared automatically according to retention and eviction behavior.

The guide says cached prompts do count toward TPM rate limits. Prompt caching can reduce latency and input-token cost, but it does not remove token usage from rate-limit accounting. A high-throughput application still needs rate limiting and token budgeting even when many tokens are cache hits.

For Zero Data Retention requests, the guide distinguishes policies. In-memory cache retention does not save data to disk. Extended prompt caching may store key/value tensors in GPU-local storage, and those tensors are derived from customer content. The source says they are not retained beyond cache expiration, typically 1 to 2 hours for most usage and at most 24 hours. Extended prompt caching requests are not blocked when Zero Data Retention is enabled for a project, and other Zero Data Retention protections still apply, such as excluding customer content from abuse logs and preventing `store=True`.

For Data Residency, in-memory prompt caching does not store data and therefore does not affect residency. Extended caching temporarily stores data on GPU machines and is kept in-region only when using Regional Inference.

# Static and dynamic prompt layout, cache keys, and usage observability

The source's optimization guidance can be summarized as prompt layout discipline plus measurement. Prompt caching is automatic, but applications only benefit when repeated requests share exact long prefixes and those prefixes are routed and retained effectively.

## Static-first prompt layout

The guide's main best practice is to put static or repeated content first and dynamic, user-specific content last.

Stable prefix candidates include:

- developer instructions and safety rules;
- answer style and citation requirements;
- no-answer policy;
- structured output schemas;
- tool definitions;
- few-shot examples;
- fixed product or domain background;
- reused long context for a batch or session.

Dynamic suffix candidates include:

- the user's current request;
- user-specific account or permission details;
- conversation messages that change each turn;
- RAG search results;
- request-specific source snippets;
- timestamps, trace IDs, or other volatile metadata.

This layout also supports the latency guidance from the OpenAI latency optimization source: stable prompt prefixes are more cache-friendly when dynamic portions appear later.

## RAG prompt layout

In a RAG system, prompt caching is useful but needs care because retrieved context changes from query to query. A good default layout is:

1. Stable developer instructions.
2. Stable no-answer and citation policy.
3. Stable response schema or format instructions.
4. Stable examples, if used.
5. User question and dynamic route metadata.
6. Selected retrieved context.

If an application runs many questions against the same document, case file, tenant policy, or evaluation fixture, some reused source context may be moved earlier to increase caching. That should be done only when the context is truly shared across many requests and does not introduce access-control or relevance problems.

RAG systems should avoid placing retrieved chunks before stable instructions unless the retrieved context is intentionally part of a repeated shared prefix. Otherwise, each query changes the prefix and prevents later static content from being reused.

## `prompt_cache_key` design

The `prompt_cache_key` parameter can improve hit rates by influencing routing for requests that share common prefixes. The source recommends using it consistently across requests that share common prefixes.

The key should be chosen at a useful granularity. If the key is too broad, many unrelated prefixes may compete under the same routing pattern and some may overflow when the same prefix-key combination becomes hot. If the key is too narrow, requests that could share a cache may be split apart. The source specifically recommends selecting a granularity that keeps each unique prefix and `prompt_cache_key` combination below approximately 15 requests per minute to avoid cache overflow.

Possible RAG key dimensions include:

- application or feature name;
- tenant or organization when prompts are tenant-specific;
- prompt template version;
- stable tool/schema version;
- shared document set or evaluation run identifier when the same context is reused.

The key should not include volatile data such as request IDs, timestamps, random UUIDs, or the user's exact latest message. Including those values would defeat reuse.

## Cache observability

The guide recommends monitoring cache performance metrics, including cache hit rates, latency, and the proportion of tokens cached. The source says cached token counts can be monitored by logging the API `usage` field or through the OpenAI Usage dashboard.

At minimum, an application should record:

- total prompt tokens;
- cached prompt tokens;
- completion tokens;
- model;
- prompt template version;
- `prompt_cache_key`, if used;
- latency for the request;
- whether the request used in-memory or extended retention when configured.

From those fields, the application can compute cached-token ratio:

```text
cached_token_ratio = usage.prompt_tokens_details.cached_tokens / usage.prompt_tokens
```

This ratio should be interpreted with latency and cost. A high cached-token ratio should generally correspond to lower prompt-side cost and lower latency, but output generation, tool calls, retrieval, and downstream processing may still dominate end-to-end time.

## Cache hit-rate troubleshooting

When cached tokens remain low, the likely causes are practical:

- the prompt is shorter than 1024 tokens;
- static content is placed after dynamic content;
- a timestamp, request ID, or user-specific field appears near the beginning;
- examples, tools, images, or schemas are not identical between requests;
- the prompt template changes frequently;
- requests are too sparse and the cache is evicted before reuse;
- traffic for a hot prefix-key combination overflows to additional machines;
- the wrong `prompt_cache_key` granularity splits requests that should share a route.

The source recommends maintaining a steady stream of requests with identical prompt prefixes to reduce evictions and increase cache benefits. For batch evaluation or repeated RAG testing, grouping similar requests by prompt template and shared context can increase the chance of cache reuse.

## Prompt caching versus application caching

Prompt caching is not the same as caching final model responses. It does not store the answer. It reuses prompt-side computation and then generates output for the current request. Therefore, it should not be used to skip generation, bypass authorization checks, or assume that two similar requests have identical answers.

Application-level caches may still be useful for deterministic operations such as manifest loading, token counting, retrieval indexes, embedding lookup, or exact repeated query-answer pairs. Prompt caching complements those techniques by reducing model prefill work for long repeated prefixes.

## Operational implications

Prompt caching affects cost and latency, not correctness by itself. It does not change model behavior or generated output, according to the source. The main engineering work is designing prompts so stable material stays stable, choosing `prompt_cache_key` granularity carefully, logging usage details, and balancing retention with privacy and residency requirements.

For this project's RAG quality corpus, the key lessons are:

- keep durable RAG instructions, answer format, and citation rules in a stable prefix;
- place retrieved chunks and user-specific content later unless they are intentionally reused;
- track cached tokens in traces when evaluating latency and cost;
- do not confuse cached prompt tokens with lower TPM consumption;
- avoid volatile metadata in the prompt prefix;
- treat prompt template versioning as part of cache strategy.
