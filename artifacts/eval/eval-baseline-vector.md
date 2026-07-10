# Evaluation report: eval-baseline-vector

## Run summary

| Field | Value |
| --- | --- |
| Run ID | eval-baseline-vector |
| Created at | 2026-07-10T11:23:41.371849+00:00 |
| Retrieval mode | baseline-vector |
| Golden set | golden\questions.json |
| Question count | 16 |
| Trace count | 16 |
| JSON artifact | artifacts\eval\eval-baseline-vector.json |
| Case mix | ambiguous_boundary: 5, answerable: 7, fallback_routing: 2, no_answer: 2 |

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
| fallback_rate | 0 |  |
| recall_at_k | 0.8571 |  |
| mrr | 0.6071 |  |
| citation_source_match | 0.8571 |  |
| no_answer_accuracy | 1 |  |
| average_context_tokens | 609.7 |  |
| average_included_chunks | 2.938 |  |

## Per-question table

| Question | Case type | Status | Trace | Expected sources | Retrieved sources | Errors |
| --- | --- | --- | --- | --- | --- | --- |
| q-answerable-001 | answerable | pass | artifacts\eval\traces\baseline-vector\trace-96c468a8ab1647bcbf4ec872d72910ec.json | openai-api-prompt-engineering | openai-gpt5-prompting-guide, openai-evaluation-flywheel, openai-api-prompt-engineering | none |
| q-answerable-002 | answerable | pass | artifacts\eval\traces\baseline-vector\trace-fce25e0224ef4ac1b4f10ca3cb0e8f89.json | azure-ai-search-rag-overview, openai-question-answering-embeddings | microsoft-foundry-rag-evaluators, openai-question-answering-embeddings, owasp-llm04-data-model-poisoning | none |
| q-answerable-003 | answerable | pass | artifacts\eval\traces\baseline-vector\trace-9950abc03e954ee2a9590c8be5d1b2bc.json | trec-common-evaluation-measures, ragas-rag-metrics | trec-common-evaluation-measures, microsoft-foundry-rag-evaluators, openai-api-prompt-engineering | none |
| q-answerable-004 | answerable | pass | artifacts\eval\traces\baseline-vector\trace-de1893ce95ba4197908a78f5b9b96e01.json | owasp-llm01-prompt-injection | owasp-llm01-prompt-injection | none |
| q-answerable-005 | answerable | pass | artifacts\eval\traces\baseline-vector\trace-ab0cd85aa2b7495898436b6389c1ce97.json | openai-token-counting | openai-token-counting, openai-prompt-caching | none |
| q-answerable-006 | answerable | pass | artifacts\eval\traces\baseline-vector\trace-e1eb1a8010a94809923ecdf15f3f1922.json | azure-ai-search-chunk-documents | azure-ai-search-chunk-documents, azure-ai-search-rag-overview | none |
| q-no-answer-001 | no_answer | pass | artifacts\eval\traces\baseline-vector\trace-4005ba0e18c3424187fba81bd9f63c13.json | none | owasp-llm08-vector-embedding-weaknesses, openai-rate-limits | none |
| q-no-answer-002 | no_answer | pass | artifacts\eval\traces\baseline-vector\trace-1d5b4151bdbd4d43917dd5006ce56af1.json | none | azure-ai-search-chunk-documents, owasp-llm04-data-model-poisoning, openai-token-counting | none |
| q-cross-category-001 | ambiguous_boundary | pass | artifacts\eval\traces\baseline-vector\trace-4b8a5c23ad6b42358de77565dead62ce.json | microsoft-foundry-rag-evaluators, ragas-rag-metrics | microsoft-foundry-rag-evaluators, trec-common-evaluation-measures | none |
| q-cross-category-002 | ambiguous_boundary | pass | artifacts\eval\traces\baseline-vector\trace-e3dadb99662842d5963fb5fcf3a15b52.json | openai-cost-optimization, openai-latency-optimization, azure-ai-search-rag-overview | openai-latency-optimization, owasp-llm02-sensitive-information-disclosure, ragas-rag-metrics | none |
| q-cross-category-003 | ambiguous_boundary | source retrieval miss | artifacts\eval\traces\baseline-vector\trace-88452fb7d24f41f28dcecf579ab2694a.json | openai-prompt-caching, openai-cost-optimization | openai-gpt5-prompting-guide, openai-api-prompt-engineering, openai-evaluation-flywheel | none |
| q-cross-category-004 | ambiguous_boundary | pass | artifacts\eval\traces\baseline-vector\trace-480e44731eca4f78b05dddac6d161ed0.json | owasp-llm01-prompt-injection, owasp-llm08-vector-embedding-weaknesses | owasp-llm02-sensitive-information-disclosure, openai-api-prompt-engineering, owasp-llm01-prompt-injection | none |
| q-cross-category-005 | ambiguous_boundary | pass | artifacts\eval\traces\baseline-vector\trace-04db403594e7402d9f3b5e1b6ee04345.json | ragas-rag-metrics, microsoft-foundry-rag-evaluators | openai-question-answering-embeddings, microsoft-foundry-rag-evaluators, azure-ai-search-vector-relevance-ranking | none |
| q-fallback-001 | fallback_routing | pass | artifacts\eval\traces\baseline-vector\trace-b36714e211ac4b7c99b3a0f28f5d5bc0.json | openai-api-prompt-engineering, azure-ai-search-rag-overview, deepeval-rag-metrics, openai-token-counting | openai-latency-optimization, ragas-rag-metrics, openai-token-counting | none |
| q-fallback-002 | fallback_routing | source retrieval miss | artifacts\eval\traces\baseline-vector\trace-8fcce30eedce47939a7083eaf1b08194.json | owasp-llm08-vector-embedding-weaknesses, azure-ai-search-vector-relevance-ranking, openai-gpt5-prompting-guide, microsoft-foundry-rag-evaluators | openai-latency-optimization, owasp-llm04-data-model-poisoning | none |
| q-security-boundary-001 | answerable | pass | artifacts\eval\traces\baseline-vector\trace-59e2908c9ff340c185f9387d89548b06.json | owasp-llm01-prompt-injection | openai-gpt5-prompting-guide, owasp-llm01-prompt-injection | none |

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
- Define prompts explicitly with: a clear role/domain, required outcome, critical workflow rules, constraints on disallowed behavior, output format expectations, and examples only where behavior is hard to describe.[C1] This reduces ambiguity and makes the model’s behavior more observable and controllable.[C1]

- Use precise, testable instructions instead of vague ones—for example, in RAG, specify “answer only from provided excerpts, cite evidence for each claim, and return a no‑answer string if evidence is missing,” rather than generic instructions like “be accurate.”[C1][C2]

- Design prompts with explicit RAG rules when applicable: require citations to retrieved chunks, define no‑answer behavior if context lacks evidence, clarify retrieval-context boundaries, and forbid using unsupported outside knowledge.[C2]

- Treat prompt design as an engineering process: version prompts, change them minimally based on failure analysis, and evaluate each version with consistent graders and test cases, especially retrieval‑aware tests.[C1][C2]

- Record and monitor prompt behavior per model snapshot and configuration (prompt template version, model, retrieval mode, context, outputs) so behavior changes across models or upgrades can be detected and controlled.[C3]
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
- Retrieval-augmented generation first retrieves context chunks that are semantically similar to the user’s query and assembles them into a bounded context window for the model. [C1][C2]  
- The model is then explicitly instructed to answer only from this provided evidence, which “grounds” the response in the retrieved documents instead of unconstrained model knowledge. [C1][C2]  
- Groundedness evaluation checks that the response aligns strictly with the supplied context and does not introduce material outside it, directly targeting and reducing unsupported generation. [C1]  
- When the retrieved sources are trusted, versioned, and validated, grounding to these sources further reduces hallucination risk by ensuring answers come from known, reliable documents rather than potentially poisoned or unknown data. [C3]
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
- In a golden-set retrieval evaluation, you can compare ranked search results using recall@k, precision@k, and MRR/first relevant rank to assess whether relevant documents are retrieved, how many are useful, and how early the first useful document appears in the ranking. [C1]  
- You can also use AP/MAP to evaluate overall ranking quality, bpref when relevance judgments are incomplete, and GMAP or per-question diagnostics when robustness across difficult questions matters. [C1]  
- Additional ranked metrics include NDCG, XDCG (top‑k ranking quality), max relevance among the top‑k, and hole-related measures (holes, holes_ratio) that check for retrieved documents lacking judgments. [C2]
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
- Prompt injection is a vulnerability where user or other parsed inputs alter an LLM’s behavior or outputs in unintended ways, including when the injected content is not obvious to humans but is still interpreted by the model. [C1] This arises because LLM apps mix instructions with untrusted data such as user prompts, retrieved documents, tool outputs, files, or websites in a single context, allowing hostile content to be misinterpreted as new instructions. [C1]

- Impacts include violating guidelines, producing harmful content, leaking sensitive information, triggering unauthorized actions, or unduly influencing decisions. [C1] Jailbreaking is a specific form of prompt injection where inputs cause the model to broadly ignore safety protocols. [C1]

- RAG and fine-tuning do not remove prompt injection risk: RAG increases grounding but also introduces additional untrusted external content, and fine-tuning can improve behavior but cannot prevent hostile inputs from influencing the model at inference time. [C1]

- Mitigations include application-level safeguards that constrain what the LLM can do with injected content and reduce the impact of malicious prompts. [C1] More durable jailbreak resistance additionally depends on ongoing model training and safety updates, not just app-layer controls. [C1]

- Prompt injection is tied to MITRE ATLAS techniques for direct and indirect prompt injection and jailbreak injection, which helps situate it within a broader adversarial ML threat landscape. [C2]
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
- Token counting lets you estimate how many tokens a full request (instructions, user message, retrieved context, tools, schemas, and answer) will use before calling the model, so you can stay within a fixed prompt budget. [C1]  
- In RAG systems, counting tokens inside the context-assembly step means you can keep adding retrieved chunks only until the combined prompt reaches your budget, instead of admitting a fixed number of chunks that might overflow limits. [C1]  
- Matching the tokenizer to the target model’s encoding improves the accuracy of these estimates, which helps control both cost and the risk of hitting model token limits. [C1]  
- When embeddings and generation models use different encodings, separate token counts for chunking and for generation help keep both retrieval and prompts within their respective budgets. [C1]  
- Logging prompt token estimates alongside actual API-reported usage lets you track and debug prompt-size regressions or accounting changes over time, improving ongoing budget management. [C1]
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
- Chunking turns large or broad documents into smaller, semantically focused units that can be represented by individual vectors and retrieved more precisely than entire documents, which may cover many unrelated subtopics. [C1][C2]

- Embedding models have strict token limits (for example, around 8k tokens), so you must split documents into chunks before generating embeddings; otherwise, text will be truncated or rejected, and the resulting vectors will not faithfully represent the content. [C1]

- Retrieved chunks must also fit into the downstream chat/completion model’s context window, so chunking and embeddings are done up front to ensure that vector search returns passages that both match the query well and can be included in the answer context. [C1][C2]

- Index-time chunking plus embedding (vectorization) creates the vector store that vector search uses; without this step, there are no appropriately sized, semantically coherent vectors for the retriever to work with. [C1][C2]
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
- Groundedness checks whether the generated answer’s content is supported by the retrieved context and avoids fabricating material beyond that evidence; it is a system-level evaluation of the final response. [C1][C2]

- Retrieval quality metrics evaluate how well the retriever selects and ranks relevant documents or chunks for a query (e.g., using recall@k, precision@k, MRR, AP/MAP, NDCG), and are process-level measures applied before answer generation. [C2][C3]

- In practice, groundedness asks “does the answer stay within what the context actually says?”, while retrieval metrics ask “did the system retrieve and rank the right evidence for this question?” [C1][C3]
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
- Limiting retrieved context directly reduces the number of input tokens the model must process, which lowers latency and cost, since large, repetitive, or noisy context is a major source of unnecessary tokens in RAG prompts. [C1]  
- Pruning low-scoring or off-topic chunks, removing boilerplate/HTML artifacts, and deduplicating near-identical passages prevents irrelevant text from entering the prompt, shrinking context size and speeding up inference. [C1]  
- Keeping only passages that contain the asked attribute and necessary source identifiers concentrates the prompt on high-value evidence, reducing both token usage and the amount of extraneous material the model might cite. [C1]  
- Better context precision (less irrelevant or noisy context) lowers the chance that the model will be influenced by misleading or off-topic passages, which in turn reduces citation noise and improves faithfulness and response relevancy. [C1][C3]  
- A prompt layout that separates stable instructions from dynamic retrieved context makes it easier to trim only the dynamic portion while reusing the rest, further cutting tokens and latency without adding citation clutter. [C1]
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
- Keep the shared prefix (developer instructions, schemas, rubric, and examples) stable across runs so provider-side prompt caching can reuse those tokens. [C2][C3]

- Avoid adding volatile content (IDs, timestamps, random seeds) near that shared prefix, since even small changes can break cache reuse and raise costs. [C2]

- Place retrieved RAG context and per-question details after the stable instructions and rubric; this keeps the cacheable portion large while only recomputing the dynamic tail. [C2][C3]

- Track prompt-token and cached-token usage during eval runs and iterate on prompt layout to maximize cached tokens without harming grading quality. [C1][C2]

- Version prompts and rubrics but change them minimally between evals; test new versions against the same golden questions so you only pay extra when you intentionally modify the shared prefix. [C1][C3]
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
- This is a prompt injection / instruction-hijacking problem, where untrusted retrieved context tries to override system or developer instructions and expose hidden prompts. [C1][C3]

- It should be mitigated by:
  - Treating all retrieved context as untrusted evidence, not as instructions, especially in RAG systems. [C3]  
  - Using a system prompt that explicitly tells the model to ignore attempts to modify core instructions and to comply only with approved tasks and topics. [C3]  
  - Concealing system prompts and configuration details, and ensuring they do not contain secrets that could be exposed if injection succeeds. [C1]
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
- Use a **groundedness check**: verify that each part of the generated answer is directly supported by the retrieved context; if the answer goes beyond what the chunks say, the evidence is insufficient. [C2]  

- Use a **response completeness check**: confirm that the answer includes the critical information that should be present according to ground truth; missing key facts indicates the retrieved chunks did not contain enough relevant evidence. [C2]  

- Combine these with **retrieval quality checks**: assess whether the “right evidence” reached the model at all; poor retrieval quality means the selected chunks lack the needed support even if the answer looks plausible. [C2]  

- Optionally add **document retrieval metrics** (when labels exist) to see if the relevant documents and chunks are ranked high enough; low scores suggest your retrieved chunks are not sufficiently evidence-rich. [C2]
````

### q-fallback-001

| Field | Value |
| --- | --- |
| Case type | fallback_routing |
| Status | pass |
| No-answer response | no |

**Request**

````text
How do prompt structure, retrieved context, evaluation metrics, and token budgets interact during a RAG quality review?
````

**Response**

````text
- Prompt structure in RAG typically follows a stable-prefix pattern: durable developer instructions, output schema and citation rules, and any examples come first, followed by the user question and then the selected retrieved context. [C1] This layout keeps reusable text stable across requests and makes the dynamic context section easier to trim without rewriting the whole prompt. [C1]

- Retrieved context must be filtered so it is both high quality and token-efficient. RAG trimming removes low-scoring or off-topic chunks, boilerplate, duplicated or near-identical passages, and HTML artifacts, while keeping the most answer-relevant passages, necessary source identifiers, and section labels for citations. [C1] The goal is to maximize useful evidence while leaving enough token budget for the answer itself. [C1]

- Token budgets are enforced in the context assembly path: the system reserves space for instructions, user question, metadata, and an answer budget, then admits retrieved chunks only until the overall prompt budget is reached. [C3] Token counting should be aligned with the generation model, and traces should log model name, token estimates, and usage so changes in accounting or models can be distinguished from retrieval or prompt regressions. [C3]

- Evaluation metrics such as context precision, context recall, noise sensitivity, response relevancy, and faithfulness decompose RAG quality across retrieval and generation. [C2] For example, low context recall signals missing necessary context, low context precision signals noisy or poorly ranked context, low faithfulness shows the answer makes unsupported claims, and low response relevancy shows the answer fails to address the question even if context is good. [C2]

- These metrics guide how you adjust prompt structure, trimming, and token budgets: metric inputs explicitly track `user_input`, `retrieved_contexts`, `response`, and optionally `reference` and context IDs, letting you see whether issues come from retrieval selection (context fields) or from how the model uses the provided context within the structured prompt under a given token budget. [C2][C3]
````

### q-fallback-002

| Field | Value |
| --- | --- |
| Case type | fallback_routing |
| Status | source retrieval miss |
| No-answer response | no |

**Request**

````text
What tradeoffs connect vector embedding weaknesses, retrieval filtering, prompt instructions, and evaluation diagnostics?
````

**Response**

````text
- Vector/embedding weaknesses mean that poisoned or unvalidated content can be retrieved with high similarity and appear authoritative, so filtering and validation before indexing are critical; once bad data is in the corpus, retrieval amplifies it and output filters may be too late. [C2]

- Retrieval filtering must balance pruning noisy or marginal chunks (to improve relevance, reduce latency/cost, and avoid distraction) against the risk of omitting needed evidence; systems are urged to select high‑signal passages, remove boilerplate, and respect token budgets rather than passing everything vaguely related. [C1]

- Prompt instructions and stable prefixes interact with retrieval: durable guidance, policies, and schemas should be kept in a stable prefix to support caching and consistent behavior, leaving room for dynamic RAG context while constraining how retrieved content is used. [C1]

- Evaluation diagnostics should focus on measured bottlenecks—such as oversized context, retrieval latency, or serial routing calls—and on how changes in filtering, prompt design, or model calls affect answer quality, so teams iteratively adjust these levers instead of blindly applying every optimization. [C3]

- Overall, there is a tradeoff between tighter retrieval/prompt controls (better security, relevance, and efficiency but possible recall loss) and looser settings (more coverage but greater exposure to embedding weaknesses, poisoning, and higher latency/cost), which must be tuned based on observed system behavior. [C1][C2][C3]
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
- Treat retrieved content as untrusted evidence, not as instructions that can change the system or developer messages. [C2]  
- Explicitly ignore any retrieved directions that ask to modify core instructions, reveal hidden prompts, or override role/capability constraints. [C2]  
- Continue to follow the original system prompt: answer only from the selected context, keep citation requirements, and abstain if evidence is insufficient. [C2][C3]
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
| q-fallback-001 | 975 | 3 |
| q-fallback-002 | 671 | 3 |
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
