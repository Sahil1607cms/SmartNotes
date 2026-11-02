# SmartNotes Overview

## 1. What problem the project solves
SmartNotes is a local-first AI knowledge engine designed to combat information overload. It solves the challenge of manually sifting through long video lectures, media recordings, and dense PDF documents by automatically extracting key insights and summaries. It also overcomes Large Language Model (LLM) token limits by chunking text, processing it via a map-reduce pipeline, and enabling Retrieval-Augmented Generation (RAG) to ensure AI answers are grounded in actual document facts rather than hallucinated.

## 2. Main features
* **YouTube Video Summarization**: Pasting a YouTube URL extracts transcripts, cleans filler words, and summarizes the content.
* **Audio/Video Summarization**: Uploaded media is accelerated with FFmpeg and transcribed locally using Faster-Whisper before being summarized.
* **PDF Document Summarization**: Extracts text from long PDFs using PyMuPDF and summarizes it.
* **RAG AI Chat Assistant**: An interactive Q&A assistant that strictly answers based on the context of the processed documents using vector search.
* **Study Flashcard & Prompt Generation**: Uses local regex parsing or an LLM fallback to generate interactive study flashcards and prompt suggestions.
* **History & Real-Time Syncing**: Keeps all past notes cached in `localStorage` for instant loading and synchronizes with MongoDB.

## 3. Complete tech stack

### Languages
* **Python 3.12**: Powers the backend REST API, machine learning inference, and asynchronous processing.
* **JavaScript (React 19)**: Powers the frontend Single Page Application (SPA).

### Frameworks & Libraries
* **FastAPI**: Serves the high-performance backend REST API gateway.
* **React 19**: Framework used for building the dynamic, component-based frontend.
* **Vite 7**: Frontend build tool and development server.
* **Tailwind CSS 4**: Utility-first CSS framework for styling the UI.
* **Framer Motion**: Adds 3D grid animations and interactive popups to the flashcards.
* **LangChain (langchain-groq)**: Orchestrates the text chunking and asynchronous Map-Reduce summarization pipeline.
* **sentence-transformers**: Provides the `all-MiniLM-L6-v2` embedding model for generating 384-dimensional vectors.
* **PyMuPDF (`fitz`)**: Extracts raw text from uploaded PDF documents.
* **youtube-transcript-api**: Fetches English/Hindi subtitles from YouTube video URLs.
* **PyMongo**: Python driver to interact with the MongoDB Atlas database.
* **Faster-Whisper (CTranslate2)**: Executes fast, local speech-to-text inference with GPU/CPU support.

### Database
* **MongoDB Atlas**: Cloud NoSQL database storing user notes, raw transcripts, and vector embeddings (using `$vectorSearch`).

### External APIs
* **Groq Cloud API**: Executes lightning-fast LLM inference (`openai/gpt-oss-20b`) for map-reduce summaries and RAG chat.
* **YouTube oEmbed API**: Retrieves video metadata and titles for frontend UI previews.
* **Firebase Authentication**: Provides secure Google OAuth 2.0 user login and session management.

### Tools
* **FFmpeg**: Speeds up audio file tempo to 2.0x prior to transcription to cut down Whisper inference time.

## 4. High-level architecture

```text
  +----------------------+          +-------------------------+
  |    Frontend (React)  |          |   Groq LLM Cloud API    |
  | - UI Components      |          | - Summarization         |
  | - Firebase Auth      |          | - RAG Q&A               |
  | - localStorage Cache |          +-------------------------+
  +----------+-----------+                      ^
             | HTTP/REST                        | HTTPS
             v                                  v
  +-----------------------------------------------------------+
  |                   FastAPI Backend                         |
  |                                                           |
  |  [Routers] -> [Services: YT, Media, PDF, Sum, Vector]     |
  |                                                           |
  |  - Local Faster-Whisper STT                               |
  |  - In-RAM MiniLM-L6-v2 Embeddings                         |
  |  - Background Tasks (Vector Embeddings)                   |
  +-----------------------------------------------------------+
             |                                  |
             | PyMongo                          | FFmpeg/OS
             v                                  v
  +----------------------+          +-------------------------+
  |   MongoDB Atlas      |          |   Local File System     |
  | - notesDB.notes      |          | - /uploads directory    |
  | - $vectorSearch      |          | - Media & PDF Storage   |
  +----------------------+          +-------------------------+
```

## 5. Folder-by-folder explanation

* **`backend/`**: Contains the complete FastAPI Python server.
  * **`backend/app/api/`**: The FastAPI route handlers defining the REST endpoints (e.g., `/chat`, `/summarize-yt`).
  * **`backend/app/core/`**: Central configuration, MongoDB database initialization (`database.py`), and LLM setup (`llm.py`).
  * **`backend/app/models/`**: Pydantic data schemas used for request validation and response formatting.
  * **`backend/app/services/`**: Core business logic modules including `media_processor.py` (FFmpeg, Whisper, PyMuPDF), `summarizer.py` (Langchain Map-Reduce), `vector_search.py` (Embeddings & RAG), and `youtube.py` (Transcript fetching).
  * **`backend/uploads/`**: Temporary local storage directory for uploaded audio, video, and PDF files.
* **`frontend/`**: Contains the React + Vite frontend application.
  * **`frontend/src/assets/`**: Static assets like icons and images.
  * **`frontend/src/components/`**: Reusable React UI components like navigation (`Navbar.jsx`, `Sidebar.jsx`), interactive viewers (`VideoPreview.jsx`), and layout shells.
  * **`frontend/src/context/`**: React Context providers, specifically `AuthContext.jsx` for managing Firebase authentication state.
  * **`frontend/src/pages/`**: The main route views including `Login.jsx`, specific summarizers (`YoutubeSummarizer.jsx`, `PdfTextSummarizer.jsx`), and the `History.jsx` view.
  * **`frontend/src/utils/`**: Helper utilities like `historyStorage.js` which manages the `localStorage` cache and custom event bus for cross-tab synchronization.

## 6. How the app starts and what its entry points are

**Backend Entry Point:**
The backend starts through `backend/main.py`. When launched (e.g., via `uvicorn app.main:app --reload`), FastAPI triggers an `@asynccontextmanager` called `lifespan`. This lifespan event first establishes a connection to MongoDB Atlas and then pre-loads the HuggingFace `all-MiniLM-L6-v2` embedding model directly into RAM to prevent first-request latency. Afterwards, the REST API routes are fully registered and ready to accept connections.

**Frontend Entry Point:**
The frontend starts via `frontend/src/main.jsx`. Vite bundles the application and injects the React virtual DOM into `index.html`. `main.jsx` wraps the core `App.jsx` component inside a `BrowserRouter` for routing and an `AuthProvider` for Firebase Google OAuth state initialization. Once running, users hit `App.jsx` which delegates rendering to either `PublicOnlyRoute` (for the Login page) or `ProtectedRoute` (for the main dashboard layout).
