# Pipeline 05: Flashcard & Prompt-Suggestion Generation

## A. One-paragraph summary
The Flashcard and Prompt-Suggestion pipeline generates interactive study flashcards and contextual suggested questions from document summaries. To maximize speed and minimize API costs, the backend first runs zero-cost local parsers that use regular expressions and string analysis to extract existing bullet points and markdown headers directly from the summary. If the summary lacks sufficient markdown structure, it seamlessly falls back to the Groq LLM to synthesize concise bullet points or short discussion questions. On the frontend, flashcards are animated in a 3D grid with Framer Motion, and prompts appear as clickable pills in the chat interface.

---

## B. Pipeline at a glance

```text
======================= 1. FLASHCARD GENERATION =======================
[User] Switches to "Flashcards" tab -> clicks "Generate Flashcards"
   │
   ▼
[Frontend: Flashcards.jsx]
   └── Sends POST /summarize-flashcard { summary }
   │
   ▼
[API Layer: backend/app/api/flashcards.py -> summarize_for_flashcard]
   ├── Tier 1: Zero-Cost Local Bullet Parser (Regex / String scanning)
   │      └── Found >= 4 bullets? -> Returns bullets immediately (source: "local_parser")
   └── Tier 2: Groq LLM Fallback (if < 4 bullets found)
          └── Calls ChatGroq with 6-bullet extraction prompt (source: "groq_api")
   │
   ▼
[Frontend: Flashcards.jsx]
   ├── Converts bullets to card array & saves to `localStorage["flashcards_data"]`
   └── Renders Framer Motion 3D Card Grid with interactive modal popups

======================= 2. PROMPT SUGGESTIONS =======================
[Trigger] `SummaryPage.jsx` renders summary -> `ChatAssistant.jsx` mounts
   │
   ▼
[Frontend: ChatAssistant.jsx]
   └── Sends POST /prompts { summary }
   │
   ▼
[API Layer: backend/app/api/flashcards.py -> generate_prompts]
   ├── Tier 1: Zero-Cost Header Parser (Markdown `#` extraction)
   └── Tier 2: Groq LLM Fallback (Synthesizes 3 short questions)
   │
   ▼
[Frontend: ChatAssistant.jsx]
   └── Renders blue clickable pill buttons; clicking auto-sends to RAG Chat
```

---

## C. Step-by-step trace

### Part 1: Flashcard Pipeline Trace

#### Step 1.1: Flashcard Generation Trigger & Cache Check
* **File & Function**: [`frontend/src/components/Flashcards.jsx`](file:///home/hardik/SmartNotes/frontend/src/components/Flashcards.jsx#L30-L72) (`handleGenerateFlashcards`)
* **What happens**:
  1. When mounting, `Flashcards.jsx` checks `localStorage["flashcards_data"]`. If flashcards already exist, it hydrates them immediately.
  2. If the user clicks **Generate Flashcards**, it verifies `summary` is non-empty, sets `loading = true`, and initiates a POST request to `/summarize-flashcard`.
* **Input**: `summary` string.
* **API Call**: `POST http://localhost:8000/summarize-flashcard`
  - **Payload**: `{"summary": "# Executive Summary\n- Key Point 1\n- Key Point 2..."}`
* **Output**: Awaiting backend response.

#### Step 1.2: Zero-Cost Local Bullet Extraction
* **File & Function**: [`backend/app/api/flashcards.py`](file:///home/hardik/SmartNotes/backend/app/api/flashcards.py#L20-L40) (`summarize_for_flashcard`)
* **What happens**:
  1. Splits `summary` by newlines: `lines = req.summary.strip().split("\n")`.
  2. Scans for bullet characters (`-`, `*`, `•`) or numbered lists (`1.`, `2)`).
  3. Cleans leading bullet punctuation and validates length (`10 <= len(cleaned) <= 150`).
  4. If $\ge 4$ valid bullet points are found, takes the first 6 points and returns immediately without making any external API calls:
     ```json
     {
       "status": "success",
       "bullet_points": ["First key takeaway", "Second key takeaway", ...],
       "count": 6,
       "source": "local_parser"
     }
     ```

#### Step 1.3: Groq LLM Fallback for Flashcards
* **File & Function**: [`backend/app/api/flashcards.py`](file:///home/hardik/SmartNotes/backend/app/api/flashcards.py#L42-L77)
* **What happens**:
  1. If fewer than 4 bullet points were found, initializes Groq LLM (`temperature=0.7`).
  2. Prompts the LLM:
     ```text
     Extract exactly 6 key bullet points from the following summary.
     Each bullet point should be concise (max 15 words) and capture the main idea.
     Format as a numbered list (1., 2., 3., etc).
     ```
  3. Parses the numbered response lines and returns the first 6 cleaned points with `"source": "groq_api"`.

#### Step 1.4: Frontend 3D Flashcard Animation & Interaction
* **File & Function**: [`frontend/src/components/Flashcards.jsx`](file:///home/hardik/SmartNotes/frontend/src/components/Flashcards.jsx#L56-L158)
* **What happens**:
  1. Transforms bullet strings into card objects `[{ id: 0, text: "..." }]`.
  2. Saves cards to `localStorage["flashcards_data"]`.
  3. Randomizes and displays cards in a 3-column Framer Motion grid (`whileHover={{ scale: 1.15 }}`).
  4. Clicking any card sets `activeCard` state, rendering a backdrop modal popup showing the key point text.

---

### Part 2: Prompt-Suggestion Pipeline Trace

#### Step 2.1: Automatic Prompt Fetching on Summary Ready
* **File & Function**: [`frontend/src/components/ChatAssistant.jsx`](file:///home/hardik/SmartNotes/frontend/src/components/ChatAssistant.jsx#L16-L31)
* **What happens**: Whenever the `summary` prop changes, a `useEffect` hook triggers an asynchronous POST request to `/prompts`.
* **API Call**: `POST http://localhost:8000/prompts`
  - **Payload**: `{"summary": "..."}`

#### Step 2.2: Zero-Cost Header Parser & LLM Fallback
* **File & Function**: [`backend/app/api/flashcards.py`](file:///home/hardik/SmartNotes/backend/app/api/flashcards.py#L82-L133) (`generate_prompts`)
* **What happens**:
  1. **Local Parser**: Extracts markdown section headings (`# Heading`). Filters out generic titles like "Summary", "Overview", "Introduction".
  2. If headings are found, constructs suggested questions like `"What is {Heading}?"` and `"Can you explain {Heading} in detail?"`, returning up to 3 prompts with `"source": "local_parser"`.
  3. **LLM Fallback**: If no headings exist, prompts Groq LLM to generate 3 short, direct questions based strictly on the summary with `"source": "groq_api"`.

#### Step 2.3: Prompt Rendering and One-Click Chat Submission
* **File & Function**: [`frontend/src/components/ChatAssistant.jsx`](file:///home/hardik/SmartNotes/frontend/src/components/ChatAssistant.jsx#L93-L108)
* **What happens**: Renders suggested prompts as horizontal pills above the chat input box. Clicking any pill populates `chatInput` and immediately triggers `handleSendMessage()`.

---

## D. What runs in the background or after the response
Neither `/summarize-flashcard` nor `/prompts` launch any background tasks.

---

## E. What can fail

1. **Empty Summary Submitted**:
   - *Where handled*: [`backend/app/api/flashcards.py`](file:///home/hardik/SmartNotes/backend/app/api/flashcards.py#L17-L18,L89-L91).
   - *User sees*: Returns `{"error": "Summary is required"}` or empty prompts list.
2. **Groq API Failure During Fallback**:
   - *Where handled*: [`backend/app/api/flashcards.py`](file:///home/hardik/SmartNotes/backend/app/api/flashcards.py#L78-L79,L131-L132).
   - *User sees*: Alert: *"❌ Failed to generate flashcards."* in `Flashcards.jsx`; prompts simply remain empty.

---

## F. Reading order for studying

1. [`frontend/src/components/Flashcards.jsx`](file:///home/hardik/SmartNotes/frontend/src/components/Flashcards.jsx) — Flashcard state, Framer Motion animations, and `localStorage` cache.
2. [`frontend/src/components/ChatAssistant.jsx`](file:///home/hardik/SmartNotes/frontend/src/components/ChatAssistant.jsx#L16-L31,L93-L108) — Prompt-fetching effect and pill click handlers.
3. [`backend/app/api/flashcards.py`](file:///home/hardik/SmartNotes/backend/app/api/flashcards.py) — Local regex parser optimizations and Groq fallback endpoints.

---

## G. Key concepts to know before reading the code

* **Zero-Cost Parsing Optimization**: Analyzing pre-generated markdown text with regex instead of making repeated LLM API calls, saving latency and API cost.
* **Framer Motion `AnimatePresence`**: A React animation library component that enables smooth exit animations when elements are removed from the React component tree.
