# SmartNotes - Intelligent Content Summarization & RAG Platform

## 📋 Project Overview

**SmartNotes** is an intelligent note-taking and content summarization platform that uses AI-powered Retrieval-Augmented Generation (RAG) to help users efficiently process and interact with various forms of media content.

### Key Features
- 📹 **YouTube Summarization**: Extract and summarize video transcripts
- 📄 **PDF Processing**: Upload and summarize PDF documents
- 🎵 **Audio/Video Summarization**: Process audio and video files
- 📊 **Live Meeting Transcription**: Transcribe and summarize meetings
- 🤖 **AI Chat Assistant**: Ask questions about your content using RAG
- 📚 **Flashcard Generation**: Create study flashcards from summaries
- 💾 **History Management**: Save, search, and manage all your notes
- 🔐 **Firebase Authentication**: Secure user authentication

---

## 🛠️ System Requirements

### Minimum Requirements
- **OS**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **RAM**: 8GB (16GB+ recommended for faster processing)
- **Storage**: 5GB free space minimum
- **GPU**: Optional (NVIDIA GPU with CUDA support recommended for faster embeddings)

### Software Requirements
- **Python**: 3.10 or higher
- **Node.js**: 18.0 or higher
- **npm**: 9.0 or higher
- **MongoDB**: Local or remote instance (Atlas free tier supported)
- **Git**: For version control

---

## 📦 Prerequisites & API Keys

Before starting, gather these API credentials:

1. **Groq API Key** - For LLM operations
   - Sign up at https://console.groq.com
   - Generate API key

2. **MongoDB Connection String**
   - Local: `mongodb://localhost:27017`
   - Cloud: MongoDB Atlas (free tier available)

3. **Firebase Configuration**
   - Create a Firebase project at https://firebase.google.com
   - Generate web configuration credentials

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

**Last Updated**: December 2024  
**Status**: ✅ Active Development

