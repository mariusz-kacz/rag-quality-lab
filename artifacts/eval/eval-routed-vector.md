# Evaluation report: eval-routed-vector

These results are evidence from a small, manually curated benchmark over the pinned corpus and included golden questions; they should not be generalized to other corpora or query distributions.

## Run summary

| Field | Value |
| --- | --- |
| Run ID | eval-routed-vector |
| Created at | 2026-07-11T08:14:54.388775+00:00 |
| Retrieval mode | routed-vector |
| Golden set | golden\questions.json |
| Question count | 16 |
| Trace count | 16 |
| JSON artifact | artifacts\eval\eval-routed-vector.json |
| Case mix | ambiguous_boundary: 5, answerable: 7, multi_category_routing: 2, no_answer: 2 |

## Retrieval mode and configuration

| Field | Value |
| --- | --- |
| Retrieval mode | routed-vector |
| top_k | 3 |
| max_context_tokens | 1000 |
| output_token_limit | 800 |
| router_category_margin | 0.15 |

## Aggregate metrics

| Metric | Value | Reason |
| --- | --- | --- |
| routing_accuracy | 7/12 questions, 58.3% |  |
| average_searched_categories | 2.312 |  |
| hit_rate_at_k | 13/14 questions, 92.9% |  |
| mrr | 0.6786 |  |
| citation_source_match | 13/14 questions, 92.9% |  |
| no_answer_accuracy | 16/16 questions, 100.0% |  |
| average_context_tokens | 597.8 |  |
| average_included_chunks | 2.812 |  |

## Per-question table

| Question | Case type | Status | Top category | Searched categories | Trace | Expected sources | Retrieved sources | Errors |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| q-answerable-001 | answerable | pass | prompting techniques | prompting techniques | artifacts\eval\traces\routed-vector\trace-36ddf058f940418ba4c597b49fba2ef8.json | openai-api-prompt-engineering | openai-gpt5-prompting-guide, openai-api-prompt-engineering | none |
| q-answerable-002 | answerable | pass | RAG and context handling | RAG and context handling | artifacts\eval\traces\routed-vector\trace-25ea5cc90de64080a7eef35f50f92c07.json | azure-ai-search-rag-overview, openai-question-answering-embeddings | openai-question-answering-embeddings, azure-ai-search-rag-overview | none |
| q-answerable-003 | answerable | pass | RAG evaluation and quality | RAG evaluation and quality | artifacts\eval\traces\routed-vector\trace-5f271e6ada7a415d8c8f788961f16f42.json | trec-common-evaluation-measures, ragas-rag-metrics | trec-common-evaluation-measures, microsoft-foundry-rag-evaluators | none |
| q-answerable-004 | answerable | pass | LLM security and risks | LLM security and risks | artifacts\eval\traces\routed-vector\trace-f5a44ae3fc974a4f9df99548531052ee.json | owasp-llm01-prompt-injection | owasp-llm01-prompt-injection | none |
| q-answerable-005 | answerable | pass | LLM settings, cost, and tokens | LLM settings, cost, and tokens, prompting techniques | artifacts\eval\traces\routed-vector\trace-be162d1b63304cf88da79a914adda8e7.json | openai-token-counting | openai-token-counting, openai-prompt-caching | none |
| q-answerable-006 | answerable | pass | RAG and context handling | RAG and context handling, RAG evaluation and quality | artifacts\eval\traces\routed-vector\trace-dc180d12ce5a4dbcb6a420be6d318d19.json | azure-ai-search-chunk-documents | azure-ai-search-chunk-documents, azure-ai-search-rag-overview | none |
| q-no-answer-001 | no_answer | pass | LLM settings, cost, and tokens | LLM settings, cost, and tokens, RAG evaluation and quality, LLM security and risks | artifacts\eval\traces\routed-vector\trace-2257f8206c0f4e669b05a796956950a4.json | none | owasp-llm08-vector-embedding-weaknesses, openai-rate-limits | none |
| q-no-answer-002 | no_answer | pass | RAG evaluation and quality | RAG evaluation and quality, prompting techniques, RAG and context handling, LLM security and risks, LLM settings, cost, and tokens | artifacts\eval\traces\routed-vector\trace-3b3754578bd444ada13dc96917168877.json | none | azure-ai-search-chunk-documents, owasp-llm04-data-model-poisoning, openai-token-counting | none |
| q-cross-category-001 | ambiguous_boundary | pass | RAG evaluation and quality | RAG evaluation and quality | artifacts\eval\traces\routed-vector\trace-b509c67f21c14422a7e3e21e1dfe9eb8.json | microsoft-foundry-rag-evaluators, ragas-rag-metrics | microsoft-foundry-rag-evaluators, trec-common-evaluation-measures | none |
| q-cross-category-002 | ambiguous_boundary | pass | RAG evaluation and quality | RAG evaluation and quality, RAG and context handling, LLM settings, cost, and tokens | artifacts\eval\traces\routed-vector\trace-ad6e507c27c34de4b5c6393428f9360e.json | openai-cost-optimization, openai-latency-optimization, azure-ai-search-rag-overview | openai-latency-optimization, ragas-rag-metrics, openai-rate-limits | none |
| q-cross-category-003 | ambiguous_boundary | route filter miss | RAG evaluation and quality | RAG evaluation and quality, prompting techniques | artifacts\eval\traces\routed-vector\trace-ab1bf170f48b443cbb41ac50cca8ba2a.json | openai-prompt-caching, openai-cost-optimization | openai-gpt5-prompting-guide, openai-api-prompt-engineering, openai-evaluation-flywheel | none |
| q-cross-category-004 | ambiguous_boundary | pass | prompting techniques | prompting techniques, RAG and context handling, LLM security and risks | artifacts\eval\traces\routed-vector\trace-fda5c91c7ca347d89cd58f0d13ab7ec7.json | owasp-llm01-prompt-injection, owasp-llm08-vector-embedding-weaknesses | owasp-llm02-sensitive-information-disclosure, openai-api-prompt-engineering, owasp-llm01-prompt-injection | none |
| q-cross-category-005 | ambiguous_boundary | pass | RAG and context handling | RAG and context handling, RAG evaluation and quality | artifacts\eval\traces\routed-vector\trace-0ae2eae95de64d3bb3ef912c8adacdba.json | ragas-rag-metrics, microsoft-foundry-rag-evaluators | openai-question-answering-embeddings, microsoft-foundry-rag-evaluators, azure-ai-search-vector-relevance-ranking | none |
| q-multi-category-001 | multi_category_routing | pass | RAG evaluation and quality | RAG evaluation and quality, LLM settings, cost, and tokens | artifacts\eval\traces\routed-vector\trace-a526e40f76334a569e889dfe93bf208c.json | openai-api-prompt-engineering, azure-ai-search-rag-overview, deepeval-rag-metrics, openai-token-counting | openai-latency-optimization, ragas-rag-metrics, openai-token-counting | none |
| q-multi-category-002 | multi_category_routing | pass | prompting techniques | prompting techniques, RAG and context handling, RAG evaluation and quality, LLM settings, cost, and tokens | artifacts\eval\traces\routed-vector\trace-bfb892eb1ac74e5e82684e0031f6abf9.json | owasp-llm08-vector-embedding-weaknesses, azure-ai-search-vector-relevance-ranking, openai-gpt5-prompting-guide, microsoft-foundry-rag-evaluators | openai-latency-optimization, azure-ai-search-vector-relevance-ranking | none |
| q-security-boundary-001 | answerable | pass | prompting techniques | prompting techniques, RAG and context handling, RAG evaluation and quality, LLM security and risks | artifacts\eval\traces\routed-vector\trace-1c6d8ed5573b421597c8929fbc47e408.json | owasp-llm01-prompt-injection | openai-gpt5-prompting-guide, owasp-llm01-prompt-injection | none |

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
- Define the model’s role or domain, desired outcome, relevant workflow rules, prohibitions, and output format; use examples only when behavior is difficult to specify directly. [C1]
- Make instructions explicit and observable—for example, require context-only answers, sentence-level citations, and a precise no-answer response instead of vague directions such as “be accurate.” [C1]
- Version prompts in code with typed inputs, code review, tests, fixtures, and evaluation cases, rather than relying on invisible prompt settings. [C3]
- Pin production applications to model snapshots and test prompts after model changes, recording retrieval settings, prompt versions, selected context, outputs, citations, and validation results. [C2]
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
- RAG retrieves semantically relevant chunks for the user’s question, ranks them, and assembles a bounded context while preserving clear source boundaries. [C1]
- The model is explicitly instructed to answer from that supplied evidence, so the retrieved content grounds the response rather than relying only on the model’s internal knowledge. [C1]
- Retrieval can combine keyword, vector, and semantic ranking to find relevant material even when the question’s wording differs from the source text. [C2]
- If the evidence does not contain an answer, the system should define explicit no-answer behavior; inspecting retrieval separately from generation helps identify unsupported responses. [C1]
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
- **Recall@k, precision@k, and MRR** (or first relevant rank) can compare whether relevant results appear and how quickly they appear. [C1]
- **AP/MAP** can evaluate ranking quality across more of the result list; **bpref** is useful when relevance judgments are incomplete. [C1]
- **GMAP** and per-question diagnostics can assess robustness across difficult queries. [C1]
- **NDCG** measures ranking quality against an ideal ordering, while **XDCG** focuses on top-*k* ranking quality. [C2]
- Other available comparisons include **Fidelity**, **Max Relevance**, and **Holes** for missing relevance judgments. [C2]
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
- **Prompt injection** occurs when user input or other model-parsed content changes an LLM’s behavior or output in unintended ways. This is especially risky when applications combine instructions with untrusted user input, retrieved documents, tool outputs, files, or websites in one context. [C1]
- Potential impacts include bypassing guidelines, generating harmful content, exposing sensitive information, triggering unauthorized actions, or influencing decisions. Indirect injections can be hidden in external content and need not be readable to humans, only interpretable by the model. [C1]
- **Mitigations** should use application-level safeguards to limit the impact of injected instructions, including controls around untrusted content and authorization of model-triggered actions. RAG and fine-tuning may improve grounding or behavior, but neither eliminates prompt-injection risk. [C1]
- Durable resistance to jailbreak-style attacks also requires ongoing model training and safety updates; application safeguards reduce impact but do not fully solve the underlying inference-time vulnerability. [C1]
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
- Token counting estimates how many tokens a request will use before submission, helping ensure the prompt stays within the model’s budget and leaves room for the expected answer. [C1]
- Count all major components: system/developer instructions, conversation and user input, retrieved content, delimiters and metadata, tool definitions, output schemas, and the expected completion. Add retrieved chunks until the token budget is nearly reached rather than selecting a fixed number. [C1]
- Use the tokenizer for the target generation model, since encodings and accounting rules can differ; record the model, encoding assumption, estimate, API-reported usage, and counting-helper version for evaluation. [C1]
- After sending requests, compare estimates with API usage and log total prompt and completion tokens, model, template version, and related metadata to improve future budgeting and detect changes. [C2]
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
- **Chunking** splits large or broad documents into smaller, semantically focused passages. This avoids embedding and chat-model input limits, prevents truncation, and lets retrieval match a question to a specific section rather than an entire document. [C1]
- **Embeddings** convert those chunks into vectors that represent their semantic meaning; vector search then compares the query vector with chunk vectors to find relevant passages. [C2]
- Without chunking, a vector may represent too many unrelated topics, reducing retrieval precision; without embeddings, vector search lacks the semantic representations needed for similarity matching. [C1][C2]
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
- **Groundedness checks evaluate the generated answer after retrieval**: whether its claims are supported by the supplied context and whether it avoids fabrication. [C2]
- **Retrieval quality metrics evaluate the retrieval step before generation**: whether relevant chunks or documents were selected and ranked for the query. [C2]
- Without ground-truth relevance labels, retrieval can be judged with an LLM-based relevance evaluator; with labels or qrels, document-retrieval metrics such as NDCG, XDCG, and Fidelity can be used. [C2]
- Thus, retrieval metrics ask whether the system found the right evidence, while groundedness asks whether the model stayed within that evidence when answering. Both are needed because good retrieval does not guarantee a grounded answer. [C1]
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
- Limit `top_k` or impose a context budget, then remove low-scoring, off-topic, duplicated, and boilerplate content. This reduces retrieved input tokens and therefore token-related latency and cost, especially when tokens per minute are the bottleneck. [C1] [C3]
- Keep only passages containing evidence for the user’s specific attribute or question, rather than passages that merely mention the entity. Smaller prompts give the model less context to process and reduce irrelevant evidence that can distort the answer. [C1] [C2]
- Preserve source identifiers and section labels while trimming everything else unnecessary for citations. This reduces citation noise without removing the metadata needed to produce grounded citations. [C1]
- Place stable instructions, schemas, and citation rules in a reusable prompt prefix, with the trimmed retrieved context later in the prompt. This supports cache-friendly requests and makes dynamic context easier to reduce. [C1]
````

### q-cross-category-003

| Field | Value |
| --- | --- |
| Case type | ambiguous_boundary |
| Status | route filter miss |
| No-answer response | no |

**Request**

````text
How can I keep repeated RAG evaluation runs cheaper when the prompt prefix and rubric stay mostly the same?
````

**Response**

````text
- Put the stable prompt prefix first: reusable instructions, schemas, and rubric/examples; place dynamic user queries and retrieved chunks afterward. This improves provider-side prompt-cache reuse and makes context easier to trim. [C2]
- Keep the prefix truly stable by avoiding volatile IDs, timestamps, or other changing content near its beginning. [C2]
- Record prompt-token and cached-token usage when available so you can verify that repeated evaluations are benefiting from caching. [C2]
- Version the stable prompt and rubric, then rerun the same representative and edge-case evaluations after changes rather than judging individual successful answers. [C1] [C3]
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
- This is a **prompt-injection attack**, specifically indirect injection through retrieved content, where untrusted text attempts to override higher-priority instructions and extract hidden prompts or configuration. [C3]
- Mitigate it by treating retrieved content as **untrusted evidence, not instructions**; explicitly require adherence to system instructions, restrict responses to approved tasks and selected context, and refuse or abstain when evidence is insufficient. [C3]
- Do not place secrets in prompts or model context; keep them in secure infrastructure and access them through deterministic application code. [C1]
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
- **Groundedness:** Check whether the generated answer is supported by the retrieved context rather than inventing claims. [C2]
- **Relevance:** Check whether the answer directly addresses the user’s question; groundedness alone does not ensure this. [C2]
- **Completeness:** When ground truth or expected information is available, check whether the answer contains all critical expected points. [C2]
- **Retrieval quality:** Evaluate whether the retrieved chunks contain the right evidence in the first place, separately from answer-generation quality. [C1][C2]
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
- A RAG quality review should examine prompt structure first: keep stable instructions, schemas, citation rules, and examples in a reusable prefix, followed by the question and selectively trimmed retrieved context [C1]. This makes context easier to reduce while preserving citation metadata and answer space [C1].
- Retrieved context should be judged separately from generation: context precision and recall assess whether useful evidence was retrieved, while faithfulness and response relevancy assess whether the answer is supported and addresses the question [C2].
- Token budgets connect these concerns: admit chunks based on available prompt capacity—not a fixed chunk count—while reserving tokens for instructions, the question, metadata, and the expected answer [C3]. Trimming noisy, duplicated, or low-scoring passages can reduce cost and improve signal, but excessive trimming may lower context recall [C1][C2].
- The review should record `user_input`, retrieved contexts, response, references where needed, token estimates, model/encoding assumptions, and actual usage so metric changes can be distinguished from prompt or token-accounting changes [C2][C3].
````

### q-multi-category-002

| Field | Value |
| --- | --- |
| Case type | multi_category_routing |
| Status | pass |
| No-answer response | no |

**Request**

````text
What tradeoffs connect vector embedding weaknesses, retrieval filtering, prompt instructions, and evaluation diagnostics?
````

**Response**

````text
- **Vector embeddings are useful but imperfect:** retrieval quality depends on compatible embedding models, the right similarity metric, chunk size/overlap, and approximate-search settings; hybrid or semantic ranking may be needed when pure vector ranking is insufficient. [C3]
- **Filtering improves the tradeoff between relevance, cost, and latency:** selecting only high-signal, nonduplicate passages preserves token budget and reduces distracting context, but overly narrow filtering can remove needed evidence; increasing `k` may help when the model needs more candidates. [C1][C3]
- **Prompt instructions should complement retrieval rather than compensate for poor retrieval:** durable instructions, schemas, and examples can be kept stable and placed before dynamic retrieved content, supporting caching while leaving context focused on relevant evidence. [C1]
- **Evaluation diagnostics reveal which tradeoff to adjust:** inspect top results and scores, verify embedding compatibility, compare approximate retrieval with exhaustive KNN, and retest after tuning; the measured bottleneck may be recall, context size, retrieval latency, serial routing, or answer generation. [C2][C3]
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
- Treat retrieved content as untrusted evidence, not as instructions. Ignore any embedded request to override system instructions or reveal hidden prompts. [C2]
- Continue following the system’s role, constraints, citation requirements, and approved-task limits; answer only from the selected context. [C2]
- If the content does not provide sufficient evidence, abstain using the configured no-answer response rather than relying on outside knowledge. [C2]
````

## Token-budget diagnostics

| Field | Value |
| --- | --- |
| Configured max context tokens | 1000 |
| Configured output token limit | 800 |
| Average context tokens | 597.8125 |
| Average included chunks | 2.8125 |

| Question | Context tokens | Included chunks |
| --- | --- | --- |
| q-answerable-001 | 433 | 3 |
| q-answerable-002 | 581 | 2 |
| q-answerable-003 | 707 | 2 |
| q-answerable-004 | 604 | 3 |
| q-answerable-005 | 622 | 3 |
| q-answerable-006 | 769 | 2 |
| q-no-answer-001 | 261 | 3 |
| q-no-answer-002 | 363 | 3 |
| q-cross-category-001 | 891 | 3 |
| q-cross-category-002 | 626 | 3 |
| q-cross-category-003 | 560 | 3 |
| q-cross-category-004 | 356 | 3 |
| q-cross-category-005 | 629 | 3 |
| q-multi-category-001 | 975 | 3 |
| q-multi-category-002 | 790 | 3 |
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
