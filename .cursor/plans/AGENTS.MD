# AGENTS.MD - Project Architecture & Agent Guidelines

## Project Overview

This is a **multi-service RAG (Retrieval-Augmented Generation) system with zero vendor lock-in** and real-time AI companion capabilities. The system consists of three main services:

1. **rag-api**: FastAPI backend with ChromaDB Vector Search, OpenAI embeddings, and Gemini Live WebSocket support
2. **next-holo-ui**: Next.js 14 + TypeScript frontend with holographic UI for Gemini Live voice/video
3. **companion-api**: Real-time AI companion service with Deepgram STT, OpenAI GPT-4o, and ElevenLabs TTS

---

## Core Entry Points

### Backend Services

#### rag-api (`rag-api/app.py`)
- **Main Entry**: FastAPI application at `app = FastAPI(...)`
- **Port**: 8080 (default)
- **Key Endpoints**:
  - `GET /` - API information
  - `GET /health` - Health check with ChromaDB connection test
  - `POST /query` - RAG query with hybrid search
  - `POST /upload` - Document upload (PDF, DOCX, TXT, MD)
  - `GET /documents` - List all documents
  - `POST /gemini-live/create-session` - Create Gemini Live session
  - `WS /gemini-live/ws/{session_id}` - WebSocket for real-time communication
  - `GET/DELETE /gemini-live/sessions/{session_id}` - Session management

#### companion-api (`companion-api/main.py`)
- **Main Entry**: FastAPI application
- **Port**: 8080 (default)
- **Key Endpoints**:
  - `GET /health` - Health check
  - `POST /companion/session/create` - Create companion session
  - `WS /companion/ws/{session_id}` - WebSocket for real-time companion interaction
  - `GET /companion/memories` - Retrieve conversation memories
  - `DELETE /companion/memories/{memory_id}` - Delete memory
  - `POST /companion/config` - Update configuration

### Frontend

#### next-holo-ui (`next-holo-ui/pages/index.tsx`)
- **Main Entry**: Next.js Pages Router (`pages/index.tsx`)
- **App Entry**: `pages/_app.tsx` - Wraps all pages with global styles
- **Port**: 3000 (dev), 8080 (Cloud Run)
- **Key Components**:
  - `Hero` - Landing section
  - `ChatPanel` - Text chat interface
  - `ArtifactPanel` - Document artifacts display
  - `VoiceVideo` - Gemini Live voice/video interface
  - `SettingsDrawer` - Configuration UI
  - `StatusBar` - Backend status indicator

---

## Main Data Flows

### 1. RAG Query Flow (rag-api)
```
User Query (text)
  ↓
POST /query
  ↓
embed_text() → Gemini embedding-004
  ↓
search_bigquery() → BigQuery vector search + keyword scoring
  ↓
generate_answer() → Gemini 2.0-flash-exp
  ↓
Response with sources
```

### 2. Document Upload Flow (rag-api)
```
File Upload (PDF/DOCX/TXT/MD)
  ↓
POST /upload
  ↓
extract_text_from_file() → Text extraction
  ↓
chunk_text() → Overlapping chunks (500 words, 50 overlap)
  ↓
embed_text_for_document() → Gemini embeddings
  ↓
insert_rows_json() → BigQuery table
```

### 3. Gemini Live Flow (rag-api + next-holo-ui)
```
Frontend: createGeminiSession()
  ↓
POST /gemini-live/create-session
  ↓
Frontend: WebSocket connection
  ↓
WS /gemini-live/ws/{session_id}
  ↓
Message Types:
  - text_input → RAG query → Response
  - video_frame → Gemini vision → Description
  - audio_chunk → Acknowledgment (simplified)
  - multimodal_query → RAG + Vision → Combined response
```

### 4. Companion Flow (companion-api + next-holo-ui)
```
Frontend: Browser audio capture
  ↓
WebSocket: audio_chunk (base64 PCM)
  ↓
companion.process_audio_chunk() → Deepgram Live
  ↓
Deepgram → Transcript
  ↓
OpenAI GPT-4o (streaming) → Text response
  ↓
ElevenLabs Flash v2.5 → Audio stream
  ↓
WebSocket: audio_chunk (base64 MP3) → Browser playback
```

---

## Key Libraries & Versions

### Backend (rag-api)

| Library | Version | Purpose |
|---------|---------|---------|
| `fastapi` | 0.115.6 | Web framework |
| `uvicorn` | 0.34.0 | ASGI server |
| `pydantic` | 2.10.5 | Data validation |
| `google-generativeai` | 0.8.3 | Gemini API client |
| `google-cloud-bigquery` | 3.28.0 | BigQuery client |
| `openai` | >=1.0.0 | OpenAI API (web search fallback) |
| `python-docx` | >=1.1.0 | DOCX parsing |
| `PyPDF2` | >=3.0.0 | PDF parsing |
| `python-multipart` | >=0.0.6 | File upload handling |
| `numpy` | >=1.24.0 | Vector operations |

### Backend (companion-api)

| Library | Version | Purpose |
|---------|---------|---------|
| `fastapi` | >=0.104.0 | Web framework |
| `uvicorn[standard]` | >=0.24.0 | ASGI server |
| `deepgram-sdk` | >=3.0.0,<4.0.0 | Speech-to-text |
| `openai` | >=1.0.0 | GPT-4o LLM |
| `elevenlabs` | >=1.0.0 | Text-to-speech |
| `chromadb` | >=0.4.0 | Vector memory storage |
| `pydantic` | >=2.0.0 | Data validation |
| `websockets` | >=12.0 | WebSocket support |
| `python-dotenv` | >=1.0.0 | Environment variables |

### Frontend (next-holo-ui)

| Library | Version | Purpose |
|---------|---------|---------|
| `next` | 14.2.5 | React framework |
| `react` | 18.3.1 | UI library |
| `react-dom` | 18.3.1 | DOM rendering |
| `framer-motion` | ^11.2.10 | Animations |
| `clsx` | ^2.1.1 | Conditional classes |
| `tailwindcss` | ^3.4.11 | Styling |
| `typescript` | ^5.5.4 | Type safety |

---

## Architectural Patterns

### 1. Lazy Initialization Pattern
**Location**: `rag-api/app_bigquery.py`
- Gemini API: `configure_gemini()` - Only initializes when first used
- BigQuery Client: `get_bq_client()` - Singleton pattern with lazy creation
- **Rationale**: Avoids initialization errors if environment variables are missing

### 2. Hybrid Search Pattern
**Location**: `rag-api/app_bigquery.py::search_bigquery()`
- Combines vector similarity (70%) + keyword matching (30%)
- Reranking: Boosts documents with high keyword scores
- **Rationale**: Improves retrieval accuracy for both semantic and exact matches

### 3. WebSocket Message Type Pattern
**Location**: `rag-api/app_bigquery.py::gemini_live_websocket()`
- Type-based message routing: `data.get("type")`
- Supported types: `text_input`, `video_frame`, `audio_chunk`, `multimodal_query`, `close`
- **Rationale**: Extensible message protocol for multimodal communication

### 4. Async Queue Pattern
**Location**: `companion-api/companion_web.py`
- `transcript_queue`: AsyncQueue for inter-task communication
- `audio_chunk_queue`: Browser audio chunks
- **Rationale**: Decouples audio processing from LLM generation

### 5. Streaming Pattern
**Location**: `companion-api/companion_web.py::generate_and_speak()`
- LLM streaming: `response_stream` → async generator
- TTS streaming: `text_iterator()` → ElevenLabs stream
- **Rationale**: Minimizes latency (sub-800ms target)

### 6. Memory Injection Pattern
**Location**: `companion-api/companion_web.py::generate_and_speak()`
- Memory context inserted at position 1 (after system prompt)
- Format: `"Relevant Memories: {context_memory}"`
- **Rationale**: Follows guidance document pattern for memory retrieval

### 7. Sliding Window Pattern
**Location**: `companion-api/companion_web.py`
- Conversation history: Last 15 turns (`MAX_CONTEXT_TURNS`)
- Automatic trimming when exceeding limit
- **Rationale**: Manages context window size for LLM efficiency

### 8. Component Composition Pattern
**Location**: `next-holo-ui/pages/index.tsx`
- Page-level state management
- Props drilling to child components
- Custom hooks: `useLocalStorage`, `useGeminiLive`
- **Rationale**: React best practices for Next.js Pages Router

### 9. Path Alias Pattern
**Location**: `next-holo-ui/tsconfig.json`
- `@/*` maps to project root
- **Rationale**: Clean imports without relative path hell

### 10. Type Safety Pattern
**Location**: `next-holo-ui/types.ts`
- Centralized type definitions
- Strict TypeScript mode enabled
- **Rationale**: Prevents runtime errors, improves IDE support

---

## Forbidden Patterns & Libraries

### ❌ Forbidden Patterns

1. **Hardcoded API Keys**
   - **Rule**: Never commit API keys in code
   - **Current**: ✅ Uses `os.getenv()` / `process.env`
   - **Location**: All services use environment variables

2. **Synchronous Blocking Operations in Async Context**
   - **Rule**: Avoid blocking I/O in async functions
   - **Current**: ⚠️ `companion.process_audio_chunk()` is synchronous but called from async context
   - **Note**: Should be wrapped in `asyncio.run_in_executor()` if performance issues arise

3. **Global State Mutation Without Locks**
   - **Rule**: Use thread-safe patterns for shared state
   - **Current**: ⚠️ `active_sessions` dict in `rag-api` and `companion-api` - not thread-safe
   - **Note**: Acceptable for single-instance deployment, but should use locks for multi-instance

4. **CORS Wildcard in Production**
   - **Rule**: Restrict CORS origins in production
   - **Current**: ⚠️ `allow_origins=["*"]` in both services
   - **Note**: Should be restricted to specific domains in production

5. **No Input Validation on WebSocket Messages**
   - **Rule**: Validate all WebSocket message types and payloads
   - **Current**: ⚠️ Basic type checking with `data.get("type")` but no Pydantic validation
   - **Note**: Should add Pydantic models for WebSocket messages

### ❌ Forbidden Libraries

1. **Qdrant Client** (Legacy)
   - **Status**: Found in `rag-api/rag_system.py` but NOT used in main app
   - **Current**: ✅ Main app uses BigQuery, not Qdrant
   - **Action**: Legacy file, can be removed if not needed

2. **Streamlit** (Legacy UI)
   - **Status**: `knowledge-base-ui/app.py` exists but is legacy
   - **Current**: ✅ Main frontend is Next.js (`next-holo-ui`)
   - **Action**: Keep for reference, but not primary UI

3. **PyAudio** (Companion API Only)
   - **Status**: Only used in `companion-api` for local microphone (not web version)
   - **Current**: ✅ Web version (`companion_web.py`) doesn't use PyAudio
   - **Note**: Required for local testing, not for Cloud Run deployment

---

## Configuration Files

### Backend
- `rag-api/requirements.txt` - Python dependencies
- `companion-api/requirements.txt` - Python dependencies
- `rag-api/Dockerfile` - Container configuration
- `companion-api/Dockerfile` - Container configuration

### Frontend
- `next-holo-ui/package.json` - Node dependencies
- `next-holo-ui/tsconfig.json` - TypeScript configuration
- `next-holo-ui/.eslintrc.json` - Linting rules

---

## Environment Variables

### rag-api
- `GEMINI_API_KEY` - **Required**: Gemini API key for answer generation
- `OPENAI_API_KEY` - **Required**: OpenAI API key for embeddings
- `CHROMADB_PATH` - **Optional**: ChromaDB storage path (default: `./rag_knowledge_base`)

### companion-api
- `DEEPGRAM_API_KEY` - **Required**: Deepgram API key
- `OPENAI_API_KEY` - **Required**: OpenAI API key
- `ELEVENLABS_API_KEY` - **Required**: ElevenLabs API key
- `ELEVENLABS_VOICE_ID` - **Optional**: Voice ID (default: `uju3wxzG5OhpWcoi3SMy`)
- `ELEVENLABS_MODEL` - **Optional**: Model ID (default: `eleven_flash_v2_5`)
- `DEEPGRAM_MODEL` - **Optional**: Model name (default: `nova-2`)
- `CHROMADB_PATH` - **Optional**: Memory storage path (default: `./companion_memory`)

### next-holo-ui
- `NEXT_PUBLIC_API_BASE` - **Required**: Backend API URL (HTTPS for production)
- **Note**: Falls back to `https://rag-api-883324649002.us-central1.run.app` in production if not set

---

## Database & Storage

### ChromaDB (RAG Documents)
- **Path**: `./rag_knowledge_base` (local) or `CHROMADB_PATH` env var
- **Collection**: `documents` (auto-created)
- **Embedding Model**: `text-embedding-3-small` (OpenAI)
- **Purpose**: Vector storage for RAG document retrieval
- **Storage**: Persistent file-based storage (works on any platform)

### ChromaDB (Companion Memory)
- **Path**: `./companion_memory` (local) or `CHROMADB_PATH` env var
- **Collection**: `companion_history`
- **Embedding Model**: `text-embedding-3-small` (OpenAI)
- **Purpose**: Persistent conversation memory for companion-api
- **Storage**: Persistent file-based storage (works on any platform)

---

## Deployment Configuration

### Railway (Backend Services)
- **rag-api**: Deploy to Railway (recommended)
  - Auto-detects Dockerfile
  - Provides HTTPS URL automatically
  - Persistent storage for ChromaDB
  - Environment variables via dashboard
- **companion-api**: Deploy to Railway (same project, different service)
  - Same deployment process as rag-api
  - Separate service for isolation

### Vercel (Frontend)
- **Service**: `next-holo-ui`
- **Framework**: Next.js 14
- **Build Command**: `npm run build` (auto-detected)
- **Output Directory**: `.next` (auto-detected)
- **Environment Variables**: Set `NEXT_PUBLIC_API_BASE` to Railway URL

---

## Code Standards

### Python
- **Type Hints**: Required (`from typing import List, Optional`)
- **Error Handling**: Use `HTTPException` with descriptive messages
- **Async/Await**: Use for I/O operations
- **Docstrings**: Include for public functions

### TypeScript
- **Strict Mode**: Enabled (`"strict": true` in tsconfig.json)
- **No `any` Types**: Use proper interfaces/types
- **Path Aliases**: Use `@/` for imports
- **React Hooks**: Prefer hooks over class components

---

## Testing & Development

### Local Development
- **rag-api**: `uvicorn app:app --reload --port 8080`
- **companion-api**: `uvicorn main:app --reload --port 8080`
- **next-holo-ui**: `npm run dev` (port 3000)

### Health Checks
- **rag-api**: `GET /health` - Tests ChromaDB connection
- **companion-api**: `GET /health` - Returns active session count

---

## Known Limitations

1. **Gemini Live Audio**: Current implementation uses simplified approach with standard Gemini API. Full streaming requires SDK integration.
2. **WebSocket Session Storage**: In-memory dict (`active_sessions`) - not persistent across restarts.
3. **ChromaDB Vector Search**: Uses hybrid search (vector similarity + keyword matching) with in-memory scoring.
4. **CORS**: Currently allows all origins - should be restricted in production.

---

## Next Steps for Agents

When working on this codebase:

1. **Verify Library Versions**: Check `requirements.txt` and `package.json` before adding dependencies
2. **Follow Lazy Initialization**: Use `configure_gemini()` and `get_chromadb_collection()` patterns
3. **Maintain Type Safety**: Use TypeScript strict mode, no `any` types
4. **Test WebSocket Messages**: Validate message types and payloads
5. **Use Environment Variables**: Never hardcode API keys or URLs
6. **Respect Architecture Patterns**: Follow existing patterns (hybrid search, streaming, etc.)
7. **Zero Vendor Lock-in**: Use platform-agnostic solutions (ChromaDB, standard APIs)
8. **Update This Document**: Keep AGENTS.MD updated when adding new patterns or libraries

---

**Last Updated**: 2025-01-XX
**Maintained By**: Development Team

