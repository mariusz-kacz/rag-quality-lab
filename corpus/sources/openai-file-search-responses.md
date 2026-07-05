# Source snapshot

Source metadata:
- source_slug: openai-file-search-responses
- category: RAG and context handling
- upstream_url: https://github.com/openai/openai-cookbook/blob/8730772/examples/File_Search_Responses.ipynb
- source_notebook: https://github.com/openai/openai-cookbook/blob/8730772/examples/File_Search_Responses.ipynb
- license: MIT
- pinned_version: openai-cookbook@8730772
- snapshot_type: normalized documentation digest from notebook markdown and compact code cells
- normalization: extracted the reusable managed file-search and vector-store retrieval workflow from notebook markdown and code; removed package-install scaffolding, local PDF inventory outputs, progress bars, generated question dumps, raw answer text, and notebook execution metadata; retained vector-store creation, PDF upload, standalone vector search, Responses API file_search use, retrieval annotations, search-result inclusion, and evaluation metrics methodology

---
# Managed file-search workflow

The notebook demonstrates `file_search`, a hosted retrieval tool available through the OpenAI Responses API. It frames the tool as a managed alternative to building every RAG ingestion and retrieval step manually. A traditional PDF RAG workflow requires parsing PDFs, defining chunking strategy, uploading chunks to storage, embedding those chunks, storing embeddings in a vector database, querying that database, and inserting retrieved text into a model request. The hosted workflow moves file parsing, chunking, embedding, vector storage, retrieval, and context delivery into OpenAI-managed vector stores and the `file_search` tool.

The example corpus consists of PDFs extracted from OpenAI blog pages. The notebook uploads those PDFs to an OpenAI vector store, then asks questions that require retrieved content from that store. It notes that file search was previously available through the Assistants API and is now available through the Responses API, which can be used in stateful or stateless workflows and supports newer features such as metadata filtering.

The notebook begins by using a local directory of PDF files:

```python
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import concurrent
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
dir_pdfs = "openai_blog_pdfs"
pdf_files = [os.path.join(dir_pdfs, f) for f in os.listdir(dir_pdfs)]
```

The local directory and file list are setup details rather than part of the managed retrieval contract. The reusable part is that source files are uploaded to OpenAI, attached to a vector store, and then searched by the Responses API.

The notebook creates a vector store with `client.vector_stores.create`. A vector store is the managed retrieval container: OpenAI reads uploaded PDFs, separates their content into chunks of text, embeds those chunks, and stores both text and embeddings so future queries can retrieve relevant content.

Compact form of vector store creation:

```python
def create_vector_store(store_name: str) -> dict:
    vector_store = client.vector_stores.create(name=store_name)
    return {
        "id": vector_store.id,
        "name": vector_store.name,
        "created_at": vector_store.created_at,
        "file_count": vector_store.file_counts.completed,
    }

vector_store_details = create_vector_store("openai_blog_store")
```

The upload workflow has two steps for each PDF. First, create a file object with `client.files.create`. Second, attach that file to the vector store with `client.vector_stores.files.create`. The notebook uses `purpose="assistants"` when creating files, matching the API pattern in the pinned source.

Compact form of a single-file upload:

```python
def upload_single_pdf(file_path: str, vector_store_id: str) -> dict:
    file_name = os.path.basename(file_path)
    try:
        file_response = client.files.create(
            file=open(file_path, "rb"),
            purpose="assistants",
        )
        client.vector_stores.files.create(
            vector_store_id=vector_store_id,
            file_id=file_response.id,
        )
        return {"file": file_name, "status": "success"}
    except Exception as exc:
        return {"file": file_name, "status": "failed", "error": str(exc)}
```

The notebook uploads multiple PDFs in parallel with a `ThreadPoolExecutor`, tracking total files, successful uploads, failed uploads, and errors. Parallel upload is useful for setup throughput, but it also means a production ingestion script should record per-file status and handle failures without silently losing documents.

Compact form of the multi-file upload loop:

```python
def upload_pdf_files_to_vector_store(vector_store_id: str) -> dict:
    pdf_files = [os.path.join(dir_pdfs, f) for f in os.listdir(dir_pdfs)]
    stats = {
        "total_files": len(pdf_files),
        "successful_uploads": 0,
        "failed_uploads": 0,
        "errors": [],
    }

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(upload_single_pdf, file_path, vector_store_id): file_path
            for file_path in pdf_files
        }
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result["status"] == "success":
                stats["successful_uploads"] += 1
            else:
                stats["failed_uploads"] += 1
                stats["errors"].append(result)

    return stats
```

For RAG architecture, this workflow changes where responsibilities live. The application still chooses documents, uploads them, tracks vector store IDs, decides which store to search, and evaluates retrieval quality. OpenAI manages document parsing, chunking, embeddings, storage, and retrieval execution. The simplified API reduces application code, but the application still needs provenance tracking, access control strategy, ingestion audit logs, and evaluation data.

The notebook then shows standalone vector store search before integrating retrieval into a model call. Standalone search is useful when an application wants to inspect retrieval behavior directly, debug ranking, or evaluate the vector store without asking a model to synthesize an answer.

Compact form of standalone vector search:

```python
query = "What's Deep Research?"
search_results = client.vector_stores.search(
    vector_store_id=vector_store_details["id"],
    query=query,
)

for result in search_results.data:
    text = result.content[0].text
    print(len(text), result.filename, result.score)
```

The source describes the returned chunks as different sizes and different underlying texts, each with a relevance score calculated by a ranker using hybrid search. This is a useful distinction from hand-built embedding-only retrieval. The managed search result is not simply an application-side cosine scan over a local vector table. The service returns scored file chunks selected by the hosted retrieval system.

Relevant upstream concepts:

- OpenAI vector store search API: https://platform.openai.com/docs/api-reference/vector-stores/search
- OpenAI Responses API: https://platform.openai.com/docs/api-reference/responses
- OpenAI file search tool guide: https://platform.openai.com/docs/guides/tools-file-search

# Vector-store retrieval and context delivery

The core Responses API pattern is to provide a user query, a model, and a `file_search` tool configured with one or more vector store IDs. Instead of manually querying the vector store and passing the retrieved text into a separate chat or response request, the notebook lets the model call the hosted retrieval tool as part of the same Responses API request.

Compact form of the integrated call:

```python
query = "What's Deep Research?"
response = client.responses.create(
    input=query,
    model="gpt-4o-mini",
    tools=[
        {
            "type": "file_search",
            "vector_store_ids": [vector_store_details["id"]],
        }
    ],
)
```

The response contains both the file-search call and the generated answer. In the notebook's output structure, the generated text and annotations are read from the response output item after the tool call. The code treats item `0` as the file-search call and item `1` as the message that contains answer content.

Compact form of extracting files used and answer text:

```python
annotations = response.output[1].content[0].annotations
retrieved_files = {result.filename for result in annotations}

print(f"Files used: {retrieved_files}")
print(response.output[1].content[0].text)
```

Annotations connect the generated answer back to retrieved file evidence. In the notebook example, the answer to a question about Deep Research uses content from a specific PDF that contains the most relevant chunks. For RAG systems, annotations are important because they expose which files contributed to an answer, support citation or provenance display, and provide raw material for retrieval evaluation.

The source notes that deeper analysis of retrieved chunks is possible by adding an `include` option to the Responses API request:

```python
include = ["output[*].file_search_call.search_results"]
```

Including search results lets the application inspect the text snippets and scores returned by the search engine, not just the answer and file annotations. This is useful for debugging ranking, identifying irrelevant chunks, checking whether answer failures are caused by retrieval or generation, and saving trace data for offline evaluation.

The notebook also demonstrates evaluation of file-search retrieval. It first generates an evaluation dataset from local PDFs by extracting PDF text and asking a model to create a question that can only be answered from that document. This creates a mapping of `filename` to `question`. The source is explicit that this generated dataset is imperfect and recommends human-verified evaluation data for real use cases. Generated questions can be too generic, such as asking what a main stakeholder said, making it hard to determine which document should be retrieved.

Compact form of question generation:

```python
import PyPDF2

def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text

def generate_questions(pdf_path: str) -> str:
    text = extract_text_from_pdf(pdf_path)
    prompt = (
        "Can you generate a question that can only be answered from this document?:\n"
        f"{text}\n\n"
    )
    response = client.responses.create(input=prompt, model="gpt-4o")
    return response.output[0].content[0].text
```

The evaluation step converts the generated mapping into rows containing a query and expected document ID. For each query, it calls Responses with `file_search`, forces tool use with `tool_choice="required"`, limits retrieval with `max_num_results`, extracts annotations, and checks whether the expected filename appears in the top `k` retrieved files.

Compact form of the retrieval evaluation call:

```python
k = 5

response = client.responses.create(
    input=query,
    model="gpt-4o-mini",
    tools=[
        {
            "type": "file_search",
            "vector_store_ids": [vector_store_details["id"]],
            "max_num_results": k,
        }
    ],
    tool_choice="required",
)
```

The notebook handles response annotations defensively because the response object can expose annotations in slightly different places:

```python
annotations = None
if hasattr(response.output[1], "content") and response.output[1].content:
    annotations = response.output[1].content[0].annotations
elif hasattr(response.output[1], "annotations"):
    annotations = response.output[1].annotations
```

From the annotations, it extracts retrieved filenames, checks the expected filename, and calculates retrieval metrics:

- Recall at `k`: whether the expected file appears in the top `k` retrieved files.
- Reciprocal rank: `1 / rank` when the expected file appears, otherwise `0`.
- Average precision: precision at each position where the expected file appears, averaged across relevant hits.
- MRR: mean reciprocal rank across all queries.
- MAP: mean average precision across all queries.

Compact form of the per-query metric logic:

```python
retrieved_files = [result.filename for result in annotations[:k]]
if expected_filename in retrieved_files:
    rank = retrieved_files.index(expected_filename) + 1
    reciprocal_rank = 1 / rank
    correct = True
else:
    reciprocal_rank = 0
    correct = False

precisions = []
num_relevant = 0
for i, filename in enumerate(retrieved_files):
    if filename == expected_filename:
        num_relevant += 1
        precisions.append(num_relevant / (i + 1))

average_precision = sum(precisions) / len(precisions) if precisions else 0
```

The notebook logs cases where the expected file is missing from retrieved files or where a different file ranks first. This diagnostic output is more useful than aggregate metrics alone. When retrieval fails, the evaluator can inspect whether the query was too generic, whether multiple documents contain overlapping content, whether the expected label is wrong, or whether the retrieval configuration needs adjustment.

At the end, the notebook computes aggregate values for recall, precision, MRR, and MAP over the generated query set. It notes that an imperfect generated evaluation dataset can produce apparent retrieval failures when the expected file is ambiguous or when another document is a reasonable match.

The practical lessons for RAG quality work are:

- Managed file search can simplify RAG by combining file storage, parsing, chunking, embeddings, vector storage, retrieval, and answer-time context delivery.
- Applications still need to track vector store IDs, uploaded files, expected provenance, and retrieval traces.
- Standalone vector store search is useful for debugging retrieval before involving a model answer.
- Responses API annotations expose which files were used and can support citations, audits, and evaluation.
- Including file-search search results gives deeper visibility into retrieved chunks and ranking.
- `max_num_results` and `tool_choice="required"` are useful evaluation controls when measuring retrieval behavior.
- Human-verified evaluation datasets are preferable because generated questions can be generic or ambiguous.
- Retrieval metrics should be paired with diagnostic logs that show expected files, first retrieved files, and full top-`k` filenames.

For this project's corpus, the source is most useful as an example of managed retrieval in a RAG pipeline. It shows how vector stores and `file_search` can replace much of the manual embedding-search plumbing while still leaving open the core quality tasks: selecting documents, tracing context delivery, evaluating top-`k` retrieval, and checking whether the final answer is grounded in the files actually retrieved.
