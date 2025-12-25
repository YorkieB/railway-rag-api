# app.py Setup Guide

**Date:** 2025-12-25  
**Status:** ✅ Main app.py created

---

## ✅ What's Done

The main `app.py` file has been created with all components integrated:
- ✅ All routers included
- ✅ All middleware configured
- ✅ Enhanced `/query` endpoint
- ✅ Health check endpoints
- ✅ Error handling

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd rag-api
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file in `rag-api/`:

```bash
# Budget Configuration
MAX_CONTEXT_TOKENS=100000
WARN_THRESHOLD=0.8
RAG_CONFIDENCE_THRESHOLD=0.6

# API Keys
DEEPGRAM_API_KEY=your-deepgram-key
OPENAI_API_KEY=your-openai-key
ELEVENLABS_API_KEY=your-elevenlabs-key

# CORS (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# ChromaDB (optional)
CHROMADB_PERSIST_DIR=./chroma_db
```

### 3. Install Browser Dependencies

```bash
playwright install chromium
```

### 4. Run the Server

```bash
uvicorn app:app --reload
```

The API will be available at:
- **API:** http://localhost:8000
- **Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## ⚠️ Important: Complete the /query Endpoint

The `/query` endpoint has placeholder functions that need to be implemented:

### 1. Implement `retrieve_rag_documents()`

Replace the placeholder with your actual RAG retrieval:

```python
async def retrieve_rag_documents(query: str):
    """
    Retrieve relevant documents from your RAG system.
    
    Returns:
        Tuple of (chunks, scores) where:
        - chunks: List of document chunks with 'text' field
        - scores: List of relevance scores (0.0-1.0)
    """
    # TODO: Replace with your actual RAG retrieval
    # Example:
    # from your_rag_system import search_documents
    # results = await search_documents(query)
    # return results.chunks, results.scores
    
    return [{"text": "Example document", "score": 0.85}], [0.85]
```

### 2. Implement `call_llm()`

Replace the placeholder with your actual LLM call:

```python
async def call_llm(messages: List[Dict[str, str]]):
    """
    Call your LLM API (OpenAI, Gemini, etc.).
    
    Args:
        messages: List of message dicts with 'role' and 'content'
    
    Returns:
        Dict with 'answer' and optional 'sources'
    """
    # TODO: Replace with your actual LLM API call
    # Example:
    # from openai import OpenAI
    # client = OpenAI()
    # response = client.chat.completions.create(
    #     model="gpt-4",
    #     messages=messages
    # )
    # return {"answer": response.choices[0].message.content, "sources": []}
    
    return {
        "answer": "This is a placeholder response.",
        "sources": []
    }
```

---

## 📋 Available Endpoints

### Core Endpoints
- `GET /` - API information
- `GET /health` - Health check
- `POST /query` - Enhanced RAG query

### Memory API (`/memory`)
- `POST /memory` - Create memory
- `GET /memory` - List memories
- `GET /memory/{id}` - Get memory
- `PUT /memory/{id}` - Update memory
- `DELETE /memory/{id}` - Delete memory
- `GET /memory/search` - Search memories

### Live Sessions (`/live-sessions`)
- `POST /live-sessions` - Create session
- `GET /live-sessions/{id}` - Get session
- `GET /live-sessions` - List sessions
- `PUT /live-sessions/{id}/pause` - Pause session
- `PUT /live-sessions/{id}/resume` - Resume session
- `PUT /live-sessions/{id}` - Update session
- `DELETE /live-sessions/{id}` - End session

### LS1A Audio Pipeline (`/ls1a`)
- `WS /ls1a/ws/{session_id}?user_id={user_id}` - WebSocket endpoint

### Browser Automation (`/browser`)
- `POST /browser/sessions` - Create browser session
- `GET /browser/sessions/{id}` - Get session
- `GET /browser/sessions` - List sessions
- `POST /browser/sessions/{id}/navigate` - Navigate to URL
- `GET /browser/sessions/{id}/ax-tree` - Get AX tree
- `POST /browser/sessions/{id}/actions/click` - Click element
- `POST /browser/sessions/{id}/actions/type` - Type text
- `POST /browser/sessions/{id}/actions/extract` - Extract text
- `POST /browser/sessions/{id}/actions/plan` - Execute plan
- `DELETE /browser/sessions/{id}` - Close session

### Budget (`/budget`)
- `GET /budget/status?user_id={user_id}` - Get budget status

---

## 🧪 Testing

### Test the API

```bash
# Health check
curl http://localhost:8000/health

# Get budget status
curl http://localhost:8000/budget/status?user_id=test-user

# Create a memory
curl -X POST http://localhost:8000/memory \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "content": "User prefers dark mode",
    "memory_type": "preference"
  }'
```

### Run Unit Tests

```bash
pytest rag-api/tests/ -v
```

---

## 🔧 Troubleshooting

### Import Errors

If you get import errors, make sure:
1. You're running from the `rag-api/` directory
2. The `rag-api` package is in your Python path
3. All dependencies are installed

### Middleware Issues

If middleware doesn't work:
1. Check that `cost_tracker` is initialized before adding middleware
2. Verify environment variables are set

### Router Issues

If routers don't load:
1. Check that all router files exist
2. Verify imports are correct
3. Check for circular import issues

---

## 📚 Next Steps

1. **Implement RAG retrieval** - Replace `retrieve_rag_documents()`
2. **Implement LLM call** - Replace `call_llm()`
3. **Test all endpoints** - Verify everything works
4. **Configure production** - Set up environment variables
5. **Deploy** - Follow `DEPLOYMENT_GUIDE.md`

---

## ✅ Status

**Main app.py:** ✅ Created and ready  
**Integration:** ✅ All components wired  
**Next:** Implement RAG retrieval and LLM calls

---

**See also:**
- `INTEGRATION_CHECKLIST.md` - Full integration guide
- `API_REFERENCE.md` - Complete API documentation
- `COMPLETE_INTEGRATION_GUIDE.md` - Detailed integration examples

