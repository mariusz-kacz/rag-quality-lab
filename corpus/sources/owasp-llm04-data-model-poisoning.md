# Source snapshot

Source metadata:
- source_slug: owasp-llm04-data-model-poisoning
- category: LLM security and risks
- upstream_url: https://github.com/OWASP/www-project-top-10-for-large-language-model-applications/blob/0205957/2_0_vulns/LLM04_DataModelPoisoning.md
- source_markdown: https://raw.githubusercontent.com/OWASP/www-project-top-10-for-large-language-model-applications/0205957/2_0_vulns/LLM04_DataModelPoisoning.md
- license: CC BY-SA 4.0
- pinned_version: owasp-llm-top-10@0205957
- snapshot_type: normalized documentation digest from OWASP markdown
- normalization: removed repository page chrome and compacted reference-list detail; retained data and model poisoning definition, affected lifecycle stages, model-repository and backdoor risks, examples, attack scenarios, and mitigation controls with RAG ingestion implications

---
# Data and model poisoning risks

OWASP LLM04:2025 defines data and model poisoning as manipulation of pre-training, fine-tuning, embedding, or other model-development data to introduce vulnerabilities, backdoors, bias, degraded performance, toxic behavior, or exploitable downstream effects. The source frames poisoning as an integrity attack: tampered data can change the model's ability to make accurate and safe predictions.

The risk is not limited to model pre-training. OWASP names multiple lifecycle stages where poisoning may originate:

- pre-training, where a model learns from broad general data;
- fine-tuning, where a model is adapted to a narrower task or domain;
- embedding, where text or other content is converted into numerical vectors for retrieval;
- transfer learning, where a pre-trained model is reused on a new task.

External data sources are a recurring concern because they may be unverified, malicious, outdated, biased, or controlled by an attacker. In a RAG system, this maps directly to ingestion risk: documents, tickets, wikis, web pages, PDFs, user uploads, or third-party feeds can be indexed and later retrieved as evidence. If the ingestion pipeline admits poisoned content, the generator may treat that content as trustworthy context.

## Poisoning effects

OWASP identifies several possible outcomes:

- degraded model performance;
- biased outputs;
- toxic or harmful content;
- erroneous claims;
- compromised output quality;
- exploitation of downstream systems;
- backdoors that activate only when a trigger appears.

Backdoors are especially difficult because normal behavior may appear unchanged until a specific trigger causes a harmful behavior change. The source compares this to sleeper-agent behavior: the model or model-connected system can pass ordinary tests while retaining hidden triggered behavior.

For RAG applications, a backdoor does not need to live inside model weights. It may live in indexed content. A poisoned source can include hidden instructions, false facts, malicious links, biased language, or trigger phrases that only affect the model when retrieved for a targeted query.

## Model repository and artifact risk

The OWASP source also warns that shared repositories and open-source model platforms can carry risks beyond ordinary data poisoning. Models distributed through shared repositories may include malware through serialization or loading techniques, such as malicious pickle files that execute code when loaded.

This connects poisoning to supply-chain risk. A team may trust a downloaded model, adapter, dataset, or embedding artifact because it is popular or open source, but the artifact itself may be malicious or tampered with. Corpus and RAG pipelines should therefore treat models, datasets, and precomputed embeddings as software supply-chain artifacts that need provenance, scanning, and controlled loading.

## RAG-specific poisoning paths

LLM04 complements vector and embedding weaknesses by focusing on how unsafe data enters the system before retrieval. In a RAG quality lab, common poisoning paths include:

- indexing user-submitted documents without validation;
- allowing hidden text or prompt instructions inside PDFs, resumes, tickets, or HTML;
- mixing trusted and untrusted sources in one vector store without labels;
- accepting third-party documentation or vendor content without source authentication;
- reusing generated model output as future retrieval material without review;
- failing to version datasets and detect unexpected changes;
- importing embeddings or model artifacts from untrusted locations.

Once poisoned content enters the corpus, retrieval can amplify it. A high similarity score can make the poisoned chunk appear authoritative for the exact question the attacker targeted. Output filters may be too late if the model already received and incorporated the poisoned evidence.

# Lifecycle, scenarios, and mitigation controls

OWASP's mitigation strategy is to preserve data and model integrity across the lifecycle: track provenance, validate sources, restrict access to untrusted data, version datasets, test robustness, monitor anomalous behavior, and ground inference with trusted sources.

## Common vulnerability examples

The source gives several examples of vulnerable conditions:

1. Malicious actors introduce harmful data during training, causing biased outputs. OWASP names split-view data poisoning and frontrunning poisoning as example techniques.
2. Attackers inject harmful content directly into the training process, compromising output quality.
3. Users unknowingly provide sensitive or proprietary information during interactions, and that information may later be exposed in outputs.
4. Unverified training data increases the risk of biased or erroneous outputs.
5. Weak resource-access restrictions allow unsafe data to be ingested and reflected in model behavior.

For RAG systems, the same examples can apply to the knowledge base even when the base model is unchanged. If the corpus contains poisoned or sensitive material, the system can produce biased, incorrect, or leaking answers during retrieval-augmented generation.

## Mitigation controls

OWASP recommends tracking data origins and transformations. It names OWASP CycloneDX, ML-BOM approaches, and dynamic analysis of third-party software as ways to improve provenance and artifact review. The reusable control is provenance: know where data, models, adapters, and embeddings came from; how they changed; and which version is active.

The source also recommends rigorous vendor vetting and validation of model outputs against trusted sources. A model or RAG system should not rely on an untrusted source simply because it was retrieved. Critical answers should be grounded in sources with known provenance and appropriate authority.

Sandboxing is another mitigation. The model and ingestion pipeline should have limited exposure to unverified data sources. Resource controls should prevent models, tools, or crawlers from accessing unintended data locations. In RAG systems, this means ingestion jobs should not crawl broad file shares, private folders, or arbitrary URLs unless the source is explicitly approved.

Data version control is a core integrity measure. OWASP recommends DVC-style tracking to detect dataset manipulation. A RAG corpus should similarly keep source snapshots, content hashes, chunk IDs, embedding versions, and ingestion timestamps so unexpected changes are visible and reproducible.

OWASP recommends anomaly detection to filter adversarial data and monitoring training loss or model behavior for signs of poisoning. For RAG, analogous monitoring can inspect unusual retrieval patterns, sudden changes in source distribution, chunks with hidden text, source updates that strongly affect answers, or generated answers that diverge from trusted references.

The source also recommends testing robustness with red-team campaigns and adversarial techniques. For a RAG lab, this includes adversarial documents, hidden instructions, poisoned candidate resumes, conflicting source records, misleading FAQs, and targeted queries designed to retrieve malicious chunks.

## User-supplied information and retraining

OWASP recommends storing user-supplied information in a vector database so adjustments can be made without retraining the entire model. This can reduce the need to put volatile user data into model weights. It does not remove poisoning risk; it moves the risk into retrieval infrastructure where versioning, access control, source labels, deletion, and re-indexing can be managed more directly.

This is a useful design distinction:

- model training and fine-tuning changes are harder to inspect and roll back;
- RAG corpus changes can be versioned, filtered, removed, re-embedded, and audited.

The system still needs controls. User-supplied retrieval content should be labeled, permissioned, scanned, and separated from trusted reference material when appropriate.

## Grounding and RAG as mitigation

The OWASP source says that during inference, Retrieval-Augmented Generation and grounding techniques can reduce hallucination risks. In this corpus, that guidance should be read carefully. RAG can reduce unsupported generation when the retrieved sources are trusted and relevant. RAG can also become an attack path if the retrieval corpus is poisoned.

The practical rule is that grounding must be source-aware:

- retrieve from trusted, versioned, and authorized sources;
- validate source identity and integrity before indexing;
- preserve metadata through chunking and embedding;
- prefer high-authority sources when conflicts exist;
- reject or quarantine suspicious source updates;
- evaluate whether answers cite the correct and trusted evidence.

## Attack scenarios

OWASP provides five compact scenarios:

1. An attacker biases model outputs by manipulating training data or using prompt injection, spreading misinformation.
2. Toxic data passes through without proper filtering and leads to harmful or biased outputs.
3. A malicious actor or competitor creates falsified training documents, causing outputs to reflect inaccuracies.
4. Inadequate filtering lets an attacker insert misleading data through prompt injection, compromising outputs.
5. An attacker uses poisoning to insert a backdoor trigger, creating exposure to authentication bypass, data exfiltration, or hidden command execution.

For RAG, these scenarios are concrete ingestion test cases. A good evaluation set should include poisoned documents, falsified records, hidden text, misleading source conflicts, and trigger-like instructions to verify that ingestion, retrieval, and generation controls work together.

## Related frameworks and references

OWASP links this topic to MITRE ATLAS backdoor model techniques, the NIST AI Risk Management Framework, and the OWASP Machine Learning Security Top 10 transfer learning attack. The source reference list also points to research and incidents on web-scale training-data poisoning, PoisonGPT, malicious model repositories, malicious pickled model files, backdoor attacks, and sleeper-agent behavior.

The detailed bibliography is compacted here because the corpus value is in the normalized OWASP vulnerability guidance. The main lesson for this project is that RAG quality depends on corpus integrity. A retriever cannot compensate for a knowledge base that has admitted malicious, falsified, unauthorized, or poorly governed content.
