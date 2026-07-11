# Evaluation report: eval-baseline-vector

These results are evidence from a small, manually curated benchmark over the pinned corpus and included golden questions; they should not be generalized to other corpora or query distributions.

## Run summary

| Field | Value |
| --- | --- |
| Run ID | eval-baseline-vector |
| Created at | 2026-07-11T08:11:53.214146+00:00 |
| Retrieval mode | baseline-vector |
| Golden set | golden\questions.json |
| Question count | 16 |
| Trace count | 16 |
| JSON artifact | artifacts\eval\eval-baseline-vector.json |
| Case mix | ambiguous_boundary: 5, answerable: 7, multi_category_routing: 2, no_answer: 2 |

## Retrieval mode and configuration

| Field | Value |
| --- | --- |
| Retrieval mode | baseline-vector |
| top_k | 3 |
| max_context_tokens | 1000 |
| output_token_limit | 800 |
| router_category_margin | 0.15 |

## Aggregate metrics

| Metric | Value | Reason |
| --- | --- | --- |
| routing_accuracy | n/a | Not applicable for this run or no eligible golden questions. |
| average_searched_categories | 5 |  |
| hit_rate_at_k | 12/14 questions, 85.7% |  |
| mrr | 0.6071 |  |
| citation_source_match | 12/14 questions, 85.7% |  |
| no_answer_accuracy | 16/16 questions, 100.0% |  |
| average_context_tokens | 609.7 |  |
| average_included_chunks | 2.938 |  |

## Per-question table

| Question | Case type | Status | Top category | Searched categories | Trace | Expected sources | Retrieved sources | Errors |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| q-answerable-001 | answerable | pass | none | prompting techniques, RAG and context handling, RAG evaluation and quality, LLM security and risks, LLM settings, cost, and tokens | artifacts\eval\traces\baseline-vector\trace-6b45c7d4599a49729a2930de17edf196.json | openai-api-prompt-engineering | openai-gpt5-prompting-guide, openai-evaluation-flywheel, openai-api-prompt-engineering | none |
| q-answerable-002 | answerable | pass | none | prompting techniques, RAG and context handling, RAG evaluation and quality, LLM security and risks, LLM settings, cost, and tokens | artifacts\eval\traces\baseline-vector\trace-6f1f6c59c8d64995a1f9a440d0068680.json | azure-ai-search-rag-overview, openai-question-answering-embeddings | microsoft-foundry-rag-evaluators, openai-question-answering-embeddings, owasp-llm04-data-model-poisoning | none |
| q-answerable-003 | answerable | pass | none | prompting techniques, RAG and context handling, RAG evaluation and quality, LLM security and risks, LLM settings, cost, and tokens | artifacts\eval\traces\baseline-vector\trace-214a7b3f7513492396476185acc653c4.json | trec-common-evaluation-measures, ragas-rag-metrics | trec-common-evaluation-measures, microsoft-foundry-rag-evaluators, openai-api-prompt-engineering | none |
| q-answerable-004 | answerable | pass | none | prompting techniques, RAG and context handling, RAG evaluation and quality, LLM security and risks, LLM settings, cost, and tokens | artifacts\eval\traces\baseline-vector\trace-11076a402281405f84b23d4e485d98c1.json | owasp-llm01-prompt-injection | owasp-llm01-prompt-injection | none |
| q-answerable-005 | answerable | pass | none | prompting techniques, RAG and context handling, RAG evaluation and quality, LLM security and risks, LLM settings, cost, and tokens | artifacts\eval\traces\baseline-vector\trace-68b79ff7166841d7ac4d0148ac9938ba.json | openai-token-counting | openai-token-counting, openai-prompt-caching | none |
| q-answerable-006 | answerable | pass | none | prompting techniques, RAG and context handling, RAG evaluation and quality, LLM security and risks, LLM settings, cost, and tokens | artifacts\eval\traces\baseline-vector\trace-5cfdca05cd674cb296c08f23b941202e.json | azure-ai-search-chunk-documents | azure-ai-search-chunk-documents, azure-ai-search-rag-overview | none |
| q-no-answer-001 | no_answer | pass | none | prompting techniques, RAG and context handling, RAG evaluation and quality, LLM security and risks, LLM settings, cost, and tokens | artifacts\eval\traces\baseline-vector\trace-f379613374b54063a904b9d9366ff1da.json | none | owasp-llm08-vector-embedding-weaknesses, openai-rate-limits | none |
| q-no-answer-002 | no_answer | pass | none | prompting techniques, RAG and context handling, RAG evaluation and quality, LLM security and risks, LLM settings, cost, and tokens | artifacts\eval\traces\baseline-vector\trace-164dfa49691545d1a9568877ddf569a2.json | none | azure-ai-search-chunk-documents, owasp-llm04-data-model-poisoning, openai-token-counting | none |
| q-cross-category-001 | ambiguous_boundary | pass | none | prompting techniques, RAG and context handling, RAG evaluation and quality, LLM security and risks, LLM settings, cost, and tokens | artifacts\eval\traces\baseline-vector\trace-e0d31240705a45eda1ae3118b86957ca.json | microsoft-foundry-rag-evaluators, ragas-rag-metrics | microsoft-foundry-rag-evaluators, trec-common-evaluation-measures | none |
| q-cross-category-002 | ambiguous_boundary | pass | none | prompting techniques, RAG and context handling, RAG evaluation and quality, LLM security and risks, LLM settings, cost, and tokens | artifacts\eval\traces\baseline-vector\trace-ee143d2ec450494db9237cbbc2b84669.json | openai-cost-optimization, openai-latency-optimization, azure-ai-search-rag-overview | openai-latency-optimization, owasp-llm02-sensitive-information-disclosure, ragas-rag-metrics | none |
| q-cross-category-003 | ambiguous_boundary | source retrieval miss | none | prompting techniques, RAG and context handling, RAG evaluation and quality, LLM security and risks, LLM settings, cost, and tokens | artifacts\eval\traces\baseline-vector\trace-9baeb9653ed34da4b7a4ba3026b67d05.json | openai-prompt-caching, openai-cost-optimization | openai-gpt5-prompting-guide, openai-api-prompt-engineering, openai-evaluation-flywheel | none |
| q-cross-category-004 | ambiguous_boundary | pass | none | prompting techniques, RAG and context handling, RAG evaluation and quality, LLM security and risks, LLM settings, cost, and tokens | artifacts\eval\traces\baseline-vector\trace-2d07f75c701a401ca2d538506c8634a9.json | owasp-llm01-prompt-injection, owasp-llm08-vector-embedding-weaknesses | owasp-llm02-sensitive-information-disclosure, openai-api-prompt-engineering, owasp-llm01-prompt-injection | none |
| q-cross-category-005 | ambiguous_boundary | pass | none | prompting techniques, RAG and context handling, RAG evaluation and quality, LLM security and risks, LLM settings, cost, and tokens | artifacts\eval\traces\baseline-vector\trace-f5fd99c00600484ebf2440ba9eda426b.json | ragas-rag-metrics, microsoft-foundry-rag-evaluators | openai-question-answering-embeddings, microsoft-foundry-rag-evaluators, azure-ai-search-vector-relevance-ranking | none |
| q-multi-category-001 | multi_category_routing | pass | none | prompting techniques, RAG and context handling, RAG evaluation and quality, LLM security and risks, LLM settings, cost, and tokens | artifacts\eval\traces\baseline-vector\trace-802fbd0688294e33a66f083267a0005f.json | openai-api-prompt-engineering, azure-ai-search-rag-overview, deepeval-rag-metrics, openai-token-counting | openai-latency-optimization, ragas-rag-metrics, openai-token-counting | none |
| q-multi-category-002 | multi_category_routing | source retrieval miss | none | prompting techniques, RAG and context handling, RAG evaluation and quality, LLM security and risks, LLM settings, cost, and tokens | artifacts\eval\traces\baseline-vector\trace-a59b87c722b34744b73b718d00f7fe51.json | owasp-llm08-vector-embedding-weaknesses, azure-ai-search-vector-relevance-ranking, openai-gpt5-prompting-guide, microsoft-foundry-rag-evaluators | openai-latency-optimization, owasp-llm04-data-model-poisoning | none |
| q-security-boundary-001 | answerable | pass | none | prompting techniques, RAG and context handling, RAG evaluation and quality, LLM security and risks, LLM settings, cost, and tokens | artifacts\eval\traces\baseline-vector\trace-da973e98b85f48da90967177551643c1.json | owasp-llm01-prompt-injection | openai-gpt5-prompting-guide, owasp-llm01-prompt-injection | none |

## Request-response pairs

### q-answerable-001

| Field | Value |
| --- | --- |
| Case type | answerable |
| Status | pass |
| No-answer response | no |

**Request**

````text
Which prompt components and instruction design practices can make model responses more reliable and easier to control?
````

**Response**

````text
- Specify the model’s **role/domain**, required **outcome**, relevant **workflow rules**, prohibitions, and **output format**; use examples only when the desired behavior is difficult to describe explicitly. [C1]
- Make requirements **observable and testable**, such as citing source-dependent sentences, refusing to answer when evidence is missing, and avoiding unsupported outside knowledge. [C1]
- For RAG, define clear **context boundaries**, explicit **no-answer behavior**, citation requirements, and formats that expose uncertainty or evidence. [C2]
- Improve prompts iteratively through annotated failures, graders, versioning, and evaluation against consistent, retrieval-aware test cases; distinguish retrieval problems from generation-prompt problems. [C2]
- Pin model snapshots when stable behavior matters and record prompt/model versions, retrieval settings, context, outputs, citations, and validation results to detect regressions. [C3]
````

### q-answerable-002

| Field | Value |
| --- | --- |
| Case type | answerable |
| Status | pass |
| No-answer response | no |

**Request**

````text
How does retrieval augmented generation use retrieved context to ground an answer and reduce unsupported generation?
````

**Response**

````text
- RAG first retrieves document chunks relevant to the user’s question, assembles them within a token budget, and presents them as bounded evidence to the model. [C2]
- The model is instructed to answer from that supplied context, so the retrieved evidence constrains generation and helps reduce unsupported or hallucinated claims—especially when sources are trusted and relevant. [C2] [C3]
- Groundedness evaluates whether the final answer aligns with the context and avoids adding material not supported by it; retrieval quality and answer grounding are evaluated as separate failure surfaces. [C1] [C2]
- This approach does not guarantee correctness: poisoned, irrelevant, or untrusted sources can undermine grounding, so source identity, integrity, authority, and citations should be validated. [C3]
````

### q-answerable-003

| Field | Value |
| --- | --- |
| Case type | answerable |
| Status | pass |
| No-answer response | no |

**Request**

````text
Which retrieval metrics can be used to compare ranked search results in a golden-set evaluation?
````

**Response**

````text
- **Recall@k** and **precision@k** measure how much relevant content appears within the top *k* results and how useful that context is, respectively. [C1]
- **MRR** or first-relevant rank measures how quickly the first relevant result appears. [C1]
- **Average Precision (AP)** and **Mean Average Precision (MAP)** evaluate ranking quality across more of the result list. [C1]
- **NDCG** measures ranking quality relative to an ideal ordering, while **XDCG** focuses on top-*k* ranking quality. [C2]
- **R-precision**, **bpref** for incomplete judgments, and **GMAP** for robustness across difficult queries can also be used. [C1]
````

### q-answerable-004

| Field | Value |
| --- | --- |
| Case type | answerable |
| Status | pass |
| No-answer response | no |

**Request**

````text
What are prompt injection risks in LLM applications, and which mitigations can reduce their impact?
````

**Response**

````text
- Prompt injection occurs when crafted user inputs or other model-parsed data alter an LLM’s behavior or output unexpectedly; the input may be hidden or unreadable to humans. [C1]
- Risks arise when applications combine instructions with untrusted user content, retrieved documents, tool outputs, files, or websites. The model may treat that data as instructions, causing harmful content, sensitive-data disclosure, guideline violations, unauthorized actions, or manipulated decisions. [C1]
- RAG and fine-tuning do not eliminate the risk: RAG can introduce additional untrusted content, while fine-tuning does not prevent hostile inputs from influencing inference-time behavior. [C1]
- Mitigations include application-level safeguards to limit the impact of injected instructions, alongside ongoing model training and safety updates for more durable jailbreak resistance. [C1]
````

### q-answerable-005

| Field | Value |
| --- | --- |
| Case type | answerable |
| Status | pass |
| No-answer response | no |

**Request**

````text
How can token counting help estimate prompt size and manage prompt budgets before sending a request to a model?
````

**Response**

````text
- Count the prompt’s tokens before sending it, using the tokenizer that matches the target model where possible; tokenization can differ across models, and model aliases or accounting rules may change. [C1]
- Build the estimate from every prompt component: system/developer instructions, conversation and user input, retrieved text plus delimiters and citation metadata, tool definitions, output schemas, and the expected response budget. [C1]
- Reserve space for the model’s response, then admit retrieved chunks until the total reaches the prompt budget rather than selecting a fixed number of chunks. [C1]
- Log the estimated prompt tokens, model, encoding assumption, and helper version, and compare them with API-reported usage when available to detect estimation errors or prompt regressions. [C1]
- For repeated prompts, also track total and cached prompt tokens; this helps evaluate whether stable prefixes are reducing input cost and latency. [C2]
````

### q-answerable-006

| Field | Value |
| --- | --- |
| Case type | answerable |
| Status | pass |
| No-answer response | no |

**Request**

````text
Why does a RAG system usually need chunking and embeddings before vector search can retrieve useful passages?
````

**Response**

````text
A RAG system usually needs **chunking** because whole documents may exceed embedding or chat-model input limits, causing truncation, and because a document covering many topics is a poor single retrieval unit. Smaller, focused chunks can match a user’s question more precisely. [C1]

It needs **embeddings** because vector search compares numerical representations of meaning; embedding each chunk lets the system retrieve chunks that are semantically similar to the query rather than relying only on exact words. Chunking should occur before embedding and vector storage, with enough metadata retained to keep each retrieved passage understandable. [C2]
````

### q-no-answer-001

| Field | Value |
| --- | --- |
| Case type | no_answer |
| Status | pass |
| No-answer response | yes |

**Request**

````text
What uptime warranty does this project provide for an enterprise production deployment?
````

**Response**

````text
There is not enough evidence in the selected context to answer.
````

### q-no-answer-002

| Field | Value |
| --- | --- |
| Case type | no_answer |
| Status | pass |
| No-answer response | yes |

**Request**

````text
Which private customer database records were used to build this corpus?
````

**Response**

````text
There is not enough evidence in the selected context to answer.
````

### q-cross-category-001

| Field | Value |
| --- | --- |
| Case type | ambiguous_boundary |
| Status | pass |
| No-answer response | no |

**Request**

````text
When evaluating a RAG answer, how do groundedness checks differ from retrieval quality metrics?
````

**Response**

````text
- **Groundedness** evaluates the generated answer after retrieval: whether its claims are supported by the supplied context and whether it avoids fabrication. [C2]
- **Retrieval quality metrics** evaluate the retrieval step before generation: whether relevant chunks or documents were selected and ranked well. Without relevance labels, retrieval may use an LLM judge; with labels/qrels, metrics include NDCG, XDCG, MRR, recall@k, and precision@k. [C2][C3]
- Thus, retrieval metrics ask **“Did the system find the right evidence?”**, while groundedness asks **“Did the answer stay within that evidence?”** They are complementary, since good retrieval does not guarantee a grounded answer. [C1][C3]
````

### q-cross-category-002

| Field | Value |
| --- | --- |
| Case type | ambiguous_boundary |
| Status | pass |
| No-answer response | no |

**Request**

````text
How can limiting retrieved context reduce latency, token usage, and citation noise in a RAG workflow?
````

**Response**

````text
- Filter retrieved context to keep only high-scoring, answer-relevant passages; drop off-topic or low-scoring chunks. This reduces input tokens and therefore can lower latency and cost. [C1]
- Remove boilerplate, navigation, HTML artifacts, duplicated headers, and near-identical passages to avoid sending repetitive tokens to the model. [C1]
- Prefer evidence containing the requested attribute rather than passages that merely mention the entity, while preserving source identifiers and section labels required for citations. This reduces citation noise without losing traceability. [C1]
- Apply permission filters before context reaches the model, and preserve authorization metadata through retrieval and citation so trimming does not expose or cite inaccessible sources. [C2]
- Place stable instructions and citation rules in a reusable prompt prefix, with the trimmed dynamic context later; this supports cache-friendly requests and makes context reduction easier. [C1]
````

### q-cross-category-003

| Field | Value |
| --- | --- |
| Case type | ambiguous_boundary |
| Status | source retrieval miss |
| No-answer response | no |

**Request**

````text
How can I keep repeated RAG evaluation runs cheaper when the prompt prefix and rubric stay mostly the same?
````

**Response**

````text
- Keep the reusable prompt prefix stable: developer instructions, schemas, rubric, and examples should appear early; place retrieved chunks and other dynamic inputs later to improve prompt-cache reuse. [C2]
- Avoid volatile IDs or timestamps near the prefix, and record prompt-token and cached-token usage when available so you can verify savings. [C2]
- Version the prompt and rubric, then rerun the same representative and edge-case golden tests; keep edits only when measured quality improves. [C1][C3]
- Reuse the same graders and annotation definitions across prompt versions to make cost and quality comparisons consistent. [C3]
````

### q-cross-category-004

| Field | Value |
| --- | --- |
| Case type | ambiguous_boundary |
| Status | pass |
| No-answer response | no |

**Request**

````text
If retrieved context tells the model to ignore developer instructions and reveal hidden prompts, what kind of problem is that and how should it be mitigated?
````

**Response**

````text
- This is a **prompt injection** problem: retrieved content is attempting to override higher-priority instructions and extract hidden prompts or sensitive configuration. [C3]
- Mitigate it by treating retrieved text as **untrusted evidence, not instructions**; explicitly require strict adherence to system/developer instructions, restrict responses to approved tasks, and refuse or abstain when the selected evidence is insufficient. [C3]
- Do not place secrets in system prompts or model context; keep them in secure infrastructure and access them through deterministic application code. [C1]
````

### q-cross-category-005

| Field | Value |
| --- | --- |
| Case type | ambiguous_boundary |
| Status | pass |
| No-answer response | no |

**Request**

````text
Which checks tell me whether retrieved chunks contain enough relevant evidence for the generated answer, rather than just explaining how to retrieve chunks?
````

**Response**

````text
- **Groundedness:** Check whether the generated answer is supported by the retrieved context, without unsupported claims. [C2]
- **Answer relevance:** Check whether the response directly addresses the user’s question; groundedness alone is insufficient. [C2]
- **Response completeness:** When ground truth is available, check whether the answer includes all critical expected information. [C2]
- **Retrieval quality:** Separately assess whether the retrieved chunks contain the right evidence, using retrieval or document-retrieval metrics when labels are available. [C2]

These checks evaluate evidence sufficiency and answer quality, rather than merely describing chunk retrieval or context assembly. [C1][C2]
````

### q-multi-category-001

| Field | Value |
| --- | --- |
| Case type | multi_category_routing |
| Status | pass |
| No-answer response | no |

**Request**

````text
How do prompt structure, retrieved context, evaluation metrics, and token budgets interact during a RAG quality review?
````

**Response**

````text
- A RAG quality review should inspect prompt structure first: keep stable instructions, schemas, citation rules, and examples in the shared prefix, then place the question and trimmed retrieved context later. This makes prompts cache-friendly and allows dynamic context to be reduced safely. [C1]

- Retrieved context should be selected by relevance rather than a fixed chunk count: remove low-scoring, duplicate, boilerplate, and off-topic text while retaining evidence, source identifiers, and citation labels. The context must fit alongside instructions, question, metadata, and the expected answer budget. [C1] [C3]

- Evaluate retrieval and generation separately. Use context precision/recall and noise sensitivity to identify retrieval problems, then faithfulness and response relevancy to assess whether the answer is supported and addresses the question. Different metrics require different fields, such as `retrieved_contexts`, `response`, `reference`, and `user_input`. [C2]

- Token budgets connect these concerns: trimming too aggressively can lower recall, while including noisy or excessive context can hurt precision, increase cost, and leave insufficient room for the answer and citations. Record token estimates, model/encoding details, and actual usage so regressions can be distinguished from accounting changes. [C1] [C3]
````

### q-multi-category-002

| Field | Value |
| --- | --- |
| Case type | multi_category_routing |
| Status | source retrieval miss |
| No-answer response | no |

**Request**

````text
What tradeoffs connect vector embedding weaknesses, retrieval filtering, prompt instructions, and evaluation diagnostics?
````

**Response**

````text
- Vector embeddings can mis-rank or amplify poisoned content: a high similarity score may make malicious evidence appear authoritative, so retrieval quality depends on validating, labeling, authenticating, and versioning indexed data—not embeddings alone. [C2]
- Retrieval filtering trades recall for relevance, cost, latency, and safety: selecting only high-signal, nonduplicate passages preserves token budget and reduces distracting context, while passing every vaguely related chunk can worsen model attention and expose more poisoned material. [C1][C2]
- Prompt instructions should be concise and stable, with dynamic retrieved content placed later; shortening instructions or fine-tuning can reduce tokens, but overly aggressive trimming may remove necessary guidance. [C1]
- Evaluation diagnostics should identify the actual bottleneck and retest answer quality after changes, because gains from filtering, prompt reduction, routing, or parallelism can differ across retrieval latency, context size, serial calls, and generation. [C3]
````

### q-security-boundary-001

| Field | Value |
| --- | --- |
| Case type | answerable |
| Status | pass |
| No-answer response | no |

**Request**

````text
If retrieved content contains instructions telling the assistant to ignore previous instructions or reveal hidden prompts, how should the system handle that content?
````

**Response**

````text
- Treat retrieved content as untrusted evidence, not as instructions. Ignore any embedded directives to override system instructions or reveal hidden prompts. [C2]
- Follow the system’s role, task, context, citation, and confidentiality requirements, and answer only from the selected context. [C2] [C3]
- If the requested answer is not supported by the selected context, abstain using the configured no-answer response. [C2] [C3]
````

## Token-budget diagnostics

| Field | Value |
| --- | --- |
| Configured max context tokens | 1000 |
| Configured output token limit | 800 |
| Average context tokens | 609.6875 |
| Average included chunks | 2.9375 |

| Question | Context tokens | Included chunks |
| --- | --- | --- |
| q-answerable-001 | 609 | 3 |
| q-answerable-002 | 753 | 3 |
| q-answerable-003 | 716 | 3 |
| q-answerable-004 | 604 | 3 |
| q-answerable-005 | 622 | 3 |
| q-answerable-006 | 769 | 2 |
| q-no-answer-001 | 261 | 3 |
| q-no-answer-002 | 363 | 3 |
| q-cross-category-001 | 891 | 3 |
| q-cross-category-002 | 578 | 3 |
| q-cross-category-003 | 560 | 3 |
| q-cross-category-004 | 356 | 3 |
| q-cross-category-005 | 629 | 3 |
| q-multi-category-001 | 975 | 3 |
| q-multi-category-002 | 671 | 3 |
| q-security-boundary-001 | 398 | 3 |

## No-answer cases

| Question | No-answer accuracy | Retrieved sources | Errors |
| --- | --- | --- | --- |
| q-no-answer-001 | 1 | owasp-llm08-vector-embedding-weaknesses, openai-rate-limits | none |
| q-no-answer-002 | 1 | azure-ai-search-chunk-documents, owasp-llm04-data-model-poisoning, openai-token-counting | none |

## Citation validation failures

None recorded.

## Limitations and interpretation notes

- These results are evidence from a small, manually curated benchmark over the pinned corpus and included golden questions; they should not be generalized to other corpora or query distributions.
- The benchmark is small enough that a difference between modes may represent only one changed question; the current hit-rate difference is exactly one of 14 retrieval-scored questions.
- Top-category routing accuracy can be lower than retrieval hit rate because soft multi-category routing may search the expected category even when it is not ranked first.
- Category margins are heuristic rather than calibrated probabilities.
- Retrieval and routing configuration was adjusted while inspecting this same small benchmark, so these results are useful engineering evidence, not holdout validation.
- Citation validation checks whether cited chunk IDs were included in the selected context; it does not prove claim-level factual correctness.
- No-answer accuracy depends on the selected context and generation behavior for this run.
- Token diagnostics use recorded estimates and model usage when available; provider-side accounting can differ.
