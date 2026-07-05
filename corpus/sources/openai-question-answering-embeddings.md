# Source snapshot

Source metadata:
- source_slug: openai-question-answering-embeddings
- category: RAG and context handling
- upstream_url: https://github.com/openai/openai-cookbook/blob/8730772/examples/Question_answering_using_embeddings.ipynb
- source_notebook: https://github.com/openai/openai-cookbook/blob/8730772/examples/Question_answering_using_embeddings.ipynb
- license: MIT
- pinned_version: openai-cookbook@8730772
- snapshot_type: normalized documentation digest from notebook markdown and compact code cells
- normalization: extracted the reusable Search-Ask retrieval workflow from notebook markdown and code; removed package-install scaffolding, API-key setup text, execution counts, long copied Wikipedia excerpts, raw notebook outputs, and large retrieved context dumps; retained search rationale, prepared embedding dataset loading, cosine ranking, token-budgeted context assembly, answer prompting, no-answer behavior, and retrieval debugging guidance

---
# Search-Ask retrieval workflow

The notebook demonstrates a two-step Search-Ask method for answering questions with a library of reference text. It starts from the observation that GPT can answer many questions from model training, but cannot reliably know unfamiliar topics such as recent events, private documents, past conversations, or other information absent from the model's training data. The workflow is:

1. Search the text library for relevant sections.
2. Insert the retrieved sections into a model message.
3. Ask the model to answer the user question from those sections.

The source explicitly contrasts this approach with fine-tuning for factual knowledge. Fine-tuning changes model weights and is better suited to tasks, formats, or styles than factual recall. Supplying text in the input message is treated like giving the model open notes: the relevant facts are available in short-term context at answer time. The practical constraint is that the model can only read a bounded amount of text in one request, so a large document library must be searched and trimmed before it is inserted into the prompt.

The notebook uses embedding-based search. It notes that text can be searched lexically, graph-based, or with embeddings, and presents embeddings as a simple starting point that works well for questions because a question often does not lexically overlap with its answer. The source also acknowledges that stronger systems can combine multiple signals, including keyword search, popularity, recency, user history, redundancy with prior results, click-rate data, and transformations such as HyDE, where a question is transformed into a hypothetical answer before embedding. GPT can also be used to rewrite questions into keyword or search-term sets.

The full procedure has three phases:

1. Prepare search data once per document: collect source documents, chunk them into mostly self-contained sections, embed each section, and store text plus embeddings. The notebook uses a prepared dataset of a few hundred Wikipedia articles about the 2022 Winter Olympics. The companion notebook `Embedding_Wikipedia_articles_for_search.ipynb` shows how the dataset was constructed.
2. Search once per query: embed the user question with the same embedding model family, compare the query embedding with stored text embeddings, and rank text sections by relatedness.
3. Ask once per query: put the question and the highest-ranked sections into a message for GPT and return the model's answer.

The prepared search data is loaded from `data/winter_olympics_2022.csv`. The file contains pre-chunked text and pre-computed embeddings. Because embeddings are stored in CSV as strings, the notebook converts them back to list values before search.

Compact form of the prepared data loading:

```python
import ast
import pandas as pd

embeddings_path = "data/winter_olympics_2022.csv"
df = pd.read_csv(embeddings_path)
df["embedding"] = df["embedding"].apply(ast.literal_eval)
```

The dataframe has two required columns:

- `text`: a retrievable article section string;
- `embedding`: the stored vector for that section.

The notebook selects `text-embedding-3-small` for embeddings and keeps a list of answer models such as `gpt-4o` and `gpt-4o-mini`. It uses `scipy.spatial.distance.cosine` to calculate relatedness as one minus cosine distance. The search function embeds the query, scores every stored section against the query vector, sorts the pairs from most related to least related, and returns the top texts with their relatedness scores.

Compact form of the search function:

```python
from scipy import spatial

EMBEDDING_MODEL = "text-embedding-3-small"

def strings_ranked_by_relatedness(
    query: str,
    df: pd.DataFrame,
    relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y),
    top_n: int = 100,
) -> tuple[list[str], list[float]]:
    query_embedding_response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=query,
    )
    query_embedding = query_embedding_response.data[0].embedding
    strings_and_relatednesses = [
        (row["text"], relatedness_fn(query_embedding, row["embedding"]))
        for _, row in df.iterrows()
    ]
    strings_and_relatednesses.sort(key=lambda x: x[1], reverse=True)
    strings, relatednesses = zip(*strings_and_relatednesses)
    return strings[:top_n], relatednesses[:top_n]
```

This implementation is intentionally direct: it scans the dataframe and sorts scores in memory. That is sufficient for the notebook's demonstration dataset. For larger corpora, the same conceptual contract moves into a vector database or search index: store section embeddings, embed the query, rank nearest sections, and return the strongest candidates with scores and source metadata.

The notebook's search examples inspect relatedness scores and retrieved strings for a query such as `curling gold medal`. This inspection matters because RAG quality failures can originate in either retrieval or generation. If the search step does not retrieve text containing the answer, no answer prompt can reliably fix the missing evidence. If the right text is retrieved but the model answers incompletely, the fix is likely in prompt design, context ordering, or model choice.

The cost discussion also separates embedding search from answer generation. The source states that, for systems with meaningful query volume, the GPT answer step is likely to dominate cost because chat/completion models are more expensive than embedding search. Exact costs depend on model choice, token count, and usage pattern, but the design implication is stable: use retrieval to send a compact evidence set rather than passing large libraries into the answer model.

# Context assembly, answer grounding, and no-answer behavior

After ranking candidate strings, the notebook builds a model message by inserting as many relevant article sections as fit within a token budget. This is the context assembly step: it converts ranked retrieval results into the concrete text that the answer model will see.

The helper function `num_tokens` uses `tiktoken.encoding_for_model` to estimate token count for a string and model. The `query_message` function then:

1. retrieves strings ranked by relatedness to the query;
2. starts with an instruction describing the source corpus and no-answer rule;
3. appends retrieved article sections one by one;
4. stops when adding the next section plus the question would exceed the token budget;
5. returns the assembled message followed by the user question.

Compact form of the context assembly:

```python
import tiktoken

GPT_MODELS = ["gpt-4o", "gpt-4o-mini"]

def num_tokens(text: str, model: str = GPT_MODELS[0]) -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def query_message(
    query: str,
    df: pd.DataFrame,
    model: str,
    token_budget: int,
) -> str:
    strings, relatednesses = strings_ranked_by_relatedness(query, df)
    introduction = (
        'Use the below articles on the 2022 Winter Olympics to answer the '
        'subsequent question. If the answer cannot be found in the articles, '
        'write "I could not find an answer."'
    )
    question = f"\n\nQuestion: {query}"
    message = introduction

    for string in strings:
        next_article = f'\n\nWikipedia article section:\n"""\n{string}\n"""'
        if num_tokens(message + next_article + question, model=model) > token_budget:
            break
        message += next_article

    return message + question
```

The message format uses a short introduction, repeated `Wikipedia article section` labels, triple-quoted section blocks, and a final `Question:` line. This makes retrieved evidence visibly separate from the user question. The quoted blocks also reduce ambiguity about which text is source material and which text is instruction.

The no-answer rule is part of the user message assembled for the model:

```text
If the answer cannot be found in the articles, write "I could not find an answer."
```

This is central to answer grounding. The notebook is not asking the model to answer from general knowledge when the retrieved articles do not contain the answer. It instructs the model to return a fixed no-answer phrase when evidence is absent. For RAG systems, this pattern is useful because it gives evaluators a concrete behavior to test on out-of-scope, false-premise, subjective, or insufficient-evidence questions.

The `ask` function wraps context assembly and generation. It creates the retrieval-augmented message, optionally prints it for debugging, sends it to the chat model with a system message that constrains the domain to the 2022 Winter Olympics, uses `temperature=0`, and returns the answer text.

Compact form of the answer function:

```python
def ask(
    query: str,
    df: pd.DataFrame = df,
    model: str = GPT_MODELS[0],
    token_budget: int = 4096 - 500,
    print_message: bool = False,
) -> str:
    message = query_message(query, df, model=model, token_budget=token_budget)
    if print_message:
        print(message)

    messages = [
        {
            "role": "system",
            "content": "You answer questions about the 2022 Winter Olympics.",
        },
        {"role": "user", "content": message},
    ]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message.content
```

The default token budget reserves about 500 tokens for the model's answer by setting the prompt budget to `4096 - 500`. This constant reflects the notebook's demonstration setup rather than a universal best practice. The reusable idea is to reserve output space and stop adding retrieved chunks before the prompt exhausts the model context window.

The notebook uses examples to illustrate both success and failure modes:

- a direct lookup question about gold medal winners in curling can succeed when relevant medal sections are retrieved;
- a counting question about records can be answered if the retrieved sections include the needed counts;
- a comparison question can partially answer when one compared entity is present and the other is absent;
- subjective questions should return the no-answer phrase because the evidence does not establish a factual answer;
- false-premise questions should return the no-answer phrase when no source supports the premise;
- questions outside the corpus scope, such as questions about a different Olympics or simple arithmetic, should not be answered from unrelated model knowledge;
- misspelled questions can still succeed because embedding search can match semantic intent without exact lexical overlap;
- open-ended questions can work when several retrieved sections collectively cover the topic.

The source also shows an instruction-injection-style user query that asks the model to ignore prior instructions and write unrelated content. The example is useful as a reminder that RAG prompts should separate user requests, system constraints, and retrieved context. The notebook's simple prompt is not presented as a complete security design, but it demonstrates that the model should remain focused on the stated domain and retrieved evidence rather than following an unrelated user instruction.

For debugging, the notebook recommends calling `ask(..., print_message=True)` to inspect the exact context sent to the model. This helps determine whether an error came from retrieval or generation. In one example, the top retrieved article section contained the necessary medalists, but later retrieved results emphasized some tournaments more than others, which could distract the answer model from producing a complete list. When the evidence is present but the answer is incomplete, possible fixes include changing model choice, improving the prompt, adjusting ranking or context order, reducing distracting chunks, or making the answer format more explicit.

The notebook notes that using a more capable model can improve the ask step when retrieval has already supplied enough source text. This distinction is important for evaluation. Retrieval metrics should check whether the relevant source text appears in selected context, while answer metrics should check whether the model used that context correctly and followed no-answer instructions.

The Search-Ask workflow can be summarized as a RAG contract:

1. retrieve candidate chunks by semantic similarity to the question;
2. assemble context in rank order until the token budget is reached;
3. preserve clear boundaries around source text;
4. ask the model to answer from the provided evidence;
5. define explicit behavior when the answer is absent;
6. inspect selected context when answers fail;
7. evaluate retrieval and answer generation as separate failure surfaces.

For this project's RAG corpus, the source is most relevant as a compact example of baseline vector retrieval plus bounded context construction. It provides concrete implementation details for similarity ranking, context budgeting, model prompting, answer grounding, and no-answer behavior, while also showing where a production implementation would need stronger indexing, metadata, citation validation, injection resistance, and evaluation.
