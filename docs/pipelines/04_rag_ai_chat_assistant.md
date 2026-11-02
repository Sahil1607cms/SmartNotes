# Pipeline 04: RAG AI Chat Assistant ("Ask AI")

## A. One-paragraph summary
The RAG (Retrieval-Augmented Generation) AI Chat Assistant allows users to engage in a grounded conversational Q&A session with their summarized notes. When a user submits a question in the "Ask AI" tab, the backend embeds the query using HuggingFace's `all-MiniLM-L6-v2` model and attempts to retrieve the top 4 most relevant text chunks using MongoDB Atlas native `$vectorSearch`. If Atlas vector search is unindexed or unavailable, it automatically falls back to an in-memory NumPy cosine similarity calculation against the stored embeddings. The retrieved context chunks and the last 4 conversation turns are fed into a Groq LLM prompt to generate an accurate, hallucination-free answer.

---

## B. Pipeline at a glance

```text
[User] Enters a question in "Ask AI" tab
   │
   ▼
[Frontend: ChatAssistant.jsx]
   ├── Appends user message to UI state
   └── Sends POST /chat { message, summary, note_id, history }
   │
   ▼
[API Layer: backend/app/api/chat.py -> chat_with_rag]
   │
   ▼
[Service Layer: vector_search.py -> generate_rag_reply]
   │
   ├── 1. HuggingFaceEmbeddings: `model.embed_query(message)` -> 384-d float vector
   │
   ├── 2. Dual-Retrieval Vector Search:
   │      ├── Attempt A: MongoDB Atlas `$vectorSearch` Aggregation
   │      ├── Fallback B: Local In-Memory NumPy Cosine Similarity Matrix Search
   │      └── Fallback C: Summary / Note Content text fallback
   │
   ├── 3. Conversational Memory: Formats last 4 messages from `history`
   │
   ├── 4. Grounded Prompt Generation: Injects (Context + History + Question) into Groq LLM
   │
   ▼
[Response Payload] { reply: "...", context_source: "numpy_cosine_similarity" }
   │
   ▼
[Frontend: ChatAssistant.jsx]
   └── Renders AI Markdown response bubble in chat thread
```

---

## C. Step-by-step trace

### Step 1: User Sends Message from Chat UI
* **File & Function**: [`frontend/src/components/ChatAssistant.jsx`](file:///home/hardik/SmartNotes/frontend/src/components/ChatAssistant.jsx#L33-L67) (`handleSendMessage`)
* **What happens**:
  1. The user types a question in the input field or clicks one of the suggested prompt pills.
  2. The component creates `userMsg = { from: "user", text: chatInput }` and appends it to `chatMessages`.
  3. Captures `historyPayload` (the current list of prior messages before adding the new one).
  4. Sets `thinking = true` (showing an animated loading bubble) and initiates an HTTP POST request to `/chat`.
* **Input**: `chatInput` string, `noteId` string, `summary` string, `chatMessages` array.
* **API Call**: `POST http://localhost:8000/chat`
  - **Payload**:
    ```json
    {
      "message": "What is the primary conclusion of the document?",
      "summary": "# Executive Summary...",
      "note_id": "66c61f2e8f1b2c3d4e5f6a7b",
      "history": [
        { "from": "user", "text": "Who is the speaker?" },
        { "from": "bot", "text": "The speaker is Dr. Smith." }
      ]
    }
    ```
* **Output**: Awaiting backend response.

### Step 2: Route Entry & Parameter Sanitization
* **File & Function**: [`backend/app/api/chat.py`](file:///home/hardik/SmartNotes/backend/app/api/chat.py#L7-L34) (`chat_with_rag`)
* **What happens**: Receives JSON body, extracts `message`, `summary`, `note_id`, and `history`, checks that `message` is non-empty, and calls `generate_rag_reply()`.
* **Input**: Request JSON dictionary.
* **Output**: Awaited dictionary response from the vector search service.

### Step 3: Query Embedding Generation
* **File & Function**: [`backend/app/services/vector_search.py`](file:///home/hardik/SmartNotes/backend/app/services/vector_search.py#L84-L97) (`search_vector_context`)
* **What happens**:
  1. Retrieves the pre-loaded embedding model from RAM via `get_embedding_model()`.
  2. Calls `model.embed_query(message)` to convert the user's question into a 384-dimensional dense floating-point vector.
* **Technology**: `langchain_huggingface` (`HuggingFaceEmbeddings`), `sentence-transformers/all-MiniLM-L6-v2`.
* **Output**: `query_vector` (List of 384 floats).

### Step 4: Dual-Retrieval Vector Context Search
* **File & Function**: [`backend/app/services/vector_search.py`](file:///home/hardik/SmartNotes/backend/app/services/vector_search.py#L101-L181) (`search_vector_context`)
* **What happens**: Executes a cascading 4-tier retrieval strategy:
  1. **Tier 1 — MongoDB Atlas `$vectorSearch`**:
     Constructs an aggregation pipeline targeting `vector_index` filtering strictly on `{"_id": ObjectId(note_id)}` with `numCandidates=100, limit=4`. If documents are returned, returns joined text chunks with source `"mongo_vectorSearch"`.
  2. **Tier 2 — Local In-Memory NumPy Cosine Similarity**:
     If Atlas vector search fails (e.g. index is not yet built), fetches the note document via `get_note_by_id(note_id)`. Converts `note["embeddings"]` to float32 NumPy arrays and computes cosine similarity scores against `query_arr`:
     $$\text{sim}(S, Q) = \frac{S \cdot Q}{\|S\| \times \|Q\| + 10^{-8}}$$
     Sorts chunks in descending order of similarity, selects the top 4 chunks, and returns joined text with source `"numpy_cosine_similarity"`.
  3. **Tier 3 — Summary Fallback**:
     If no embeddings exist for the note yet, uses the plain `summary` text string with source `"summary_fallback"`.
  4. **Tier 4 — Note Content Fallback**:
     Uses `note["summary"]` with source `"note_summary_fallback"`.
* **Output**: Tuple `(context_text: str, retrieval_method: str)`.

### Step 5: Conversational Memory Formatting
* **File & Function**: [`backend/app/services/vector_search.py`](file:///home/hardik/SmartNotes/backend/app/services/vector_search.py#L184-L204) (`format_chat_history`)
* **What happens**: Takes the incoming `history` array, isolates the last 4 turns (`history[-4:]`), and formats them into a clean dialogue string:
  ```text
  User: Who is the speaker?
  Assistant: The speaker is Dr. Smith.
  ```
* **Output**: String representation of recent conversation turns (or `"None"` if empty).

### Step 6: Grounded RAG Prompt Generation & LLM Inference
* **File & Function**: [`backend/app/services/vector_search.py`](file:///home/hardik/SmartNotes/backend/app/services/vector_search.py#L221-L264) (`generate_rag_reply`)
* **What happens**:
  1. Configures Groq `ChatGroq` with `temperature=0.3` (low temperature for strict factual accuracy) and `max_tokens=2048`.
  2. Formulates the prompt with `RAG_PROMPT_TEMPLATE`:
     ```text
     Use the retrieved context and recent conversation history to answer the user's current question accurately.
     
     Retrieved Context:
     {context}
     
     Recent Conversation:
     {chat_history}
     
     Current User Question:
     {question}
     
     Answer:
     ```
  3. Calls `chain.ainvoke()` via LangChain.
* **Output**: Grounded answer string.

### Step 7: Frontend Response Rendering & State Update
* **File & Function**: [`frontend/src/components/ChatAssistant.jsx`](file:///home/hardik/SmartNotes/frontend/src/components/ChatAssistant.jsx#L53-L66)
* **What happens**:
  1. Receives `{ reply: "...", context_source: "..." }`.
  2. Appends `botMsg = { from: "bot", text: data.reply }` to `chatMessages`.
  3. Sets `thinking = false`.
  4. ReactMarkdown renders the formatted answer and auto-scrolls down to `messagesEndRef`.

---

## D. What runs in the background or after the response
There are no additional asynchronous background tasks launched by `/chat`. All retrieval and LLM generation occurs within the request lifecycle.

---

## E. What can fail

1. **Missing Note ID**:
   - *Where handled*: [`frontend/src/components/ChatAssistant.jsx`](file:///home/hardik/SmartNotes/frontend/src/components/ChatAssistant.jsx#L6).
   - *User sees*: Component returns `null` (chat interface is hidden until note is saved).
2. **Note Has No Processed Context / Embeddings**:
   - *Where handled*: [`backend/app/services/vector_search.py`](file:///home/hardik/SmartNotes/backend/app/services/vector_search.py#L230-L234).
   - *User sees*: Bot response: *"I don't have enough context to answer your question. Please ensure the note has been processed and saved."*.
3. **Groq API Outage / Key Error**:
   - *Where handled*: [`backend/app/services/vector_search.py`](file:///home/hardik/SmartNotes/backend/app/services/vector_search.py#L261-L263).
   - *User sees*: Bot bubble: *"❌ Error generating reply: [error details]"*.

---

## F. Reading order for studying

1. [`frontend/src/components/ChatAssistant.jsx`](file:///home/hardik/SmartNotes/frontend/src/components/ChatAssistant.jsx) — UI chat message state, history capturing, and suggested prompt integration.
2. [`backend/app/api/chat.py`](file:///home/hardik/SmartNotes/backend/app/api/chat.py) — Endpoint definition for `/chat`.
3. [`backend/app/services/vector_search.py`](file:///home/hardik/SmartNotes/backend/app/services/vector_search.py#L84-L182) — `search_vector_context` dual-retrieval engine (MongoDB `$vectorSearch` and NumPy cosine similarity).
4. [`backend/app/services/vector_search.py`](file:///home/hardik/SmartNotes/backend/app/services/vector_search.py#L184-L264) — Conversational memory formatter and `generate_rag_reply` LLM prompt execution.

---

## G. Key concepts to know before reading the code

* **Retrieval-Augmented Generation (RAG)**: A pattern where an LLM's prompt is augmented with relevant document snippets retrieved from a vector database, grounding the answer strictly in factual source material.
* **Vector Cosine Similarity**: A mathematical calculation measuring the cosine of the angle between two multi-dimensional vectors (dot product divided by the product of vector magnitudes), quantifying semantic similarity.
* **Conversational Memory Window**: Passing the last $N$ turns of chat history into the LLM prompt so the model understands pronouns and contextual follow-ups without needing full stateful server memory.
