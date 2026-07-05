# Source snapshot

Source metadata:
- source_slug: azure-openai-structured-outputs
- category: prompting techniques
- upstream_url: https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/structured-outputs
- source_markdown: https://github.com/MicrosoftDocs/azure-ai-docs/blob/main/articles/foundry/openai/includes/how-to-structured-outputs-content.md
- license: CC BY 4.0 content / MIT code examples
- pinned_version: microsoft-azure-ai-docs@main
- observed_source_commit: 777f84fbedeb0995f4fdea6c65bee2f2a4af1657
- snapshot_type: normalized documentation digest from source markdown include
- normalization: removed YAML metadata, page chrome, repeated SDK boilerplate, and long generated outputs; retained API shapes, schema rules, limitations, model/API support, and compact examples

---
# Schema-constrained outputs

Structured outputs let an Azure OpenAI model return data that conforms to a JSON Schema supplied with the request. They are stricter than JSON mode: JSON mode only ensures syntactically valid JSON, while structured outputs are intended to make the response match the declared object shape, required fields, enums, arrays, and nested objects.

Use structured outputs when downstream code needs a stable contract, for example:

- extracting fields from unstructured text into typed records;
- returning planner steps or classifications in a predictable object;
- constraining function-call arguments before a tool is executed;
- separating machine-readable answer data from user-facing prose.

The feature can be used in two main ways: response formatting and function calling. In both cases, the practical design pattern is the same: keep the schema narrow, mark every field as required, set every object to reject extra properties, and validate the returned object before relying on it.

## Response format flow

For direct model responses, set `response_format` to `json_schema`, name the schema, set `strict: true`, and provide the object schema. The model response content is then expected to be a JSON object matching the schema.

Compact request shape:

```json
{
  "model": "YOUR_MODEL_DEPLOYMENT_NAME",
  "messages": [
    {
      "role": "system",
      "content": "Extract the event information."
    },
    {
      "role": "user",
      "content": "Alice and Bob are going to a science fair on Friday."
    }
  ],
  "response_format": {
    "type": "json_schema",
    "json_schema": {
      "name": "calendar_event",
      "strict": true,
      "schema": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "date": { "type": "string" },
          "participants": {
            "type": "array",
            "items": { "type": "string" }
          }
        },
        "required": ["name", "date", "participants"],
        "additionalProperties": false
      }
    }
  }
}
```

Expected parsed object shape:

```json
{
  "name": "Science Fair",
  "date": "Friday",
  "participants": ["Alice", "Bob"]
}
```

Python callers can also define schemas with Pydantic and use the OpenAI Python client's parsing helpers. That style is useful when the application already has typed request or response models, but the same Azure OpenAI schema limitations still apply after the Pydantic model is converted to JSON Schema.

## Function calling flow

Structured outputs for function calling are enabled on the function definition by setting `strict: true` and supplying a compliant `parameters` schema. This constrains the generated tool arguments, which is useful when tool execution has side effects or accepts only a small set of valid values.

Important operational note: structured outputs are not supported with parallel function calls. When using structured outputs with tools, set `parallel_tool_calls` to `false` so the model emits one constrained tool call at a time.

Compact tool definition:

```json
{
  "type": "function",
  "function": {
    "name": "query_orders",
    "description": "Query order records.",
    "strict": true,
    "parameters": {
      "type": "object",
      "properties": {
        "status": {
          "type": "string",
          "enum": ["fulfilled", "pending", "canceled"]
        },
        "late_only": {
          "type": "boolean"
        },
        "month": {
          "type": ["string", "null"],
          "description": "Month name or null when unspecified."
        }
      },
      "required": ["status", "late_only", "month"],
      "additionalProperties": false
    }
  }
}
```

The schema makes `status`, `late_only`, and `month` mandatory. `month` is nullable rather than omitted, which keeps the object shape stable while still representing an unknown or optional value.

## Design guidance

Use the schema as an API contract, not just a formatting hint. A good structured-output schema is small enough for the model to satisfy reliably and strict enough for application code to consume without fragile post-processing.

Practical guidance:

- Prefer semantic field names and short descriptions that explain how each field should be used.
- Use enums for closed sets such as status names, modes, categories, or units.
- Use arrays only when the downstream code can handle zero, one, or many items consistently.
- Represent optional fields as a required field whose type includes `null`.
- Keep nested objects shallow where possible; use `$defs` for repeated object shapes.
- Validate the returned object in application code even when strict schema mode is enabled.

# Constraints, model support, and compact examples

Azure OpenAI structured outputs support a subset of JSON Schema. The subset is enough for common typed-output and tool-argument contracts, but it intentionally excludes several validation keywords and places limits on nesting and property counts.

## Supported schema features

Supported JSON Schema types and constructs:

- `string`
- `number`
- `boolean`
- `integer`
- `object`
- `array`
- `enum`
- `anyOf`
- `$defs`
- `$ref`
- recursive schemas

The root schema must be an object. A nested property may use `anyOf`, but the root object itself cannot be `anyOf`.

## Required fields and nullable optionals

All fields and function parameters must appear in the schema's `required` list. To emulate an optional value, make the field required and include `null` in its type.

```json
{
  "type": "object",
  "properties": {
    "location": {
      "type": "string"
    },
    "unit": {
      "type": ["string", "null"],
      "enum": ["F", "C", null]
    }
  },
  "required": ["location", "unit"],
  "additionalProperties": false
}
```

This contract always returns `location` and `unit`. When the unit is unknown, the model should return `"unit": null` instead of omitting the key.

## Object constraints

Every object in the schema must set:

```json
{
  "additionalProperties": false
}
```

This applies to the root object and to nested objects inside arrays, `anyOf`, or `$defs`. The setting prevents undeclared key-value pairs from appearing in the output.

Other object and structure limits:

- A schema can contain up to 100 object properties total.
- Nesting depth is limited to five levels.
- Output key order follows schema property order.

## Unsupported validation keywords

Several type-specific JSON Schema validation keywords are not supported. Put these checks in application validation code instead of relying on the model schema.

| Type | Unsupported keywords |
| --- | --- |
| String | `minLength`, `maxLength`, `pattern`, `format` |
| Number | `minimum`, `maximum`, `multipleOf` |
| Object | `patternProperties`, `unevaluatedProperties`, `propertyNames`, `minProperties`, `maxProperties` |
| Array | `unevaluatedItems`, `contains`, `minContains`, `maxContains`, `minItems`, `maxItems`, `uniqueItems` |

## Nested `anyOf` example

Nested `anyOf` is supported when every branch follows the same structured-output subset. Each object branch still needs complete `required` fields and `additionalProperties: false`.

```json
{
  "type": "object",
  "properties": {
    "item": {
      "anyOf": [
        {
          "type": "object",
          "properties": {
            "name": { "type": "string" },
            "age": { "type": "number" }
          },
          "required": ["name", "age"],
          "additionalProperties": false
        },
        {
          "type": "object",
          "properties": {
            "street": { "type": "string" },
            "city": { "type": "string" }
          },
          "required": ["street", "city"],
          "additionalProperties": false
        }
      ]
    }
  },
  "required": ["item"],
  "additionalProperties": false
}
```

## `$defs` example

Use `$defs` when the same nested shape appears in more than one place, or when a schema is easier to read with named subtypes.

```json
{
  "type": "object",
  "properties": {
    "steps": {
      "type": "array",
      "items": { "$ref": "#/$defs/step" }
    },
    "final_answer": {
      "type": "string"
    }
  },
  "$defs": {
    "step": {
      "type": "object",
      "properties": {
        "explanation": { "type": "string" },
        "output": { "type": "string" }
      },
      "required": ["explanation", "output"],
      "additionalProperties": false
    }
  },
  "required": ["steps", "final_answer"],
  "additionalProperties": false
}
```

## Recursive schema example

Recursive schemas are supported through references. This is useful for tree-like or linked structures.

```json
{
  "type": "object",
  "properties": {
    "linked_list": {
      "$ref": "#/$defs/node"
    }
  },
  "$defs": {
    "node": {
      "type": "object",
      "properties": {
        "value": { "type": "number" },
        "next": {
          "anyOf": [
            { "$ref": "#/$defs/node" },
            { "type": "null" }
          ]
        }
      },
      "required": ["value", "next"],
      "additionalProperties": false
    }
  },
  "required": ["linked_list"],
  "additionalProperties": false
}
```

## Unsupported Azure OpenAI scenarios

Structured outputs are not currently supported with:

- Bring your own data scenarios;
- Assistants;
- Foundry Agents Service;
- `gpt-4o-audio-preview` version `2024-12-17`;
- `gpt-4o-mini-audio-preview` version `2024-12-17`.

## Supported models

The upstream Azure OpenAI documentation lists structured-output support for these model versions:

- `gpt-5.1-codex` version `2025-11-13`
- `gpt-5.1-codex mini` version `2025-11-13`
- `gpt-5.1` version `2025-11-13`
- `gpt-5.1-chat` version `2025-11-13`
- `gpt-5-pro` version `2025-10-06`
- `gpt-5-codex` version `2025-09-11`
- `gpt-5` version `2025-08-07`
- `gpt-5-mini` version `2025-08-07`
- `gpt-5-nano` version `2025-08-07`
- `codex-mini` version `2025-05-16`
- `o3-pro` version `2025-06-10`
- `o3-mini` version `2025-01-31`
- `o1` version `2024-12-17`
- `gpt-4o-mini` version `2024-07-18`
- `gpt-4o` version `2024-08-06`
- `gpt-4o` version `2024-11-20`
- `gpt-4.1` version `2025-04-14`
- `gpt-4.1-nano` version `2025-04-14`
- `gpt-4.1-mini` version `2025-04-14`
- `o4-mini` version `2025-04-16`
- `o3` version `2025-04-16`

## API support

API version `2024-08-01-preview` is the first Azure OpenAI API version that supports structured outputs. The current preview APIs and the GA `v1` API also support the feature.

## Implementation checklist

Before using structured outputs in an application:

- Confirm the target Azure OpenAI deployment uses a supported model version.
- Use API version `2024-08-01-preview` or later, or the GA `v1` API.
- Keep the root schema as an object, not `anyOf`.
- Mark every field as required.
- Use nullable required fields for optional values.
- Set `additionalProperties: false` on every object.
- Avoid unsupported JSON Schema validation keywords.
- Disable parallel tool calls when using structured outputs with tools.
- Validate parsed output in application code before executing side effects.
