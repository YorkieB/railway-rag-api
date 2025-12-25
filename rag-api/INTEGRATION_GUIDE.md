# Integration Guide: Memory & Budget Enforcement

This guide shows how to integrate the memory system and budget enforcement into your existing RAG API.

## Quick Integration

### Step 1: Import Required Modules

```python
from rag_api.budget import ContextBudgetEnforcer
from rag_api.memory_storage import ChromaDBMemoryStorage
from rag_api.memory_api import router as memory_router
from rag_api.rag_integration import RAGPipeline, integrate_memory_into_query
```

### Step 2: Initialize Components in app.py

```python
from fastapi import FastAPI

app = FastAPI()

# Initialize budget enforcer
budget_enforcer = ContextBudgetEnforcer()

# Initialize memory storage
memory_storage = ChromaDBMemoryStorage()

# Include memory API router
app.include_router(memory_router)
```

### Step 3: Integrate into /query Endpoint

```python
@app.post("/query")
async def query(
    request: QueryRequest,
    private_session: bool = False
):
    """
    Enhanced RAG query with memory and budget enforcement.
    """
    # Use integration helper
    context = integrate_memory_into_query(
        query=request.message,
        user_id=request.user_id,
        project_id=request.project_id,
        history=request.history or [],
        rag_docs=rag_docs,  # Your RAG retrieval results
        system_prompt=SYSTEM_PROMPT,
        budget_enforcer=budget_enforcer,
        memory_storage=memory_storage,
        private_session=private_session
    )
    
    # Build messages for LLM
    messages = [
        {"role": "system", "content": context["enhanced_system_prompt"]}
    ]
    messages.extend(context["prepared_history"])
    messages.append({"role": "user", "content": request.message})
    
    # Call LLM with prepared context
    response = await call_llm(messages)
    
    # Format response with memory citations
    pipeline = RAGPipeline(budget_enforcer, memory_storage)
    formatted_response = pipeline.format_response_with_memories(
        answer=response["answer"],
        sources=response["sources"],
        memories=context["memories"],
        uncertain=response.get("uncertain", False)
    )
    
    # Add budget warning if present
    if context["warning"]:
        formatted_response["warning"] = context["warning"]
    
    return formatted_response
```

## Manual Integration (More Control)

### Step 1: Retrieve Memories

```python
# Search for relevant memories
memories = memory_storage.search(
    user_id=user_id,
    query=user_query,
    project_id=project_id,
    limit=5
)
memory_contents = [mem.content for mem in memories]
```

### Step 2: Track Token Usage

```python
breakdown = budget_enforcer.track_components(
    system_prompt=system_prompt,
    history=history,
    rag_docs=rag_docs,
    memory_items=memory_contents
)
```

### Step 3: Enforce Budget

```python
truncated_history, truncated_rag, warning = budget_enforcer.enforce_budget(
    system_prompt=system_prompt,
    history=history,
    rag_docs=rag_docs,
    memory_items=memory_contents
)
```

### Step 4: Build Enhanced Context

```python
# Format memories for context
memory_context = "\n".join([
    f"[{mem.memory_type.upper()}] {mem.content}"
    for mem in memories
])

# Enhanced system prompt
enhanced_system = f"""{system_prompt}

## User Context & Preferences
{memory_context}
"""
```

### Step 5: Format Response

```python
response = {
    "answer": llm_answer,
    "sources": rag_sources,
    "uncertain": is_uncertain
}

# Add memory citations
if memories:
    response["memories_used"] = [
        {
            "id": mem.id,
            "content": mem.content,
            "type": mem.memory_type
        }
        for mem in memories
    ]

# Add budget warning
if warning:
    response["warning"] = warning
```

## Environment Variables

Add to your `.env` or environment:

```bash
# Context Budget
MAX_CONTEXT_TOKENS=100000
WARN_THRESHOLD=0.8

# Memory Storage (optional)
MEMORY_DB_PATH=./memory_db
```

## Private Session Handling

Always check `private_session` flag before memory writes:

```python
if not private_session:
    # Memory operations allowed
    memory_storage.create(memory)
else:
    # Block memory operations
    raise HTTPException(403, "Memory operations not allowed in private session")
```

## Testing

Test the integration:

```python
# Test budget enforcement
enforcer = ContextBudgetEnforcer()
breakdown = enforcer.track_components(
    system_prompt="You are a helpful assistant.",
    history=[{"role": "user", "content": "Hello"}],
    rag_docs=["Document chunk 1", "Document chunk 2"],
    memory_items=["User prefers Slack"]
)
assert breakdown.total > 0

# Test memory storage
storage = ChromaDBMemoryStorage()
memory = MemoryItem(
    user_id="test_user",
    content="Test memory",
    memory_type="fact"
)
created = storage.create(memory)
assert created.id == memory.id
```

## Next Steps

1. Integrate into your `/query` endpoint
2. Add memory API endpoints (already included via router)
3. Test with evaluation suite
4. Monitor budget warnings
5. Update frontend to show memory citations

