# Source snapshot

Source metadata:
- source_slug: openai-embedding-wikipedia-search
- category: RAG and context handling
- upstream_url: https://github.com/openai/openai-cookbook/blob/8730772/examples/Embedding_Wikipedia_articles_for_search.ipynb
- source_notebook: https://github.com/openai/openai-cookbook/blob/8730772/examples/Embedding_Wikipedia_articles_for_search.ipynb
- license: MIT
- pinned_version: openai-cookbook@8730772
- snapshot_type: normalized documentation digest from notebook markdown and compact code cells
- normalization: extracted the reusable ingestion workflow from the notebook; removed package-install scaffolding, API-key setup text, execution counts, notebook display output, and long example article text; retained collection strategy, Wikipedia section parsing, section cleaning, token-budget chunking, embedding batching, and storage guidance

---
# Document collection and cleaning

The notebook demonstrates the ingestion side of a simple retrieval system. It prepares a dataset of Wikipedia article sections for semantic search, then uses the resulting file in a companion question-answering notebook. The source frames the workflow as four stages: collect source documents, split them into short sections, embed each section with the OpenAI API, and store the text with its embedding for later retrieval. For large datasets, the notebook notes that a vector database is more appropriate than a flat CSV file.

The example corpus is a few hundred Wikipedia articles related to the 2022 Winter Olympics. The notebook uses `mwclient` to traverse the `Category:2022 Winter Olympics` page on `en.wikipedia.org`, collecting article titles from the category and one level of subcategories. The collection function distinguishes article pages from nested category pages, adds page names to a set so duplicates are collapsed, and recurses into subcategories only while the configured depth remains above zero.

Compact form of the collection pattern:

```python
CATEGORY_TITLE = "Category:2022 Winter Olympics"
WIKI_SITE = "en.wikipedia.org"

def titles_from_category(category, max_depth: int) -> set[str]:
    titles = set()
    for member in category.members():
        if type(member) == mwclient.page.Page:
            titles.add(member.name)
        elif isinstance(member, mwclient.listing.Category) and max_depth > 0:
            titles.update(titles_from_category(member, max_depth=max_depth - 1))
    return titles

site = mwclient.Site(WIKI_SITE)
category_page = site.pages[CATEGORY_TITLE]
titles = titles_from_category(category_page, max_depth=1)
```

This pattern is useful for RAG corpora because it separates source discovery from chunk construction. The retrieved article titles become stable document identifiers for the downstream splitting, cleaning, embedding, and storage steps.

After collecting titles, the notebook prepares the documents for search. It explicitly connects this preprocessing to model context limits: GPT models can only read a limited amount of text at once, so large documents need to be split into chunks that are short enough to retrieve and pass into a prompt. The notebook's Wikipedia-specific preparation has five main rules:

- discard low-value article sections such as `External links`, `References`, `Footnotes`, and other citation or bibliography sections;
- remove reference tags and surrounding whitespace from section text;
- drop blank or extremely short sections;
- split each article into nested sections while preserving page titles and subtitles;
- prepend titles and subtitles to each section so the retrieved text carries enough local context.

The ignored-section list is tailored to Wikipedia articles. It contains headings such as `See also`, `References`, `External links`, `Further reading`, `Bibliography`, `Sources`, `Citations`, `Notes`, `Photo gallery`, `Works cited`, and similar variants. The retrieval lesson is broader than the list itself: ingestion should remove repeated navigation, citation-only, or page-chrome content when those sections are unlikely to help answer user questions.

The notebook uses `mwparserfromhell` to parse raw wiki markup and walk article sections. For each page, it records the lead summary as a section with the page title as its only parent title. For every level-two section, it recursively extracts nested subsections. Each extracted unit is represented as a pair:

```python
([page_title, optional_heading, optional_subheading], section_text)
```

For nested sections, the heading path is retained rather than flattened away. That makes each later chunk more self-contained: the text is not just an isolated paragraph, but text attached to the page title and section hierarchy that give the model context during retrieval and answer generation.

Compact form of the section-walking pattern:

```python
def all_subsections_from_title(title: str, site_name: str = WIKI_SITE):
    site = mwclient.Site(site_name)
    page = site.pages[title]
    parsed_text = mwparserfromhell.parse(page.text())
    headings = [str(h) for h in parsed_text.filter_headings()]

    if headings:
        summary_text = str(parsed_text).split(headings[0])[0]
    else:
        summary_text = str(parsed_text)

    results = [([title], summary_text)]
    for subsection in parsed_text.get_sections(levels=[2]):
        results.extend(all_subsections_from_section(subsection, [title], SECTIONS_TO_IGNORE))
    return results
```

The recursive helper checks the current section heading, skips the section when the normalized heading is in the ignored list, and otherwise returns the current section text plus all nested child sections. When a section contains child headings, the helper keeps the text before the first child heading as the current section and then descends into the children. This preserves the document hierarchy without storing whole articles as monolithic records.

The cleaning step is deliberately small and easy to audit. It strips inline Wikipedia reference tags with a regular expression, trims whitespace, and filters out text shorter than 16 characters. In the notebook run, this reduced the extracted section set before chunking. The exact counts are specific to the state of Wikipedia at execution time, but the reusable rule is stable: keep enough text to answer questions and remove fragments that add embedding noise.

Compact form of the cleaning pattern:

```python
def clean_section(section: tuple[list[str], str]) -> tuple[list[str], str]:
    titles, text = section
    text = re.sub(r"<ref.*?</ref>", "", text)
    return (titles, text.strip())

def keep_section(section: tuple[list[str], str]) -> bool:
    titles, text = section
    return len(text) >= 16

wikipedia_sections = [clean_section(section) for section in wikipedia_sections]
wikipedia_sections = [section for section in wikipedia_sections if keep_section(section)]
```

For a RAG corpus, the important ingestion choices are the same even when the source is not Wikipedia. Keep provenance-bearing titles, retain semantically meaningful section boundaries, remove repeated boilerplate, and make every retained unit understandable when retrieved alone.

# Token-budget chunking, embedding, and storage

After section extraction and cleaning, the notebook recursively splits long sections into strings that fit a token budget. It notes that there is no perfect recipe for splitting text into sections. The chunk size changes retrieval behavior, cost, and answer quality, so chunking is an engineering tradeoff rather than a fixed rule.

The source highlights these tradeoffs:

- longer sections can help questions that require more context;
- longer sections can hurt retrieval because unrelated topics may be mixed into one embedding;
- shorter sections reduce cost because cost is proportional to token count;
- shorter sections let the retriever return more distinct sections, which can improve recall;
- overlapping or boundary-aware chunks can prevent answers from being split away from needed context.

The notebook chooses a simple token budget of 1,600 tokens per string for this Wikipedia dataset. It uses `tiktoken` and a selected GPT model name only to choose the tokenizer. If a section is within the budget, it is kept as one string. If it is too long, the algorithm recursively splits it in half, preferring delimiters that usually preserve semantic boundaries: double newlines, then single newlines, then sentence-like `. ` boundaries. If no useful split is found after the recursion limit, the string is truncated to the maximum token count.

The prepared string joins the title path and section text with blank lines:

```python
string = "\n\n".join(titles + [text])
```

That is a small but important retrieval detail. If a chunk is retrieved by similarity search, the model sees the page title and section headings directly above the body text. This helps the answer step interpret pronouns, dates, entities, and partial paragraphs that would otherwise be ambiguous.

Compact form of the token counting and recursive split:

```python
GPT_MODEL = "gpt-4o-mini"

def num_tokens(text: str, model: str = GPT_MODEL) -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def split_strings_from_subsection(
    subsection: tuple[list[str], str],
    max_tokens: int = 1000,
    model: str = GPT_MODEL,
    max_recursion: int = 5,
) -> list[str]:
    titles, text = subsection
    string = "\n\n".join(titles + [text])

    if num_tokens(string, model=model) <= max_tokens:
        return [string]
    if max_recursion == 0:
        return [truncated_string(string, model=model, max_tokens=max_tokens)]

    for delimiter in ["\n\n", "\n", ". "]:
        left, right = halved_by_delimiter(text, delimiter=delimiter)
        if left and right:
            chunks = []
            for half in [left, right]:
                chunks.extend(
                    split_strings_from_subsection(
                        (titles, half),
                        max_tokens=max_tokens,
                        model=model,
                        max_recursion=max_recursion - 1,
                    )
                )
            return chunks

    return [truncated_string(string, model=model, max_tokens=max_tokens)]
```

The supporting `halved_by_delimiter` function tries to balance the token count on both sides of a split rather than splitting by character count. It splits the input text on a delimiter, estimates the total token count, then walks candidate split points until moving farther would make the left side less balanced. This keeps both recursive branches close to the same token size while still respecting paragraph or line boundaries when available.

The supporting truncation function encodes the text, keeps the first `max_tokens` tokens, and decodes them back to text. In a production RAG system, truncation should be treated as a last-resort fallback because it can cut off useful evidence. The notebook uses it only when recursive splitting cannot find a better boundary within the configured recursion depth.

For the example run, the notebook sets:

```python
MAX_TOKENS = 1600
wikipedia_strings = []
for section in wikipedia_sections:
    wikipedia_strings.extend(split_strings_from_subsection(section, max_tokens=MAX_TOKENS))
```

Once the corpus is represented as bounded strings, the notebook embeds each string using `text-embedding-3-small`. It batches requests in groups of 1,000 inputs, with a comment noting that the API supports up to 2,048 embedding inputs per request. For each response, the notebook checks that the returned embedding index matches the input position before appending the embedding vector. That index check protects against accidental input-output ordering bugs during ingestion.

Compact form of the embedding batch:

```python
EMBEDDING_MODEL = "text-embedding-3-small"
BATCH_SIZE = 1000

embeddings = []
for batch_start in range(0, len(wikipedia_strings), BATCH_SIZE):
    batch = wikipedia_strings[batch_start : batch_start + BATCH_SIZE]
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=batch)
    for i, item in enumerate(response.data):
        assert i == item.index
    embeddings.extend(item.embedding for item in response.data)

df = pd.DataFrame({"text": wikipedia_strings, "embedding": embeddings})
```

For larger embedding jobs, the notebook points to the Cookbook's parallel request processor as a way to parallelize requests while respecting rate limits. The operational lesson is that ingestion throughput must be controlled: embedding every chunk is embarrassingly parallel, but a production pipeline still needs batching, retry behavior, rate-limit handling, and checks that preserve the mapping between text and vector.

The final storage step writes the text and embedding columns to `data/winter_olympics_2022.csv`:

```python
SAVE_PATH = "data/winter_olympics_2022.csv"
df.to_csv(SAVE_PATH, index=False)
```

The CSV format is sufficient for the notebook's few thousand strings and for a companion demonstration that reads the file back into memory. The source explicitly recommends using a vector database for larger datasets because a vector database can provide more performant similarity search and production storage features. In a full RAG system, the stored record would typically include at least the chunk text, embedding vector, source title, section path, source URL or document identifier, token count, and any access-control metadata needed for retrieval-time filtering.

The notebook's end-to-end pattern can be summarized as an ingestion contract:

1. discover source documents and assign stable titles;
2. extract semantically meaningful sections;
3. remove low-value source artifacts;
4. keep section title paths with the text;
5. split text against a token budget using semantic boundaries where possible;
6. embed every retrievable string with a consistent model;
7. preserve text-vector ordering during batching;
8. store each text chunk and vector with enough metadata to support search, grounding, citation, and later corpus refreshes.

For RAG quality work, this source is most useful as a concrete example of how retrieval quality begins before search ranking. The embedding model can only retrieve the chunks it receives. If ingestion leaves noisy references, breaks semantic context, drops titles, or creates chunks that exceed the downstream prompt budget, the answer step inherits those errors.
