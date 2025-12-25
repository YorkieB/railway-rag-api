# Implementation Examples for app.py

**Date:** 2025-12-25  
**Purpose:** Example implementations for placeholder functions in `app.py`

---

## Overview

The `/query` endpoint in `app.py` has two placeholder functions that need to be implemented:
1. `retrieve_rag_documents()` - RAG document retrieval
2. `call_llm()` - LLM API call

This document provides example implementations for both.

---

## Example 1: RAG Retrieval with ChromaDB

### Basic Implementation

```python
async def retrieve_rag_documents(query: str):
    """
    Retrieve relevant documents from ChromaDB.
    
    Returns:
        Tuple of (chunks, scores) where:
        - chunks: List of document chunks with 'text' field
        - scores: List of relevance scores (0.0-1.0)
    """
    import chromadb
    from chromadb.config import Settings
    
    # Initialize ChromaDB client
    client = chromadb.PersistentClient(
        path="./rag_db",  # Or use environment variable
        settings=Settings(anonymized_telemetry=False)
    )
    
    # Get or create collection
    collection = client.get_or_create_collection(
        name="documents",
        metadata={"hnsw:space": "cosine"}
    )
    
    # Query ChromaDB
    results = collection.query(
        query_texts=[query],
        n_results=5,  # Number of documents to retrieve
        include=["documents", "distances", "metadatas"]
    )
    
    # Format results
    chunks = []
    scores = []
    
    if results["ids"] and len(results["ids"][0]) > 0:
        for i, doc in enumerate(results["documents"][0]):
            # Convert distance to similarity score (1 - distance)
            distance = results["distances"][0][i] if "distances" in results else 0.5
            similarity = 1.0 - min(distance, 1.0)  # Ensure score is 0-1
            
            chunks.append({
                "text": doc,
                "score": similarity,
                "metadata": results["metadatas"][0][i] if "metadatas" in results else {}
            })
            scores.append(similarity)
    
    return chunks, scores
```

### Advanced Implementation with Filtering

```python
async def retrieve_rag_documents(query: str, project_id: Optional[str] = None):
    """
    Retrieve relevant documents with optional filtering.
    """
    import chromadb
    from chromadb.config import Settings
    
    client = chromadb.PersistentClient(
        path=os.getenv("CHROMADB_RAG_DIR", "./rag_db"),
        settings=Settings(anonymized_telemetry=False)
    )
    
    collection = client.get_or_create_collection(
        name="documents",
        metadata={"hnsw:space": "cosine"}
    )
    
    # Build where clause for filtering
    where = {}
    if project_id:
        where["project_id"] = project_id
    
    # Query with filtering
    results = collection.query(
        query_texts=[query],
        where=where if where else None,
        n_results=5,
        include=["documents", "distances", "metadatas"]
    )
    
    chunks = []
    scores = []
    
    if results["ids"] and len(results["ids"][0]) > 0:
        for i, doc in enumerate(results["documents"][0]):
            distance = results["distances"][0][i] if "distances" in results else 0.5
            similarity = max(0.0, 1.0 - distance)
            
            chunks.append({
                "text": doc,
                "score": similarity,
                "metadata": results["metadatas"][0][i] if "metadatas" in results else {}
            })
            scores.append(similarity)
    
    return chunks, scores
```

---

## Example 2: LLM Call with OpenAI

### Basic Implementation

```python
async def call_llm(messages: List[Dict[str, str]]):
    """
    Call OpenAI API.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
    
    Returns:
        Dict with 'answer' and optional 'sources'
    """
    from openai import AsyncOpenAI
    import os
    
    # Initialize OpenAI client
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Call OpenAI API
    response = await client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4"),
        messages=messages,
        temperature=0.7,
        max_tokens=1000
    )
    
    # Extract answer
    answer = response.choices[0].message.content
    
    return {
        "answer": answer,
        "sources": []  # Add sources if available
    }
```

### Advanced Implementation with Streaming

```python
async def call_llm(messages: List[Dict[str, str]], stream: bool = False):
    """
    Call OpenAI API with optional streaming.
    """
    from openai import AsyncOpenAI
    import os
    
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    if stream:
        # Streaming response
        stream_response = await client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
            messages=messages,
            temperature=0.7,
            stream=True
        )
        
        answer = ""
        async for chunk in stream_response:
            if chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content
        
        return {
            "answer": answer,
            "sources": []
        }
    else:
        # Non-streaming response
        response = await client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        return {
            "answer": response.choices[0].message.content,
            "sources": []
        }
```

### Implementation with Cost Tracking

```python
async def call_llm(messages: List[Dict[str, str]], request: Request):
    """
    Call OpenAI API with cost tracking.
    """
    from openai import AsyncOpenAI
    import os
    
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    response = await client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4"),
        messages=messages,
        temperature=0.7,
        max_tokens=1000
    )
    
    # Track costs in request state
    cost_info = {
        "text_tokens": response.usage.prompt_tokens + response.usage.completion_tokens,
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_cost": calculate_cost(response.usage, model=os.getenv("OPENAI_MODEL", "gpt-4"))
    }
    
    # Store in request state for middleware
    request.state.cost_info = cost_info
    
    return {
        "answer": response.choices[0].message.content,
        "sources": [],
        "usage": {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        }
    }
```

---

## Example 3: Using Existing Memory Storage

If you want to use the existing memory storage for RAG retrieval:

```python
async def retrieve_rag_documents(query: str, user_id: str, project_id: Optional[str] = None):
    """
    Retrieve documents using existing memory storage.
    """
    from .memory_storage import ChromaDBMemoryStorage
    
    # Use existing memory storage instance
    # Note: This uses the memory collection, not a separate RAG collection
    storage = ChromaDBMemoryStorage(collection_name="memories")
    
    # Search memories (which are stored as documents)
    memories = storage.search(
        user_id=user_id,
        query=query,
        project_id=project_id,
        limit=5
    )
    
    # Convert memories to chunks
    chunks = []
    scores = []
    
    for memory in memories:
        chunks.append({
            "text": memory.content,
            "score": 0.9,  # Memory search doesn't return scores directly
            "metadata": {
                "memory_id": memory.id,
                "memory_type": memory.memory_type
            }
        })
        scores.append(0.9)
    
    return chunks, scores
```

---

## Example 4: Complete Integration

Here's how to integrate both functions into `app.py`:

```python
# At the top of app.py, add imports
import os
from openai import AsyncOpenAI
import chromadb
from chromadb.config import Settings

# Initialize clients (outside the function, at module level)
_openai_client = None
_rag_collection = None

def get_openai_client():
    """Get or create OpenAI client."""
    global _openai_client
    if _openai_client is None:
        _openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _openai_client

def get_rag_collection():
    """Get or create RAG collection."""
    global _rag_collection
    if _rag_collection is None:
        client = chromadb.PersistentClient(
            path=os.getenv("CHROMADB_RAG_DIR", "./rag_db"),
            settings=Settings(anonymized_telemetry=False)
        )
        _rag_collection = client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
    return _rag_collection

# In the query endpoint, replace the placeholder functions:

async def retrieve_rag_documents(query: str):
    """Retrieve relevant documents from ChromaDB."""
    collection = get_rag_collection()
    
    results = collection.query(
        query_texts=[query],
        n_results=5,
        include=["documents", "distances"]
    )
    
    chunks = []
    scores = []
    
    if results["ids"] and len(results["ids"][0]) > 0:
        for i, doc in enumerate(results["documents"][0]):
            distance = results["distances"][0][i] if "distances" in results else 0.5
            similarity = max(0.0, 1.0 - distance)
            
            chunks.append({"text": doc, "score": similarity})
            scores.append(similarity)
    
    return chunks, scores

async def call_llm(messages: List[Dict[str, str]]):
    """Call OpenAI API."""
    client = get_openai_client()
    
    response = await client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4"),
        messages=messages,
        temperature=0.7,
        max_tokens=1000
    )
    
    return {
        "answer": response.choices[0].message.content,
        "sources": []
    }
```

---

## Environment Variables

Add these to your `.env` file:

```bash
# OpenAI
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4  # or gpt-3.5-turbo

# ChromaDB
CHROMADB_RAG_DIR=./rag_db  # Directory for RAG documents
```

---

## Dependencies

Make sure these are in `requirements.txt`:

```txt
openai>=1.0.0
chromadb>=0.4.0
```

---

## Testing

After implementing, test with:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the capital of France?",
    "user_id": "test-user"
  }'
```

---

## Notes

1. **ChromaDB Setup**: Make sure you've indexed your documents in ChromaDB before querying
2. **OpenAI API Key**: Ensure your API key is set in environment variables
3. **Error Handling**: Add try/except blocks for production use
4. **Caching**: Consider adding caching for frequently queried documents
5. **Rate Limiting**: Implement rate limiting for OpenAI API calls

---

**See also:**
- `rag-api/APP_PY_SETUP.md` - Setup guide
- `rag-api/COMPLETE_INTEGRATION_GUIDE.md` - Full integration guide
- `API_REFERENCE.md` - API documentation

