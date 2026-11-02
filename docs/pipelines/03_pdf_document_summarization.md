# Pipeline 03: PDF Document Summarization

## A. One-paragraph summary
The PDF Document Summarization pipeline allows users to upload PDF documents (e.g. research papers, technical reports, lecture notes) and receive concise executive summaries. The backend validates the document, saves it to a user-specific directory, and extracts raw text across all pages using PyMuPDF (`fitz`). The extracted text is processed through the shared Groq Map-Reduce summarization engine, persisted into MongoDB Atlas with full document content, and asynchronously indexed into 384-dimensional vector embeddings in the background for grounded RAG Q&A.

---

## B. Pipeline at a glance

```text
[User] Selects a .pdf File
   │
   ▼
[Frontend: PdfTextSummarizer.jsx]
   └── Packages file into `FormData` and sends POST /summarize-pdf
   │
   ▼
[API Layer: backend/app/api/summarizer.py -> summarize_pdf]
   ├── Validates .pdf extension
   ├── Saves file to `uploads/{user_id}/{task_id}_{filename}`
   │
   ▼
[Service Layer: media_processor.py -> extract_pdf_text]
   └── Uses PyMuPDF (`fitz`) to extract text page-by-page
   │
   ▼
[Service Layer: summarizer.py -> summarize_long_content]
   └── (Shared Map-Reduce Pipeline: Chunking -> Groq LLM Map-Reduce)
   │
   ▼
[Database: database.py -> create_note]
   └── Inserts NoteModel (type: "PDF", pdf_content: [text]) into MongoDB
   │
   ▼
[Background Task: vector_search.py -> async_generate_and_save_embeddings]
   └── Computes and updates 384-d MiniLM-L6-v2 vector embeddings
   │
   ▼
[Frontend: PdfTextSummarizer.jsx & SummaryPage.jsx]
   ├── Displays executive summary in Markdown
   ├── Saves note to local history cache (historyStorage.js)
   └── Mirrors state to `localStorage["summary_pdf_state"]`
```

---

## C. Step-by-step trace

### Step 1: File Selection and Form Submission
* **File & Function**: [`frontend/src/pages/PdfTextSummarizer.jsx`](file:///home/hardik/SmartNotes/frontend/src/pages/PdfTextSummarizer.jsx#L56-L102) (`handleSummarize`)
* **What happens**: The user selects a PDF file via the file picker input. When **Summarize PDF** is clicked, it checks Firebase authentication (`userID`), sets `loading = true`, and appends the file to `FormData`.
* **Input**: `file` (File object, MIME type `application/pdf`), `userID` string.
* **API Call**: `POST http://localhost:8000/summarize-pdf`
  - **Content-Type**: `multipart/form-data`
  - **Form Fields**: `file` (Binary), `user_id` (string), `type="PDF"` (string).
* **Output**: Awaiting backend JSON response.

### Step 2: Route Handling, Extension Check & Staging
* **File & Function**: [`backend/app/api/summarizer.py`](file:///home/hardik/SmartNotes/backend/app/api/summarizer.py#L153-L178) (`summarize_pdf`)
* **What happens**:
  1. Validates that `Path(file.filename).suffix.lower() == ".pdf"`.
  2. Generates a unique `task_id` (`uuid4()`).
  3. Ensures user directory exists: `backend/uploads/{user_id}/`.
  4. Streams binary data from `file.file` into `backend/uploads/{user_id}/{task_id}_{filename}` with `shutil.copyfileobj()`.
* **Input**: FastAPI `UploadFile`, `user_id` string, `type` string.
* **Output**: Local filesystem path string.
* **Validation**: Returns HTTP 400 if `filename` is empty or does not have a `.pdf` extension.

### Step 3: Page-by-Page PDF Text Extraction
* **File & Function**: [`backend/app/services/media_processor.py`](file:///home/hardik/SmartNotes/backend/app/services/media_processor.py#L76-L90) (`extract_pdf_text`)
* **What happens**:
  1. Opens the file using `fitz.open(file_path)`.
  2. Iterates across all pages: `for page in doc: text = page.get_text("text")`.
  3. Collects non-empty text strings and closes the document handle.
  4. Joins pages using double newlines: `"\n\n".join(text_chunks)`.
* **Input**: `file_path` string.
* **Output**: `full_text` string containing all extracted document content.
* **Technology**: PyMuPDF (`fitz`).
* **Validation**: Raises `ValueError("The uploaded PDF file contains no extractable text.")` if the PDF is blank or contains only scanned raster images without OCR.

### Step 4: Map-Reduce Summarization Pipeline
* **File & Function**: [`backend/app/services/summarizer.py`](file:///home/hardik/SmartNotes/backend/app/services/summarizer.py#L127-L167) (`summarize_long_content`)
* **What happens**: Passes the extracted PDF text string to the shared Map-Reduce engine (see [Pipeline 01](file:///home/hardik/SmartNotes/docs/pipelines/01_youtube_summarization.md#step-5-text-cleaning-chunking-and-map-reduce-summarization) for details on LangChain `RecursiveCharacterTextSplitter`, `asyncio.Semaphore`, and Groq `safe_summarize` LLM retries).
* **Output**: Final unified Markdown summary string.

### Step 5: Database Persistence & Background Vector Indexing
* **File & Function**: [`backend/app/api/summarizer.py`](file:///home/hardik/SmartNotes/backend/app/api/summarizer.py#L185-L212)
* **What happens**:
  1. Instantiates `NoteModel(user_id=user_id, title=filename, type="PDF", summary=summary, pdf_content=[extracted_text], source=local_file_path, task_id=task_id)`.
  2. Inserts document into MongoDB Atlas via `create_note()` ([`backend/app/core/database.py`](file:///home/hardik/SmartNotes/backend/app/core/database.py#L25-L35)).
  3. Enqueues `async_generate_and_save_embeddings` into FastAPI `BackgroundTasks` with the note ID and raw `extracted_text`.
  4. Returns HTTP 200 with status, summary, saved note, and processing logs.

### Step 6: Frontend State Hydration & Caching
* **File & Function**: [`frontend/src/pages/PdfTextSummarizer.jsx`](file:///home/hardik/SmartNotes/frontend/src/pages/PdfTextSummarizer.jsx#L82-L95) & [`frontend/src/utils/historyStorage.js`](file:///home/hardik/SmartNotes/frontend/src/utils/historyStorage.js#L50-L72)
* **What happens**: Updates React state variables (`summary`, `noteId`, `logs`), calls `addNoteToHistory(data.note)`, mirrors `{ summary, noteId, logs }` to `localStorage["summary_pdf_state"]`, and renders the summary in [`SummaryPage.jsx`](file:///home/hardik/SmartNotes/frontend/src/pages/SummaryPage.jsx).

---

## D. What runs in the background or after the response

* **Background Task**: [`backend/app/services/vector_search.py`](file:///home/hardik/SmartNotes/backend/app/services/vector_search.py#L61-L82) (`async_generate_and_save_embeddings`)
* **Process**: Computes 384-dimensional dense vectors using HuggingFace `all-MiniLM-L6-v2` over 600-character chunks of the extracted PDF text and saves the vector list to the MongoDB document in the background.

---

## E. What can fail

1. **Non-PDF File Uploaded**:
   - *Where handled*: [`backend/app/api/summarizer.py`](file:///home/hardik/SmartNotes/backend/app/api/summarizer.py#L166-L168).
   - *User sees*: Error box: *"Only PDF files are supported."*.
2. **Scanned Image PDF / No Extractable Text**:
   - *Where handled*: [`backend/app/services/media_processor.py`](file:///home/hardik/SmartNotes/backend/app/services/media_processor.py#L87-L88).
   - *User sees*: Error banner: *"The uploaded PDF file contains no extractable text."*.
3. **Groq API Rate Limits / Payloads**:
   - *Where handled*: [`backend/app/services/summarizer.py`](file:///home/hardik/SmartNotes/backend/app/services/summarizer.py#L78-L95).
   - *User sees*: Log output: *"❌ Error processing PDF file."*.

---

## F. Reading order for studying

1. [`frontend/src/pages/PdfTextSummarizer.jsx`](file:///home/hardik/SmartNotes/frontend/src/pages/PdfTextSummarizer.jsx) — PDF file upload interface and state management.
2. [`backend/app/api/summarizer.py`](file:///home/hardik/SmartNotes/backend/app/api/summarizer.py#L153-L221) — The `/summarize-pdf` route handler.
3. [`backend/app/services/media_processor.py`](file:///home/hardik/SmartNotes/backend/app/services/media_processor.py#L76-L90) — `extract_pdf_text` implementation using PyMuPDF (`fitz`).
4. [`backend/app/services/summarizer.py`](file:///home/hardik/SmartNotes/backend/app/services/summarizer.py) — The shared Map-Reduce summarization engine.
5. [`backend/app/services/vector_search.py`](file:///home/hardik/SmartNotes/backend/app/services/vector_search.py) — Background vector generation.

---

## G. Key concepts to know before reading the code

* **PyMuPDF (`fitz`)**: A high-performance Python binding for the MuPDF C library used for reading, parsing, and extracting text from PDF documents.
* **Dense Vector Indexing**: Transforming unstructured text paragraphs into 384-dimensional floating-point vectors representing semantic meaning.
* **Pydantic Model Serialization**: Automatic mapping of Python class objects to JSON-compatible dictionaries and database documents with schema validation.
