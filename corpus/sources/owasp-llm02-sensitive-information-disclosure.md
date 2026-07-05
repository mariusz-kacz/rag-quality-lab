# Source snapshot

Source metadata:
- source_slug: owasp-llm02-sensitive-information-disclosure
- category: LLM security and risks
- upstream_url: https://github.com/OWASP/www-project-top-10-for-large-language-model-applications/blob/0205957/2_0_vulns/LLM02_SensitiveInformationDisclosure.md
- source_markdown: https://raw.githubusercontent.com/OWASP/www-project-top-10-for-large-language-model-applications/0205957/2_0_vulns/LLM02_SensitiveInformationDisclosure.md
- license: CC BY-SA 4.0
- pinned_version: owasp-llm-top-10@0205957
- snapshot_type: normalized documentation digest from OWASP markdown
- normalization: removed repository page chrome and compacted reference-list detail; retained sensitive-data risk definition, common disclosure examples, mitigation categories, attack scenarios, and related taxonomy links

---
# Sensitive information disclosure risks

OWASP LLM02:2025 defines sensitive information disclosure as the risk that an LLM application exposes protected, confidential, proprietary, or otherwise sensitive data through model outputs or application behavior.

Sensitive information can belong to the user, the application owner, the model provider, or a third party. The source names several examples:

- personally identifiable information (PII);
- financial details;
- health records;
- confidential business data;
- security credentials;
- legal documents;
- proprietary training methods;
- model source code or other closed-model internals.

The risk is broader than a model repeating a secret. In an LLM application, sensitive information can enter through prompts, retrieved context, tool responses, logs, training data, fine-tuning data, embeddings, external data sources, system prompts, configuration details, or error messages. If the application does not control those paths, the model can disclose information to the wrong user or expose internal implementation details.

OWASP emphasizes that users also need to understand the risk of entering sensitive information into LLM applications. Data provided during interaction can be retained, logged, reused for training, or later exposed through generated output depending on the system's data handling practices.

## Disclosure through LLM output

LLMs embedded in applications may expose sensitive data, proprietary algorithms, or confidential details through generated responses. This can lead to unauthorized access, privacy violations, and intellectual property breaches.

For a RAG system, disclosure risk often comes from over-broad retrieval or weak authorization filtering. A user query may retrieve chunks that the user is not allowed to see. If those chunks are sent to the model context, the generator may summarize or cite them even if the final answer appears natural and helpful.

Examples of risky outputs include:

- returning another user's personal data;
- summarizing confidential documents outside the requester's permissions;
- exposing API keys, tokens, or credentials that were included in indexed content;
- revealing internal system prompts, deployment settings, or security controls;
- reconstructing training examples or proprietary algorithms.

## PII leakage

PII leakage occurs when personal data is disclosed during interaction with the LLM. This may happen because the model has memorized data, because sensitive user data was included in training or logs, or because the application retrieves data without enforcing user-specific permissions.

In a RAG workflow, PII leakage can happen when document chunks contain names, addresses, account identifiers, health details, or messages that should be scoped to a particular user. Retrieval, reranking, and context assembly should therefore preserve authorization boundaries and avoid indexing sensitive data unless the application has controls for it.

## Proprietary algorithm and training-data exposure

The source notes that poorly configured outputs can reveal proprietary algorithms or data. Revealing training data can expose models to inversion attacks, where attackers extract sensitive information or reconstruct inputs. OWASP cites the "Proof Pudding" attack as an example where disclosed training data contributed to model extraction and inversion against machine learning controls.

The general lesson is that model outputs can reveal information about training data, implementation, or learned behavior. That risk increases when prompts are crafted to elicit memorized data, when models are trained or fine-tuned on sensitive corpora, or when internal implementation details are placed in prompts.

## Sensitive business data disclosure

Generated responses can inadvertently include confidential business information. Examples include customer records, private contracts, internal policies, incident notes, product plans, legal work product, and private operational metrics.

In enterprise RAG systems, business data disclosure can occur when:

- the index includes documents with mixed sensitivity levels;
- source-level access controls are not applied during retrieval;
- a broad role token is used for all users;
- retrieved context is logged without redaction;
- the model is asked to explain its hidden instructions or system configuration;
- generated answers include more detail than the user needs.

## System prompts and configuration details

OWASP recommends concealing the system preamble and limiting users' ability to override or access initial settings. System prompts, internal policies, routing rules, tool descriptions, and configuration details can reveal how to bypass controls or extract further sensitive information.

System prompts should not contain secrets. If a model can read a value, a prompt injection or ordinary mistake may cause it to disclose that value. Secrets should live in secure infrastructure and be used by deterministic application code, not embedded in model context.

# Data leakage scenarios and mitigations

OWASP groups prevention and mitigation guidance into sanitization, access controls, privacy-preserving techniques, user education and transparency, secure system configuration, and advanced techniques. The controls are complementary; prompt text alone is not a sufficient defense because prompt restrictions may be bypassed by prompt injection or other methods.

## Data sanitization

LLM applications should sanitize data before it enters training, fine-tuning, prompts, retrieved context, logs, or model outputs. Sanitization can include scrubbing, masking, tokenizing, or redacting sensitive content.

For RAG systems, sanitization should be considered at several points:

- ingestion: detect and remove secrets or fields that should not be indexed;
- chunking: avoid splitting records in ways that separate authorization context from sensitive values;
- retrieval: filter results by tenant, user, role, and document permissions;
- context assembly: remove unnecessary sensitive fields before sending context to the model;
- output: detect and block sensitive information in generated answers;
- logging: avoid storing raw prompts, retrieved context, or answers that contain secrets.

Sanitization should use deterministic checks where possible. Pattern matching can catch common secrets such as keys, tokens, account numbers, and structured identifiers. Semantic checks can help detect sensitive categories that do not follow simple patterns. Neither approach is complete by itself.

## Robust input validation

OWASP recommends strict input validation to detect and filter harmful or sensitive inputs. Input validation protects both the user and the application: users may accidentally paste private data, and attackers may provide prompts designed to extract or reveal sensitive information.

Validation should define what data types are expected for each workflow. A resume analysis tool, for example, may need work history but not government identity numbers. A support chatbot may need an order number but not a password. Unexpected sensitive fields can be rejected, redacted, or routed to a safer process.

## Access controls and least privilege

Applications should enforce strict access controls based on least privilege. Users and processes should only access data necessary for the specific task.

For RAG, access controls must be applied before context reaches the model. It is not enough to tell the model not to reveal unauthorized data after it has already received it. Retrieval filters should enforce tenant, user, group, document, and field-level permissions. Tool calls should use user-scoped authorization rather than a single broad service credential where possible.

A secure RAG pipeline should preserve permission metadata from ingestion through retrieval and citation. If the answer cites a source, the user should be authorized to view that source.

## Restrict data sources

OWASP recommends limiting model access to external data sources and securely managing runtime data orchestration. Each connected source expands the disclosure surface.

Applications should inventory which data sources a model can reach, what data each source contains, which users can trigger access, and what is logged. Sources with sensitive data should have explicit retrieval policies and monitoring.

## Federated learning and differential privacy

OWASP lists federated learning and differential privacy as privacy-preserving techniques. Federated learning trains models using decentralized data stored across servers or devices, reducing the need to centralize raw data. Differential privacy adds noise to data or outputs so it is harder to infer individual data points.

These techniques are most relevant to model training and analytics. They do not replace runtime access control in a RAG application. A system can use privacy-preserving training and still leak sensitive records if retrieval sends unauthorized context to the model.

## User education and transparency

The source recommends educating users on safe LLM use and maintaining transparent policies for data retention, usage, deletion, and training. Users should be told what data not to enter and whether their inputs may be retained or used for training. They should also have clear opt-out choices where applicable.

Application owners should provide terms of use and privacy notices that match actual data handling. If prompts, uploaded files, retrieved context, or generated answers are logged, the policy should say so.

## Secure system configuration

OWASP recommends concealing system preambles and applying security misconfiguration best practices. Applications should avoid leaking sensitive details through errors, debug output, stack traces, environment settings, route decisions, or prompt templates.

Secure configuration practices for LLM applications include:

- keep secrets out of prompts and retrieved documents;
- disable verbose errors in user-facing responses;
- avoid returning raw tool outputs when they contain sensitive fields;
- separate user-visible reasoning from internal traces;
- restrict access to logs and traces;
- redact sensitive context in persisted artifacts;
- monitor unusual requests for system prompts, credentials, or hidden configuration.

## Tokenization, redaction, and homomorphic encryption

OWASP lists tokenization and redaction as advanced techniques for preprocessing sensitive information. Tokenization replaces sensitive values with controlled substitutes. Redaction removes or masks sensitive values before processing. These techniques are practical for prompts, logs, indexing, and output filtering.

The source also names homomorphic encryption as a way to support privacy-preserving data analysis and machine learning, allowing computation while data remains confidential. This is a specialized control and may not be practical for every RAG workflow, but it reflects the broader principle that sensitive data should be protected during processing, not only at rest.

## Example attack scenarios

OWASP provides three compact scenarios:

- Unintentional data exposure: a user receives a response containing another user's personal data because data sanitization was inadequate.
- Targeted prompt injection: an attacker bypasses input filters to extract sensitive information.
- Training-data leak: negligent inclusion of sensitive data in training leads to disclosure in model output.

RAG-specific versions of these scenarios include:

- a user retrieves a private HR record because the vector index lacks user-level filtering;
- a prompt injection asks the model to reveal hidden system instructions or private context;
- a generated answer cites a confidential source because the application validates citation syntax but not source authorization;
- logs retain retrieved context containing credentials or customer data;
- an evaluation artifact stores raw traces that include sensitive inputs.

## Related frameworks and provenance

OWASP links sensitive information disclosure to MITRE ATLAS techniques related to training data membership inference, model inversion, and model extraction:

- AML.T0024.000 - Infer Training Data Membership;
- AML.T0024.001 - Invert ML Model;
- AML.T0024.002 - Extract ML Model.

The source reference list points to incidents and research on enterprise data leaks, repeated-token extraction of sensitive data, differential privacy, and Proof Pudding model extraction. The detailed bibliography is compacted here because the corpus value is in the normalized OWASP vulnerability guidance and mitigation structure.
