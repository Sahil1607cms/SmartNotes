# SmartNotes Feature Pipelines Index

This directory contains technical walkthroughs for the core features of the SmartNotes project. Each document traces the complete execution path from user interaction in the React frontend to the FastAPI backend, background workers, AI models, and database storage.

---

## 1. Pipelines Overview

1. [**01. YouTube Video Summarization**](file:///home/hardik/SmartNotes/docs/pipelines/01_youtube_summarization.md)  
   Ingests a YouTube URL, retrieves and filters transcripts, generates a map-reduce summary via Groq LLM, stores the note in MongoDB Atlas, and triggers background vector embedding indexing.

2. [**02. Audio/Video Summarization**](file:///home/hardik/SmartNotes/docs/pipelines/02_audio_video_summarization.md)  
   Uploads local audio/video media files, accelerates audio tempo 2.0x via FFmpeg, transcribes speech with local Faster-Whisper, executes map-reduce summarization, and schedules background vector indexing.

3. [**03. PDF Document Summarization**](file:///home/hardik/SmartNotes/docs/pipelines/03_pdf_document_summarization.md)  
   Uploads PDF documents, extracts page-by-page raw text using PyMuPDF (`fitz`), summarizes text via Groq, persists the note in MongoDB, and queues background vector generation.

4. [**04. RAG AI Chat Assistant**](file:///home/hardik/SmartNotes/docs/pipelines/04_rag_ai_chat_assistant.md)  
   Powers conversational Q&A over processed notes using a dual-retrieval engine (MongoDB Atlas `$vectorSearch` with an in-memory NumPy cosine similarity fallback) and conversational context memory.

5. [**05. Flashcard & Prompt Generation**](file:///home/hardik/SmartNotes/docs/pipelines/05_flashcard_and_prompt_generation.md)  
   Extracts interactive 3D study flashcard bullet points and suggested follow-up questions using zero-cost local regex parsers first, with Groq LLM fallback when structured content is sparse.

6. [**06. History & Real-Time Syncing**](file:///home/hardik/SmartNotes/docs/pipelines/06_history_and_realtime_syncing.md)  
   Provides instant 0ms note loading via browser `localStorage`, background synchronization with MongoDB Atlas, and cross-tab reactive updates using a custom window event bus.

---

## 2. Shared Files and Cross-Feature Matrix

The following matrix shows how backend services, database handlers, and frontend utilities are shared across different features:

| File / Component Path | Primary Responsibility | YouTube (01) | Media (02) | PDF (03) | RAG Chat (04) | Flashcards / Prompts (05) | History Sync (06) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| [`backend/app/services/summarizer.py`](file:///home/hardik/SmartNotes/backend/app/services/summarizer.py) | Text chunking & Map-Reduce Groq pipeline | Shared | Shared | Shared | — | — | — |
| [`backend/app/services/vector_search.py`](file:///home/hardik/SmartNotes/backend/app/services/vector_search.py) | HuggingFace embeddings, background indexing, dual retrieval | Background Task | Background Task | Background Task | Primary Engine | — | — |
| [`backend/app/core/llm.py`](file:///home/hardik/SmartNotes/backend/app/core/llm.py) | Groq `ChatGroq` model factory | Shared | Shared | Shared | Shared | Fallback | — |
| [`backend/app/core/database.py`](file:///home/hardik/SmartNotes/backend/app/core/database.py) | PyMongo MongoDB CRUD operations | Save Note | Save Note | Save Note | Fetch Note Vectors | — | Fetch / Delete Notes |
| [`backend/app/services/youtube.py`](file:///home/hardik/SmartNotes/backend/app/services/youtube.py) | YouTube transcripts & filler word cleaner | Fetch & Clean | — | — | — | — | — |
| [`backend/app/services/media_processor.py`](file:///home/hardik/SmartNotes/backend/app/services/media_processor.py) | FFmpeg tempo, Faster-Whisper STT, PyMuPDF | — | STT / FFmpeg | PyMuPDF | — | — | — |
| [`frontend/src/pages/SummaryPage.jsx`](file:///home/hardik/SmartNotes/frontend/src/pages/SummaryPage.jsx) | Tabbed container for summary, chat, and flashcards | Shared View | Shared View | Shared View | Parent Container | Parent Container | Modal Viewer |
| [`frontend/src/utils/historyStorage.js`](file:///home/hardik/SmartNotes/frontend/src/utils/historyStorage.js) | `localStorage` cache & event bus dispatch | Add Note | Add Note | Add Note | — | — | Primary Sync Engine |
| [`frontend/src/context/AuthContext.jsx`](file:///home/hardik/SmartNotes/frontend/src/context/AuthContext.jsx) | Firebase Google Auth state & UID provider | User ID | User ID | User ID | — | — | User ID Filter |
