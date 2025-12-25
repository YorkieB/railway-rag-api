# Complete Integration Guide: Sprint 1.1 & 1.2

This guide shows how to integrate all Sprint 1.1 and 1.2 features into your existing RAG API.

## Overview

**Sprint 1.1 Components:**
- ContextBudgetEnforcer
- Memory system (models, storage, APIs)
- RAG pipeline integration

**Sprint 1.2 Components:**
- UncertaintyChecker
- CostTracker
- Cost tracking middleware
- Enhanced RAG pipeline

---

## Step 1: Import All Modules

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Sprint 1.1
from rag_api.budget import ContextBudgetEnforcer
from rag_api.memory_storage import ChromaDBMemoryStorage
from rag_api.memory_api import router as memory_router
from rag_api.models import MemoryItem

# Sprint 1.2
from rag_api.uncertainty import UncertaintyChecker
from rag_api.cost import CostTracker
from rag_api.cost_middleware import CostTrackingMiddleware
from rag_api.enhanced_rag_integration import EnhancedRAGPipeline
```

---

## Step 2: Initialize Components

```python
app = FastAPI(title="Jarvis RAG API")

# Initialize all components
budget_enforcer = ContextBudgetEnforcer()
memory_storage = ChromaDBMemoryStorage()
uncertainty_checker = UncertaintyChecker()
cost_tracker = CostTracker()

# Initialize enhanced pipeline
pipeline = EnhancedRAGPipeline(
    budget_enforcer=budget_enforcer,
    memory_storage=memory_storage,
    uncertainty_checker=uncertainty_checker,
    cost_tracker=cost_tracker
)

# Include memory API router
app.include_router(memory_router)

# Add cost tracking middleware
app.add_middleware(CostTrackingMiddleware, cost_tracker=cost_tracker)
```

---

## Step 3: Update /query Endpoint

```python
@app.post("/query")
async def query(
    request: QueryRequest,
    http_request: Request
):
    """
    Enhanced RAG query with all features.
    """
    # Extract user_id (adjust based on your auth system)
    user_id = request.user_id or http_request.headers.get("X-User-ID") or "anonymous"
    
    # Perform RAG retrieval (your existing code)
    rag_chunks, rag_scores = await retrieve_rag_documents(request.message)
    
    # Process with enhanced pipeline
    result = pipeline.process_query(
        query=request.message,
        user_id=user_id,
        system_prompt=SYSTEM_PROMPT,
        history=request.history or [],
        rag_chunks=rag_chunks,
        rag_scores=rag_scores,
        project_id=request.project_id,
        private_session=request.private_session or False
    )
    
    # Check for budget exceeded error
    if "error" in result:
        return JSONResponse(
            status_code=429,
            content=result
        )
    
    # Check for uncertain response (no LLM call needed)
    if result.get("uncertain_response"):
        return result["uncertain_response"]
    
    # Call LLM with prepared context
    prepared = result["prepared_context"]
    messages = [
        {"role": "system", "content": prepared["system_prompt"]}
    ]
    messages.extend(prepared["history"])
    messages.append({"role": "user", "content": request.message})
    
    # Call your LLM
    llm_response = await call_llm(messages)
    
    # Format final response
    response = pipeline.format_response(
        llm_answer=llm_response["answer"],
        sources=llm_response.get("sources", []),
        memories=result.get("memories", []),
        uncertain=llm_response.get("uncertain", False),
        budget_warning=result.get("budget_warning"),
        cost_info=result.get("cost_info")
    )
    
    # Store cost info in request state for middleware
    http_request.state.cost_info = result.get("cost_info", {})
    
    return response
```

---

## Step 4: Add Budget Status Endpoint

```python
@app.get("/budget/status")
async def get_budget_status(
    user_id: str,
    http_request: Request
):
    """
    Get current budget status for user.
    """
    user_id = user_id or http_request.headers.get("X-User-ID") or "anonymous"
    status = cost_tracker.get_budget_status(user_id)
    return status
```

---

## Step 5: Environment Variables

Add to your `.env`:

```bash
# Context Budget
MAX_CONTEXT_TOKENS=100000
WARN_THRESHOLD=0.8

# Uncertainty Protocol
RAG_CONFIDENCE_THRESHOLD=0.6

# Cost Tracking (optional)
DAILY_TEXT_TOKENS_LIMIT=500000
DAILY_VISION_TOKENS_LIMIT=50000
DAILY_AUDIO_MINUTES_LIMIT=60.0
DAILY_DOLLARS_LIMIT=10.0

# Memory Storage
MEMORY_DB_PATH=./memory_db
```

---

## Response Format Examples

### Successful Response

```json
{
  "answer": "Based on your documents...",
  "sources": [
    {
      "document_name": "Q3 Financials",
      "chunk_index": 3,
      "text": "...",
      "score": 0.85
    }
  ],
  "memories_used": [
    {
      "id": "mem_123",
      "content": "User prefers Slack notifications",
      "type": "preference"
    }
  ],
  "uncertain": false,
  "warning": "Context usage at 85.2% (85,200/100,000 tokens).",
  "cost": {
    "tokens": 85200,
    "dollars": 0.85
  }
}
```

### Uncertain Response

```json
{
  "answer": "I don't have information about 'X' in your knowledge base.",
  "uncertain": true,
  "suggestions": [
    "search the web for this information",
    "ask you directly for clarification",
    "check if you have documents that might contain this information"
  ],
  "reason": "empty_retrieval"
}
```

### Budget Exceeded Response

```json
{
  "error": "Daily budget limit reached",
  "message": "Please try again tomorrow or contact support to increase your limit.",
  "code": "BUDGET_EXCEEDED",
  "budget_status": {
    "text_tokens": {
      "used": 500000,
      "limit": 500000,
      "remaining": 0
    }
  }
}
```

---

## Testing

### Test Uncertainty Protocol

```python
# Empty retrieval
retrieval = RetrievalResult(chunks=[], scores=[], total_chunks=0)
uncertain = uncertainty_checker.check_retrieval(retrieval, "test query")
assert uncertain is not None
assert uncertain.uncertain == True

# Low confidence
retrieval = RetrievalResult(
    chunks=[{"text": "test"}],
    scores=[0.4],  # Below threshold
    total_chunks=1
)
uncertain = uncertainty_checker.check_retrieval(retrieval, "test query")
assert uncertain is not None
```

### Test Cost Tracking

```python
# Check budget
is_allowed, error, budget = cost_tracker.check_budget(
    user_id="test_user",
    estimated_text_tokens=1000
)
assert is_allowed == True

# Track usage
budget, cost_info = cost_tracker.track_usage(
    user_id="test_user",
    text_tokens=1000
)
assert cost_info["text_tokens"] == 1000
```

---

## Next Steps

1. Integrate into your `app.py`
2. Test with evaluation suite
3. Monitor cost tracking accuracy
4. Adjust cost estimates
5. Update frontend to show budget/memory/uncertainty

---

**Status:** Ready for integration! 🚀

