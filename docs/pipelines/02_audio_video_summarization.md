# Pipeline 02: Audio/Video Media Summarization

## A. One-paragraph summary
The Audio/Video Media Summarization pipeline enables users to upload local audio or video recordings (e.g., MP3, WAV, MP4, MOV) to generate structured notes. On the backend, the file is stored locally, its audio track is accelerated to 2.0x speed via FFmpeg CLI filters to halve transcription processing time, and speech is transcribed locally using `faster-whisper` (CTranslate2) with Voice Activity Detection (VAD). The resulting transcript is chunked and summarized via Groq's LLM Map-Reduce engine (shared with Pipeline 01), stored in MongoDB Atlas, and asynchronously indexed into vector embeddings in the background.

---

## B. Pipeline at a glance

```text
[User] Selects/Drops Audio or Video File (.mp3, .mp4, etc.)
   │
   ▼
[Frontend: AudioVideoSummarizer.jsx]
   └── Packages file into `FormData` and sends POST /summarize-media
   │
   ▼
[API Layer: backend/app/api/summarizer.py -> summarize_media]
   ├── Validates file extension against allowed whitelist
   ├── Saves file locally to `uploads/{user_id}/{task_id}_{filename}`
   │
   ▼
[Service Layer: media_processor.py -> process_media_file]
   ├── 1. FFmpeg CLI atempo=2.0 speedup conversion -> `{file}_speedup.wav`
   ├── 2. Faster-Whisper (WhisperModel "small") transcription with VAD
   └── 3. Cleans up temporary accelerated wav file
   │
   ▼
[Service Layer: summarizer.py -> summarize_long_content]
   └── (Shared with Pipeline 01: Chunking -> Groq LLM Map-Reduce)
   │
   ▼
[Database: database.py -> create_note]
   └── Inserts NoteModel (type: "media") into MongoDB Atlas `notes` collection
   │
   ▼
[Background Task: vector_search.py -> async_generate_and_save_embeddings]
   └── Computes and updates 384-d MiniLM-L6-v2 vector embeddings
   │
   ▼
[Frontend: AudioVideoSummarizer.jsx & SummaryPage.jsx]
   ├── Hydrates summary text and note ID in React state
   ├── Updates local history cache via historyStorage.js
   └── Mirrors state to `localStorage["summary_media_state"]`
```

---

## C. Step-by-step trace

### Step 1: File Selection and Form Submission
* **File & Function**: [`frontend/src/pages/AudioVideoSummarizer.jsx`](file:///home/hardik/SmartNotes/frontend/src/pages/AudioVideoSummarizer.jsx#L47-L96) (`handleSummarize`)
* **What happens**: The user selects or drags an audio/video file. When **Summarize** is clicked, the component verifies authentication (`user.uid`), appends the file to `FormData`, and posts it to the backend.
* **Input**: `file` (Binary File object), `user.uid` string.
* **API Call**: `POST http://localhost:8000/summarize-media`
  - **Content-Type**: `multipart/form-data`
  - **Form Fields**: `file` (Binary), `user_id` (string), `type="media"` (string).
* **Output**: Awaiting backend JSON response.

### Step 2: Route Handling, Extension Validation & Disk Staging
* **File & Function**: [`backend/app/api/summarizer.py`](file:///home/hardik/SmartNotes/backend/app/api/summarizer.py#L79-L106) (`summarize_media`)
* **What happens**:
  1. Validates that `file.filename` exists and has an extension in:
     `[".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac", ".mp4", ".avi", ".mov", ".mkv", ".webm"]`.
  2. Generates a unique `task_id` (`uuid4()`).
  3. Creates user staging directory: `backend/uploads/{user_id}/`.
  4. Streams the uploaded binary data into `local_file_path`: `backend/uploads/{user_id}/{task_id}_{filename}` using `shutil.copyfileobj()`.
* **Input**: FastAPI `UploadFile`, `user_id`, `type`.
* **Output**: Local absolute file path string.
* **Validation**: Returns HTTP 400 if file extension is unsupported or file name is missing.

### Step 3: FFmpeg Audio Acceleration (2.0x Tempo)
* **File & Function**: [`backend/app/services/media_processor.py`](file:///home/hardik/SmartNotes/backend/app/services/media_processor.py#L11-L25) (`convert_media_tempo`)
* **What happens**: Executes the FFmpeg command-line subprocess to double the audio playback tempo, resample to 16,000 Hz, strip video streams, and downmix to 1 channel:
  ```bash
  ffmpeg -y -i <input_path> -filter:a "atempo=2.0" -vn -ar 16000 -ac 1 <output_speedup.wav>
  ```
* **Input**: Input file path, output path (`{file_path}_speedup.wav`), `tempo=2.0`.
* **Output**: Boolean `True` on success, `False` if FFmpeg is missing or fails (in which case it falls back to the original unaccelerated file).
* **Technology**: System `ffmpeg` binary via Python `subprocess.run`.

### Step 4: Faster-Whisper Local Speech-to-Text Transcription
* **File & Function**: [`backend/app/services/media_processor.py`](file:///home/hardik/SmartNotes/backend/app/services/media_processor.py#L27-L74) (`process_media_file`)
* **What happens**:
  1. Detects available hardware via `torch.cuda.is_available()` (chooses `"cuda"` with `float16` if NVIDIA GPU is present, otherwise `"cpu"` with `float32`).
  2. Instantiates `WhisperModel("small", device=device, compute_type=compute_type)`.
  3. Calls `model.transcribe()` with `beam_size=5` and Voice Activity Detection (VAD) filter (`min_silence_duration_ms=500`) to ignore silent gaps.
  4. Iterates over transcribed segments and formats them as `[{"time": "0.00s -> 5.20s", "text": "..."}]`.
  5. Cleans up the temporary `{file_path}_speedup.wav` in the `finally` block.
* **Technology**: `faster-whisper` (CTranslate2 inference engine), PyTorch.
* **Error Handling**: Catches exceptions and returns a fallback placeholder segment `[{"time": "0.00s -> 0.00s", "text": "Transcribed content for {filename}"}]`.

### Step 5: Map-Reduce Summarization Pipeline
* **File & Function**: [`backend/app/services/summarizer.py`](file:///home/hardik/SmartNotes/backend/app/services/summarizer.py#L127-L167) (`summarize_long_content`)
* **What happens**: Passes the transcribed segment list to the shared Map-Reduce engine (see [Pipeline 01](file:///home/hardik/SmartNotes/docs/pipelines/01_youtube_summarization.md#step-5-text-cleaning-chunking-and-map-reduce-summarization) for complete breakdown of LangChain chunking, semaphore concurrency, and Groq `ChatGroq` LLM execution).
* **Output**: Structured Markdown summary string.

### Step 6: Database Persistence & Background Vector Indexing
* **File & Function**: [`backend/app/api/summarizer.py`](file:///home/hardik/SmartNotes/backend/app/api/summarizer.py#L113-L135)
* **What happens**:
  1. Instantiates `NoteModel(user_id=user_id, title=filename, type="media", summary=summary, transcript=transcripts, source=local_file_path, task_id=task_id)`.
  2. Inserts document into MongoDB Atlas via `create_note()` ([`backend/app/core/database.py`](file:///home/hardik/SmartNotes/backend/app/core/database.py#L25-L35)).
  3. Registers `async_generate_and_save_embeddings` with `background_tasks`.
  4. Returns HTTP 200 with `status`, `summary`, `note`, and `logs`.

### Step 7: Frontend State Hydration & Caching
* **File & Function**: [`frontend/src/pages/AudioVideoSummarizer.jsx`](file:///home/hardik/SmartNotes/frontend/src/pages/AudioVideoSummarizer.jsx#L76-L86) & [`frontend/src/utils/historyStorage.js`](file:///home/hardik/SmartNotes/frontend/src/utils/historyStorage.js#L50-L72)
* **What happens**: Sets `summary` and `noteId` state, calls `addNoteToHistory(data.note)`, saves `{ summary, noteId, logs }` to `localStorage["summary_media_state"]`, and displays the summary view on [`SummaryPage.jsx`](file:///home/hardik/SmartNotes/frontend/src/pages/SummaryPage.jsx).

---

## D. What runs in the background or after the response

* **Background Task**: [`backend/app/services/vector_search.py`](file:///home/hardik/SmartNotes/backend/app/services/vector_search.py#L61-L82) (`async_generate_and_save_embeddings`)
* **Process**: Concatenates transcript segments, splits them into 600-character chunks with 120-character overlap, computes 384-dimensional vector embeddings with HuggingFace `all-MiniLM-L6-v2`, and updates the MongoDB document `embeddings` field without delaying the user.

---

## E. What can fail

1. **Unsupported File Format**:
   - *Where handled*: [`backend/app/api/summarizer.py`](file:///home/hardik/SmartNotes/backend/app/api/summarizer.py#L93-L96).
   - *User sees*: Error banner: *"Unsupported file format: .xyz"*.
2. **FFmpeg Failure / Missing Binary**:
   - *Where handled*: [`backend/app/services/media_processor.py`](file:///home/hardik/SmartNotes/backend/app/services/media_processor.py#L22-L24).
   - *System response*: Gracefully logs a warning and falls back to passing the raw unaccelerated media file directly to Faster-Whisper.
3. **Whisper Transcription Out of Memory / Failure**:
   - *Where handled*: [`backend/app/services/media_processor.py`](file:///home/hardik/SmartNotes/backend/app/services/media_processor.py#L64-L67).
   - *System response*: Returns fallback dummy transcript string so the downstream summarizer can still complete.
4. **Groq API Rate Limits**:
   - *Where handled*: [`backend/app/services/summarizer.py`](file:///home/hardik/SmartNotes/backend/app/services/summarizer.py#L78-L95).
   - *System response*: Retries with exponential backoff up to 3 times before returning HTTP 413/500 error.

---

## F. Reading order for studying

1. [`frontend/src/pages/AudioVideoSummarizer.jsx`](file:///home/hardik/SmartNotes/frontend/src/pages/AudioVideoSummarizer.jsx) — Examine drag-and-drop file input and `FormData` upload.
2. [`backend/app/api/summarizer.py`](file:///home/hardik/SmartNotes/backend/app/api/summarizer.py#L79-L152) — Review `/summarize-media` router handling, disk saving, and response payload.
3. [`backend/app/services/media_processor.py`](file:///home/hardik/SmartNotes/backend/app/services/media_processor.py#L11-L74) — Study `convert_media_tempo` and `process_media_file` (Whisper + FFmpeg).
4. [`backend/app/services/summarizer.py`](file:///home/hardik/SmartNotes/backend/app/services/summarizer.py) — Follow the shared Map-Reduce text summarizer.
5. [`backend/app/services/vector_search.py`](file:///home/hardik/SmartNotes/backend/app/services/vector_search.py) — Follow vector embedding background calculation.

---

## G. Key concepts to know before reading the code

* **Audio Tempo Filtering (`atempo=2.0`)**: An FFmpeg DSP audio filter that doubles audio speed while preserving original pitch, allowing speech recognition models to process half the audio samples in half the time.
* **Voice Activity Detection (VAD)**: An algorithm in Faster-Whisper that identifies human speech and filters out silent intervals, preventing hallucinated repetitive text during long pauses.
* **CTranslate2**: A fast inference engine for Transformer models optimized for CPU and GPU that powers `faster-whisper`.
* **Multipart Form Data**: An HTTP content-type standard used for uploading binary files alongside key-value fields to an API endpoint.
