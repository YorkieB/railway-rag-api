"""
Complete Integrated App Example

This file shows how to integrate ALL Sprint 1, 2.1, 2.2, 2.3, and 2.4 components
into a single FastAPI application.

IMPORTANT: This is an EXAMPLE file. Use this as a reference for integrating
into your actual app.py.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import os

# ============================================================================
# SPRINT 1: MVP Foundation Imports
# ============================================================================
from .budget import ContextBudgetEnforcer
from .memory_storage import ChromaDBMemoryStorage
from .memory_api import router as memory_router
from .uncertainty import UncertaintyChecker
from .cost import CostTracker
from .cost_middleware import CostTrackingMiddleware
from .enhanced_rag_integration import EnhancedRAGPipeline

# ============================================================================
# SPRINT 2.1: Enhanced Live Sessions Imports
# ============================================================================
from .live_session_storage import InMemoryLiveSessionStorage
from .live_session_api import router as live_session_router
from .ls1a_router import router as ls1a_router

# ============================================================================
# SPRINT 2.2 & 2.3: Browser Automation Imports
# ============================================================================
from .browser.browser_api import router as browser_router
from .browser.action_api import router as browser_action_router

# ============================================================================
# Initialize FastAPI App
# ============================================================================
app = FastAPI(
    title="Jarvis RAG API",
    description="Complete RAG API with Memory, Budget, Live Sessions, and Browser Automation",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Initialize Components
# ============================================================================

# Sprint 1 Components
budget_enforcer = ContextBudgetEnforcer()
memory_storage = ChromaDBMemoryStorage()
uncertainty_checker = UncertaintyChecker()
cost_tracker = CostTracker()

# Enhanced RAG Pipeline
enhanced_pipeline = EnhancedRAGPipeline(
    budget_enforcer=budget_enforcer,
    memory_storage=memory_storage,
    uncertainty_checker=uncertainty_checker,
    cost_tracker=cost_tracker
)

# Sprint 2.1 Components
live_session_storage = InMemoryLiveSessionStorage()

# ============================================================================
# Include Routers
# ============================================================================

# Sprint 1: Memory API
app.include_router(memory_router)

# Sprint 2.1: Live Sessions
app.include_router(live_session_router)

# Sprint 2.1: LS1A Audio Pipeline
app.include_router(ls1a_router, prefix="/ls1a")

# Sprint 2.2 & 2.3: Browser Automation
app.include_router(browser_router)
app.include_router(browser_action_router)

# ============================================================================
# Add Middleware
# ============================================================================

# Sprint 1.2: Cost Tracking Middleware
app.add_middleware(CostTrackingMiddleware, cost_tracker=cost_tracker)

# ============================================================================
# Enhanced Query Endpoint (Sprint 1 Integration)
# ============================================================================

class QueryRequest(BaseModel):
    message: str
    user_id: str
    project_id: Optional[str] = None
    history: Optional[List[Dict[str, str]]] = None
    private_session: bool = False


class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict]
    uncertain: bool
    suggestions: Optional[List[str]] = None
    memories_used: Optional[List[Dict]] = None
    warning: Optional[str] = None
    cost: Optional[Dict] = None


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest, http_request: Request):
    """
    Enhanced RAG query endpoint with all Sprint 1 features:
    - Context budget enforcement
    - Memory retrieval and injection
    - Uncertainty protocol
    - Cost tracking
    """
    # Example RAG retrieval (replace with your actual implementation)
    async def retrieve_rag_documents(query: str):
        # Placeholder - replace with actual ChromaDB/vector search
        return [{"text": "Example document", "score": 0.85}], [0.85]
    
    # Example LLM call (replace with your actual implementation)
    async def call_llm(messages: List[Dict[str, str]]):
        # Placeholder - replace with actual OpenAI/Gemini API call
        return {
            "answer": "This is a placeholder response. Replace with actual LLM call.",
            "sources": []
        }
    
    # Perform RAG retrieval
    rag_chunks, rag_scores = await retrieve_rag_documents(request.message)
    
    # Process with enhanced pipeline
    result = enhanced_pipeline.process_query(
        query=request.message,
        user_id=request.user_id,
        system_prompt="You are a helpful AI assistant.",
        history=request.history or [],
        rag_chunks=rag_chunks,
        rag_scores=rag_scores,
        project_id=request.project_id,
        private_session=request.private_session
    )
    
    # Check for budget exceeded error
    if "error" in result:
        return JSONResponse(status_code=429, content=result)
    
    # Check for uncertain response
    if result.get("uncertain_response"):
        uncertain = result["uncertain_response"]
        return QueryResponse(
            answer=uncertain["answer"],
            sources=[],
            uncertain=True,
            suggestions=uncertain.get("suggestions", []),
            memories_used=result.get("memories", [])
        )
    
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
    response = enhanced_pipeline.format_response(
        llm_answer=llm_response["answer"],
        sources=llm_response.get("sources", []),
        memories=result.get("memories", []),
        uncertain=llm_response.get("uncertain", False),
        budget_warning=result.get("budget_warning"),
        cost_info=result.get("cost_info")
    )
    
    # Store cost info in request state for middleware
    http_request.state.cost_info = result.get("cost_info", {})
    
    return QueryResponse(**response)

# ============================================================================
# Health Check & Info Endpoints
# ============================================================================

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "components": {
            "budget_enforcer": "ok",
            "memory_storage": "ok",
            "uncertainty_checker": "ok",
            "cost_tracker": "ok",
            "live_session_storage": "ok",
            "browser_automation": "ok"
        }
    }


@app.get("/")
async def root():
    """API information endpoint."""
    return {
        "name": "Jarvis RAG API",
        "version": "1.0.0",
        "features": [
            "Context budget enforcement",
            "Memory system",
            "Uncertainty protocol",
            "Cost tracking",
            "Live sessions (LS1A)",
            "Browser automation"
        ],
        "endpoints": {
            "query": "POST /query",
            "memory": "GET/POST/PUT/DELETE /memory",
            "live_sessions": "GET/POST/PUT/DELETE /live-sessions",
            "ls1a": "WS /ls1a/ws/{session_id}",
            "browser": "GET/POST/DELETE /browser/sessions",
            "browser_actions": "POST /browser/sessions/{id}/actions/*",
            "budget": "GET /budget/status",
            "health": "GET /health"
        }
    }


@app.get("/budget/status")
async def get_budget_status(user_id: str):
    """Get current budget status for user."""
    status = cost_tracker.get_budget_status(user_id)
    return status


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000"))
    )

