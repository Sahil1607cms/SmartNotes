# SmartNotes Component Architecture

This document breaks down the major components of the SmartNotes project, explaining their responsibilities, implementations, interactions, and non-obvious logic.

---

## 1. Frontend Components (React 19 + Vite)

### App Routing & Authentication
- **Responsibility**: Bootstraps the application, manages client-side routing, and wraps the app in Firebase Authentication state.
- **Implementation**: `frontend/src/main.jsx`, `frontend/src/App.jsx`, `frontend/src/context/AuthContext.jsx`
- **Logic**: Uses React Router to determine what page to render. Protects internal routes (like `/yt`) using a `ProtectedRoute` component that checks for an active Firebase `user` in `AuthContext`.
- **Connections**: Talks to Firebase via `firebase.js` to get OAuth status.

### Summarizer Pages (Form & State Controllers)
- **Responsibility**: Provides the user interface for submitting media, handles file uploads, and maintains local component state for the summarization process.
- **Implementation**: `frontend/src/pages/YoutubeSummarizer.jsx`, `AudioVideoSummarizer.jsx`, `PdfTextSummarizer.jsx`
- **Logic / Non-obvious behavior**: These components heavily rely on `localStorage` for state mirroring. If a user navigates away and comes back, the page restores its state (e.g., the current summary, terminal logs) from local storage to provide a persistent experience without reloading.
- **Connections**: Send `POST` requests to backend endpoints (`/summarize-yt`, `/summarize-media`, `/summarize-pdf`). Render the `SummaryPage.jsx` when data is ready.

### Results Viewer (`SummaryPage.jsx`)
- **Responsibility**: A tabbed container displaying the output of the summarization process (Summary, Ask AI, Flashcards).
- **Implementation**: `frontend/src/pages/SummaryPage.jsx`, `frontend/src/components/ChatAssistant.jsx`, `frontend/src/components/Flashcards.jsx`
- **Logic**: Uses client-side markdown parsing (`react-markdown`) and PDF export libraries (`jspdf`) to let users read and download summaries.
- **Connections**: `ChatAssistant` sends user queries to `/chat`. `Flashcards` fetches bullet points from `/summarize-flashcard`.

### Local Storage & Event Bus Sync
- **Responsibility**: Caches notes locally for 0ms load times and synchronizes state across multiple browser tabs.
- **Implementation**: `frontend/src/utils/historyStorage.js`
- **Logic / Non-obvious behavior**: Uses a custom window event (`smartnotes_history_updated`). When a note is deleted or added, it fires this event, causing all open tabs to re-render and reflect the database changes instantly without repeated polling.

---

## 2. Backend Gateway & API Layer (FastAPI)

### Application Lifespan & Initialization
- **Responsibility**: Starts the server, sets up CORS, and handles startup/shutdown hooks.
- **Implementation**: `backend/main.py`
- **Logic / Non-obvious behavior**: Contains an `@asynccontextmanager` `lifespan` function. Before accepting HTTP traffic, it explicitly pings MongoDB to verify connection, and it pre-loads the 80MB HuggingFace embedding model (`all-MiniLM-L6-v2`) into RAM. This eliminates a massive latency spike that would otherwise hit the first user query.

### Summarizer Routers
- **Responsibility**: Exposes endpoints for uploading/submitting links and files to be summarized.
- **Implementation**: `backend/app/api/summarizer.py`
- **Logic**: Orchestrates the entire ingest flow. For files, it physically saves them to `backend/uploads/{user_id}/`. It chains together extraction, chunk summarization, and database saves. 
- **Non-obvious behavior**: Uses FastAPI's `BackgroundTasks` to schedule vector embedding generation *after* returning the HTTP summary response, ensuring the user isn't kept waiting for embeddings to calculate.

### Chat & Flashcard Routers
- **Responsibility**: Exposes `/chat` for Q&A and `/summarize-flashcard` for study tools.
- **Implementation**: `backend/app/api/chat.py`, `backend/app/api/flashcards.py`
- **Logic**: The flashcard router utilizes a "Zero-Cost Local Parser." Before calling the LLM, it attempts to parse markdown headers and bullet points directly via regex. If it finds enough, it returns them without making any expensive Groq API calls.

---

## 3. Backend Core Services

### Map-Reduce Summarizer Engine
- **Responsibility**: Breaks long text into processable chunks and aggregates LLM summaries to bypass token limits.
- **Implementation**: `backend/app/services/summarizer.py`
- **Logic / Non-obvious behavior**:
  - Uses `RecursiveCharacterTextSplitter` to cut text into 5000-character chunks.
  - Implements an `asyncio.Semaphore` to cap concurrent Groq API calls and prevent Rate Limit / TPM (Tokens Per Minute) bans.
  - Includes an exponential backoff retry loop specifically catching `HTTP 413` and `429` errors.
  - If only 1 chunk is generated, it skips the final synthesis LLM prompt entirely to save money and latency.

### Dual-Retrieval Vector Engine
- **Responsibility**: Computes dense vectors and performs RAG context retrieval.
- **Implementation**: `backend/app/services/vector_search.py`
- **Logic / Non-obvious behavior**: Implements a cascading fallback retrieval strategy:
  1. Tries to use MongoDB Atlas native `$vectorSearch` pipeline for high-performance retrieval.
  2. If the Atlas vector index is unbuilt or fails, it falls back to a custom, in-memory NumPy cosine similarity matrix computation (calculating dot-products between float arrays).
  3. Formats the last 4 chat history messages into a conversational context window for the RAG LLM prompt.

### Media & Document Extractors
- **Responsibility**: Extracts raw text strings from various media types.
- **Implementation**: `backend/app/services/media_processor.py`, `backend/app/services/youtube.py`
- **Logic / Non-obvious behavior**:
  - **YouTube**: Fetches via `youtube-transcript-api` and runs a regex cleaner to strip out conversational filler words (e.g., "um", "like", "हम्म") in both English and Hindi to save LLM tokens.
  - **Audio/Video**: Before passing audio to Faster-Whisper, it calls `ffmpeg -filter:a atempo=2.0`. Speeding the audio up by 2x drastically cuts down the GPU/CPU inference time of Whisper without significantly degrading transcription quality.

### Database Layer
- **Responsibility**: PyMongo driver connections and basic CRUD.
- **Implementation**: `backend/app/core/database.py`
- **Connections**: Connects directly to MongoDB Atlas. Manipulates the `notesDB.notes` collection. Automatically converts `_id` ObjectIds to string formats for JSON serializability to the frontend.

---

## 4. Component Dependency Map

```text
React User Interface
 │
 ├──> historyStorage.js (Local Cache & Event Bus)
 │
 └──> API Requests (fetch)
        │
        ▼
 FastAPI Routers (app/api/)
  ├──> summarizer.py (POST /summarize-yt, /summarize-media, /summarize-pdf)
  ├──> chat.py (POST /chat)
  ├──> flashcards.py (POST /summarize-flashcard)
  └──> notes.py (GET /notes)
        │
        ▼
 Backend Services (app/services/)
  ├──> youtube.py (Extracts YT Transcripts, strips fillers)
  ├──> media_processor.py (FFmpeg Audio 2.0x -> Faster-Whisper STT, PyMuPDF)
  ├──> summarizer.py (Chunking, Semaphore concurrency, Map-Reduce Groq)
  └──> vector_search.py (MiniLM-L6 Embeddings, MongoDB $vectorSearch / NumPy Cosine)
        │
        ▼
 Backend Core (app/core/)
  ├──> llm.py (LangChain Groq Client)
  └──> database.py (PyMongo CRUD)
        │
        ▼
 External Systems
  ├──> MongoDB Atlas (Storage & Vector Index)
  ├──> Groq Cloud API (LLM Inference)
  └──> Local File System (backend/uploads/)
```
