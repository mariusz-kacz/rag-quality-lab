# Evaluation report: eval-routed-vector

## Run summary

| Field | Value |
| --- | --- |
| Run ID | eval-routed-vector |
| Created at | 2026-07-10T11:25:42.019113+00:00 |
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
| routing_accuracy | 0.5833 |  |
| fallback_count | 0 |  |
| fallback_rate | 0 |  |
| average_searched_categories | 2.312 |  |
| hit_rate_at_k | 0.9286 |  |
| mrr | 0.6786 |  |
| citation_source_match | 0.9286 |  |
| no_answer_accuracy | 1 |  |
| average_context_tokens | 597.8 |  |
| average_included_chunks | 2.812 |  |

## Per-question table

| Question | Case type | Status | Top category | Searched categories | Global fallback | Trace | Expected sources | Retrieved sources | Errors |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| q-answerable-001 | answerable | pass | prompting techniques | prompting techniques | no | artifacts\eval\traces\routed-vector\trace-1ec3130e708a4660a32bf9a80d8f9622.json | openai-api-prompt-engineering | openai-gpt5-prompting-guide, openai-api-prompt-engineering | none |
| q-answerable-002 | answerable | pass | RAG and context handling | RAG and context handling | no | artifacts\eval\traces\routed-vector\trace-6e845fdaaa5a4ae5b857d52c2372489a.json | azure-ai-search-rag-overview, openai-question-answering-embeddings | openai-question-answering-embeddings, azure-ai-search-rag-overview | none |
| q-answerable-003 | answerable | pass | RAG evaluation and quality | RAG evaluation and quality | no | artifacts\eval\traces\routed-vector\trace-f3a497f788134aca9537a430af38d399.json | trec-common-evaluation-measures, ragas-rag-metrics | trec-common-evaluation-measures, microsoft-foundry-rag-evaluators | none |
| q-answerable-004 | answerable | pass | LLM security and risks | LLM security and risks | no | artifacts\eval\traces\routed-vector\trace-4f1a162876284995919104adb7ab6792.json | owasp-llm01-prompt-injection | owasp-llm01-prompt-injection | none |
| q-answerable-005 | answerable | pass | LLM settings, cost, and tokens | LLM settings, cost, and tokens, prompting techniques | no | artifacts\eval\traces\routed-vector\trace-dbc46405eb894c67aa3eb491ef38e212.json | openai-token-counting | openai-token-counting, openai-prompt-caching | none |
| q-answerable-006 | answerable | pass | RAG and context handling | RAG and context handling, RAG evaluation and quality | no | artifacts\eval\traces\routed-vector\trace-f75b0f167cb9498c905a02a62d5c4c1c.json | azure-ai-search-chunk-documents | azure-ai-search-chunk-documents, azure-ai-search-rag-overview | none |
| q-no-answer-001 | no_answer | pass | LLM settings, cost, and tokens | LLM settings, cost, and tokens, RAG evaluation and quality, LLM security and risks | no | artifacts\eval\traces\routed-vector\trace-886d5a23eed94750a9e7a63d5c64005b.json | none | owasp-llm08-vector-embedding-weaknesses, openai-rate-limits | none |
| q-no-answer-002 | no_answer | pass | RAG evaluation and quality | RAG evaluation and quality, prompting techniques, RAG and context handling, LLM security and risks, LLM settings, cost, and tokens | no | artifacts\eval\traces\routed-vector\trace-82942bd02cfe40049bb1d9de24eb2de7.json | none | azure-ai-search-chunk-documents, owasp-llm04-data-model-poisoning, openai-token-counting | none |
| q-cross-category-001 | ambiguous_boundary | pass | RAG evaluation and quality | RAG evaluation and quality | no | artifacts\eval\traces\routed-vector\trace-114235b6f8bb4a93b481ebe41e6abb17.json | microsoft-foundry-rag-evaluators, ragas-rag-metrics | microsoft-foundry-rag-evaluators, trec-common-evaluation-measures | none |
| q-cross-category-002 | ambiguous_boundary | pass | RAG evaluation and quality | RAG evaluation and quality, RAG and context handling, LLM settings, cost, and tokens | no | artifacts\eval\traces\routed-vector\trace-2b1ca32e85ce415081a9451b8fecd293.json | openai-cost-optimization, openai-latency-optimization, azure-ai-search-rag-overview | openai-latency-optimization, ragas-rag-metrics, openai-rate-limits | none |
| q-cross-category-003 | ambiguous_boundary | route filter miss | RAG evaluation and quality | RAG evaluation and quality, prompting techniques | no | artifacts\eval\traces\routed-vector\trace-b70e614bed3f4a28a356e6a9b6ea69e1.json | openai-prompt-caching, openai-cost-optimization | openai-gpt5-prompting-guide, openai-api-prompt-engineering, openai-evaluation-flywheel | none |
| q-cross-category-004 | ambiguous_boundary | pass | prompting techniques | prompting techniques, RAG and context handling, LLM security and risks | no | artifacts\eval\traces\routed-vector\trace-7fa95e48f0d14a3ea565dc95caa87412.json | owasp-llm01-prompt-injection, owasp-llm08-vector-embedding-weaknesses | owasp-llm02-sensitive-information-disclosure, openai-api-prompt-engineering, owasp-llm01-prompt-injection | none |
| q-cross-category-005 | ambiguous_boundary | pass | RAG and context handling | RAG and context handling, RAG evaluation and quality | no | artifacts\eval\traces\routed-vector\trace-441b25eea24343339b95a5563fba5ce9.json | ragas-rag-metrics, microsoft-foundry-rag-evaluators | openai-question-answering-embeddings, microsoft-foundry-rag-evaluators, azure-ai-search-vector-relevance-ranking | none |
| q-multi-category-001 | multi_category_routing | pass | RAG evaluation and quality | RAG evaluation and quality, LLM settings, cost, and tokens | no | artifacts\eval\traces\routed-vector\trace-900b3638e98b4bfe94887d1a11d992c2.json | openai-api-prompt-engineering, azure-ai-search-rag-overview, deepeval-rag-metrics, openai-token-counting | openai-latency-optimization, ragas-rag-metrics, openai-token-counting | none |
| q-multi-category-002 | multi_category_routing | pass | prompting techniques | prompting techniques, RAG and context handling, RAG evaluation and quality, LLM settings, cost, and tokens | no | artifacts\eval\traces\routed-vector\trace-8b9aa6468aba4d0385d8f971502580e5.json | owasp-llm08-vector-embedding-weaknesses, azure-ai-search-vector-relevance-ranking, openai-gpt5-prompting-guide, microsoft-foundry-rag-evaluators | openai-latency-optimization, azure-ai-search-vector-relevance-ranking | none |
| q-security-boundary-001 | answerable | pass | prompting techniques | prompting techniques, RAG and context handling, RAG evaluation and quality, LLM security and risks | no | artifacts\eval\traces\routed-vector\trace-d824b0959ada48018ba665cc100eacf5.json | owasp-llm01-prompt-injection | openai-gpt5-prompting-guide, owasp-llm01-prompt-injection | none |

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
- Define explicit components in the prompt: role/domain, required outcome, workflow rules, constraints on what not to do, and output format expectations; add examples only when behavior is hard to describe.[C1] Making each rule observable (e.g., “use a citation after every sentence that depends on source evidence; do not use background knowledge”) improves reliability and control compared with vague goals like “be accurate.”[C1]

- Treat prompts as living, testable artifacts: iteratively adjust minimal instructions to fix wrong behaviors, and store production prompts in code with typed arguments, tests, fixtures, and code review so changes are visible and controlled.[C1][C3]

- Version prompts and models together for traceability and stability: pin to specific model snapshots, and log each prompt/model change with retrieval mode, template version, deployment, selected context, token budget, answer text, and evaluation results to separate retrieval issues from prompt or model regressions.[C2][C3]
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
- Retrieval-augmented generation first finds and ranks content that is semantically similar to the user’s question, then assembles a bounded context from those top-ranked chunks within a token budget. [C1][C2]  
- This retrieved content is then passed to the model as grounding data, and the prompt explicitly instructs the model to answer using only that provided evidence, which constrains and reduces unsupported generation. [C1][C2]  
- Clear boundaries are preserved around each source chunk and explicit “no-answer” behavior is defined for cases where the retrieved context doesn’t contain an answer, further discouraging the model from inventing information. [C1]
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
- Common retrieval metrics for golden-set evaluations include recall@k, precision@k, MRR or first relevant rank, average precision (AP), mean average precision (MAP), bpref, and geometric mean average precision (GMAP). [C1]  
- Additional ranked-search metrics from the document retrieval evaluator include Fidelity, NDCG (and ndcg@k variants), XDCG (and xdcg@k), Max Relevance (e.g., top1_relevance, top3_max_relevance), and Holes / holes_ratio. [C2]
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
- Prompt injection is a vulnerability where user prompts or other model‑parsed inputs alter an LLM’s behavior or output in unintended ways, even if the injected content is not obvious or readable to humans. [C1] Because LLM apps blend system instructions, user input, retrieved content, tool output, and other data into one context, the model may misinterpret untrusted data as instructions. [C1]

- This can lead to guideline violations, harmful content, sensitive data disclosure, unauthorized actions, or manipulated decisions. [C1] Prompt injection is related to but broader than jailbreaking: jailbreaking is a subtype where inputs push the model to broadly ignore safety protocols. [C1]

- RAG and fine‑tuning do not eliminate prompt injection risk: RAG introduces additional untrusted external content into prompts, and fine‑tuning cannot prevent hostile inputs from influencing behavior at inference time. [C1]

- Mitigations include application‑level safeguards that constrain what the LLM can do with untrusted content and reduce the impact of injected instructions, while more durable resistance to jailbreaking and injection also depends on ongoing model training and safety updates. [C1]

- OWASP maps these risks to MITRE ATLAS techniques for direct and indirect prompt injection and jailbreak injection, providing a broader framework and research base for understanding and defending against such attacks. [C2]
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
- Token counting lets you estimate how many tokens a full prompt will use (instructions, user query, retrieved context, tools, schemas, and answer budget) before you send it, so you can stay within a model’s prompt budget. [C1]  
- In RAG systems, counting tokens during context assembly helps you admit retrieved chunks only until you approach the budget, instead of using a fixed number of chunks, which makes better use of available space and avoids truncation. [C1]  
- Using a tokenizer that matches the target generation model and recording prompt token estimates alongside API-reported usage lets you track and refine budgeting over time, and distinguish prompt or retrieval regressions from changes in model-side accounting. [C1]
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
- RAG systems usually deal with documents that are too large or too broad to be treated as a single retrievable unit, so they must first be split into smaller chunks that can be individually retrieved and fit within embedding-model and chat-model token limits. [C1][C2]

- Chunking before embedding lets each vector correspond to a narrower, semantically coherent unit, which improves the chance that vector search retrieves a passage that directly matches the user’s question instead of a broad, mixed-topic document. [C1][C2]

- Because embeddings are computed over chunks, not whole documents, retrieval can return multiple focused passages that collectively fit within the answer model’s context budget and provide enough evidence for grounded responses. [C1][C2]
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
- Groundedness checks whether the **generated answer** stays within and is supported by the retrieved context, i.e., it measures if the model avoids fabricating content beyond that evidence. [C1][C2]

- Retrieval quality metrics evaluate the **retrieval step**, i.e., how well the system finds and ranks relevant documents or chunks for the query (using measures like recall@k, precision@k, MRR, AP/MAP, etc.). They judge evidence selection, not what the model says with that evidence. [C2][C3]

- A grounded answer can still be poor if retrieval was bad (it is faithfully based on the context, but the context lacked the right evidence), and good retrieval can still lead to an ungrounded answer if the model invents content not supported by the retrieved documents. [C1][C2]
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
- Retrieved context often dominates input tokens in RAG; pruning low-scoring or off‑topic chunks and removing boilerplate, duplicates, and HTML artifacts directly reduces input-token count, which lowers both latency and cost. [C1][C3]

- Keeping only the most answer‑relevant passages and needed source identifiers leaves more token budget for the answer and citations, improving efficiency while maintaining necessary evidence. [C1]

- Lowering context budgets (for example via smaller `top_k` and trimmed chunks) addresses token-per-minute bottlenecks common in RAG, which reduces end-to-end latency when tokens are the limiting factor. [C3]

- Removing noisy or irrelevant retrieved passages reduces the chance that the model overreacts to misleading context, improving context precision and lowering noise sensitivity, so fewer incorrect claims are driven by spurious citations. [C1][C2]
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
- Structure the prompt so that stable instructions, schemas, and examples come first, and dynamic user input plus retrieved chunks come later; this layout is more cache-friendly and lets provider-side prompt caching reuse the shared prefix across runs. [C2]

- Keep developer instructions and the prompt prefix as stable as possible across evaluations, and avoid including volatile data like IDs or timestamps near the prefix, so cache hits are more likely and repeated runs become cheaper. [C2]

- Place retrieved RAG chunks after the stable rubric and schemas so only the variable tail changes between test cases, improving cacheability while still letting you trim context when token budgets are tight. [C2]

- Track prompt-token and cached-token usage metrics to see whether your layout is actually benefiting from caching and reducing cost, and adjust the prompt structure accordingly. [C2]

- When you do need to change the prompt, make the smallest edits and re-use the same evaluation setup so you preserve as much of the cached, stable prefix as possible while still iterating on RAG quality. [C1][C3]
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
- This is a prompt injection / instruction-hijacking problem in a retrieval-augmented generation (RAG) system, where untrusted retrieved content attempts to override core instructions and expose system prompts or configuration details. [C1][C3]

- It should be mitigated by:
  - Treating retrieved content strictly as untrusted evidence, not as instructions, and explicitly telling the model to ignore attempts to modify core behavior. [C3]
  - Using a strong system prompt that enforces context adherence, limits responses to approved tasks, and forbids disclosing system prompts or configuration details. [C1][C3]
  - Keeping secrets and sensitive configuration out of prompts entirely and instead in secure infrastructure, so that even if injection succeeds, no secrets are exposed. [C1]
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
- Use a groundedness check to see whether each key claim in the answer is directly supported by specific retrieved snippets; if important answer statements lack clear backing in the context, the chunks do not contain enough relevant evidence. [C2]

- Use a response completeness check (when you have ground truth) to verify that critical expected information from the source material appears in the answer; missing critical facts indicate that the retrieved chunks did not bring the right evidence into context. [C2]

- Separately evaluate retrieval quality itself (e.g., whether the “right” documents or passages were retrieved) so you can distinguish “answering badly from good evidence” from “answering with the wrong or insufficient evidence.” [C1][C2]
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
- Prompt structure defines where stable instructions, schemas, and examples sit relative to the user question and retrieved context, enabling a “shared prefix” that stays constant while only the dynamic context section changes. This makes it easier to trim or swap retrieved chunks without rewriting the whole prompt, and supports cache-friendly, traceable RAG layouts. [C1]

- Retrieved context must be filtered and pruned so that only the most answer-relevant, non-duplicative, and non-boilerplate chunks are included, while preserving source identifiers for citations and leaving enough room for the model’s answer. This trimming directly affects both context precision/recall and the faithfulness of downstream answers. [C1][C2]

- Evaluation metrics like context precision/recall, faithfulness, and response relevancy use the triplet of `user_input`, `retrieved_contexts`, and `response` (plus optional `reference` data) to diagnose whether failures stem from retrieval (bad or missing context), generation (unfaithful use of context), or prompt design (answer not addressing the question). This separation lets you tie observed issues back to specific parts of the prompt and context-building pipeline. [C2]

- Token budgets are enforced in the context assembly path: you must reserve space for instructions, user input, tools/schemas, and an explicit answer budget, then admit retrieved chunks only until the remaining budget is filled. This forces tradeoffs between including more context versus preserving answer-length capacity, and it interacts with trimming strategies and evaluation metrics that reveal when over-trimming harms recall or under-trimming bloats context with noise. [C1][C3]

- For reliable RAG quality review over time, traces should store model names, token counts, and budgeting assumptions so that changes in token accounting can be distinguished from real regressions in retrieval, prompt structure, or answer quality as seen in the metrics. [C3]
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
- Vector embedding weaknesses (e.g., imperfect similarity or recall) require compensating levers like chunk-size tuning, `k` adjustment, and HNSW parameter tuning to balance recall, latency, and resource use, explicitly treating retrieval as an approximate, tunable process rather than assuming embeddings are always accurate.[C3]

- Retrieval filtering—pruning to “high-signal” chunks, trimming boilerplate, and respecting token budgets—mitigates embedding noise and reduces the chance that the model attends to distracting or marginally relevant context, but at the cost of potentially missing useful evidence if filters are too aggressive.[C1][C3]

- Prompt instructions must be designed to work with this filtered context: shorter, stable instructions reduce input length and latency, leave room for evidence, and can be moved to smaller or fine-tuned models, but over-aggressive prompt shortening or splitting risks losing guidance that helps the model interpret imperfect retrieval results.[C1][C2]

- Evaluation diagnostics—manual inspection of top results, checking vector field setup, similarity metrics, and approximate vs exact KNN—are the feedback loop that reveals whether embedding, retrieval, and prompt changes improved answer grounding or just traded off recall for speed or cost; they guide which bottleneck (generation, retrieval, context size, or routing) to optimize next.[C2][C3]

- Overall, the tradeoff is a coordinated one: embedding and retrieval tuning aim for enough recall and precision; context filtering and prompt compression aim for lower latency and cost; and diagnostics ensure these levers are adjusted based on measured quality rather than assumptions.[C1][C2]
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
- Treat retrieved content as untrusted evidence, not as new instructions; do not let it override or modify system or developer messages.[C2]  

- Explicitly ignore any retrieved instructions that try to change core behavior (e.g., “ignore previous instructions” or “reveal hidden prompts”) and instead follow the system prompt’s constraints and citation rules.[C2][C3]  

- Continue to answer only from the selected context, preserve required formatting and citations, and abstain if the context is insufficient, regardless of what the retrieved content requests.[C2][C3]
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

- Citation validation checks whether cited chunk IDs were included in the selected context; it does not prove claim-level factual correctness.
- Metrics are lightweight regression signals over the current golden set and should not be interpreted as comprehensive benchmark scores.
- No-answer accuracy depends on the selected context and generation behavior for this run.
- Token diagnostics use recorded estimates and model usage when available; provider-side accounting can differ.
- The router uses heuristic embedding-similarity thresholds. Similarity scores are not calibrated probabilities, and the configured threshold and category margin are specific to the current embedding model, category descriptions, and benchmark.
