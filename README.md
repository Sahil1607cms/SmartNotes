# SmartNotes - Intelligent Content Summarization & RAG Platform

## 📋 Table of Contents

1. [Project Overview](#-project-overview)
2. [Key Features](#key-features)
3. [System Architecture](#-system-architecture)
4. [Technology Stack](#-technology-stack)
5. [UML Diagrams](#-uml-diagrams)
6. [System Requirements](#-system-requirements)
7. [Installation & Setup](#-installation--setup)
8. [Database Design](#-database-design)
9. [API Documentation](#-api-documentation)
10. [Component Details](#-component-details)
11. [Data Flow](#-data-flow)
12. [Configuration](#-configuration)
13. [Troubleshooting](#-troubleshooting)
14. [Performance Optimization](#-performance-optimization)
15. [Deployment](#-deployment)

---

## 📋 Project Overview

**SmartNotes** is an intelligent note-taking and content summarization platform that leverages Retrieval-Augmented Generation (RAG) to help users efficiently process and interact with content.

### Core Concept
The application combines:
- **LLM Intelligence** (Groq API) for fast, accurate summarization
- **Vector Embeddings** (HuggingFace) for semantic search
- **Vector Database** (FAISS) for efficient retrieval
- **Full-Stack Architecture** (FastAPI + React) for seamless UX

### Problem Statement
Users struggle with:
- Information overload from multiple content sources
- Time spent on manual note-taking
- Difficulty finding relevant information in past notes
- Limited ability to ask intelligent questions about content

### Solution
SmartNotes provides:
- One-click summarization of YouTube videos
- Intelligent Q&A using RAG on summarized content
- Persistent storage with intelligent search
- Interactive flashcard generation for studying

---

## Key Features

### 1. **YouTube Summarization** 📹
- Extract transcripts from YouTube videos
- Intelligent summarization using Groq LLM
- Preserve key points and context
- Support for videos with captions

### 2. **AI Chat Assistant** 🤖
- Ask questions about summarized content
- Context-aware responses using RAG
- Multi-turn conversations
- Intelligent prompt suggestions

### 3. **Flashcard Generation** 📚
- Auto-generate study flashcards from summaries
- Q&A format with answers
- Perfect for exam preparation
- Downloadable flashcard sets

### 4. **History Management** 💾
- Save all summaries and conversations
- Full-text search capabilities
- Edit and delete notes
- Organization by date and source

### 5. **Firebase Authentication** 🔐
- Secure user registration and login
- Email verification
- Password reset functionality
- User session management

### 6. **Interactive Dashboard** 📊
- View all saved notes
- Quick access to recent summaries
- Statistics and usage analytics
- Dark/Light mode support

---

## 🏗️ System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                       CLIENT LAYER                              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │        React Frontend (Vite)                             │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │   │
│  │  │  YouTube    │  │  Chat       │  │  Flashcard  │      │   │
│  │  │  Summarizer │  │  Component  │  │  Generator  │      │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘      │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │   │
│  │  │  History    │  │  Auth       │  │  Navbar     │      │   │
│  │  │  Page       │  │  Context    │  │  Sidebar    │      │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘      │   │
│  └──────────────────────────────────────────────────────────┘   │
│                          (Port 5173)                            │
└─────────────────────────────────────────────────────────────────┘
                              ↕ HTTP/REST
┌─────────────────────────────────────────────────────────────────┐
│                    API GATEWAY LAYER                            │
│            FastAPI Application (Port 8000)                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Authentication & Authorization (Firebase)              │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   BUSINESS LOGIC LAYER                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  YouTube     │  │  Chat        │  │  Flashcard   │          │
│  │  Summarizer  │  │  Service     │  │  Service     │          │
│  │  Service     │  │  (RAG)       │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Note        │  │  History     │  │  Embedding   │          │
│  │  Service     │  │  Service     │  │  Service     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   DATA ACCESS LAYER                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  MongoDB     │  │  FAISS       │  │  Cache       │          │
│  │  Connection  │  │  Vector DB   │  │  (Redis)     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   EXTERNAL SERVICES                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Groq LLM    │  │  YouTube     │  │  HuggingFace │          │
│  │  API         │  │  Transcript  │  │  Embeddings  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### Detailed Component Architecture

```
FRONTEND LAYER
├── React Components
│   ├── Pages
│   │   ├── YoutubeSummarizer.jsx
│   │   ├── History.jsx
│   │   ├── Login.jsx
│   │   └── Dashboard.jsx
│   ├── Components
│   │   ├── ChatAssistant.jsx
│   │   ├── Flashcards.jsx
│   │   ├── Navbar.jsx
│   │   ├── Sidebar.jsx
│   │   └── NoteCard.jsx
│   ├── Context
│   │   └── AuthContext.jsx
│   └── Utils
│       ├── api.js
│       ├── firebase.js
│       └── helpers.js

BACKEND LAYER
├── FastAPI Application (main.py)
├── Routes
│   ├── youtube_routes.py
│   ├── chat_routes.py
│   ├── flashcard_routes.py
│   ├── notes_routes.py
│   └── prompt_routes.py
├── Services
│   ├── YT_summarizer.py
│   ├── chat_service.py
│   ├── flashcard_service.py
│   └── RAG_service.py
├── Database
│   ├── config.py
│   ├── crud.py
│   ├── historySchema.py
│   └── vectorstore/
│       └── index.faiss
└── Utils
    └── youtube_transcript.py
```

---

## 🛠️ Technology Stack

### Frontend
| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Framework** | React 19.1.1 | UI library |
| **Build Tool** | Vite 5.0.0 | Fast bundling |
| **Routing** | React Router 7.9.1 | Page navigation |
| **Styling** | TailwindCSS 4.1.13 | Utility-first CSS |
| **Icons** | Lucide React 0.544.0 | Icon library |
| **Auth** | Firebase 12.3.0 | Authentication |
| **Markdown** | React Markdown 10.1.0 | Content rendering |
| **HTTP Client** | Axios/Fetch | API communication |

### Backend
| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Framework** | FastAPI 0.121.2 | REST API |
| **Server** | Uvicorn 0.38.0 | ASGI server |
| **Database** | MongoDB 4.15.4 | NoSQL data storage |
| **LLM** | Groq API | Fast inference |
| **LLM Chains** | LangChain 1.0.7 | LLM orchestration |
| **Embeddings** | HuggingFace | Vector embeddings |
| **Vector DB** | FAISS | Vector similarity search |
| **ML Framework** | PyTorch 2.5.1 | Deep learning |
| **Auth** | Firebase Admin SDK | Token verification |

### DevOps & Infrastructure
| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Version Control** | Git | Code management |
| **Environment** | Python 3.10+ | Runtime |
| **Package Manager** | pip, npm | Dependency management |
| **Containerization** | Docker (optional) | Deployment |
| **Cloud Database** | MongoDB Atlas | Hosted database |

---

## 📊 UML Diagrams

### 1. Use Case Diagram

```
                          ┌─────────────────┐
                          │    SmartNotes   │
                          │    System       │
                          └─────────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
           ┌────────▼────────┐   ┌─▼─────────────┐   ┌──────────────┐
           │  Authenticated  │   │   External    │   │  Admin User  │
           │     User        │   │   Systems     │   └──────────────┘
           └────────┬────────┘   └───────────────┘
                    │
        ┌───────────┼───────────┬───────────────┬──────────────┐
        │           │           │               │              │
    ┌───▼──┐  ┌────▼────┐  ┌──▼─────┐  ┌─────▼──┐  ┌────────▼────┐
    │Login │  │Summarize│  │  Chat  │  │Generate│  │   Manage    │
    │Sign  │  │YouTube  │  │  with  │  │Flash-  │  │   History   │
    │Up    │  │ Videos  │  │ RAG    │  │cards   │  │   & Search  │
    └──────┘  └────┬────┘  └──┬─────┘  └────────┘  └─────────────┘
                   │           │
             ┌─────▼───────┬───▼────┐
             │             │        │
        ┌────▼────┐  ┌────▼─────┐ ┌▼─────────────┐
        │Fetch    │  │Extract   │ │Store Summary │
        │YouTube  │  │ & Process│ │in Database   │
        │Transcript   │Transcript    │ & Vector DB │
        └──────────┘  └──────────┘ └──────────────┘
```

### 2. Activity Diagram - YouTube Summarization Flow

```
                        ┌─────────────────┐
                        │      Start      │
                        └────────┬────────┘
                                 │
                        ┌────────▼────────┐
                        │ User Enters URL │
                        └────────┬────────┘
                                 │
                        ┌────────▼────────┐
                        │ Validate URL    │
                        └────┬───────┬────┘
                             │       │
                        Valid│       │Invalid
                             │       │
                        ┌────▼┐   ┌─▼──────────┐
                        │     │   │ Show Error │
                        │     │   └────┬───────┘
                        │     │        │
                        │     └────────┴──────┐
                        │                      │
                ┌───────▼──────────┐   ┌──────▼──────┐
                │ Fetch Transcript │   │   Retry     │
                │ from YouTube     │   └──────────────┘
                └───────┬──────────┘
                        │
                ┌───────▼──────────────┐
                │ Extract Key Points   │
                │ Preprocess Text      │
                └───────┬──────────────┘
                        │
                ┌───────▼──────────────┐
                │ Send to Groq LLM     │
                │ for Summarization    │
                └───────┬──────────────┘
                        │
                ┌───────▼──────────────┐
                │ Generate Embeddings  │
                │ (HuggingFace)        │
                └───────┬──────────────┘
                        │
                ┌───────▼──────────────┐
                │ Store in MongoDB     │
                │ & FAISS Index        │
                └───────┬──────────────┘
                        │
                ┌───────▼──────────────┐
                │ Return to Frontend   │
                │ Display Summary      │
                └───────┬──────────────┘
                        │
                ┌───────▼──────────────┐
                │      End            │
                └─────────────────────┘
```

### 3. Activity Diagram - Chat & RAG Flow

```
                        ┌─────────────────┐
                        │ User Asks Query │
                        └────────┬────────┘
                                 │
                        ┌────────▼────────┐
                        │ Validate Input   │
                        └────────┬────────┘
                                 │
                        ┌────────▼────────────┐
                        │ Generate Query      │
                        │ Embedding           │
                        │ (HuggingFace)       │
                        └────────┬────────────┘
                                 │
                        ┌────────▼────────────┐
                        │ Search FAISS Index  │
                        │ for Similar Chunks  │
                        └────────┬────────────┘
                                 │
                        ┌────────▼────────────┐
                        │ Retrieve Top-K      │
                        │ Relevant Context    │
                        └────────┬────────────┘
                                 │
                        ┌────────▼────────────┐
                        │ Build Prompt with   │
                        │ Context             │
                        └────────┬────────────┘
                                 │
                        ┌────────▼────────────┐
                        │ Send to Groq LLM    │
                        │ for Response        │
                        └────────┬────────────┘
                                 │
                        ┌────────▼────────────┐
                        │ Store Q&A in        │
                        │ MongoDB             │
                        └────────┬────────────┘
                                 │
                        ┌────────▼────────────┐
                        │ Stream Response to  │
                        │ Frontend            │
                        └────────┬────────────┘
                                 │
                        ┌────────▼────────────┐
                        │      End           │
                        └────────────────────┘
```

### 4. Sequence Diagram - YouTube Summarization

```
User        Frontend        Backend API      Groq LLM       MongoDB    FAISS
 │              │                │              │              │          │
 │ Enter URL    │                │              │              │          │
 ├─────────────>│                │              │              │          │
 │              │ POST /summarize-yt             │              │          │
 │              ├───────────────>│              │              │          │
 │              │                │ Fetch Video │              │          │
 │              │                ├─────────────────────────────>          │
 │              │                │< Transcript                 │          │
 │              │                │              │              │          │
 │              │                │ Preprocess Text            │          │
 │              │                │ Build Prompt               │          │
 │              │                │              │              │          │
 │              │                │ POST Summarize Request      │          │
 │              │                ├──────────────────────────>  │          │
 │              │                │              │ Generate Summary        │
 │              │                │<──────────────────────────  │          │
 │              │                │              │              │          │
 │              │                │ Chunk Summary              │          │
 │              │                │ Generate Embeddings        │          │
 │              │                │              │              │          │
 │              │                │ Save Document             │          │
 │              │                ├──────────────────────────> │          │
 │              │                │              │              │          │
 │              │                │ Add to Vector Index        │          │
 │              │                ├─────────────────────────────────────> │
 │              │<───────────────┤              │              │          │
 │              │ Response {id, summary, date}  │              │          │
 │<─────────────┤                │              │              │          │
 │ Display      │                │              │              │          │
 │ Summary      │                │              │              │          │
 │              │                │              │              │          │
```

### 5. Sequence Diagram - Chat with RAG

```
User      Frontend       Backend API    FAISS Index    Groq LLM    MongoDB
 │           │               │            │              │           │
 │ Ask Query │               │            │              │           │
 ├──────────>│               │            │              │           │
 │           │ POST /chat    │            │              │           │
 │           ├──────────────>│            │              │           │
 │           │               │ Get Note ID│              │           │
 │           │               │ Verify User│              │           │
 │           │               │            │              │           │
 │           │               │ Create Query Embedding    │           │
 │           │               │            │              │           │
 │           │               │ Search Similar Chunks    │           │
 │           │               ├───────────>│              │           │
 │           │               │<───────────┤ Top-K Chunks│           │
 │           │               │            │              │           │
 │           │               │ Build Prompt with Context│           │
 │           │               │            │              │           │
 │           │               │ Generate Completion       │           │
 │           │               ├───────────────────────────>           │
 │           │               │            │              │ Response  │
 │           │               │<───────────────────────────           │
 │           │               │            │              │           │
 │           │               │ Store Q&A Pair           │           │
 │           │               ├──────────────────────────────────────>│
 │           │               │            │              │           │
 │           │<──────────────┤ Response {answer, score}  │           │
 │           │ Stream Answer │            │              │           │
 │<──────────┤               │            │              │           │
 │ View Ans. │               │            │              │           │
 │           │               │            │              │           │
```

### 6. Class Diagram - Core Models

```
                    ┌────────────────────┐
                    │      User          │
                    ├────────────────────┤
                    │ - uid: string      │
                    │ - email: string    │
                    │ - displayName: str │
                    │ - createdAt: date  │
                    └────────┬───────────┘
                             │
                ┌────────────┼────────────┐
                │            │            │
        ┌───────▼────────┐   │   ┌────────▼──────────┐
        │   Note         │   │   │   ChatMessage     │
        ├────────────────┤   │   ├───────────────────┤
        │ - _id: ObjectId│   │   │ - _id: ObjectId   │
        │ - userId: str  │   │   │ - noteId: str     │
        │ - title: str   │   │   │ - userId: str     │
        │ - content: str │   │   │ - question: str   │
        │ - summary: str │   │   │ - answer: str     │
        │ - source: enum │   │   │ - timestamp: date │
        │ - createdAt    │   │   │ - embedding: []   │
        │ - updatedAt    │   │   └───────────────────┘
        └────────┬───────┘   │
                 │           │
                 └───────────┘
                         │
                 ┌───────▼──────────┐
                 │   Flashcard      │
                 ├──────────────────┤
                 │ - _id: ObjectId  │
                 │ - noteId: str    │
                 │ - userId: str    │
                 │ - cards: []      │
                 │   - question: str│
                 │   - answer: str  │
                 │ - createdAt: date│
                 └──────────────────┘


    ┌──────────────────────┐
    │   Embedding/Vector   │
    ├──────────────────────┤
    │ - _id: ObjectId      │
    │ - noteId: str        │
    │ - userId: str        │
    │ - chunkIndex: int    │
    │ - vector: [float]    │  → Stored in FAISS
    │ - metadata: {}       │
    │ - createdAt: date    │
    └──────────────────────┘
```

### 7. Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND REACT COMPONENTS                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐                      ┌──────────────┐        │
│  │   Navbar     │◄──────────────────────┤ AuthContext  │        │
│  └──────────────┘                      └──────────────┘        │
│         │                                      ▲                │
│         │                                      │                │
│  ┌──────▼──────────┐         ┌────────────────┼──────┐         │
│  │   Sidebar       │         │                │      │         │
│  ├─────────────────┤         │    ┌───────────▼────┐ │         │
│  │ - Routes        │         │    │  YoutubeSummary│ │         │
│  │ - Navigation    │         │    ├────────────────┤ │         │
│  └─────────────────┘         │    │ - Input URL    │ │         │
│                              │    │ - Display Summ.│ │         │
│  ┌──────────────────────┐    │    │ - Call API     │ │         │
│  │   Dashboard          │    │    └────────────────┘ │         │
│  ├──────────────────────┤    │                        │         │
│  │ - Recent Notes       │    │    ┌──────────────┐   │         │
│  │ - Quick Stats        │    │    │  ChatPanel   │   │         │
│  └──────────────────────┘    │    ├──────────────┤   │         │
│                              │    │ - Chat Input │   │         │
│  ┌──────────────────────┐    │    │ - Messages   │   │         │
│  │   History Page       │    │    │ - Call Chat  │   │         │
│  ├──────────────────────┤    │    │   API        │   │         │
│  │ - Note List          │    │    └──────────────┘   │         │
│  │ - Search/Filter      │    │                        │         │
│  │ - Note Preview       │    │    ┌──────────────┐   │         │
│  └──────────────────────┘    │    │ Flashcards   │   │         │
│                              │    ├──────────────┤   │         │
│  ┌──────────────────────┐    │    │ - Card View  │   │         │
│  │   Login/SignUp       │    │    │ - Flip Card  │   │         │
│  ├──────────────────────┤    │    │ - Generate   │   │         │
│  │ - Firebase Auth      │    │    └──────────────┘   │         │
│  │ - Form Validation    │    │                        │         │
│  └──────────────────────┘    └────────────────────────┘         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ HTTP/REST APIs
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND FASTAPI ROUTES                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  Authentication Middleware (Firebase)                  │   │
│  │  - Verify JWT Token                                    │   │
│  │  - Check User Permission                               │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐                   │
│  │  youtube_routes  │  │  notes_routes    │                   │
│  ├──────────────────┤  ├──────────────────┤                   │
│  │ POST /summarize- │  │ GET /notes       │                   │
│  │       yt         │  │ DELETE /notes/id │                   │
│  │ GET /transcript  │  │ PUT /notes/id    │                   │
│  └────────┬─────────┘  └────────┬─────────┘                   │
│           │                      │                             │
│  ┌────────▼──────────┐  ┌────────▼──────────┐                 │
│  │ YT_summarizer     │  │ notes_service     │                 │
│  │ Service           │  │                   │                 │
│  ├───────────────────┤  ├───────────────────┤                 │
│  │ - Fetch Video     │  │ - Create Note     │                 │
│  │ - Extract Text    │  │ - Update Note     │                 │
│  │ - Summarize       │  │ - Delete Note     │                 │
│  │ - Generate Emb.   │  │ - Get Notes       │                 │
│  │ - Store Results   │  └───────────────────┘                 │
│  └────────┬──────────┘                                        │
│           │                                                   │
│  ┌────────▼───────────────────┐                              │
│  │  chat_routes               │                              │
│  ├────────────────────────────┤                              │
│  │ POST /chat                 │                              │
│  │ GET /prompts               │                              │
│  └────────┬────────────────────┘                             │
│           │                                                   │
│  ┌────────▼────────────────────┐                             │
│  │  RAG Service                │                             │
│  ├─────────────────────────────┤                             │
│  │ - Retrieve Context (FAISS) │                             │
│  │ - Build Prompt              │                             │
│  │ - Query LLM                 │                             │
│  │ - Stream Response            │                             │
│  └────────┬─────────────────────┘                            │
│           │                                                   │
│  ┌────────▼─────────────────────┐                            │
│  │  flashcard_routes            │                            │
│  ├──────────────────────────────┤                            │
│  │ POST /flashcards/generate    │                            │
│  │ GET /flashcards/{noteId}     │                            │
│  └────────┬──────────────────────┘                           │
│           │                                                   │
│  ┌────────▼──────────────────┐                               │
│  │ flashcard_service         │                               │
│  ├───────────────────────────┤                               │
│  │ - Generate Q&A from Summ. │                               │
│  │ - Format Flashcards       │                               │
│  │ - Store in MongoDB        │                               │
│  └───────────────────────────┘                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────▼─────────────────────────────────────┐
│                    DATA PERSISTENCE LAYER                         │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────┐  ┌──────────────────────┐             │
│  │  MongoDB             │  │  FAISS Vector DB     │             │
│  ├──────────────────────┤  ├──────────────────────┤             │
│  │ Collections:         │  │ - Indexed Vectors    │             │
│  │ - users              │  │ - Fast Similarity    │             │
│  │ - notes              │  │   Search             │             │
│  │ - chat_messages      │  │ - Approximate NNS    │             │
│  │ - flashcards         │  └──────────────────────┘             │
│  └──────────────────────┘                                       │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────▼─────────────────────────────────────┐
│                  EXTERNAL API INTEGRATIONS                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Groq LLM     │  │ YouTube      │  │ HuggingFace  │          │
│  │ API          │  │ API          │  │ Models       │          │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤          │
│  │ - Summarize  │  │ - Fetch      │  │ - Generate   │          │
│  │ - Chat/Q&A   │  │   Transcript │  │   Embeddings │          │
│  │ - Flashcard  │  │ - Extract    │  │              │          │
│  │   Generation │  │   Captions   │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ System Requirements

### Minimum Hardware
- **Processor**: Intel i5/AMD Ryzen 5 (4-cores)
- **RAM**: 8GB (16GB+ recommended)
- **Storage**: 5GB free space
- **GPU**: Optional (NVIDIA RTX 3060+ for best performance)

### Software Requirements
- **Python**: 3.10+ with pip
- **Node.js**: 18.0+ with npm
- **MongoDB**: 5.0+ (local or Atlas)
- **Git**: 2.30+
- **CUDA**: 12.1 (optional, for GPU)

### Browser Support
- Chrome/Chromium 90+
- Firefox 88+
- Safari 14+
- Edge 90+

---

## 📦 Prerequisites & API Keys

Before starting, you'll need:

1. **Groq API Key**
   - Visit https://console.groq.com
   - Sign up/Login
   - Create API key
   
2. **MongoDB Connection String**
   - Local: `mongodb://localhost:27017`
   - Cloud: Use MongoDB Atlas (free tier)
   
3. **Firebase Configuration**
   - Create project at https://firebase.google.com
   - Enable Authentication (Email/Password)
   - Generate web credentials
   
4. **YouTube API** (for transcript extraction)
   - Automatically used via free YouTube API

---

## 🚀 Installation & Setup

### Phase 1: Clone Repository

```bash
git clone https://github.com/Sahil1607cms/SmartNotes.git
cd SmartNotes
```

### Phase 2: Backend Setup

```bash
# Navigate to backend
cd backend

# Create Python virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Verify Python version
python --version  # Should be 3.10+

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

**Expected Installation Time**: 15-30 minutes (PyTorch is large)

### Phase 3: Backend Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
# Windows:
notepad .env
# macOS/Linux:
nano .env
```

**Required .env values:**
```env
GROQ_API_KEY=your_groq_key_here
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=notesDB
ENVIRONMENT=development
DEBUG=True
```

### Phase 4: Frontend Setup

```bash
# Navigate to frontend
cd ../frontend

# Install Node dependencies
npm install

# Note: If npm install fails, try:
npm install --legacy-peer-deps
```

**Expected Installation Time**: 5-10 minutes

### Phase 5: Firebase Configuration

Edit `frontend/src/firebase.js`:

```javascript
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_AUTH_DOMAIN",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_STORAGE_BUCKET",
  messagingSenderId: "YOUR_SENDER_ID",
  appId: "YOUR_APP_ID",
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
```

### Phase 6: Verify Installation

```bash
# Test backend imports
cd backend
python -c "import fastapi; import torch; import langchain; print('✓ All imports successful')"

# Check GPU availability
python -c "import torch; print(f'GPU Available: {torch.cuda.is_available()}')"

# Test MongoDB connection
python -c "from pymongo import MongoClient; client = MongoClient('mongodb://localhost:27017'); print('✓ MongoDB Connected')"
```

### Phase 7: Run Application

**Terminal 1 - Backend:**
```bash
cd backend
.venv\Scripts\activate  # Windows
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Press CTRL+C to quit
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Expected output:
```
VITE v5.0.0  ready in 234 ms
➜  Local:   http://localhost:5173/
```

### Access Application

- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs (Swagger)
- **API ReDoc**: http://localhost:8000/redoc

---

## 🗄️ Database Design

### MongoDB Collections Schema

#### Users Collection
```javascript
{
  _id: ObjectId,
  uid: String,              // Firebase UID
  email: String,            // User email
  displayName: String,      // Display name
  photoURL: String,         // Avatar URL
  createdAt: Date,          // Account creation
  lastLogin: Date,          // Last login timestamp
  preferences: {
    darkMode: Boolean,
    notifications: Boolean,
    language: String
  }
}
```

#### Notes Collection
```javascript
{
  _id: ObjectId,
  userId: String,           // Foreign key to users
  title: String,            // Note title
  content: String,          // Full content/summary
  summary: String,          // AI-generated summary
  source: String,           // "youtube" | "pdf" | "media"
  sourceUrl: String,        // Original content URL
  sourceMetadata: {
    videoId: String,        // For YouTube videos
    duration: Number,
    thumbnail: String,
    channelName: String
  },
  tokens: Number,           // Token count (for billing)
  tags: [String],           // User tags
  isPublic: Boolean,        // Share with others
  createdAt: Date,
  updatedAt: Date,
  expiresAt: Date           // Auto-delete after period
}
```

#### ChatMessages Collection
```javascript
{
  _id: ObjectId,
  noteId: String,           // Foreign key to notes
  userId: String,           // Foreign key to users
  conversationId: String,   // Group messages by conversation
  role: String,             // "user" | "assistant"
  question: String,         // User's question
  answer: String,           // Assistant's answer
  context: String,          // Retrieved context chunks
  confidenceScore: Float,   // Relevance score (0-1)
  embedding: [Float],       // Vector embedding of question
  metadata: {
    model: String,          // LLM model used
    tokens: {
      prompt: Number,
      completion: Number,
      total: Number
    },
    latency: Number         // Response time in ms
  },
  timestamp: Date,
  isUseful: Boolean         // User feedback
}
```

#### Flashcards Collection
```javascript
{
  _id: ObjectId,
  noteId: String,           // Foreign key to notes
  userId: String,           // Foreign key to users
  title: String,            // Flashcard set title
  cards: [
    {
      _id: ObjectId,
      question: String,
      answer: String,
      difficulty: String    // "easy" | "medium" | "hard"
    }
  ],
  totalCards: Number,
  difficulty: String,       // Overall difficulty
  createdAt: Date,
  updatedAt: Date,
  stats: {
    timesReviewed: Number,
    correctAnswers: Number,
    mastered: Boolean
  }
}
```

#### Embeddings Collection
```javascript
{
  _id: ObjectId,
  noteId: String,           // Foreign key to notes
  userId: String,
  chunkIndex: Number,       // Order in document
  text: String,             // Original text chunk (512 tokens)
  vector: [Float],          // 384-dim embedding (MiniLM)
  metadata: {
    source: String,
    pageNumber: Number,     // For PDFs
    startTime: Number,      // For videos
    chunkLength: Number
  },
  createdAt: Date
}
```

### FAISS Vector Index Structure

```
index.faiss
├── Vectors: [N, 384]        // N embeddings, 384 dimensions
├── IVF Config:
│   ├── nlist: 100           // Cluster count
│   ├── nprobe: 10           // Search clusters
│   └── metric: L2           // Euclidean distance
├── Mapping:
│   └── vector_id → mongo_id // Link to MongoDB
└── Metadata:
    ├── created_date: Date
    ├── total_vectors: N
    └── embedding_model: "sentence-transformers/all-MiniLM-L6-v2"
```

---

## 🔌 API Documentation

### Authentication Endpoints

#### POST `/auth/register`
Register new user
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "displayName": "John Doe"
  }'
```

#### POST `/auth/login`
Login user
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

### YouTube Summarization Endpoints

#### POST `/summarize-yt`
Summarize YouTube video
```bash
curl -X POST "http://localhost:8000/summarize-yt" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "userId": "user_id_here"
  }'
```

**Response:**
```json
{
  "_id": "note_id",
  "title": "Video Title",
  "summary": "AI-generated summary...",
  "source": "youtube",
  "sourceMetadata": {
    "videoId": "dQw4w9WgXcQ",
    "duration": 3600,
    "channelName": "Channel Name"
  },
  "createdAt": "2024-05-06T10:30:00Z"
}
```

#### GET `/transcript`
Get YouTube transcript only
```bash
curl -X GET "http://localhost:8000/transcript?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Notes Endpoints

#### GET `/notes`
Get all user notes
```bash
curl -X GET "http://localhost:8000/notes?userId=user_id&limit=10&offset=0" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**
```json
{
  "total": 45,
  "notes": [
    {
      "_id": "note_id",
      "title": "Note Title",
      "summary": "Summary preview...",
      "source": "youtube",
      "createdAt": "2024-05-06T10:30:00Z"
    }
  ]
}
```

#### DELETE `/notes/{noteId}`
Delete a note
```bash
curl -X DELETE "http://localhost:8000/notes/note_id" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Chat Endpoints

#### POST `/chat`
Chat with RAG
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "noteId": "note_id",
    "userId": "user_id",
    "question": "What were the main points discussed?",
    "conversationId": "conv_123"
  }'
```

**Response (Streaming):**
```json
{
  "answer": "The main points were...",
  "context": "Retrieved relevant chunks...",
  "confidenceScore": 0.92,
  "metadata": {
    "model": "llama-3.1-8b-instant",
    "tokens": {
      "prompt": 512,
      "completion": 256,
      "total": 768
    },
    "latency": 1245
  }
}
```

#### GET `/prompts`
Get suggested prompts for note
```bash
curl -X GET "http://localhost:8000/prompts?noteId=note_id" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**
```json
{
  "prompts": [
    "What were the main topics covered?",
    "Summarize the key takeaways",
    "What questions would a student ask about this?"
  ]
}
```

### Flashcard Endpoints

#### POST `/flashcards/generate`
Generate flashcards from note
```bash
curl -X POST "http://localhost:8000/flashcards/generate" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "noteId": "note_id",
    "userId": "user_id",
    "difficulty": "medium",
    "count": 10
  }'
```

**Response:**
```json
{
  "_id": "flashcard_set_id",
  "title": "Generated Flashcards",
  "totalCards": 10,
  "cards": [
    {
      "_id": "card_1",
      "question": "What is...?",
      "answer": "The answer is...",
      "difficulty": "medium"
    }
  ],
  "createdAt": "2024-05-06T10:30:00Z"
}
```

#### GET `/flashcards/{noteId}`
Get flashcards for note
```bash
curl -X GET "http://localhost:8000/flashcards/note_id" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 🧩 Component Details

### Backend Services

#### YT_summarizer.py
Handles YouTube video processing:
- Fetch video metadata from YouTube
- Extract transcript using yt-dlp or YouTube API
- Clean and preprocess text
- Generate summary using Groq LLM
- Create embeddings for RAG

```python
class YouTubeSummarizer:
    def __init__(self, groq_key: str):
        self.llm = Groq(api_key=groq_key)
    
    async def summarize(self, url: str) -> SummaryResponse:
        # 1. Validate URL
        # 2. Fetch transcript
        # 3. Summarize with LLM
        # 4. Generate embeddings
        # 5. Store in databases
```

#### chat_service.py (RAG Implementation)
Implements Retrieval-Augmented Generation:
- Query embedding generation
- FAISS index search for relevant chunks
- Prompt engineering with context
- LLM response generation
- Conversation history management

```python
class RAGChat:
    def __init__(self, faiss_index, llm, mongo_db):
        self.index = faiss_index
        self.llm = llm
        self.db = mongo_db
    
    async def answer_question(self, question: str, note_id: str) -> Answer:
        # 1. Generate query embedding
        # 2. Search FAISS for top-k chunks
        # 3. Build augmented prompt
        # 4. Generate response
        # 5. Store conversation
```

#### flashcard_service.py
Generates study flashcards:
- Extract key concepts from summary
- Generate Q&A pairs using LLM
- Format as flashcard objects
- Store and retrieve flashcards

```python
class FlashcardGenerator:
    async def generate(self, summary: str, difficulty: str) -> Flashcards:
        # 1. Identify key concepts
        # 2. Generate questions
        # 3. Generate answers
        # 4. Set difficulty levels
        # 5. Return formatted flashcards
```

### Frontend Components

#### YoutubeSummarizer.jsx
YouTube video summarization UI:
- URL input with validation
- YouTube metadata preview
- Loading states with progress
- Display summary with formatting
- Copy/Share options

#### ChatAssistant.jsx
Chat interface with RAG:
- Message input with suggestions
- Message history display
- Streaming response rendering
- Context highlighting
- Export conversation

#### Flashcards.jsx
Flashcard review component:
- Card flip animation
- Progress tracking
- Difficulty selector
- Study statistics
- Export/Print options

#### History.jsx
Notes management page:
- Paginated note list
- Search and filter
- Sort options (date, title, source)
- Quick preview
- Bulk actions

---

## 🔄 Data Flow

### Complete User Journey: YouTube → Summary → Chat → Flashcards

```
1. USER ACTIONS
   ├─ Enter YouTube URL
   │  └─> Click "Summarize"
   │
   ├─ Review Summary
   │  └─> Click "Ask Question"
   │
   ├─ Chat with Content
   │  └─> Get AI Answers
   │
   └─ Generate Flashcards
      └─> Study & Review

2. FRONTEND PROCESSING
   ├─ Validate URL format
   ├─ Show loading spinner
   ├─ Send HTTP request to backend
   ├─ Handle streaming responses
   ├─ Update UI with results
   └─ Cache in local state

3. BACKEND PROCESSING (Summarize)
   ├─ Receive POST /summarize-yt
   ├─ Authenticate user (Firebase JWT)
   ├─ Fetch YouTube transcript
   ├─ Preprocess & chunk text
   ├─ Send to Groq LLM
   ├─ Receive summary
   ├─ Generate embeddings (HuggingFace)
   ├─ Store in MongoDB
   ├─ Index in FAISS
   └─ Return to frontend

4. RAG SETUP
   ├─ Summary chunks in FAISS
   ├─ Full metadata in MongoDB
   ├─ Embeddings mapped to vectors
   └─ Ready for queries

5. CHAT FLOW (Per Question)
   ├─ User asks question
   ├─ Frontend sends to POST /chat
   ├─ Backend generates query embedding
   ├─ Search FAISS (similarity search)
   ├─ Retrieve top-3 relevant chunks
   ├─ Build prompt: [Context] + [Question]
   ├─ Stream response from Groq LLM
   ├─ Store Q&A pair in MongoDB
   └─ Display answer in frontend

6. FLASHCARD GENERATION
   ├─ User clicks "Generate Flashcards"
   ├─ Backend receives summary
   ├─ LLM extracts key concepts
   ├─ LLM generates Q&A pairs
   ├─ Format as flashcard objects
   ├─ Store in MongoDB
   └─ Display in frontend

7. PERSISTENCE
   ├─ All data stored in MongoDB
   ├─ Vectors indexed in FAISS
   ├─ User can retrieve anytime
   ├─ Search across all notes
   └─ Continue conversations
```

---

## ⚙️ Configuration

### Environment Variables (.env)

```env
# REQUIRED - LLM Configuration
GROQ_API_KEY=gsk_xxxxxxxxxxxxx

# REQUIRED - Database Configuration
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/notesDB
MONGODB_DB_NAME=notesDB

# OPTIONAL - Application Settings
ENVIRONMENT=development              # development or production
DEBUG=True                           # Enable debug logging
LOG_LEVEL=INFO                       # DEBUG, INFO, WARNING, ERROR

# OPTIONAL - LLM Model Settings
LLM_MODEL=llama-3.1-8b-instant      # Groq model to use
MAX_TOKENS=1000                      # Max response tokens
TEMPERATURE=0.7                      # Response randomness (0-1)

# OPTIONAL - GPU Settings
USE_GPU=True                         # Enable GPU acceleration
CUDA_DEVICE=auto                     # auto, cuda:0, cuda:1, etc.

# OPTIONAL - Embeddings Settings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
CHUNK_SIZE=800                       # Tokens per chunk
CHUNK_OVERLAP=150                    # Overlap between chunks

# OPTIONAL - Vector Search Settings
FAISS_SEARCH_K=3                     # Top-k results
SIMILARITY_THRESHOLD=0.5             # Min similarity score

# OPTIONAL - File Upload Settings
MAX_FILE_SIZE_MB=100
ALLOWED_EXTENSIONS=pdf,txt,docx

# OPTIONAL - CORS Settings
ALLOWED_ORIGINS=http://localhost:5173,https://example.com

# OPTIONAL - Security
JWT_SECRET=your_secret_key
JWT_EXPIRATION_HOURS=24

# OPTIONAL - API Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600               # Per hour
```

### Docker Setup (Optional)

**Dockerfile for Backend:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV ENVIRONMENT=production
ENV DEBUG=False

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
      - MONGODB_URI=mongodb://mongodb:27017
      - ENVIRONMENT=production
    depends_on:
      - mongodb

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    depends_on:
      - backend

  mongodb:
    image: mongo:latest
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db

volumes:
  mongodb_data:
```

---

## 🔧 Troubleshooting

### Common Issues & Solutions

#### MongoDB Connection Errors

**Error**: `[SSL: CERTIFICATE_VERIFY_FAILED]`
```
Solution:
1. Verify your system date/time is correct
2. Windows: Settings > Date & Time > Sync now
3. Restart MongoDB connection
4. Or disable SSL: mongodb://user:pass@host/?ssl=false
```

**Error**: `Connection refused: localhost:27017`
```
Solution:
1. Start MongoDB service:
   Windows: net start MongoDB
   macOS: brew services start mongodb-community
   Linux: sudo systemctl start mongod
2. Verify MongoDB is running: mongosh
```

#### Python Virtual Environment Issues

**Error**: `'python' is not recognized`
```
Solution:
1. Ensure Python is installed: python --version
2. Add Python to PATH (Windows)
3. Use full path: C:\Python310\python.exe
```

**Error**: `.venv/Scripts/activate` doesn't work
```
Solution:
1. Delete .venv: rmdir .venv /s /q
2. Recreate: python -m venv .venv
3. Activate: .venv\Scripts\activate
```

#### PyTorch/CUDA Issues

**Error**: `RuntimeError: No CUDA devices found`
```
Solution:
1. Check NVIDIA drivers: nvidia-smi
2. Update drivers from nvidia.com
3. Reinstall PyTorch with correct CUDA version:
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

#### Port Already in Use

**Error**: `OSError: [Errno 48] Address already in use`
```
Solution for Windows:
1. Find process: netstat -ano | findstr :8000
2. Kill process: taskkill /PID <PID> /F

Solution for macOS/Linux:
1. Find process: lsof -i :8000
2. Kill process: kill -9 <PID>

Or use different port:
uvicorn main:app --port 8001
```

#### Firebase Authentication Issues

**Error**: `FirebaseError: auth/invalid-api-key`
```
Solution:
1. Verify firebase.js credentials
2. Check all required fields are present
3. Regenerate credentials from Firebase Console
4. Ensure CORS is configured
```

---

## 📈 Performance Optimization

### Backend Optimization

#### 1. GPU Acceleration
```python
# Automatically enabled if CUDA available
import torch
if torch.cuda.is_available():
    device = torch.device("cuda")
    model = model.to(device)
```

#### 2. Caching Strategy
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_embedding_model():
    # Load model once, reuse
    return SentenceTransformer('all-MiniLM-L6-v2')
```

#### 3. Batch Processing
```python
# Process multiple documents efficiently
embeddings = model.encode(texts, batch_size=32, show_progress_bar=True)
```

#### 4. Database Indexing
```javascript
// MongoDB indexes
db.notes.createIndex({ userId: 1, createdAt: -1 })
db.embeddings.createIndex({ noteId: 1 })
db.chat_messages.createIndex({ noteId: 1, timestamp: -1 })
```

#### 5. Vector Search Optimization
```python
# FAISS configuration for fast search
faiss.faiss.ivf_flat(dimension, nlist=100, metric_type=faiss.METRIC_L2)
# nprobe=10 for accuracy/speed trade-off
index.nprobe = 10
```

### Frontend Optimization

#### 1. Code Splitting
```javascript
// React Router lazy loading
const YoutubeSummarizer = React.lazy(() => import('./pages/YoutubeSummarizer'))
```

#### 2. Memoization
```javascript
const MemoizedChatMessage = React.memo(({ message }) => ...)
```

#### 3. Virtual Scrolling (Large Lists)
```javascript
import { FixedSizeList } from 'react-window'
```

#### 4. Image Optimization
```javascript
// Use webp with fallback
<picture>
  <source srcSet="image.webp" type="image/webp" />
  <img src="image.jpg" />
</picture>
```

---

## 🚢 Deployment

### Deploy Backend (Railway.app)

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize
railway init

# Deploy
railway up
```

### Deploy Backend (Render.com)

1. Push code to GitHub
2. Connect Render to GitHub
3. Create Web Service
4. Set environment variables
5. Deploy

### Deploy Frontend (Vercel)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Deploy Frontend (Netlify)

```bash
# Build production
npm run build

# Deploy
netlify deploy --prod --dir=dist
```

---

## 📞 Support & Contributing

For issues, questions, or feature requests:
1. Check existing [GitHub Issues](https://github.com/Sahil1607cms/SmartNotes/issues)
2. Create detailed issue with:
   - OS and Python version
   - Error message and stacktrace
   - Steps to reproduce
   - Expected vs actual behavior

### Contributing

1. Fork repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing-feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

---

## 📝 License & Attribution

This project is licensed under the MIT License - see LICENSE file

### Acknowledgments
- **Groq AI** - Ultra-fast LLM inference
- **LangChain** - LLM application framework
- **FastAPI** - Modern Python web framework
- **React** - UI library
- **Firebase** - Authentication & cloud platform
- **MongoDB** - NoSQL database
- **HuggingFace** - Pre-trained models
- **FAISS** - Vector similarity search

---

**Version**: 1.0.0  
**Last Updated**: May 2026  
**Status**: ✅ Active Development  
**Maintainer**: [@Sahil1607cms](https://github.com/Sahil1607cms)

---

## 🚀 Installation & Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/Sahil1607cms/SmartNotes.git
cd SmartNotes
```

### Step 2: Backend Setup (Python)

#### 2.1 Create Virtual Environment

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (Python 3.10+)
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

**Verify virtual environment activation:**
```bash
python --version  # Should show Python 3.10+
pip --version    # Should show version from .venv
```

#### 2.2 Install Python Dependencies

```bash
# Ensure pip is up to date
python -m pip install --upgrade pip

# Install required packages
pip install -r requirements.txt
```

**Key Python Package Versions (from requirements.txt):**
- `fastapi==0.121.2` - API framework
- `uvicorn==0.38.0` - ASGI server
- `pymongo==4.15.4` - MongoDB driver
- `langchain==1.0.7` - LLM framework
- `langchain-groq==1.0.1` - Groq integration
- `torch==2.5.1+cu121` - PyTorch (CUDA 12.1)
- `torchaudio==2.5.1+cu121` - Audio processing
- `faster-whisper==1.2.1` - Speech-to-text
- `langchain-huggingface` - HuggingFace embeddings
- `langchain-community==0.4.1` - Vector stores (FAISS)
- `pypdf==6.3.0` - PDF processing
- `python-multipart==0.0.20` - File upload support

**Installation Time**: ~15-30 minutes (includes PyTorch, requires patience)

#### 2.3 Environment Configuration

Create a `.env` file in the `backend` directory:

```bash
# Copy the example file
cp .env.example .env

# Or create manually:
touch .env
```

Edit the `.env` file with your configuration:

```env
# Required - Get from https://console.groq.com/keys
GROQ_API_KEY=your_groq_api_key_here

# MongoDB Configuration
# Local: mongodb://localhost:27017
# Cloud: mongodb+srv://username:password@cluster.mongodb.net/notesDB
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=notesDB

# Optional - For development
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO

# Optional - LLM Configuration
LLM_MODEL=llama-3.1-8b-instant
MAX_TOKENS=1000
TEMPERATURE=0.7

# Optional - GPU Configuration
USE_GPU=True
CUDA_DEVICE=auto
```

**Complete `.env.example` file included in the project** - This template contains all possible configuration options with detailed comments.

**Key configuration values:**
- `GROQ_API_KEY`: Get from https://console.groq.com/keys
- `MONGODB_URI`: Local or MongoDB Atlas connection string
  - **Local**: `mongodb://localhost:27017`
  - **Atlas**: `mongodb+srv://<username>:<password>@<cluster>.mongodb.net/notesDB?retryWrites=true&w=majority`

#### 2.4 Verify Backend Setup

```bash
# Test imports
python -c "import fastapi; import torch; import langchain; print('✓ All imports successful')"

# Check PyTorch/CUDA
python -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}')"
```

### Step 3: Frontend Setup (Node.js/React)

#### 3.1 Navigate to Frontend Directory

```bash
cd ../frontend
```

#### 3.2 Install Node Dependencies

```bash
# Install npm packages
npm install
```

**Key Node Package Versions (from package.json):**
- `react==^19.1.1` - React framework
- `react-dom==^19.1.1` - React DOM
- `react-router-dom==^7.9.1` - Routing
- `firebase==^12.3.0` - Authentication
- `vite==^5.0.0` - Build tool
- `tailwindcss==^4.1.13` - Styling
- `lucide-react==^0.544.0` - Icons
- `react-markdown==^10.1.0` - Markdown rendering

**Installation Time**: ~5 minutes

#### 3.3 Firebase Configuration

Create a `firebase.js` file in `frontend/src/`:

```javascript
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: "YOUR_FIREBASE_API_KEY",
  authDomain: "YOUR_FIREBASE_AUTH_DOMAIN",
  projectId: "YOUR_FIREBASE_PROJECT_ID",
  storageBucket: "YOUR_FIREBASE_STORAGE_BUCKET",
  messagingSenderId: "YOUR_FIREBASE_MESSAGING_SENDER_ID",
  appId: "YOUR_FIREBASE_APP_ID",
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
```

**Note**: The `firebase.js` file should already exist. Update it with your Firebase credentials from https://firebase.google.com/console

---

## 🗄️ Database Setup

### MongoDB Local Installation (Optional)

If using local MongoDB:

```bash
# Windows - using Chocolatey (admin required)
choco install mongodb

# macOS - using Homebrew
brew tap mongodb/brew
brew install mongodb-community

# Linux - Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y mongodb

# Start MongoDB service
# Windows:
net start MongoDB
# macOS:
brew services start mongodb-community
# Linux:
sudo systemctl start mongod
```

### MongoDB Atlas (Cloud - Recommended)

1. Visit https://www.mongodb.com/cloud/atlas
2. Create a free account
3. Create a cluster
4. Get connection string: `mongodb+srv://<username>:<password>@<cluster>.mongodb.net/notesDB`
5. Update `MONGODB_URI` in `.env`

---

## ▶️ Running the Application

### Terminal 1: Start Backend Server

```bash
cd backend

# Activate virtual environment (if not already active)
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Run the FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Press CTRL+C to quit
INFO:     Started server process [12345]
```

### Terminal 2: Start Frontend Development Server

```bash
cd frontend

# Start Vite development server
npm run dev
```

Expected output:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

### Access the Application

- **Frontend**: Open http://localhost:5173 in your browser
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **API ReDoc**: http://localhost:8000/redoc

---

## 📁 Project Structure

```
SmartNotes/
├── backend/
│   ├── main.py                          # FastAPI application entry point
│   ├── requirements.txt                 # Python dependencies
│   ├── .env                            # Environment variables (create this)
│   ├── .venv/                          # Virtual environment (auto-created)
│   ├── database/
│   │   ├── config.py                   # MongoDB connection config
│   │   ├── crud.py                     # Database CRUD operations
│   │   ├── historySchema.py            # Pydantic models
│   │   └── vectorstore/
│   │       └── index.faiss             # FAISS vector database
│   ├── routes/
│   │   ├── chat_routes.py              # Chat endpoints
│   │   ├── flashcard_routes.py         # Flashcard endpoints
│   │   ├── media_routes.py             # Media endpoints
│   │   ├── notes_routes.py             # Notes endpoints
│   │   ├── pdf_routes.py               # PDF endpoints
│   │   ├── prompt_routes.py            # Prompt endpoints
│   │   └── youtube_routes.py           # YouTube endpoints
│   ├── services/
│   │   ├── YT_summarizer.py            # YouTube summarization
│   │   ├── PDF_summarizer.py           # PDF summarization
│   │   ├── Media_summarizer.py         # Audio/Video summarization
│   │   └── media_summariser/
│   │       ├── embed.py                # Embedding creation
│   │       ├── groqs.py                # Groq LLM interface
│   │       ├── process_media.py        # Media processing
│   │       └── ragvideo2.py            # RAG implementation
│   └── utils/
│       ├── pdf_loader.py               # PDF utilities
│       ├── youtube_transcript.py       # YouTube API utilities
│       └── check_gpu.py                # GPU detection
│
├── frontend/
│   ├── package.json                    # Node dependencies
│   ├── vite.config.js                  # Vite configuration
│   ├── index.html                      # HTML entry point
│   ├── src/
│   │   ├── main.jsx                    # React entry point
│   │   ├── App.jsx                     # Main App component
│   │   ├── firebase.js                 # Firebase configuration
│   │   ├── components/
│   │   │   ├── ChatAssistant.jsx       # Chat interface
│   │   │   ├── Flashcards.jsx          # Flashcard display
│   │   │   ├── Navbar.jsx              # Navigation bar
│   │   │   ├── Sidebar.jsx             # Sidebar navigation
│   │   │   └── ...other components
│   │   ├── pages/
│   │   │   ├── History.jsx             # Note history page
│   │   │   ├── YoutubeSummarizer.jsx   # YouTube page
│   │   │   ├── PdfTextSummarizer.jsx   # PDF page
│   │   │   ├── AudioVideoSummarizer.jsx # Media page
│   │   │   ├── Login.jsx               # Login page
│   │   │   └── ...other pages
│   │   ├── context/
│   │   │   └── AuthContext.jsx         # Auth context
│   │   └── assets/                     # Static assets
│   └── node_modules/                   # Dependencies (auto-created)
│
└── README.md                           # This file
```

---

## 🧪 Testing the Application

### Test Backend API

```bash
# Get all notes for a user (replace USER_ID)
curl -X GET "http://localhost:8000/notes/?user_id=YOUR_USER_ID"

# Get Swagger documentation
open http://localhost:8000/docs
```

### Test Frontend Components

1. **Login**: Create Firebase account and sign in
2. **YouTube Summarizer**: Paste a YouTube URL with captions
3. **PDF Summarizer**: Upload a PDF file
4. **Audio/Video Summarizer**: Upload an audio or video file
5. **Chat**: Ask questions about the summary
6. **Flashcards**: View generated study cards
7. **History**: Browse and manage saved notes

---

## 🔧 Troubleshooting

### Python Virtual Environment Issues

```bash
# If venv fails to activate:
# Windows - Try long path:
C:\Users\YourUsername\SmartNotes\backend\.venv\Scripts\activate

# Delete and recreate venv:
rmdir .venv /s /q
python -m venv .venv
.venv\Scripts\activate
```

### PyTorch/CUDA Installation Issues

```bash
# If torch installation is slow, pre-install CPU version:
pip install torch torchvision torchaudio

# For GPU (NVIDIA CUDA 12.1):
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### MongoDB Connection Issues

```bash
# Check if MongoDB is running
# Windows:
tasklist | findstr mongod

# macOS:
ps aux | grep mongod

# Test connection string
python -c "from pymongo import MongoClient; client = MongoClient('YOUR_CONNECTION_STRING'); print('Connected!')"
```

### Port Already in Use

```bash
# If port 8000 is busy (backend)
uvicorn main:app --reload --port 8001

# If port 5173 is busy (frontend)
npm run dev -- --port 5174
```

### Firebase Configuration Issues

```bash
# Verify firebase.js configuration
# Check that all required fields are present:
# - apiKey
# - authDomain
# - projectId
# - storageBucket
# - messagingSenderId
# - appId
```

### Memory Issues During Installation

```bash
# If npm install fails with memory error:
npm install --legacy-peer-deps

# For pip, install packages one by one:
pip install fastapi
pip install uvicorn
# Continue with other packages
```

---

## 📊 Performance Optimization

### GPU Acceleration

The application automatically detects and uses GPU if available:

```bash
# Check GPU status
python backend/check_gpu.py
```

Output for NVIDIA GPU:
```
✓ GPU Available: True
✓ GPU Model: NVIDIA GeForce RTX 3090
✓ CUDA Version: 12.1
✓ Memory: 24GB
```

### Optimize Embedding Generation

- **Batch Processing**: Large documents are automatically chunked (800 tokens, 150 overlap)
- **Caching**: Embeddings are cached in FAISS
- **Model Selection**: Uses `sentence-transformers/all-MiniLM-L6-v2` (lightweight, fast)

---

## 📝 Environment Configuration (.env File)

### Using .env.example Template

A complete `.env.example` file is provided with all configuration options:

```bash
# Copy the template
cp backend/.env.example backend/.env

# Edit with your values
nano backend/.env  # or use your preferred editor
```

### Essential .env Variables

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | ✅ Yes | `gsk_abc123...` | Groq API key from https://console.groq.com |
| `MONGODB_URI` | ✅ Yes | `mongodb://localhost:27017` | MongoDB connection string |
| `MONGODB_DB_NAME` | ✅ Yes | `notesDB` | Database name |
| `ENVIRONMENT` | ❌ No | `development` | App environment (development/production) |
| `DEBUG` | ❌ No | `True` | Enable debug logging |
| `LLM_MODEL` | ❌ No | `llama-3.1-8b-instant` | Groq model to use |
| `USE_GPU` | ❌ No | `True` | Enable GPU acceleration |

### MongoDB Connection Strings

**Local MongoDB:**
```env
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=notesDB
```

**MongoDB Atlas (Cloud):**
```env
MONGODB_URI=mongodb+srv://username:password@cluster-name.mongodb.net/notesDB?retryWrites=true&w=majority
MONGODB_DB_NAME=notesDB
```

Replace:
- `username`: Your MongoDB Atlas username
- `password`: Your MongoDB Atlas password  
- `cluster-name`: Your cluster name (e.g., `cluster0`)

### Optional Configuration

Full `.env.example` includes optional settings for:
- **CORS**: `ALLOWED_ORIGINS` - Frontend URLs allowed to call backend
- **File Upload**: `MAX_FILE_SIZE_MB`, `ALLOWED_EXTENSIONS`
- **LLM**: `MAX_TOKENS`, `TEMPERATURE` - Model behavior tuning
- **Embeddings**: `CHUNK_SIZE`, `CHUNK_OVERLAP` - Text processing
- **GPU**: `CUDA_DEVICE` - Specific GPU device selection
- **Logging**: `LOG_LEVEL`, `LOG_REQUESTS` - Detailed logging

### Security Best Practices

```bash
# 1. Never commit .env to git
echo ".env" >> .gitignore

# 2. Use .env.example for git
git add backend/.env.example
git add backend/.gitignore

# 3. For production, use environment variables
export GROQ_API_KEY="your_key_here"
export MONGODB_URI="your_connection_string"

# 4. Keep sensitive values secure
# - Use strong API keys
# - Rotate keys regularly
# - Use MongoDB IP whitelisting for Atlas
# - Enable MongoDB user authentication
```

---

## 📊 Performance Optimization

---

## 📍 Quick Reference

### API Endpoints

### Notes
- `GET /notes/?user_id={id}` - Get all notes for user
- `DELETE /notes/{note_id}` - Delete a note

### Summarization
- `POST /summarize-yt` - Summarize YouTube video
- `POST /summarize-pdf` - Summarize PDF document
- `POST /summarize-media` - Summarize audio/video file

### Chat & Flashcards
- `POST /chat` - Chat with RAG
- `POST /prompts` - Generate suggested prompts
- `POST /summarize-flashcard` - Generate flashcards

### Transcripts
- `GET /transcript/?url={url}` - Get YouTube transcript

---

## ⚙️ Configuration Reference

See **[Environment Configuration (.env File)](#-environment-configuration-env-file)** section above for:
- Complete `.env.example` template
- Required vs optional variables
- MongoDB connection strings
- Security best practices
- Development vs production setup

---

## 🚢 Deployment Guide

### Deploy Backend (FastAPI)

**Option 1: Heroku**
```bash
heroku login
heroku create your-app-name
git push heroku main
```

**Option 2: Railway**
```bash
npm i -g @railway/cli
railway login
railway init
railway up
```

### Deploy Frontend (React/Vite)

**Option 1: Vercel**
```bash
npm install -g vercel
vercel
```

**Option 2: Netlify**
```bash
npm install -g netlify-cli
netlify deploy
```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 👨‍💻 Author

**Sahil** - [@Sahil1607cms](https://github.com/Sahil1607cms)

---

## 🙏 Acknowledgments

- **Groq API** - Fast LLM inference
- **LangChain** - LLM orchestration
- **FastAPI** - Modern Python web framework
- **React** - Frontend framework
- **Firebase** - Authentication service
- **MongoDB** - Database
- **FAISS** - Vector search
- **Hugging Face** - Embeddings and models

---

## 📞 Support

For issues, questions, or suggestions:
1. Check existing GitHub issues
2. Create a new issue with detailed description
3. Include your environment details (Python version, OS, etc.)

---

## 🔄 Version History

- **v1.0.0** - Initial release
  - YouTube summarization
  - PDF processing
  - Audio/Video summarization
  - Chat with RAG
  - Flashcard generation
  - Note history management

---

**Last Updated**: December 2025  
**Status**: ✅ Active Development

## Backend Requirements
See [Backend requirements (backend/requirements.txt)](README_BACKEND_REQUIREMENTS.md)


