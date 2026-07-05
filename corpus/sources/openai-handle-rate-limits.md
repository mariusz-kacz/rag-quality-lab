# Source snapshot

Source metadata:
- source_slug: openai-handle-rate-limits
- category: LLM settings, cost, and tokens
- upstream_url: https://github.com/openai/openai-cookbook/blob/8730772/examples/How_to_handle_rate_limits.ipynb
- source_notebook: https://github.com/openai/openai-cookbook/blob/8730772/examples/How_to_handle_rate_limits.ipynb
- license: MIT
- pinned_version: openai-cookbook@8730772
- snapshot_type: normalized documentation digest from notebook markdown and compact code cells
- normalization: extracted rate-limit causes, 429 error handling, exponential backoff patterns, fallback-model cautions, max-token sizing, proactive throttling, batching, and parallel processor guidance; removed notebook execution scaffolding, API-key setup boilerplate, intentionally rate-limit-triggering loops, printed story outputs, and long repetitive examples

---
# Rate-limit causes and backoff strategies

The notebook explains how to handle OpenAI API rate limits. When an application sends requests too quickly or consumes too much quota in a short period, the API can return a `429` response such as `Too Many Requests` or raise a `RateLimitError` in the Python SDK. The source frames these errors as expected operational conditions that production systems should avoid where possible and handle gracefully when they occur.

The notebook links to a parallel request processor script for large jobs: `api_request_parallel_processor.py` in the OpenAI Cookbook. That script is presented as a practical reference for throttling parallel API requests so that high-volume workloads can stay under rate limits while still making progress.

## Why rate limits exist

The source gives three reasons for API rate limits:

- protect the API from abuse, misuse, overload, and disruption;
- ensure fair access so one organization cannot consume capacity in a way that slows everyone else;
- manage aggregate infrastructure load when request volume rises.

The practical implication is that rate limits are not just error cases to suppress. They are part of the service contract. A reliable client should respect them with backoff, throttling, batching, and monitoring rather than repeatedly retrying at full speed.

## Default limits and usage tiers

The notebook states that rate limits and spending limits are adjusted based on several factors. As API usage grows and bills are paid successfully, an organization's usage tier can increase automatically. Specific limits should be checked in OpenAI account and organization settings, including the limits page referenced by the source.

The source also points to OpenAI rate-limit documentation and Help Center articles for current limit details and guidance on `429` errors. For a pinned corpus snapshot, the durable point is that a client should not hard-code a universal limit. It should load or configure the limits that apply to the organization, model, and workload.

## Example rate-limit error

The notebook shows a typical SDK error message for sending requests too quickly. The message identifies the model or context, organization, requests-per-minute limit, current observed request rate, and a suggestion to contact support or request an increase if the issue continues.

The important fields are:

- the limit type that was exceeded, such as requests per minute;
- the configured limit;
- the current measured request rate;
- the model or default model context;
- the organization context.

An application should log enough structured information to diagnose whether the error came from request count, token count, daily quota, model-specific limits, or shared model-limit groups. It should not treat every `429` as identical.

The notebook includes a short loop that intentionally sends many completions in quick succession to trigger a rate-limit error. That loop is useful for demonstration, but it is not a production pattern. In production, clients should control concurrency and retry behavior before they reach a tight loop of failing requests.

## Exponential backoff

The primary mitigation in the source is retrying with random exponential backoff. When a rate-limit error occurs, the client waits briefly, retries, and increases the delay if the next attempt also fails. Random jitter prevents many clients or worker threads from waking and retrying at the same time.

The source lists several benefits:

- automatic retries allow transient rate-limit errors to recover without crashes or lost work;
- short initial waits keep recoverable failures responsive;
- longer waits reduce pressure when the service keeps rejecting requests;
- jitter spreads retries so they do not form a synchronized retry burst.

The source also warns that unsuccessful requests still count against per-minute limits. Continuously resending a request without delay can make the problem worse because each failed attempt consumes part of the same constrained budget.

## Tenacity example

The notebook shows `tenacity` as one way to add retry behavior in Python. Tenacity is a third-party retry library, and the source explicitly states that OpenAI does not guarantee its reliability or security.

Compact example:

```python
from tenacity import retry, stop_after_attempt, wait_random_exponential

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def completion_with_backoff(client, **kwargs):
    return client.chat.completions.create(**kwargs)

response = completion_with_backoff(
    client,
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Once upon a time,"}],
)
```

This captures the key behavior from the notebook: retry failed calls, increase wait time exponentially with randomness, and stop after a bounded number of attempts. The maximum attempts matter because unbounded retries can hide failures, increase cost, and block worker capacity.

## Backoff library example

The notebook also shows the `backoff` package, another third-party decorator library. As with Tenacity, the source says OpenAI does not guarantee the reliability or security of the dependency.

Compact example:

```python
import backoff
import openai

@backoff.on_exception(backoff.expo, openai.RateLimitError, max_time=60, max_tries=6)
def completions_with_backoff(client, **kwargs):
    return client.chat.completions.create(**kwargs)

response = completions_with_backoff(
    client,
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Once upon a time,"}],
)
```

The reusable pattern is the same: retry only selected transient errors, cap the total retry time or number of attempts, and let permanent or unexpected exceptions surface.

## Manual backoff implementation

The notebook includes a manual retry decorator for teams that do not want a third-party dependency. The source version retries functions that raise `openai.RateLimitError`, multiplies the delay after each failure, optionally adds random jitter, sleeps, and raises an exception when the maximum retry count is exceeded.

Compact manual example:

```python
import random
import time
import openai

def retry_with_exponential_backoff(
    func,
    initial_delay: float = 1,
    exponential_base: float = 2,
    jitter: bool = True,
    max_retries: int = 10,
    errors: tuple[type[Exception], ...] = (openai.RateLimitError,),
):
    def wrapper(*args, **kwargs):
        retries = 0
        delay = initial_delay

        while True:
            try:
                return func(*args, **kwargs)
            except errors:
                retries += 1
                if retries > max_retries:
                    raise RuntimeError(f"Maximum retries exceeded: {max_retries}")
                delay *= exponential_base * (1 + jitter * random.random())
                time.sleep(delay)

    return wrapper

@retry_with_exponential_backoff
def completions_with_backoff(client, **kwargs):
    return client.chat.completions.create(**kwargs)
```

Manual retry logic should preserve the source's safeguards: retry only known transient errors, include jitter, cap retries, and raise when the client cannot recover. In production, the same wrapper should also emit logs or metrics for retry count, final failure, and total wait time.

## Backoff tradeoffs for RAG systems

In a RAG pipeline, rate-limit handling affects both latency and quality. Retrying final answer generation can keep a user query from failing, but each retry increases end-to-end latency. Retrying retrieval-adjacent LLM calls, such as query rewriting or route classification, can block the entire pipeline before retrieval begins.

Useful RAG-specific practices include:

- apply backoff around each API boundary rather than around the entire pipeline only;
- use bounded retries so a single query cannot occupy workers indefinitely;
- log whether failures happened during routing, retrieval preparation, answer generation, or evaluation;
- avoid retrying deterministic validation errors as if they were rate-limit errors;
- make no-answer and error responses distinct so rate-limit failures are not confused with insufficient evidence.

For evaluation workloads, retry behavior should be part of the trace. If an answer was produced after several rate-limit retries, the trace should preserve retry count and timing so latency metrics remain interpretable.

# RPM, TPM, fallback models, max tokens, and throughput

The second half of the notebook focuses on staying productive under rate limits. It covers switching to fallback models, configuring `max_tokens`, adding proactive delay, batching tasks, and using a parallel processing script that throttles both request and token usage.

## Fallback models

The source says one response to rate-limit errors on a primary model is to switch to a secondary model. This can keep an application responsive when the primary model is throttled or unavailable.

Compact fallback example:

```python
import openai

def completions_with_fallback(client, fallback_model: str, **kwargs):
    try:
        return client.chat.completions.create(**kwargs)
    except openai.RateLimitError:
        kwargs["model"] = fallback_model
        return client.chat.completions.create(**kwargs)

response = completions_with_fallback(
    client,
    fallback_model="gpt-4o",
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Once upon a time,"}],
)
```

The notebook warns that fallback models can differ significantly in accuracy, latency, and cost. The strategy is not suitable for every workflow, especially when output consistency is critical. Some models also share rate limits, which can reduce or eliminate the benefit of switching. The source directs readers to the organization limits page to see which models share limits.

For RAG, fallback models should be evaluated explicitly. A smaller fallback model might answer more quickly but may be weaker at following citation rules, refusing unsupported answers, or synthesizing evidence across retrieved chunks. A larger fallback model may preserve quality but increase cost or latency. The fallback plan should specify which stages may fall back and how quality will be measured.

## `max_tokens` and rate-limit accounting

The source states that rate-limit usage is calculated from the greater of:

1. `max_tokens`, the maximum allowed response length;
2. an estimate of input tokens derived from the prompt's character count.

If `max_tokens` is set much higher than the expected completion length, the request can be counted as larger than the response will actually be. This can cause premature throttling. The source recommends configuring `max_tokens` close to the expected response size so usage estimates are more accurate.

Compact example:

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Once upon a time,"}],
    max_tokens=100,
)
```

The value should be chosen from the actual product requirement. A one-label classifier should not reserve a long answer budget. A short cited RAG answer might need enough tokens for a concise answer plus source references, but not an unrestricted essay. Evaluation systems should record both requested maximum output tokens and actual output tokens so teams can tune budgets without guessing.

## Requests per minute and tokens per minute

The notebook distinguishes request limits from token limits. The OpenAI API enforces separate request-per-minute or request-per-day limits and token-per-minute limits. This means an application can hit RPM while still having TPM capacity, or hit TPM while request count remains low.

The operational response depends on which limit is binding:

- If RPM is the bottleneck, batch multiple tasks into fewer requests when the model context window and output format allow it.
- If TPM is the bottleneck, reduce input context, lower output budgets, trim retrieved chunks, or slow request concurrency.
- If both are tight, combine throttling, batching, token budgeting, and workload scheduling.

This distinction is central for RAG workloads. A system with many small classification calls may hit RPM. A system that sends large retrieved contexts may hit TPM. The mitigation should match the limiting resource.

## Proactive delay for batch throughput

For real-time user requests, the source says backoff and retry can minimize failures while keeping latency reasonable. For batch processing, where throughput matters more than individual request latency, proactive throttling may be better.

If a batch job repeatedly hits the rate limit, backs off, and then immediately hits the limit again, it wastes part of the request budget on failed attempts. The source recommends calculating a delay from the rate limit and adding that delay between requests. For example, a limit of 20 requests per minute suggests a base spacing of 60 / 20, or 3 seconds per request. The notebook says a 3 to 6 second range can help operate near the ceiling without repeatedly exceeding it.

Compact delay example:

```python
import time

def delayed_completion(client, delay_in_seconds: float, **kwargs):
    time.sleep(delay_in_seconds)
    return client.chat.completions.create(**kwargs)

rate_limit_per_minute = 20
delay = 60.0 / rate_limit_per_minute

response = delayed_completion(
    client,
    delay_in_seconds=delay,
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Once upon a time,"}],
)
```

For production batch systems, this idea is usually implemented with a shared rate limiter rather than a sleep inside every request function. The important source principle is proactive pacing: do not rely only on failed requests to discover that the job is running too fast.

## Batching tasks into one request

The notebook recommends batching when an application is hitting RPM limits but still has TPM capacity. By bundling several prompts into one request, the application reduces request count and can increase throughput if token usage is managed carefully.

The source lists several cautions:

- the model has a maximum number of tokens per request, so oversized batches can fail or be truncated;
- batching can add wait time while tasks are grouped, which can hurt time-sensitive user experiences;
- the response may not arrive in the same order or format as the submitted prompts, so the client needs a way to match outputs back to inputs.

The notebook first shows a non-batched loop that asks for one story per request. It then shows a batched version using Structured Outputs so the result can be parsed reliably.

Compact structured batching example:

```python
from pydantic import BaseModel

class StoryResponse(BaseModel):
    stories: list[str]
    story_count: int

num_stories = 10
prompt_lines = [f"Story #{i + 1}: Once upon a time," for i in range(num_stories)]

response = client.beta.chat.completions.parse(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "developer",
            "content": "Respond to each prompt as a separate short story.",
        },
        {
            "role": "user",
            "content": "\n".join(prompt_lines),
        },
    ],
    response_format=StoryResponse,
)

stories = response.choices[0].message.parsed.stories
```

Structured output reduces parsing ambiguity when many tasks are combined in one call. For RAG and evaluation workloads, the same pattern can batch small independent judgments, labels, or synthetic test expansions, as long as the schema preserves a stable way to associate each result with its input.

Batching is less appropriate when each task needs a large retrieved context, strict per-user latency, or independent security boundaries. In those cases, batching may increase TPM pressure, delay individual users, or make provenance harder to audit.

## Parallel processing script

The notebook closes by pointing to an OpenAI Cookbook script for parallel processing large quantities of API requests. The source says the script:

- streams requests from a file to avoid loading giant jobs fully into memory;
- makes requests concurrently to maximize throughput;
- throttles both request and token usage to stay under limits;
- retries failed requests to avoid missing data;
- logs errors so problems can be diagnosed.

This design combines the notebook's main throughput lessons. Concurrency alone is not enough; parallel workers must share request and token budgets. Retrying alone is not enough; the job should proactively throttle before failures dominate. Logging alone is not enough; the job should preserve enough per-request state to retry or diagnose failed rows.

For a RAG quality lab, this script pattern maps to corpus-scale or golden-set workloads:

- batch ingestion or embedding jobs should stream inputs rather than reading every chunk into memory;
- eval runs should cap concurrency according to both RPM and TPM;
- retry counts and final errors should be written to artifacts;
- token budgets should be estimated before dispatch;
- failed examples should remain identifiable for rerun or analysis.

The durable operational rule is to optimize for the binding limit. If the workload is request-bound, batch or pace requests. If it is token-bound, trim prompts, reduce output budgets, or lower concurrency. If the workload is user-facing, balance retry and fallback behavior against user-visible latency. If it is offline batch processing, favor steady throughput, durable logs, and resumable execution.
