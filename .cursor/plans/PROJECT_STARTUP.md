# Project Startup & Cleanup Guide

**Date:** 2025-01-XX  
**Status:** Pre-Implementation Analysis

---

## Current Project Analysis

### ✅ What We Need (Keep)

#### rag-api (Main Backend)
- **`app.py`** ✅ **MAIN FILE** - This is the active application (ChromaDB-based)
- `requirements.txt` - Dependencies
- `Dockerfile` - Deployment config
- `test_upload.py` - Testing utility

#### companion-api (Real-Time Companion)
- **`main.py`** ✅ **MAIN FILE** - FastAPI WebSocket server
- `companion_web.py` - Browser-compatible companion
- `memory_manager.py` - ChromaDB memory
- `audio_manager.py` - PyAudio handling
- `config.py` - Configuration
- `requirements.txt` - Dependencies
- `Dockerfile` - Deployment config

#### next-holo-ui (Frontend)
- **`pages/index.tsx`** ✅ **MAIN FILE** - Next.js app
- All components in `components/`
- All hooks in `hooks/`
- `lib/api.ts` - API client
- `package.json` - Dependencies

#### Documentation
- `.cursor/plans/` - All plan files ✅
- `TODO.md` - Task tracking ✅

---

## ❌ What We Don't Need (Can Delete)

### rag-api - Legacy/Backup Files
- ❌ `app.py` - Old version (not used, Dockerfile uses `app_bigquery.py`)
- ❌ `app_original.py` - Backup
- ❌ `app_with_cors.py` - Old version
- ❌ `app_with_web.py` - Old version
- ❌ `app.py.backup` - Backup
- ❌ `app.py.original` - Backup
- ❌ `rag_system.py` - Uses Qdrant (we use ChromaDB)
- ❌ `ingest_gcs_to_qdrant.py` - Qdrant-specific (we use ChromaDB)
- ❌ `read_pdf.py` - Utility, functionality in `app.py`
- ❌ `query.json` - Test file
- ❌ `test_document.txt` - Test file
- ❌ `test_backend.bat` - Windows test script (can recreate if needed)
- ❌ `Procfile` - Railway config (we use Cloud Run)
- ❌ `railway.json` - Railway config (we use Cloud Run)

### knowledge-base-ui (Legacy Streamlit UI)
- ❌ **ENTIRE DIRECTORY** - We use `next-holo-ui` instead
  - `app.py` - Streamlit app (legacy)
  - `Dockerfile` - Not needed
  - `requirements.txt` - Not needed
  - `jarvis_preview.html` - Preview file
  - `start_ui.bat` - Not needed
  - `UI_PREVIEW.md` - Not needed

### Root Directory - Temporary Files
- ❌ `tmp-bm.js` - Temporary file
- ❌ `tmp-index.js` - Temporary file

### Root Directory - Legacy Deployment Docs
- ❌ `DEPLOY_TO_CLOUD_RUN.md` - Can consolidate
- ❌ `DEPLOY_VIA_CONSOLE.md` - Can consolidate
- ❌ `INSTALL_AND_DEPLOY.md` - Can consolidate
- ❌ `QUICK_DEPLOY.md` - Can consolidate
- ⚠️ `README.md` - **UPDATE** (references old structure)

---

## 🔧 What Needs Changes

### 1. rag-api/app.py
**Current:** Basic RAG with ChromaDB  
**Needs:**
- Context budget enforcement
- Memory system integration
- Uncertainty protocol
- Cost tracking middleware
- Enhanced session management

**Action:** This is our main file - we'll extend it, not replace it.

### 2. README.md
**Current:** References old structure  
**Needs:** Update to reflect:
- `app.py` as main file
- `next-holo-ui` as frontend (not Streamlit)
- `companion-api` as separate service
- Current architecture

**Action:** Update README.md

### 3. Dockerfile (rag-api)
**Current:** Uses `app_bigquery:app` ✅ (correct)  
**Status:** No changes needed

### 4. Environment Variables
**Need to verify:**
- `GEMINI_API_KEY` - Required
- `GCP_PROJECT` - Required (currently hardcoded in app_bigquery.py)
- `OPENAI_API_KEY` - Optional (for web search fallback)

**Action:** Move hardcoded project_id to environment variable

---

## 📋 Cleanup Steps

### Step 1: Delete Legacy Files

```bash
# rag-api legacy files
rm rag-api/app.py
rm rag-api/app_original.py
rm rag-api/app_with_cors.py
rm rag-api/app_with_web.py
rm rag-api/app.py.backup
rm rag-api/app.py.original
rm rag-api/rag_system.py
rm rag-api/ingest_gcs_to_qdrant.py
rm rag-api/read_pdf.py
rm rag-api/query.json
rm rag-api/test_document.txt
rm rag-api/test_backend.bat
rm rag-api/Procfile
rm rag-api/railway.json

# knowledge-base-ui (entire directory)
rm -rf knowledge-base-ui

# Root temporary files
rm tmp-bm.js
rm tmp-index.js

# Legacy deployment docs (optional - can archive)
rm DEPLOY_TO_CLOUD_RUN.md
rm DEPLOY_VIA_CONSOLE.md
rm INSTALL_AND_DEPLOY.md
rm QUICK_DEPLOY.md
```

### Step 2: Update Configuration

1. **Verify environment variables** in `app.py`:
   - `GEMINI_API_KEY` - Required for answer generation
   - `OPENAI_API_KEY` - Required for embeddings
   - `CHROMADB_PATH` - Optional (default: `./rag_knowledge_base`)

2. **Update README.md** to reflect current structure

### Step 3: Verify Dependencies

**rag-api/requirements.txt** - Check if we need to add:
- [ ] Any new packages for budget/cost tracking?
- [ ] Any new packages for memory system?

**companion-api/requirements.txt** - Looks good ✅

**next-holo-ui/package.json** - Looks good ✅

---

## 🚀 How to Start the Project

### Prerequisites

1. **Python 3.8+** installed
2. **Node.js 18+** installed
3. **Google Cloud SDK** installed (for BigQuery)
4. **API Keys:**
   - `GEMINI_API_KEY`
   - `OPENAI_API_KEY` (optional)
   - `DEEPGRAM_API_KEY` (for companion-api)
   - `ELEVENLABS_API_KEY` (for companion-api)

### Starting rag-api

```bash
cd rag-api
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY=your_key
export GCP_PROJECT=gen-lang-client-0118945483
export OPENAI_API_KEY=your_key  # Optional

# Run
python -m uvicorn app_bigquery:app --host 0.0.0.0 --port 8080
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

---

## ✅ Pre-Implementation Checklist

Before starting Sprint 1.1:

- [ ] Clean up legacy files (Step 1)
- [ ] Move hardcoded project_id to env var
- [ ] Update README.md
- [ ] Verify all three services can start locally
- [ ] Test basic RAG query works
- [ ] Test companion-api WebSocket works
- [ ] Test next-holo-ui connects to rag-api

---

## 📁 Final Project Structure

```
project-backup/
├── rag-api/
│   ├── app.py                   ✅ MAIN (ChromaDB-based)
│   ├── test_upload.py           ✅ Testing
│   ├── requirements.txt         ✅
│   ├── Dockerfile               ✅
│   └── [new files we'll create]
│       ├── budget.py            🆕 Sprint 1.1
│       ├── uncertainty.py       🆕 Sprint 1.2
│       ├── cost.py              🆕 Sprint 1.2
│       └── models.py            🆕 Sprint 1.1
│
├── companion-api/
│   ├── main.py                  ✅ MAIN
│   ├── companion_web.py          ✅
│   ├── memory_manager.py         ✅
│   ├── audio_manager.py          ✅
│   ├── config.py                 ✅
│   ├── requirements.txt          ✅
│   └── Dockerfile                ✅
│
├── next-holo-ui/
│   ├── pages/index.tsx           ✅ MAIN
│   ├── components/               ✅
│   ├── hooks/                    ✅
│   ├── lib/api.ts                ✅
│   ├── package.json              ✅
│   └── [new components we'll create]
│       ├── BudgetStatus.tsx      🆕 Sprint 1.3
│       └── MemoryPanel.tsx       🆕 Sprint 1.3
│
├── .cursor/plans/                ✅ All plan files
├── TODO.md                       ✅ Task tracking
└── README.md                     ⚠️ Needs update
```

---

## 🎯 Next Actions

1. **Review this cleanup plan**
2. **Execute cleanup** (delete legacy files)
3. **Update configuration** (env vars, README)
4. **Verify services start** (test all three)
5. **Begin Sprint 1.1** (ContextBudgetEnforcer)

---

**Status:** Ready for cleanup and startup verification

