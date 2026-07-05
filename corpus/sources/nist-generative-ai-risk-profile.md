# Source snapshot

Source metadata:
- source_slug: nist-generative-ai-risk-profile
- category: LLM security and risks
- upstream_url: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf
- source_pdf: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf
- license: Public NIST publication, reuse metadata pending snapshot verification
- pinned_version: nist-ai-600-1@2024-07
- snapshot_type: normalized documentation digest from NIST PDF
- normalization: removed cover pages, publication boilerplate, table formatting artifacts, footnote clutter, references, and appendix detail; retained the AI RMF profile purpose, GAI risk taxonomy, lifecycle framing, Govern/Map/Measure/Manage action structure, and RAG-oriented risk-management implications

---
# Generative AI risk taxonomy

NIST AI 600-1 is a cross-sectoral profile and companion resource for the NIST AI Risk Management Framework (AI RMF 1.0), focused on generative AI (GAI). The profile is voluntary and is meant to help organizations incorporate trustworthiness considerations into the design, development, use, and evaluation of GAI products, services, and systems.

The document treats a profile as an implementation of AI RMF functions, categories, and subcategories for a specific setting or technology. In this case, the technology is generative AI, including models and applications that generate derived synthetic content such as text, images, video, audio, or other digital content.

NIST frames GAI risks as risks that are novel to, or exacerbated by, generative AI. The profile introduces those risks and then maps suggested actions to AI RMF functions so organizations can govern, map, measure, and manage them.

## Risk dimensions

The source emphasizes that GAI risks vary by several dimensions:

- lifecycle stage: design, development, deployment, operation, or decommissioning;
- scope: individual model, application, implementation, organization, or broader ecosystem;
- source: model design, training data, inputs, outputs, human behavior, misuse, abuse, unsafe repurposing, or human-AI interaction;
- time scale: immediate, prolonged, or long-term;
- system characteristics: architecture, training mechanisms, libraries, data types, model access, weights availability, and use-case context.

This framing matters for LLM and RAG systems because a single failure can arise from multiple locations. A bad answer might reflect retrieval quality, stale source data, prompt design, user overreliance, insufficient evaluation, or weak incident response. The correct mitigation depends on where the risk originates and how it materializes.

## Known and uncertain risks

NIST notes that some GAI risks have empirical evidence, some are known but hard to estimate, and some remain uncertain. Risk estimation is difficult because GAI systems have wide ranges of stakeholders, uses, inputs, outputs, and downstream impacts. The science of AI measurement and safety is still immature, and organizations may lack visibility into training data.

The profile focuses on risks with an existing empirical evidence base at the time of publication. It does not attempt to fully cover speculative risks that may arise from future, more advanced systems. Future revisions may add risks or refine the existing ones as evidence changes.

For a RAG quality lab, this means evaluation should document what is measured and what remains unmeasured. A golden-set score is not a complete risk assessment. It is a scoped measurement under stated assumptions.

## Risk categories

NIST identifies twelve risks unique to or exacerbated by GAI:

1. CBRN information or capabilities: easier access to or synthesis of dangerous information or design capabilities related to chemical, biological, radiological, or nuclear weapons or dangerous materials.
2. Confabulation: confidently stated but erroneous or false content, including outputs that diverge from prompts, contradict prior outputs, or include false logic and citations.
3. Dangerous, violent, or hateful content: easier production of violent, inciting, radicalizing, threatening, self-harm, illegal, hateful, or disparaging content.
4. Data privacy: leakage, unauthorized use, disclosure, or de-anonymization of personal, biometric, health, location, or other sensitive data.
5. Environmental impacts: impacts from high compute resource use in training, maintaining, and operating GAI models.
6. Harmful bias or homogenization: amplification of historical, societal, or systemic biases; performance disparities across groups or languages; and overly uniform outputs that reduce diversity and may contribute to model collapse.
7. Human-AI configuration: risks from how humans interact with AI systems, including anthropomorphism, algorithmic aversion, automation bias, overreliance, or emotional entanglement.
8. Information integrity: reduced barriers to generating, exchanging, and consuming content that fails to distinguish fact from opinion or fiction, or that supports misinformation and disinformation campaigns.
9. Information security: lowered barriers for offensive cyber activity, increased attack surface, and risks to availability, confidentiality, or integrity of training data, code, and model weights.
10. Intellectual property: easier production or replication of copyrighted, trademarked, licensed, trade-secret, or plagiarized content without authorization.
11. Obscene, degrading, and/or abusive content: easier production or access to abusive imagery and related harms, including synthetic child sexual abuse material and nonconsensual intimate images.
12. Value chain and component integration: non-transparent or untraceable use of third-party components, improperly obtained data, insufficient supplier vetting, and difficulty attributing downstream behavior to specific components.

The profile maps these risks to trustworthy AI characteristics such as accountable and transparent, explainable and interpretable, fair with harmful bias managed, privacy enhanced, safe, secure and resilient, and valid and reliable.

## RAG-relevant risks

Many of the NIST risks map directly to RAG systems:

- Confabulation appears when the model generates unsupported claims, false citations, or overconfident answers despite weak context.
- Data privacy appears when retrieval sends unauthorized or sensitive chunks into context.
- Information integrity appears when retrieved or generated content cannot distinguish reliable source material from manipulated, stale, or uncertain material.
- Information security appears through prompt injection, poisoned documents, unsafe tool access, or exposed traces.
- Harmful bias and homogenization appear when a corpus, retriever, or answer generator systematically underperforms for groups, languages, or source types.
- Value chain and component integration appears when models, embeddings, vector stores, datasets, eval tools, or third-party connectors are reused without provenance and accountability.
- Human-AI configuration appears when users overtrust answers, citations, or model confidence.

NIST's taxonomy therefore supports a broader view than answer accuracy. A RAG system should be evaluated for retrieval quality, groundedness, privacy, provenance, security boundaries, user-facing uncertainty, and operational monitoring.

## Content provenance, testing, governance, and incident disclosure

Appendix A identifies four primary GAI considerations derived from NIST's public working group process:

- governance;
- content provenance;
- pre-deployment testing;
- incident disclosure.

These themes shape the suggested actions in the profile. For a RAG system, they translate into concrete practices:

- define who owns model, corpus, retrieval, and evaluation risks;
- preserve source provenance through ingestion, chunking, retrieval, context selection, and citation;
- run pre-deployment tests on answerable, no-answer, ambiguous, adversarial, and privacy-sensitive cases;
- maintain processes for reporting, triaging, and recovering from incidents such as data leakage, unsafe output, or unauthorized retrieval.

# Risk-management actions for LLM and RAG systems

NIST organizes suggested actions by AI RMF functions and subcategories. The profile uses action identifiers tied to the AI RMF functions:

- `GV`: Govern;
- `MP`: Map;
- `MS`: Measure;
- `MG`: Manage.

Each action includes a suggested activity, related GAI risks, and relevant AI actor tasks. NIST cautions that not every action applies to every actor or context. Applicability depends on the organization, system type, lifecycle stage, risk tolerance, and use of GAI.

## Govern

Govern actions establish organizational policies, accountability, and risk tolerance. NIST recommends aligning GAI development and use with applicable laws and regulations, including data privacy, copyright, and intellectual property requirements.

The profile also recommends integrating trustworthy AI characteristics into organizational policies, defining or updating risk tiers for GAI, and creating governance practices for testing, incident identification, and information sharing.

For LLM and RAG systems, governance should cover:

- acceptable uses and prohibited uses;
- ownership of corpus, model, retrieval, and evaluation decisions;
- legal review of data use, copyright, privacy, and retention;
- risk tiers for different deployments, tools, and data sensitivity levels;
- approval gates for high-impact uses;
- documentation of assumptions, limitations, and known failure modes.

Governance is also where organizations define human oversight. A RAG application used for low-stakes internal lookup may need different review, logging, and escalation than a system used for health, finance, law, hiring, or security workflows.

## Map

Map actions establish context, assumptions, system boundaries, impacts, and relevant actors. NIST recommends documenting data origin and content lineage, testing and evaluating data and content flows, and identifying how systems rely on upstream data sources or serve as dependencies for downstream systems.

NIST also recommends adversarial role-playing, GAI red-teaming, chaos testing, and threat profiling to identify anomalous or unforeseen failure modes. Organizations should regularly engage downstream AI actors and providers of inputs such as third-party data and algorithms.

For RAG systems, mapping should document:

- source repositories, document owners, licenses, and trust levels;
- ingestion transformations, chunking rules, embedding models, and vector stores;
- retrieval filters, rerankers, context assembly, and citation validation;
- how stale, conflicting, or unauthorized sources are handled;
- downstream users, affected communities, and operational contexts;
- adversarial pathways such as prompt injection, poisoned documents, and trace leakage.

Mapping prevents teams from treating the LLM as an isolated component. RAG behavior is a system property of data, retrieval, prompts, generation, tooling, users, and monitoring.

## Measure

Measure actions select and implement metrics for risks identified during mapping. NIST says unmeasured risks or trustworthiness characteristics should be documented, including why they cannot be measured.

The profile recommends provenance and anomaly-detection tools, demographic disaggregation of metrics, structured public feedback exercises, measurement of novel GAI risks, continuous monitoring of impacts across subpopulations, and evaluation of data quality and AI-generated content provenance.

NIST also recommends defining where structured human feedback, such as red-teaming, would be useful and documenting risks that cannot be measured quantitatively. For privacy, it recommends AI red-teaming for training-data output, reverse engineering, model extraction, membership inference, and disclosure of confidential or copyrighted data.

For RAG evaluation, measurement should include:

- retrieval metrics such as recall@k, precision@k, MRR, nDCG, or MAP;
- citation validity and source authorization checks;
- groundedness and answer relevance;
- no-answer correctness when evidence is insufficient;
- prompt-injection and poisoned-document tests;
- privacy checks for sensitive source leakage;
- latency, token, and cost metrics;
- subgroup, category, and case-type slices;
- documented unmeasured risks and limitations.

Measurement should also evaluate the metrics themselves. A small golden set, partial relevance labels, or model-graded rubric may not fully operationalize the risk of interest. NIST's emphasis on construct validity applies directly to RAG evaluation design.

## Manage

Manage actions develop and execute responses to prioritized risks. NIST describes response options including mitigation, transfer, avoidance, or acceptance.

The profile recommends documenting tradeoffs, decision processes, measurement results, and feedback. It also recommends monitoring the robustness and effectiveness of risk controls through red-teaming, field testing, participatory engagement, performance assessment, and user feedback.

For generated content, NIST recommends comparing outputs against predefined risk tolerance, guidelines, and principles; documenting training data sources for provenance; monitoring provenance protocols; analyzing harmful content, misinformation, and CBRN-related or abusive content; using feedback from internal and external AI actors; and using auditing tools where they help track lineage and authenticity.

For LLM and RAG systems, management actions include:

- define risk thresholds for release, rollback, or human review;
- remove or quarantine problematic sources from indexes;
- update prompts, retrieval filters, and context policies when failures are found;
- document tradeoffs between recall, precision, latency, cost, and safety;
- monitor deployed traces for citation errors, data leakage, and unsafe outputs;
- capture user and reviewer feedback into evaluation maintenance;
- maintain incident response plans for new risks and negative impacts.

## Incident response and recovery

NIST recommends incident response and recovery procedures that address new uses, unanticipated uses, the GAI value chain, and communication with downstream actors. The profile also recommends procedures for disengaging or deactivating AI systems that produce outcomes inconsistent with intended use.

It further recommends after-action assessments for incidents, policies for recording reported errors, near misses, and negative impacts, and reporting incidents in line with legal or regulatory requirements.

For RAG applications, incident response should define what happens when:

- unauthorized content is retrieved or disclosed;
- a generated answer causes or could cause harm;
- citations are fabricated or point to inaccessible sources;
- poisoned or malicious documents are discovered in the corpus;
- logs or traces contain sensitive content;
- a model or retrieval component changes behavior after an update.

An incident process should include triage, containment, source or index remediation, user notification where appropriate, evaluation-set updates, and a documented after-action review.

## Practical control pattern for a RAG lab

A compact implementation of NIST's Govern, Map, Measure, and Manage structure for RAG quality can look like this:

1. Govern: define acceptable use, data boundaries, risk tolerance, owner roles, and release criteria.
2. Map: document sources, transformations, permissions, retrieval flow, model dependencies, user groups, and failure modes.
3. Measure: run retrieval, grounding, citation, privacy, no-answer, latency, and adversarial checks against representative cases.
4. Manage: act on failures by updating corpus, prompts, retrieval filters, approval gates, monitoring, and incident procedures.

The source's core message is that GAI risk management is lifecycle work. It is not completed by one benchmark score or one prompt review. It requires governance, provenance, testing, measurement, monitoring, and incident learning across the full system.
