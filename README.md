# Jarvis - Multi-Modal AI Assistant

## Overview

Jarvis is a **sovereign, multi-modal, agentic AI assistant** that operates within your personal and work domains, grounded in your documents and tools, with zero vendor lock-in.

**Current Status:** MVP Foundation → V1 Development

## Architecture

Jarvis consists of three main services:

1. **rag-api**: FastAPI backend with ChromaDB Vector Search, OpenAI embeddings, and RAG capabilities
2. **companion-api**: Real-time AI companion service with Deepgram STT, OpenAI GPT-4o, and ElevenLabs TTS
3. **next-holo-ui**: Next.js 14 + TypeScript frontend with holographic UI for voice/video interaction

## Project Structure

```
project-backup/
├── rag-api/              # FastAPI backend service
│   ├── app.py            # Main API application (ChromaDB-based)
│   ├── Dockerfile        # Container configuration
│   └── requirements.txt  # Python dependencies
├── companion-api/        # Real-time AI companion service
│   ├── main.py          # FastAPI WebSocket server
│   ├── companion_web.py  # Browser-compatible companion
│   ├── memory_manager.py # ChromaDB memory system
│   └── requirements.txt  # Python dependencies
├── next-holo-ui/        # Next.js frontend
│   ├── pages/index.tsx  # Main application page
│   ├── components/       # React components
│   ├── hooks/           # Custom React hooks
│   └── lib/api.ts       # API client
└── .cursor/plans/       # Project plans and specifications
```

## Services

### rag-api
- **Main File**: `app.py`
- **Port**: 8080 (default)
- **Key Endpoints**:
  - `POST /query` - RAG query with hybrid search
  - `POST /upload` - Document upload (PDF/DOCX/TXT/MD)
  - `GET /documents` - List all documents
  - `POST /multimodal-live/create-session` - Create multimodal live session
  - `WS /multimodal-live/ws/{session_id}` - WebSocket for real-time multimodal communication

### companion-api
- **Main File**: `main.py`
- **Port**: 8080 (default)
- **Key Endpoints**:
  - `POST /companion/session/create` - Create companion session
  - `WS /companion/ws/{session_id}` - WebSocket for real-time companion interaction
  - `GET /companion/memories` - Retrieve conversation memories
  - `DELETE /companion/memories/{memory_id}` - Delete memory

### next-holo-ui
- **Main File**: `pages/index.tsx`
- **Port**: 3000 (dev), Vercel auto (production)
- **Features**: Chat, document upload, multimodal live voice/video, companion voice interface

## Environment Variables

### rag-api

```bash
OPENAI_API_KEY=your_openai_api_key          # Required: For embeddings and answer generation (OpenAI)
CHROMADB_PATH=./rag_knowledge_base          # Optional: ChromaDB storage path (default: ./rag_knowledge_base)
```

### companion-api

```bash
OPENAI_API_KEY=your_openai_api_key          # Required: OpenAI API key
DEEPGRAM_API_KEY=your_deepgram_api_key      # Required: Deepgram STT API key
ELEVENLABS_API_KEY=your_elevenlabs_api_key  # Required: ElevenLabs TTS API key
```

### next-holo-ui

```bash
NEXT_PUBLIC_API_BASE=http://localhost:8080  # Backend API URL (HTTPS for production)
```

## Local Development

### Prerequisites

- Python 3.8+
- Node.js 18+
- API keys (see Environment Variables above)

### Starting rag-api

```bash
cd rag-api
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY=your_key  # Required: For answer generation
export OPENAI_API_KEY=your_key  # Required: For embeddings
export CHROMADB_PATH=./rag_knowledge_base  # Optional

# Run
python -m uvicorn app:app --host 0.0.0.0 --port 8080
```

### Starting companion-api

```bash
cd companion-api
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY=your_key
export DEEPGRAM_API_KEY=your_key
export ELEVENLABS_API_KEY=your_key

# Run
python main.py
# Or: uvicorn main:app --host 0.0.0.0 --port 8080
```

### Starting next-holo-ui

```bash
cd next-holo-ui
npm install

# Set environment variable
export NEXT_PUBLIC_API_BASE=http://localhost:8080

# Run
npm run dev
```

Open http://localhost:3000 in your browser.

## Current Features (MVP)

- ✅ **RAG Query**: Text-based queries with ChromaDB vector search
- ✅ **Document Upload**: PDF, DOCX, TXT, MD support
- ✅ **Gemini Live**: WebSocket-based real-time communication (simplified)
- ✅ **Real-Time Companion**: Audio pipeline with STT/TTS
- ✅ **Memory System**: ChromaDB-based conversation memory
- ✅ **Holographic UI**: Touch-optimized Next.js interface

## Planned Features (V1)

- 🚧 **Context Budget Enforcement**: Token tracking and truncation
- 🚧 **Memory APIs**: Global and project-scoped memory management
- 🚧 **Uncertainty Protocol**: Explicit "I don't know" responses
- 🚧 **Cost Tracking**: Daily budget limits and warnings
- 🚧 **Browser Automation**: Playwright-based web automation
- 🚧 **Enhanced Live Sessions**: Screen share, video calls
- 🚧 **Windows Companion**: OS automation and control

## Database

- **ChromaDB**: Local vector database for RAG documents (default: `./rag_knowledge_base`)
- **ChromaDB**: Local/cloud vector database for companion memory (default: `./companion_memory`)

## Deployment

### Railway (Backend Services)

**Recommended deployment platform for backend services (rag-api, companion-api)**

#### Quick Start

1. **Create Railway Account**
   - Go to https://railway.app
   - Sign up with GitHub (recommended)

2. **Deploy rag-api**
   - Click "New Project" → "Deploy from GitHub"
   - Select your repository
   - Railway auto-detects the `rag-api` directory
   - Add environment variables:
     - `GEMINI_API_KEY` - Gemini API key
     - `OPENAI_API_KEY` - OpenAI API key for embeddings
     - `CHROMADB_PATH` - Optional (default: `/app/rag_knowledge_base`)
     - `PORT` - Optional (Railway sets this automatically)

3. **Deploy companion-api**
   - Create a new service in the same project
   - Deploy from GitHub (select `companion-api` directory)
   - Add environment variables:
     - `OPENAI_API_KEY` - OpenAI API key
     - `DEEPGRAM_API_KEY` - Deepgram API key
     - `ELEVENLABS_API_KEY` - ElevenLabs API key
     - `ELEVENLABS_VOICE_ID` - Optional (default: `uju3wxzG5OhpWcoi3SMy`)
     - `CHROMADB_PATH` - Optional (default: `/app/companion_memory`)

4. **Configure Persistent Storage**
   - Railway automatically provides persistent volumes
   - ChromaDB data persists across deployments
   - No additional configuration needed

**Railway automatically:**
- Builds Docker containers from Dockerfile
- Assigns HTTPS URLs
- Handles environment variables
- Provides persistent storage volumes

### Vercel (Frontend)

**Recommended deployment platform for Next.js frontend**

#### Quick Start

1. **Deploy to Vercel**
   ```bash
   cd next-holo-ui
   vercel --prod
   ```

2. **Set Environment Variables**
   - In Vercel dashboard → Project Settings → Environment Variables
   - Add: `NEXT_PUBLIC_API_BASE=https://your-rag-api.railway.app`
   - Redeploy after adding variables

3. **Or via Vercel Dashboard**
   - Import GitHub repository
   - Vercel auto-detects Next.js
   - Add `NEXT_PUBLIC_API_BASE` environment variable
   - Deploy

**Vercel automatically:**
- Builds Next.js application
- Provides HTTPS and CDN
- Handles environment variables
- Optimizes for Next.js

### Alternative: Local Development

All services can run locally for development:

```bash
# rag-api
cd rag-api
uvicorn app:app --reload --port 8080

# companion-api
cd companion-api
uvicorn main:app --reload --port 8080

# next-holo-ui
cd next-holo-ui
npm run dev
```

## Development Roadmap

See `.cursor/plans/IMPLEMENTATION_PLAN.md` for detailed sprint planning.

**Current Sprint:** 1.1 - Context Budget & Memory Foundation

## Documentation

- **Architecture**: `.cursor/plans/AGENTS.MD`
- **Implementation Plan**: `.cursor/plans/IMPLEMENTATION_PLAN.md`
- **Deployment Guide**: `DEPLOYMENT.md` (Railway + Vercel)
- **Cloud Strategy**: `.cursor/plans/CLOUD_STRATEGY_ANALYSIS.md`
- **TODO List**: `TODO.md`
- **Project Startup**: `.cursor/plans/PROJECT_STARTUP.md`

## License

[Add license information]

---

**Last Updated:** 2025-01-XX  
**Status:** Active Development
