# Source snapshot

Source metadata:
- source_slug: owasp-llm06-excessive-agency
- category: LLM security and risks
- upstream_url: https://github.com/OWASP/www-project-top-10-for-large-language-model-applications/blob/0205957/2_0_vulns/LLM06_ExcessiveAgency.md
- source_markdown: https://raw.githubusercontent.com/OWASP/www-project-top-10-for-large-language-model-applications/0205957/2_0_vulns/LLM06_ExcessiveAgency.md
- license: CC BY-SA 4.0
- pinned_version: owasp-llm-top-10@0205957
- snapshot_type: normalized documentation digest from OWASP markdown
- normalization: removed repository page chrome and compacted reference-list detail; retained excessive agency definition, root causes, tool and extension risk examples, mitigation controls, monitoring limits, and the email-assistant attack scenario

---
# Tool-use and excessive agency risks

OWASP LLM06:2025 defines excessive agency as the vulnerability that allows damaging actions to be performed because an LLM-based system has too much functionality, permission, or autonomy. The risk appears when an LLM application can call functions, use extensions, invoke tools, operate plugins, interface with downstream systems, or coordinate with other agents.

An LLM-based system often receives some degree of agency from its developer. The system may choose which tool to call, pass arguments to that tool, interpret the tool's output, and then make more calls based on the previous result. In agent-based designs, repeated LLM invocations can build on earlier outputs, which means a single unsafe decision can compound across a workflow.

Excessive agency is triggered when unexpected, ambiguous, manipulated, or low-quality LLM output causes the application to take harmful action. OWASP names several common triggers:

- hallucination or confabulation from benign but poorly engineered prompts;
- a weak or poorly performing model;
- direct prompt injection from a malicious user;
- indirect prompt injection from malicious or compromised external content;
- tool output from a malicious or compromised extension;
- influence from a malicious or compromised peer agent in a multi-agent system.

The source distinguishes excessive agency from insecure output handling. Insecure output handling concerns insufficient scrutiny of LLM output before it is consumed. Excessive agency focuses on the scope of actions the LLM-connected system is allowed to perform.

## Root causes

OWASP identifies three typical root causes:

- excessive functionality;
- excessive permissions;
- excessive autonomy.

These root causes can overlap. A tool may expose unnecessary functions, run with a privileged identity, and execute without user approval. A prompt injection that reaches such a tool has a much larger blast radius than one constrained to read-only, user-scoped, human-approved actions.

## Excessive functionality

Excessive functionality exists when the LLM agent can call extensions or functions that are not needed for the intended operation.

OWASP gives several examples:

- A developer wants the agent to read documents from a repository, but the chosen third-party extension can also modify and delete documents.
- A plugin tested during development remains available to the agent after the team switches to a better alternative.
- An open-ended tool, such as one designed to run a specific shell command, fails to prevent other shell commands from being executed.

For RAG systems, excessive functionality may look like:

- a retrieval tool that can both read and mutate source documents;
- a document connector that can export entire repositories when only one chunk is needed;
- a web-fetch tool that can access arbitrary URLs when only allowlisted sources are intended;
- a trace inspection tool that can reveal private logs to ordinary users;
- an evaluation tool that can delete or overwrite artifacts during ordinary query execution.

The core control is to expose only the functions required by the application workflow.

## Excessive permissions

Excessive permissions exist when a tool or extension has more authority in downstream systems than the application needs.

OWASP examples include:

- a read-oriented database extension that connects using an identity with `SELECT`, `UPDATE`, `INSERT`, and `DELETE` permissions;
- a tool intended to operate for an individual user but using a generic privileged identity that can access files belonging to all users.

In RAG applications, excessive permissions are a common cause of data leakage and unauthorized actions. A retrieval service account may index or retrieve documents from all tenants. A file connector may have broad workspace permissions. A tool may use a backend admin token even when the action should be constrained to a user's role.

The model should not be treated as the authorization boundary. Permissions must be enforced in deterministic application code and downstream systems.

## Excessive autonomy

Excessive autonomy exists when an LLM-based application or extension performs high-impact actions without independent verification, approval, or policy enforcement. OWASP gives the example of a document-deletion tool that deletes a user's documents without confirmation.

Autonomy risk rises with impact. Read-only summarization has a different risk profile from sending email, posting public content, deleting files, changing permissions, purchasing goods, deploying code, or approving financial transactions.

For agentic RAG workflows, autonomy controls should be explicit. The system can draft an action, but a user or trusted policy engine should approve high-impact execution.

## Impact

Excessive agency can affect confidentiality, integrity, and availability. The exact impact depends on which systems the LLM application can reach.

Possible impacts include:

- unauthorized disclosure of data through over-privileged retrieval or tool calls;
- unauthorized updates, deletions, or inserts in downstream systems;
- external messages sent with sensitive information;
- execution of unintended commands;
- workflow manipulation across repeated agent steps;
- broad damage from a single prompt injection because the agent can act beyond its intended scope.

# Permission boundaries and mitigations

OWASP's mitigation strategy is to narrow what the model-connected system can do, narrow where it can do it, and require independent checks for high-impact actions. Some controls prevent excessive agency directly. Other controls, such as monitoring and rate limiting, limit damage but do not eliminate the vulnerability.

## Minimize extensions

Only offer the LLM agent the extensions it needs. If a system does not need to fetch URL content, do not provide a URL-fetching tool. If a workflow only needs retrieval, do not expose write, delete, or send functions.

A practical tool registry should be scoped by workflow. Different routes, users, or modes can receive different tool allowlists. For example, a corpus inspection command does not need the same tool surface as an administrative ingestion workflow.

## Minimize extension functionality

Extensions should implement only the required functions. OWASP gives the example of a mailbox summarization extension: it may need to read email, but it should not also delete or send messages.

Granular tools are safer than broad tools because their behavior is easier to reason about and validate. A tool named `read_user_email_headers` is easier to constrain than a tool named `email_action` that accepts arbitrary operation names.

## Avoid open-ended extensions

OWASP recommends avoiding open-ended extensions where possible, such as generic shell execution or arbitrary URL fetching. Instead, applications should build more granular tools.

For example, if an application needs to write model output to a file, a generic shell command tool creates a large action surface. A specific file-writing extension with path restrictions, content validation, and audit logging is safer.

RAG systems should be especially cautious with open-ended tools because retrieved content can contain indirect prompt injections. If a malicious chunk tells the model to fetch a URL, run a command, or export data, an open-ended tool may turn the injected instruction into a real action.

## Minimize extension permissions

Extensions should receive only the downstream permissions needed for their task. OWASP gives the example of a product-recommendation agent that only needs read access to a products table; it should not access other tables or write records.

This should be enforced with downstream permissions for the identity used by the extension. Application prompts and model instructions are not sufficient. If the database identity can delete records, a prompt injection may eventually cause a delete operation unless code and permissions block it.

## Execute extensions in the user's context

OWASP recommends tracking user authorization and security scope so downstream actions happen in the context of the specific user. For example, an extension that reads a user's code repository should require OAuth authentication and the minimum scope necessary.

This prevents the confused-deputy pattern where the LLM application uses a privileged service identity to perform an action the user could not perform directly. User-scoped execution also improves auditability because downstream logs can identify who authorized the action.

## Require user approval

High-impact actions should require human approval before execution. OWASP notes that approval can be implemented in the downstream system or inside the extension itself.

Approval is useful for actions such as:

- sending email or external messages;
- posting public content;
- deleting files or records;
- updating permissions;
- initiating purchases or financial transfers;
- executing code or deployment operations.

The approval step should show the action, target, key parameters, and data that will be sent. The system should not ask for approval using only a vague summary generated by the same model that may have been manipulated.

## Complete mediation

OWASP recommends implementing authorization in downstream systems rather than relying on the LLM to decide whether an action is allowed. Complete mediation means every request made through extensions is validated against security policy.

For RAG and agent systems, complete mediation includes:

- validating user identity and role on every tool call;
- checking source-level access before retrieved context is returned;
- enforcing object-level permissions in downstream systems;
- validating tool parameters against allowlists and schemas;
- rejecting actions that exceed the user's scope even if the model requests them.

The model can suggest an action, but deterministic policy enforcement decides whether the action is allowed.

## Sanitize LLM inputs and outputs

OWASP recommends secure coding practices with a strong focus on input sanitization, and names SAST, DAST, and IAST as development-pipeline testing methods.

Input and output sanitization can reduce prompt injection and malformed tool-call risk, but it should not be treated as the only control. Excessive agency is best reduced by shrinking function scope, permissions, and autonomy. Sanitization helps catch suspicious instructions, malformed parameters, unsafe URLs, unexpected commands, and sensitive output before they reach tools or users.

## Monitoring and rate limiting

OWASP states that logging, monitoring, and rate limiting do not prevent excessive agency, but they can reduce damage.

Useful monitoring includes:

- tool call logs with user, tool name, parameters, authorization result, and outcome;
- alerts for unusual tool-call volume or sensitive targets;
- detection of repeated denied actions;
- review of downstream system activity initiated by LLM extensions;
- trace capture for incident analysis with sensitive data redacted.

Rate limiting can reduce the number of undesirable actions within a time window, increasing the chance that monitoring catches the issue before significant damage occurs.

## Example attack scenario

OWASP describes an LLM-based personal assistant that summarizes incoming email. The system needs mail-reading capability, but the selected extension can also send messages. The app is vulnerable to indirect prompt injection: a malicious incoming email tricks the LLM into scanning the inbox for sensitive information and forwarding it to the attacker's address.

The source identifies three direct fixes:

- eliminate excessive functionality by using an extension that only reads mail;
- eliminate excessive permissions by authenticating to the user's email service with an OAuth session scoped to read-only access;
- eliminate excessive autonomy by requiring the user to manually review and send every email drafted by the extension.

Rate limiting on the mail-sending interface would not remove the vulnerability, but it could reduce damage by limiting how many messages are sent before the issue is detected.

## Related references and provenance

The source reference list points to cases and design patterns involving Slack AI data exfiltration, rogue agents misusing APIs, cross-plugin request forgery, guardrail interface guidelines, dual-LLM patterns, and sandboxing agentic workflows. The detailed links are compacted here because the corpus value is in the normalized OWASP guidance for reducing excessive functionality, permissions, and autonomy.
