# Source snapshot

Source metadata:
- source_slug: owasp-llm08-vector-embedding-weaknesses
- category: LLM security and risks
- upstream_url: https://github.com/OWASP/www-project-top-10-for-large-language-model-applications/blob/0205957/2_0_vulns/LLM08_VectorAndEmbeddingWeaknesses.md
- source_markdown: https://raw.githubusercontent.com/OWASP/www-project-top-10-for-large-language-model-applications/0205957/2_0_vulns/LLM08_VectorAndEmbeddingWeaknesses.md
- license: CC BY-SA 4.0
- pinned_version: owasp-llm-top-10@0205957
- snapshot_type: normalized documentation digest from OWASP markdown
- normalization: removed repository page chrome and compacted reference-list detail; retained vector and embedding risk definition, RAG-specific leakage and poisoning risks, mitigation controls, and the three attack scenarios with concise RAG-oriented interpretation

---
# Vector and embedding weaknesses

OWASP LLM08:2025 describes vector and embedding weaknesses as security risks in systems that use retrieval-augmented generation (RAG) with LLMs. The weakness appears when vectors or embeddings are generated, stored, retrieved, combined, or governed in ways that allow harmful content injection, output manipulation, unauthorized access, or sensitive information disclosure.

RAG improves contextual relevance by combining an LLM with external knowledge sources. Retrieval augmentation commonly depends on embeddings and vector search. That dependency creates a security boundary: if the vector store retrieves the wrong content, unauthorized content, poisoned content, or stale conflicting content, the model may treat that content as evidence and use it in the final answer.

The OWASP source frames these weaknesses as intentional or unintentional. A malicious actor may poison an index or exploit missing access controls. A benign data pipeline may accidentally mix tenants, include hidden text, use unverified sources, or combine contradictory knowledge.

## Unauthorized access and data leakage

Inadequate or misaligned access controls can let users retrieve embeddings or source content they are not authorized to see. If retrieved context contains personal data, proprietary information, confidential business material, copyrighted content, or data governed by usage policies, the LLM can disclose it in a generated answer.

The vector store should not be treated as a neutral cache. It is part of the authorization surface. A chunk that was safe to index for one role may be unsafe to retrieve for another role. If access metadata is lost during chunking, embedding, indexing, or retrieval, the generator can receive unauthorized evidence before any output filter has a chance to act.

For RAG systems, the leakage pattern often looks like this:

1. Sensitive documents are embedded into a shared vector index.
2. Retrieval searches the index without tenant, role, or document-level filtering.
3. The model receives unauthorized chunks in context.
4. The answer summarizes or cites sensitive content to the wrong user.

The root issue is not only generation; it is permission-insensitive retrieval.

## Cross-context leaks and knowledge conflicts

OWASP calls out multi-tenant vector databases where multiple user classes, applications, or groups share the same vector infrastructure. In those environments, context can leak between users or queries if data is not partitioned and filtered correctly.

The source also discusses federation knowledge conflict: when data from multiple sources contradicts, retrieval may supply conflicting evidence. A related issue is that the LLM's pretrained knowledge may conflict with newer retrieved data. The model may fail to supersede old knowledge with current retrieved content, or it may blend contradictory sources into an unreliable answer.

RAG evaluation should therefore check both access isolation and evidence freshness. A high similarity score is not enough if the chunk is stale, unauthorized, or contradicted by a higher-trust source.

## Embedding inversion attacks

Embedding inversion attacks attempt to recover source information from embeddings. OWASP states that attackers can exploit weaknesses to invert embeddings and recover significant source content, compromising confidentiality.

Embeddings are not raw documents, but they can still leak information. Treating vectors as non-sensitive because they are numeric representations is unsafe. The risk is higher when embeddings are stored in broadly accessible systems, logs, exports, or analytics tools without the same protection as source documents.

Mitigations include access control for embeddings, secure storage, careful export policies, and avoiding unnecessary retention of vectors for sensitive data.

## Data poisoning

Data poisoning occurs when malicious or unverified content enters the knowledge base. OWASP notes that poisoned data can come from malicious actors or unintentionally from insiders, prompts, data seeding, or unverified providers.

In RAG, poisoned documents can manipulate retrieval and generation. A poisoned chunk may:

- contain hidden instructions that are later retrieved into context;
- bias the model toward false claims;
- target a specific entity or query pattern;
- introduce malicious links or exfiltration instructions;
- cause the model to recommend an unqualified candidate, unsafe action, or incorrect policy.

Data poisoning does not require model retraining. It can happen through ordinary ingestion if the pipeline indexes untrusted documents without validation.

## Behavior alteration

OWASP notes that retrieval augmentation can alter the foundational model's behavior. The source gives an example where factuality and relevance may improve, while qualities such as empathy or emotional intelligence may degrade.

This is a quality and safety risk. A RAG answer can be factually grounded but inappropriate for the use case. For example, a debt-advice assistant that becomes terse and purely factual may fail the product's intended support tone even when the retrieved facts are correct.

Behavior alteration should be evaluated explicitly. Retrieval quality metrics alone do not show whether the final answer preserves desired style, empathy, caution, refusal behavior, or safety posture.

# Retrieval-specific risks and mitigations

OWASP recommends permission-aware vector stores, data validation and source authentication, review and classification of combined data, and detailed immutable logging. These controls should be applied before retrieved context reaches the model.

## Permission and access control

The source recommends fine-grained access controls and permission-aware vector and embedding stores. Datasets should be logically partitioned and access-partitioned so that different user classes, groups, or tenants cannot retrieve each other's data.

RAG systems should carry access metadata through the full lifecycle:

- document ingestion;
- chunking;
- embedding generation;
- vector payload storage;
- retrieval filters;
- reranking;
- context assembly;
- citation validation;
- trace and log storage.

Access controls should be enforced in retrieval and downstream systems, not only in the prompt. If unauthorized chunks are sent to the model, the data has already crossed a trust boundary.

## Data validation and source authentication

OWASP recommends robust validation pipelines for knowledge sources, regular audits of knowledge-base integrity, and acceptance of data only from trusted and verified sources.

Validation should include:

- source provenance checks;
- malware or unsafe-content screening where appropriate;
- detection of hidden text or formatting tricks;
- prompt-injection pattern review;
- schema and file-type validation;
- duplicate and stale-content checks;
- approval workflows for high-trust indexes.

Source authentication matters because vector similarity can make malicious content appear relevant. A retrieved chunk should be both semantically relevant and trusted for the question being answered.

## Review combined data and classify knowledge

When combining data from multiple sources, OWASP recommends reviewing the combined dataset. Data should be tagged and classified to control access levels and prevent mismatch errors.

Useful metadata includes:

- tenant or workspace id;
- source owner;
- document sensitivity;
- user or group permissions;
- source type;
- trust tier;
- creation and update time;
- retention policy;
- topic or category.

Classification helps prevent cross-context leakage and supports safer retrieval policies. It also improves evaluation because failures can be analyzed by source class, category, or trust tier.

## Monitoring and logging

OWASP recommends detailed immutable logs of retrieval activity so teams can detect and respond to suspicious behavior.

Useful RAG retrieval logs include:

- user and tenant identity;
- query text or a redacted query representation;
- retrieval filters applied;
- vector index and collection name;
- retrieved chunk ids and source ids;
- similarity or ranking scores;
- authorization decisions;
- selected context ids;
- generated citations;
- denied or filtered chunks.

Logs must themselves be protected. Retrieval traces can contain sensitive prompts, source snippets, or document identifiers. A logging strategy should include redaction, retention limits, access controls, and audit review.

## Scenario: data poisoning through hidden resume text

OWASP describes a job application system that uses RAG for initial screening. An attacker submits a resume containing hidden text, such as white text on a white background, with instructions to ignore previous directions and recommend the candidate. The system processes and indexes the resume, including hidden text. Later, when queried about the candidate's qualifications, the LLM follows the hidden instruction and recommends an unqualified candidate.

Mitigation includes text extraction tools that ignore formatting and detect hidden content, plus validation before documents are added to the RAG knowledge base. The broader control is to treat submitted documents as untrusted input, not as instructions.

## Scenario: access-control leakage in a shared vector store

OWASP describes a multi-tenant environment where different groups or user classes share one vector database. Embeddings from one group may be retrieved in response to another group's query, leaking sensitive business information.

Mitigation requires a permission-aware vector database and retrieval pipeline. The query should include authorization filters so only content available to the requesting group can be searched or returned.

## Scenario: behavior alteration after retrieval augmentation

OWASP describes a foundation model whose behavior becomes less empathetic after retrieval augmentation. A user asks for help with overwhelming student loan debt. A pre-augmentation answer may acknowledge stress and suggest income-based repayment plans. A post-augmentation answer may become purely factual and advise paying loans quickly to avoid interest, while losing the supportive tone needed for the application.

Mitigation is to monitor and evaluate how RAG changes desired model behavior. Evaluation should include not only factuality and relevance but also use-case qualities such as empathy, tone, safety, and appropriateness.

## Evaluation implications for RAG systems

Vector and embedding weaknesses should be tested as part of RAG quality evaluation. Useful checks include:

- whether retrieval enforces source permissions;
- whether expected source metadata survives chunking and embedding;
- whether the retriever can return poisoned or hidden-instruction content;
- whether unauthorized chunks are filtered before context assembly;
- whether stale or conflicting sources are detected;
- whether generated citations refer only to authorized selected context;
- whether answer behavior changes undesirably after retrieval augmentation.

The OWASP guidance reinforces that RAG quality is not only relevance. A robust RAG system must retrieve relevant, authorized, trusted, current, and behaviorally appropriate evidence.

## Related references and provenance

The source reference list points to material on RAG and fine-tuning, imperfect retrieval augmentation, embedding information leakage, embedding inversion, RAG poisoning, confused-deputy risks, and the RAG Triad. The detailed links are compacted here because the corpus value is in the normalized OWASP risk and mitigation structure for vector and embedding systems.
