# Source snapshot

Source metadata:
- source_slug: openai-evaluation-flywheel
- category: RAG evaluation and quality
- upstream_url: https://developers.openai.com/cookbook/examples/evaluation/building_resilient_prompts_using_an_evaluation_flywheel
- source_markdown: https://raw.githubusercontent.com/openai/openai-cookbook/8730772/examples/evaluation/Building_resilient_prompts_using_an_evaluation_flywheel.md
- license: MIT
- pinned_version: openai-cookbook@8730772
- snapshot_type: normalized documentation digest from OpenAI Cookbook markdown
- normalization: removed website navigation, image-only references, author chrome, and long external-reading lists; retained evaluation flywheel methodology, qualitative failure analysis, annotation taxonomy, grader construction, prompt optimization, synthetic test expansion, LLM-judge alignment, and CI/production monitoring guidance

---
# Failure-mode discovery and annotation

The source presents an evaluation flywheel for building resilient prompts. A resilient prompt is one that produces high-quality responses across the full breadth of possible inputs. The motivation is practical: prompts that appear to work in common cases can fail on edge cases, slight wording changes, new contexts, or production traffic that differs from development examples.

The evaluation flywheel replaces ad hoc prompt changes with a structured loop:

1. Analyze: review examples qualitatively to understand how and why the system fails.
2. Measure: turn recurring failure modes into a dataset and automated graders so performance can be tracked at scale.
3. Improve: make targeted changes, such as rewriting prompts, adding examples, changing model parameters, or adjusting system components.

The process is continuous. After the system improves, new and subtler failure modes appear, and the cycle starts again. The core discipline is to diagnose failures before trying to fix them, then measure whether each proposed fix actually improves behavior.

The example application in the source is an apartment leasing assistant that answers questions from prospective renters, such as apartment size or tour availability. The workflow begins by loading the relevant prompt, traces, inputs, and outputs into an evaluation dataset. In a RAG application, the same pattern would include user query, retrieved context, generated response, citations or source references, and any tool or retrieval trace needed to understand the failure.

The source emphasizes that automated metrics are useful for tracking progress, but they do not explain why a failure occurred. Manual analysis of model outputs is the most effective way to discover actionable failure modes. The recommended method uses annotation: structured labels applied to examples so unstructured failures become categories that can be counted, prioritized, and converted into automated checks.

The annotation process has two stages: open coding and axial coding.

## Open coding

Open coding is the discovery phase. Review a sample of failing traces and apply descriptive labels to the errors found in each example. The source recommends starting with around 50 failing traces. At this stage, the goal is not a perfect taxonomy. The goal is to capture concrete, grounded descriptions of failures as they appear in data.

For the apartment leasing assistant, example open codes include:

- bot suggested a tour time that was not available;
- the amenities list was returned as one dense block of text;
- the assistant failed to cancel the original appointment when rescheduling;
- the floorplan link was broken.

These labels are intentionally specific. A label like `bad answer` is too vague to guide a fix. A label like `suggested unavailable tour time` points toward the data, retrieval, or instruction constraint that must be corrected.

For a RAG system, analogous open codes might include:

- answer cites a chunk that was not included in retrieved context;
- retrieved chunks are relevant to the entity but not to the asked attribute;
- no-answer response was not used when context lacked evidence;
- answer copied stale source text despite newer retrieved context;
- generated summary ignored a high-relevance source;
- retrieval returned near-duplicate chunks and crowded out necessary evidence.

Open coding should stay close to the observed trace. Each label should describe what failed, not jump immediately to a solution.

## Axial coding

Axial coding groups open codes into higher-level categories. The source describes this as identifying relationships between initial labels to build a structured understanding of core problems. The apartment leasing example groups failures into categories such as tour scheduling/rescheduling issues and formatting errors.

Example grouping:

```text
Tour scheduling/rescheduling issue
- Bot suggested a tour time that was not available.
- Failed to cancel the original appointment when rescheduling.

Formatting error with output
- The list of amenities was a single block of text.
- The link to the floorplan was broken.
```

The value of axial coding is prioritization. Once labels are grouped, the team can quantify which failure categories dominate. If 35% of failures relate to tour scheduling and 10% relate to formatting, improvement work should start with scheduling unless business risk says otherwise.

For RAG evaluation, axial categories can separate retrieval, context assembly, generation, and citation problems. This prevents teams from treating every answer failure as a prompt problem. A grounded but incomplete answer may require better context selection. A fluent but unsupported answer may require stricter grounding instructions or citation validation. A missing answer may require larger `top_k`, better chunking, or a different retrieval mode.

The source's qualitative workflow can be translated into a compact evaluation practice:

1. Collect failing examples from production logs, test traces, or review sessions.
2. Sample enough failures to see repeated patterns.
3. Apply open codes that describe observed errors concretely.
4. Group open codes into axial categories.
5. Count category frequencies and inspect representative examples.
6. Choose the failure categories that are frequent, high risk, or directly tied to product quality.
7. Build graders and test data around those categories.

The key idea is that evaluation starts with careful observation. Automated graders should be built after the team understands what failures actually look like.

# Automatic graders, prompt improvement, and test expansion

After the failure taxonomy is established, the source moves from qualitative analysis to measurement. The OpenAI Platform supports automated graders, including Python graders and LLM graders, that can run in bulk over a dataset. The example builds LLM graders for two issues discovered during analysis:

- a formatting grader that checks whether the response matches the desired output format;
- an availability accuracy grader that compares returned availability against ground truth fields in the dataset.

The graders are tied to the failure taxonomy. This is important: graders are not generic quality labels invented in isolation. They operationalize observed failure modes so future prompt versions, model settings, or system changes can be evaluated consistently.

With graders in place, teams can evaluate an updated prompt, new model parameters, or newly discovered edge cases without repeating the entire manual review process. The output becomes a baseline for comparison. A change is only an improvement if it reduces the targeted failure rate without causing unacceptable regressions elsewhere.

## Prompt optimization

Once errors are annotated and graders exist, the source describes two prompt improvement paths. A team can manually revise the prompt using the failure analysis, or use OpenAI's prompt optimization tool. The optimizer uses generated outputs, custom annotation columns, and graders to construct an improved prompt.

The example is intentionally small, but the source notes that a fuller dataset, such as the approximately 50 rows recommended for initial analysis, gives the optimizer more signal. After optimization, teams may iterate further by re-annotating new outputs, adding or refining graders, and optimizing again.

The source also notes that grader and annotation column specifications persist across prompt versions, allowing teams to compare prompts and model configurations in separate tabs. The practical lesson is that prompt changes should be versioned and evaluated against the same measurements. This makes prompt work more like engineering: change one or more candidate prompts, run evals, compare results, and keep changes that improve measured behavior.

For RAG systems, prompt improvement might include:

- adding explicit no-answer behavior when retrieved context does not contain the answer;
- requiring citations to included chunks;
- changing answer format to expose uncertainty or evidence;
- adding examples for ambiguous or multi-hop questions;
- making retrieval-context boundaries clearer;
- instructing the model not to use unsupported outside knowledge.

Prompt changes should be judged against retrieval-aware test cases. If the issue is missing evidence, a generation prompt cannot fully fix it. If the issue is unsupported synthesis despite good evidence, prompt and grader changes are appropriate.

## Synthetic data expansion

The source treats synthetic data as an advanced supplement to the core evaluation flywheel. It is useful when production logs are scarce, the product has not launched, a specific failure mode needs more coverage, or the team has a hypothesis about a weakness but lacks enough real examples.

The source warns that simply asking a model to generate many examples often produces homogeneous test cases. A more structured method defines dimensions of a query and generates examples across combinations of those dimensions.

In the leasing example, dimensions include:

- Channel: voice, chat, or text;
- Intent: tour scheduling, maintenance, or general information;
- Persona: prospective resident or agency.

A tuple such as `(Text, Tour Scheduling, Prospective Resident)` can be used to prompt a model for a realistic test case matching that profile. This forces coverage across multiple axes instead of producing many similar examples.

The source also recommends perturbations that make test cases harder and more realistic. Perturbations can include irrelevant information, mistakes, different slang, or other variations that test whether the prompt remains robust under noisy inputs.

For RAG evaluation, useful synthetic dimensions might include:

- answerability: answer present, absent, partially present, or contradicted;
- retrieval difficulty: exact phrase match, semantic paraphrase, entity alias, or multi-hop evidence;
- context noise: clean context, near-duplicate chunks, irrelevant chunks, or stale context;
- user behavior: concise query, vague query, misspelled query, adversarial instruction, or false premise;
- expected response: direct answer, no-answer, clarification request, or cited explanation.

Synthetic data should not replace human-reviewed production examples. Its role is to expand coverage around known risks and make edge cases explicit.

## Aligning LLM judges

The source emphasizes that an automated LLM judge is only useful if its judgments are trustworthy. Judge alignment should be measured against a human subject-matter expert using a gold-standard dataset.

Simple accuracy can be misleading because many evaluation datasets are imbalanced. If most examples pass, a judge that always predicts pass can appear accurate while never catching failures. The source recommends tracking two rates:

- True Positive Rate: how well the judge correctly identifies failures;
- True Negative Rate: how well the judge correctly identifies passes.

The goal is to achieve high scores on both. A good judge finds real failures without being overly critical.

The recommended split for aligning a judge is:

1. Train set, about 20%: select clear pass/fail examples to embed as few-shot examples in the judge prompt.
2. Validation set, about 40%: run the judge, inspect disagreements with the expert, and tune judge instructions to improve both failure detection and pass detection.
3. Test set, about 40%: hold this back until the end and run it once after tuning to estimate judge performance without overfitting.

This process matters for RAG evaluation because LLM judges can be sensitive to prompt wording, evidence presentation, and label imbalance. A groundedness judge that mostly sees passing answers may under-detect hallucinations. A strict citation judge may over-fail useful answers that cite imperfectly. Alignment against human labels makes evaluator behavior visible before it is used in CI or release gates.

## Continuous evaluation practice

The source closes by recommending that the flywheel become part of engineering practice. Graders should be integrated into CI/CD, and production data should be monitored to discover new failure modes. The flywheel does not stop after one prompt update.

A practical RAG-focused loop is:

1. Collect traces with query, retrieved chunks, selected context, answer, citations, and validation outcome.
2. Manually inspect failures and annotate them with open codes.
3. Group failures into categories such as retrieval miss, poor context assembly, unsupported generation, citation error, and incomplete answer.
4. Build graders or deterministic checks for the high-priority categories.
5. Expand the test set with production examples and structured synthetic cases.
6. Change prompts, retrieval parameters, chunking, or model settings.
7. Re-run evals and compare against the baseline.
8. Monitor production for new failure modes and restart the cycle.

For this project's corpus, the evaluation flywheel source is useful because it gives the operational method around RAG metrics. Retrieval metrics, groundedness checks, and no-answer tests are more valuable when they are tied to observed failures, judged against stable datasets, and used in an iterative loop that turns trace review into measurable improvement.
