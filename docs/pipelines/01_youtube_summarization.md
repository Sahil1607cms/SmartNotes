# Pipeline 01: YouTube Video Summarization

## A. One-paragraph summary
The YouTube Video Summarization pipeline ingests a YouTube URL, retrieves the video's subtitle/transcript segments in English or Hindi, and scrubs conversational filler words. The cleaned text is split into 5,000-character chunks and summarized through an asynchronous Map-Reduce pipeline using Groq LLMs. The resulting summary and metadata are saved to MongoDB Atlas, returned to the user with processing logs, and cached locally in the browser, while a background worker calculates and stores 384-dimensional dense vector embeddings for subsequent RAG Q&A.

---

## B. Pipeline at a glance`

```text
[User] Pastes YouTube URL
   │
   ▼
[Frontend: YoutubeSummarizer.jsx / VideoPreview.jsx]
   ├── 1. Fetches oEmbed title (YouTube API) & preview transcript (GET /transcript/)
   └── 2. User clicks "Summarize" -> POST /summarize-yt
   │
   ▼
[API Layer: backend/app/api/summarizer.py -> summarize_youtube]
   │
   ├──► [Service Layer: youtube.py -> get_transcripts & clean_transcript_text]
   │       └── Extracts Video ID -> Fetches Subtitles (en/hi) -> Regex Strips Filler Words
   │
   ├──► [Service Layer: summarizer.py -> summarize_long_content]
   │       └── LangChain Splitter (5000 chars) -> Groq LLM Map-Reduce (Bounded Semaphore)
   │
   ├──► [Database: database.py -> create_note]
   │       └── Inserts NoteModel into MongoDB Atlas `notes` Collection
   │
   ├──► [Background Task: vector_search.py -> async_generate_and_save_embeddings]
   │       └── (Runs asynchronously after HTTP response)
   │
   ▼
[Frontend: YoutubeSummarizer.jsx & SummaryPage.jsx]
   ├── Hydrates React state with summary, note ID, and logs
   ├── Calls historyStorage.js -> addNoteToHistory (localStorage cache & event bus)
   └── Mirrors full state to `localStorage["summary_yt_state"]`
```

---

## C. Step-by-step trace

### Step 1: Input URL and Automatic Preview Hydration
* **File & Function**: [`frontend/src/components/VideoPreview.jsx`](file:///home/hardik/SmartNotes/frontend/src/components/VideoPreview.jsx#L51-L92) (`fetchTranscriptAndTitle`)
* **What happens**: When the user enters a YouTube URL into the input field in [`YoutubeSummarizer.jsx`](file:///home/hardik/SmartNotes/frontend/src/pages/YoutubeSummarizer.jsx#L129-L135), `VideoPreview` detects the URL change:
  1. Parses the 11-character video ID using `getYouTubeId()`.
  2. Embeds the YouTube iframe (`https://www.youtube.com/embed/{videoId}`).
  3. Sends `GET http://localhost:8000/transcript/?url=...` to pre-fetch transcript lines.
  4. Calls the external YouTube oEmbed API (`https://www.youtube.com/oembed?url=...&format=json`) to fetch the video's official title.
* **Input**: `url` string (e.g., `"https://www.youtube.com/watch?v=dQw4w9WgXcQ"`).
* **Output**: `transcript` array `[{ time: "00:00", text: "..." }]` and `title` string stored in component state.
* **Technology**: Browser `fetch`, YouTube oEmbed API.
* **Validation & Error Handling**: Wrapped in `try/catch`. If oEmbed or transcript pre-fetch fails, it defaults title to `"YouTube Video"` and sets placeholder transcript error messages.

### Step 2: Triggering Summarization Request
* **File & Function**: [`frontend/src/pages/YoutubeSummarizer.jsx`](file:///home/hardik/SmartNotes/frontend/src/pages/YoutubeSummarizer.jsx#L62-L110) (`handleSummarize`)
* **What happens**: The user clicks the **Summarize** button. The frontend validates that the user is authenticated with Firebase (`userID`), sets `loading = true`, and initiates an HTTP POST request to the backend.
* **Input**: State variables `userID`, `title`, `url`, `transcript`.
* **API Call**: `POST http://localhost:8000/summarize-yt`
  - **Payload**:
    ```json
    {
      "user_id": "firebase_uid_string",
      "title": "Introduction to Algorithms",
      "type": "youtube",
      "url": "https://www.youtube.com/watch?v=...",
      "transcript": [{ "time": "00:00", "text": "..." }]
    }
    ```
* **Output**: Awaiting backend JSON response.

### Step 3: API Request Validation and Transcript Resolution
* **File & Function**: [`backend/app/api/summarizer.py`](file:///home/hardik/SmartNotes/backend/app/api/summarizer.py#L20-L35) (`summarize_youtube`)
* **What happens**: The FastAPI route receives and parses the request into a Pydantic `SummarizeRequest` schema:
  - If `req.transcript` was supplied by the frontend, it uses those segments.
  - If `req.transcript` is missing or empty, it calls `get_transcripts(req.url)` directly.
* **Input**: Pydantic `SummarizeRequest` object.
* **Output**: `transcripts` (list of dictionaries `[{"time": "00:00", "text": "..."}]`).
* **Validation**: Returns HTTP 400 if neither `url` nor `transcript` is provided.

### Step 4: YouTube Transcript Fetching & Fallback Parsing (if URL provided)
* **File & Function**: [`backend/app/services/youtube.py`](file:///home/hardik/SmartNotes/backend/app/services/youtube.py#L27-L69) (`get_transcripts`)
* **What happens**: 
  1. `extract_video_id()` pulls the 11-character regex match.
  2. Attempts to fetch English (`en`) or Hindi (`hi`) transcripts via `YouTubeTranscriptApi().fetch(video_id, languages=["en", "hi"])`.
  3. **Fallback 1**: If language-specific fetch fails, calls `api.fetch(video_id)` with no language restriction.
  4. **Fallback 2**: If that fails, calls `api.list(video_id)` and finds manually generated or auto-generated transcripts (`find_generated_transcript`).
  5. Formats time offsets into `MM:SS` or `HH:MM:SS` strings via `format_time_compact()`.
* **Technology**: `youtube-transcript-api`.
* **Error Handling**: Raises exceptions on `IpBlocked` or `NoTranscriptFound` which are caught by the API router.

### Step 5: Text Cleaning, Chunking, and Map-Reduce Summarization
* **File & Function**: [`backend/app/services/summarizer.py`](file:///home/hardik/SmartNotes/backend/app/services/summarizer.py#L127-L167) (`summarize_long_content`)
* **What happens**:
  1. Joins all transcript segment texts into a single string.
  2. Runs `clean_transcript_text()` ([`backend/app/services/youtube.py`](file:///home/hardik/SmartNotes/backend/app/services/youtube.py#L71-L78)) to remove English and Hindi conversational filler words (e.g. *uh, um, like, you know, अच्छा, हम्म, मतलब*) via regex.
  3. `chunk_text()` splits text with LangChain's `RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=400)`.
  4. `summarize_chunks()` processes chunks concurrently with `asyncio.gather()` bounded by `asyncio.Semaphore(MAX_CONCURRENT_SUMMARIES)` (default: 1).
  5. Each chunk calls `safe_summarize()` using Groq `openai/gpt-oss-20b` via `ChatGroq`.
  6. **Single-Chunk Bypass**: If only 1 chunk was created, returns the chunk summary immediately without calling the synthesis model.
  7. **Multi-Chunk Synthesis**: If >1 chunk was created, combines them using `combine_prompt` and invokes Groq for the final unified summary.
* **Technology**: LangChain Core (`PromptTemplate`, `StrOutputParser`), `langchain-groq` (`ChatGroq`), `RecursiveCharacterTextSplitter`.
* **Retries & Rate Limits**: `safe_summarize` catches HTTP `413`, `429`, or TPM limit errors and executes exponential backoff delays (`5s * (attempt + 1)` up to 3 retries).

### Step 6: Database Storage
* **File & Function**: [`backend/app/core/database.py`](file:///home/hardik/SmartNotes/backend/app/core/database.py#L25-L35) (`create_note`)
* **What happens**: Instantiates a `NoteModel` ([`backend/app/models/schemas.py`](file:///home/hardik/SmartNotes/backend/app/models/schemas.py#L11-L28)), inserts it into the MongoDB Atlas `notes` collection via PyMongo `insert_one()`, and attaches the generated string `_id` and `id` to the returned dictionary.
* **Input**: `NoteModel` instance (`user_id`, `title`, `type="youtube"`, `summary`, `transcript`, `source=url`, `status="Completed"`).
* **Output**: Saved note dictionary with stringified ObjectId.
* **Database**: MongoDB Atlas `notesDB.notes`.

### Step 7: Background Task Registration and API Response
* **File & Function**: [`backend/app/api/summarizer.py`](file:///home/hardik/SmartNotes/backend/app/api/summarizer.py#L55-L68) (`summarize_youtube`)
* **What happens**: The router registers `async_generate_and_save_embeddings` into FastAPI `BackgroundTasks` with the new `note_id` and full transcript text, and immediately returns the HTTP 200 response to the client.
* **Response Payload**:
  ```json
  {
    "status": "success",
    "summary": "# Summary Markdown Content...",
    "note": { "_id": "66c61f2e8f1b...", "user_id": "...", "title": "...", ... },
    "logs": [
      "📥 Fetching YouTube transcript...",
      "📄 Retrieved 142 transcript segments.",
      "🤖 Generating summary using Groq Compound...",
      "💾 Saving note to database...",
      "🧠 Scheduled local vector embedding computation in background.",
      "🚀 Done! Summary is ready."
    ]
  }
  ```

### Step 8: Frontend State Hydration, Cache Update & Tab Switch
* **File & Function**: [`frontend/src/pages/YoutubeSummarizer.jsx`](file:///home/hardik/SmartNotes/frontend/src/pages/YoutubeSummarizer.jsx#L90-L96) & [`frontend/src/utils/historyStorage.js`](file:///home/hardik/SmartNotes/frontend/src/utils/historyStorage.js#L50-L72) (`addNoteToHistory`)
* **What happens**:
  1. `YoutubeSummarizer.jsx` updates its state variables: `summary`, `noteId`, and `logs`.
  2. Calls `addNoteToHistory(data.note)` which updates `localStorage["smartnotes_history_cache"]` and dispatches `window.dispatchEvent(new Event("smartnotes_history_updated"))`.
  3. An effect hook serializes the complete page state (`{ summary, url, transcript, title, noteId, logs }`) to `localStorage["summary_yt_state"]`.
  4. [`frontend/src/pages/SummaryPage.jsx`](file:///home/hardik/SmartNotes/frontend/src/pages/SummaryPage.jsx) renders the Markdown summary and enables the **Ask AI** and **Flashcards** tabs.

---

## D. What runs in the background or after the response

* **Background Task**: [`backend/app/services/vector_search.py`](file:///home/hardik/SmartNotes/backend/app/services/vector_search.py#L61-L82) (`async_generate_and_save_embeddings`)
* **Execution**: Triggered by FastAPI `BackgroundTasks` after the HTTP response is sent.
* **Process**:
  1. Splits the transcript text into smaller vector-optimized chunks using `RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=120)`.
  2. Computes 384-dimensional dense vector embeddings for every chunk using the in-memory HuggingFace `sentence-transformers/all-MiniLM-L6-v2` model.
  3. Executes `notes_collection.update_one({"_id": ObjectId(note_id)}, {"$set": {"embeddings": embeddings}})`.
* **Completion Time**: Typically finishes in 200–800ms depending on CPU/GPU performance.

---

## E. What can fail

1. **IP Blocked / Rate Limited by YouTube**:
   - *Where handled*: [`backend/app/api/transcript.py`](file:///home/hardik/SmartNotes/backend/app/api/transcript.py#L14-L18) and [`backend/app/services/youtube.py`](file:///home/hardik/SmartNotes/backend/app/services/youtube.py#L38-L50).
   - *User sees*: Error message *"Your IP is blocked by YouTube. Try again later or from a different network."* or *"Failed to summarize YouTube video."* in the UI console and error banner.
2. **Video Has No Transcripts / Disabled Subtitles**:
   - *Where handled*: [`backend/app/services/youtube.py`](file:///home/hardik/SmartNotes/backend/app/services/youtube.py#L48-L50) raises exception.
   - *User sees*: Error box indicating transcript fetch failure.
3. **Groq API Rate Limit (TPM/429) or Payload Size (413)**:
   - *Where handled*: [`backend/app/services/summarizer.py`](file:///home/hardik/SmartNotes/backend/app/services/summarizer.py#L84-L95) logs backoff and sleeps (up to 3 retries). If retries are exhausted, [`backend/app/api/summarizer.py`](file:///home/hardik/SmartNotes/backend/app/api/summarizer.py#L72-L76) catches the error and returns HTTP 413/500.
   - *User sees*: *"❌ Error processing YouTube video."* in `LiveLogConsole`.
4. **User Not Authenticated**:
   - *Where handled*: [`frontend/src/pages/YoutubeSummarizer.jsx`](file:///home/hardik/SmartNotes/frontend/src/pages/YoutubeSummarizer.jsx#L64).
   - *User sees*: Browser alert: *"User not logged in!"*.

---

## F. Reading order for studying

1. [`frontend/src/pages/YoutubeSummarizer.jsx`](file:///home/hardik/SmartNotes/frontend/src/pages/YoutubeSummarizer.jsx) — Examine state variables, local storage persistence, and form submission.
2. [`frontend/src/components/VideoPreview.jsx`](file:///home/hardik/SmartNotes/frontend/src/components/VideoPreview.jsx) — See how oEmbed and pre-transcript fetching are handled on the frontend.
3. [`backend/app/api/summarizer.py`](file:///home/hardik/SmartNotes/backend/app/api/summarizer.py) — Follow the `/summarize-yt` route handler.
4. [`backend/app/services/youtube.py`](file:///home/hardik/SmartNotes/backend/app/services/youtube.py) — Look at regex video ID extraction, transcript fetching fallbacks, and regex filler word removal.
5. [`backend/app/services/summarizer.py`](file:///home/hardik/SmartNotes/backend/app/services/summarizer.py) — Understand the Map-Reduce pipeline, text chunking, and Groq rate-limiting backoff loops.
6. [`backend/app/services/vector_search.py`](file:///home/hardik/SmartNotes/backend/app/services/vector_search.py) — Inspect `async_generate_and_save_embeddings` to see how background vector indexing operates.
7. [`frontend/src/utils/historyStorage.js`](file:///home/hardik/SmartNotes/frontend/src/utils/historyStorage.js) — Check how the resulting note is added to the local history cache and broadcast to other components.

---

## G. Key concepts to know before reading the code

* **Map-Reduce Summarization**: A technique where a long document is broken into chunks, each chunk is summarized independently in parallel (the "Map" step), and all chunk summaries are then combined and synthesized into a final summary (the "Reduce" step).
* **Bounded Concurrency (asyncio.Semaphore)**: A concurrency control primitive that limits the maximum number of simultaneous asynchronous tasks (e.g., capping simultaneous Groq LLM API requests to 1 to avoid exceeding Tokens-Per-Minute rate limits).
* **Zero-Latency State Hydration**: Reading cached state from browser `localStorage` on component mount so the user experiences an instant 0ms interface load before any network requests complete.
* **FastAPI BackgroundTasks**: A built-in FastAPI mechanism that returns an HTTP response to the client immediately while continuing execution of non-blocking background functions (like vector embedding calculation) on the server.
