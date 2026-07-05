# Source snapshot

Source metadata:
- source_slug: openai-token-counting
- category: LLM settings, cost, and tokens
- upstream_url: https://github.com/openai/openai-cookbook/blob/8730772/examples/How_to_count_tokens_with_tiktoken.ipynb
- source_notebook: https://github.com/openai/openai-cookbook/blob/8730772/examples/How_to_count_tokens_with_tiktoken.ipynb
- license: MIT
- pinned_version: openai-cookbook@8730772
- snapshot_type: normalized documentation digest from notebook markdown and compact code cells
- normalization: extracted tokenization concepts, model encodings, counting helpers, message-format caveats, and tool-call accounting guidance; removed notebook execution counts, package-install output, API-key setup, raw verification calls, and long printed token dumps while retaining representative examples and model-specific warnings

---
# Token counting concepts

The notebook explains how to count tokens with `tiktoken`, OpenAI's open-source tokenizer library. A tokenizer converts a text string into a list of token integers. GPT models process text as tokens, so token counts are useful for two practical reasons:

1. They indicate whether an input is too long for a model's context window.
2. They help estimate API cost because usage is priced by token.

A tokenizer uses an encoding to decide how text maps to tokens. Different model families use different encodings, and the same string can produce different token counts under different encodings.

## Encodings used by OpenAI models

The source lists the main encodings used by OpenAI models:

| Encoding name | Example OpenAI models |
| --- | --- |
| `o200k_base` | `gpt-4o`, `gpt-4o-mini` |
| `cl100k_base` | `gpt-4-turbo`, `gpt-4`, `gpt-3.5-turbo`, `text-embedding-ada-002`, `text-embedding-3-small`, `text-embedding-3-large` |
| `p50k_base` | Codex models, `text-davinci-002`, `text-davinci-003` |
| `r50k_base` or `gpt2` | GPT-3 models such as `davinci` |

The source notes that `p50k_base` overlaps substantially with `r50k_base`. For non-code text, those two encodings often produce the same tokens.

The recommended way to load the encoding for a known model is `tiktoken.encoding_for_model()`:

```python
import tiktoken

encoding = tiktoken.encoding_for_model("gpt-4o-mini")
```

An encoding can also be loaded directly by name:

```python
encoding = tiktoken.get_encoding("cl100k_base")
```

The first direct load may require internet access to download the encoding files. Later runs can use the local cache.

## Tokenizer libraries

For `o200k_base`, `cl100k_base`, and `p50k_base`, the source identifies `tiktoken` as the Python tokenizer and points to community libraries for other languages, including .NET/C#, Java, Go, and Rust. For `r50k_base` or `gpt2`, tokenizer libraries are also available in JavaScript, PHP, and other ecosystems. The notebook states that OpenAI does not endorse or guarantee third-party libraries.

For local corpus use, this means non-Python implementations should be treated as tokenizer-compatible dependencies that need their own validation. If an evaluation harness counts tokens outside Python, compare representative strings against `tiktoken` before relying on the counts for prompt budgeting or model-limit enforcement.

## How text is tokenized

The notebook describes typical English tokenization as ranging from one character to one word. Spaces are usually grouped with the starts of words. For example, a tokenizer may represent text as pieces like `"t"`, `"ikt"`, `"oken"`, `" is"`, `" great"`, and `"!"`.

Token boundaries are not the same as character or word boundaries. Some languages can have tokens shorter than a character or longer than a word. This matters for RAG context sizing: counting words or characters is only an approximation, while token counts determine what the model can actually receive.

The basic tokenizer operations are:

```python
import tiktoken

encoding = tiktoken.get_encoding("o200k_base")
tokens = encoding.encode("tiktoken is great!")
token_count = len(tokens)
text = encoding.decode(tokens)
```

The source provides a helper for counting tokens in any string:

```python
import tiktoken

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Return the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    return len(encoding.encode(string))

num_tokens_from_string("tiktoken is great!", "o200k_base")
```

For single-token inspection, the notebook warns that `.decode()` can be lossy when a token does not align with UTF-8 boundaries. For individual token values, use `.decode_single_token_bytes()`:

```python
token_bytes = [
    encoding.decode_single_token_bytes(token)
    for token in encoding.encode("tiktoken is great!")
]
```

## Comparing encodings

The notebook compares several strings across `r50k_base`, `p50k_base`, `cl100k_base`, and `o200k_base`. The exact token integers are less important than the pattern:

- Long English words can be split differently across encodings. The example word `antidisestablishmentarianism` is 5 tokens in `r50k_base` and `p50k_base`, but 6 tokens in `cl100k_base` and `o200k_base`.
- Arithmetic-like text can split spaces and symbols differently. The string `2 + 2 = 4` is 5 tokens in `r50k_base` and `p50k_base`, but 7 tokens in `cl100k_base` and `o200k_base`.
- Non-English text can differ substantially across encodings. The Japanese birthday greeting example is 14 tokens in `r50k_base` and `p50k_base`, 9 tokens in `cl100k_base`, and 8 tokens in `o200k_base`.

The source's comparison helper prints token counts, token integers, and token bytes for a given string:

```python
def compare_encodings(example_string: str) -> None:
    """Print a comparison of how encodings split a string."""
    print(f'\nExample string: "{example_string}"')
    for encoding_name in ["r50k_base", "p50k_base", "cl100k_base", "o200k_base"]:
        encoding = tiktoken.get_encoding(encoding_name)
        token_integers = encoding.encode(example_string)
        token_bytes = [
            encoding.decode_single_token_bytes(token)
            for token in token_integers
        ]
        print()
        print(f"{encoding_name}: {len(token_integers)} tokens")
        print(f"token integers: {token_integers}")
        print(f"token bytes: {token_bytes}")
```

For a RAG system, the comparison reinforces that token budgeting should use the same model or encoding family intended for generation or embeddings. A context builder that estimates length with a mismatched tokenizer can underfill useful context or overrun the actual model limit.

# Prompt budgeting and model-specific token accounting

The notebook extends token counting from simple strings to message-based API requests. Chat-style requests are harder to count than plain strings because model-specific formatting adds tokens around each message, role, name, and reply preamble.

The source emphasizes that message token counts can change from model to model. The counting functions are estimates for known model snapshots, not timeless guarantees. Requests that include tools or functions can consume additional prompt tokens beyond the message text.

## Counting message tokens

The notebook provides an estimator for messages passed to chat models. The estimator:

1. Selects an encoding with `tiktoken.encoding_for_model(model)`.
2. Falls back to `o200k_base` if the model is unknown.
3. Applies known constants for supported model snapshots.
4. Adds token counts for each message field.
5. Adds extra tokens for a `name` field.
6. Adds a small fixed reply preamble.

Compact form of the message-counting helper:

```python
def num_tokens_from_messages(messages, model="gpt-4o-mini-2024-07-18"):
    """Return the estimated number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using o200k_base encoding.")
        encoding = tiktoken.get_encoding("o200k_base")

    if model in {
        "gpt-3.5-turbo-0125",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
        "gpt-4o-mini-2024-07-18",
        "gpt-4o-2024-08-06",
    }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif "gpt-3.5-turbo" in model:
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0125")
    elif "gpt-4o-mini" in model:
        return num_tokens_from_messages(messages, model="gpt-4o-mini-2024-07-18")
    elif "gpt-4o" in model:
        return num_tokens_from_messages(messages, model="gpt-4o-2024-08-06")
    elif "gpt-4" in model:
        return num_tokens_from_messages(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"num_tokens_from_messages() is not implemented for {model}."
        )

    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3
    return num_tokens
```

The notebook verifies this estimator against OpenAI API usage for example messages and model names such as `gpt-3.5-turbo`, `gpt-4`, `gpt-4o`, and `gpt-4o-mini`. The local corpus snapshot omits the credential-dependent verification call but preserves the counting logic and its caveat: model aliases can update over time, so use dated snapshots or refresh estimators when the target model changes.

## Counting tool-call overhead

The notebook also counts messages that include tools. Tool definitions are not free: function names, descriptions, parameter names, parameter descriptions, types, enums, and wrapper formatting all consume prompt tokens.

The source's tool-counting function applies model-specific constants for two groups:

- `gpt-4o` and `gpt-4o-mini`;
- `gpt-3.5-turbo` and `gpt-4`.

It then adds token counts for each function's name and description, each parameter's name/type/description, each enum item, and fixed overhead for function and property formatting. After that, it adds the normal message token count.

Compact structure of the tool-accounting logic:

```python
def num_tokens_for_tools(functions, messages, model):
    if model in ["gpt-4o", "gpt-4o-mini"]:
        func_init = 7
        prop_init = 3
        prop_key = 3
        enum_init = -3
        enum_item = 3
        func_end = 12
    elif model in ["gpt-3.5-turbo", "gpt-4"]:
        func_init = 10
        prop_init = 3
        prop_key = 3
        enum_init = -3
        enum_item = 3
        func_end = 12
    else:
        raise NotImplementedError(
            f"num_tokens_for_tools() is not implemented for {model}."
        )

    encoding = tiktoken.encoding_for_model(model)
    func_token_count = 0

    for f in functions:
        func_token_count += func_init
        function = f["function"]
        line = function["name"] + ":" + function["description"].rstrip(".")
        func_token_count += len(encoding.encode(line))

        properties = function["parameters"]["properties"]
        if properties:
            func_token_count += prop_init
            for name, property_schema in properties.items():
                func_token_count += prop_key
                if "enum" in property_schema:
                    func_token_count += enum_init
                    for item in property_schema["enum"]:
                        func_token_count += enum_item
                        func_token_count += len(encoding.encode(item))
                line = (
                    f"{name}:"
                    f"{property_schema['type']}:"
                    f"{property_schema['description'].rstrip('.')}"
                )
                func_token_count += len(encoding.encode(line))

    if functions:
        func_token_count += func_end

    return num_tokens_from_messages(messages, model) + func_token_count
```

The source verifies the estimator against API usage for a weather tool with a `location` string and a `unit` enum. The important budgeting lesson is that tool schemas should be treated as prompt content. Large tool descriptions, verbose parameter descriptions, and long enum values can materially reduce the remaining context available for retrieved documents and the generated answer.

## RAG prompt budgeting implications

For RAG, token counting belongs in the context assembly path. A robust context builder should reserve room for:

- durable developer or system instructions;
- the user's question and conversation state;
- retrieved chunks, delimiters, titles, source identifiers, and citation metadata;
- tool definitions when tools are available;
- structured-output schema text when applicable;
- the expected answer budget.

Retrieved chunks should be admitted until the request reaches the prompt budget, not simply by a fixed number of chunks. The tokenizer should match the target generation model where possible. If the system uses embeddings and generation models with different encodings, chunking and generation budgeting may need separate token counts.

Model aliases and token accounting rules can change. For repeatable evaluation, store the model name, encoding assumption, prompt token estimate, API-reported usage when available, and any counting helper version in the trace. This makes it possible to distinguish retrieval or prompt regressions from model-specific accounting changes.
