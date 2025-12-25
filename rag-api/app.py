"""
Jarvis RAG API - Main Application

Complete FastAPI application integrating all components:
- Sprint 1: MVP Foundation (Budget, Memory, Uncertainty, Cost)
- Sprint 2.1: Enhanced Live Sessions (LS1A Audio Pipeline)
- Sprint 2.2 & 2.3: Browser Automation

Usage:
    uvicorn app:app --reload
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
import chromadb
from chromadb.config import Settings
from openai import AsyncOpenAI

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
# Stage B: Production Database Imports
# ============================================================================
from .storage.firestore_live_session_storage import FirestoreLiveSessionStorage
from .storage.bigquery_memory_storage import BigQueryMemoryStorage

# ============================================================================
# SPRINT 2.2 & 2.3: Browser Automation Imports
# ============================================================================
from .browser.browser_api import router as browser_router
from .browser.action_api import router as browser_action_router

# ============================================================================
# Stage D: Deep Thinking and Reasoning Imports
# ============================================================================
from .reasoning.reasoning_router import router as reasoning_router

# ============================================================================
# Stage E: Universal Knowledge Indexing & Access Imports
# ============================================================================
from .indexing.indexing_router import router as indexing_router

# ============================================================================
# Stage C: Missing Features Imports
# ============================================================================
from .media.media_router import router as media_router
from .word_processor.word_processor_router import router as word_processor_router

# ============================================================================
# Stage B: Security Imports
# ============================================================================
from .security.rate_limit import get_rate_limiter, RateLimitMiddleware
from .security.auth_router import router as auth_router

# ============================================================================
# Stage B: Performance - Caching Imports
# ============================================================================
from .cache import get_cache
from .cache.cache_middleware import CacheMiddleware

# ============================================================================
# Initialize FastAPI App
# ============================================================================
app = FastAPI(
    title="Jarvis RAG API",
    description="Complete RAG API with Memory, Budget, Live Sessions, and Browser Automation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Initialize Components (Singleton Pattern)
# ============================================================================

# Sprint 1 Components
budget_enforcer = ContextBudgetEnforcer()
uncertainty_checker = UncertaintyChecker()
cost_tracker = CostTracker()

# ============================================================================
# Database Storage Configuration
# ============================================================================
# Use Firestore for live sessions if configured, otherwise fallback to in-memory
# Use BigQuery for memory if configured, otherwise use ChromaDB
# ============================================================================

# Memory Storage: BigQuery (production) or ChromaDB (development)
use_bigquery = os.getenv("USE_BIGQUERY_MEMORY", "false").lower() == "true"
if use_bigquery:
    try:
        memory_storage = BigQueryMemoryStorage(
            project_id=os.getenv("GOOGLE_CLOUD_PROJECT"),
            dataset_id=os.getenv("BIGQUERY_DATASET", "jarvis"),
            table_id=os.getenv("BIGQUERY_MEMORY_TABLE", "memories")
        )
        print("✅ Using BigQuery for memory storage")
    except Exception as e:
        print(f"⚠️ Failed to initialize BigQuery, falling back to ChromaDB: {e}")
        memory_storage = ChromaDBMemoryStorage()
else:
    memory_storage = ChromaDBMemoryStorage()
    print("✅ Using ChromaDB for memory storage")

# Enhanced RAG Pipeline
enhanced_pipeline = EnhancedRAGPipeline(
    budget_enforcer=budget_enforcer,
    memory_storage=memory_storage,
    uncertainty_checker=uncertainty_checker,
    cost_tracker=cost_tracker
)

# Live Session Storage: Firestore (production) or InMemory (development)
use_firestore = os.getenv("USE_FIRESTORE_SESSIONS", "false").lower() == "true"
if use_firestore:
    try:
        live_session_storage = FirestoreLiveSessionStorage(
            project_id=os.getenv("GOOGLE_CLOUD_PROJECT"),
            collection_name=os.getenv("FIRESTORE_SESSIONS_COLLECTION", "live_sessions")
        )
        print("✅ Using Firestore for live session storage")
    except Exception as e:
        print(f"⚠️ Failed to initialize Firestore, falling back to in-memory: {e}")
        live_session_storage = InMemoryLiveSessionStorage()
        print("✅ Using in-memory for live session storage (fallback)")
else:
    live_session_storage = InMemoryLiveSessionStorage()
    print("✅ Using in-memory for live session storage")

# Set the storage instance for the live session API
from .live_session_api import set_session_storage
set_session_storage(live_session_storage)

# ============================================================================
# Initialize RAG and LLM Clients (Singleton Pattern)
# ============================================================================

_openai_client = None
_rag_collection = None

def get_openai_client() -> AsyncOpenAI:
    """Get or create OpenAI client."""
    global _openai_client
    if _openai_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        _openai_client = AsyncOpenAI(api_key=api_key)
    return _openai_client

def get_rag_collection():
    """Get or create RAG collection."""
    global _rag_collection
    if _rag_collection is None:
        rag_dir = os.getenv("CHROMADB_RAG_DIR", "./rag_db")
        client = chromadb.PersistentClient(
            path=rag_dir,
            settings=Settings(anonymized_telemetry=False)
        )
        _rag_collection = client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
    return _rag_collection

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

# Stage D: Deep Thinking and Reasoning
app.include_router(reasoning_router)

# Stage E: Universal Knowledge Indexing & Access
app.include_router(indexing_router)

# Stage C: Missing Features - Media Integration
app.include_router(media_router)

# Stage C: Missing Features - Word Processor
app.include_router(word_processor_router)

# Stage B: Security - Authentication
app.include_router(auth_router)

# ============================================================================
# Add Middleware
# ============================================================================

# Sprint 1.2: Cost Tracking Middleware
app.add_middleware(CostTrackingMiddleware, cost_tracker=cost_tracker)

# Stage B: Monitoring Middleware
app.add_middleware(MonitoringMiddleware)

# Stage B: Rate Limiting Middleware
rate_limiter = get_rate_limiter()
app.add_middleware(RateLimitMiddleware, rate_limiter=rate_limiter)

# Stage B: Caching Middleware (if Redis enabled)
cache = get_cache()
if cache:
    app.add_middleware(CacheMiddleware, cache_ttl=int(os.getenv("CACHE_TTL", "300")))

# ============================================================================
# Root & Health Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Jarvis RAG API",
        "version": "1.0.0",
        "status": "operational",
        "features": [
            "Context Budget Enforcement",
            "Memory System (CRUD + RAG)",
            "Uncertainty Protocol",
            "Cost Tracking",
            "Live Sessions (LS1A)",
            "Browser Automation"
        ],
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "memory": "/memory",
            "live_sessions": "/live-sessions",
            "ls1a": "/ls1a/ws/{session_id}",
            "browser": "/browser"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return health_checker.check_health()

@app.get("/metrics")
async def metrics():
    """Metrics endpoint."""
    metrics_collector = get_metrics_collector()
    return metrics_collector.get_all_metrics()

# ============================================================================
# Enhanced Query Endpoint (Sprint 1 Integration)
# ============================================================================

class QueryRequest(BaseModel):
    """Request model for RAG query."""
    message: str
    user_id: str
    project_id: Optional[str] = None
    history: Optional[List[Dict[str, str]]] = None
    private_session: bool = False


class QueryResponse(BaseModel):
    """Response model for RAG query."""
    answer: str
    sources: List[Dict]
    uncertain: bool
    suggestions: Optional[List[str]] = None
    memories_used: Optional[List[Dict]] = None
    warning: Optional[str] = None
    cost: Optional[Dict] = None


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Enhanced RAG query endpoint with all Sprint 1 features:
    - Context budget enforcement
    - Memory retrieval and injection
    - Uncertainty protocol
    - Cost tracking
    
    NOTE: This endpoint requires you to implement:
    1. RAG document retrieval (replace retrieve_rag_documents)
    2. LLM API call (replace call_llm)
    
    See: rag-api/COMPLETE_INTEGRATION_GUIDE.md for details.
    """
    async def retrieve_rag_documents(query: str):
        """
        Retrieve relevant documents from ChromaDB RAG system.
        
        Returns:
            Tuple of (chunks, scores) where:
            - chunks: List of document chunks with 'text' field
            - scores: List of relevance scores (0.0-1.0)
        """
        try:
            collection = get_rag_collection()
            
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
                    distance = results["distances"][0][i] if "distances" in results and results["distances"] else 0.5
                    similarity = max(0.0, 1.0 - distance)  # Ensure score is 0-1
                    
                    chunks.append({
                        "text": doc,
                        "score": similarity,
                        "metadata": results["metadatas"][0][i] if "metadatas" in results and results["metadatas"] else {}
                    })
                    scores.append(similarity)
            
            # If no results found, return empty lists
            return chunks, scores
            
        except Exception as e:
            # Log error but return empty results instead of failing
            print(f"Error retrieving RAG documents: {str(e)}")
            return [], []
    
    async def call_llm(messages: List[Dict[str, str]]):
        """
        Call OpenAI API.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
        
        Returns:
            Dict with 'answer' and optional 'sources'
        """
        try:
            client = get_openai_client()
            model = os.getenv("OPENAI_MODEL", "gpt-4")
            
            # Call OpenAI API
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
                max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
            )
            
            # Extract answer
            answer = response.choices[0].message.content
            
            # Track usage in request state if available
            # Note: request is not available in this scope, usage tracking handled by middleware
            
            return {
                "answer": answer,
                "sources": []  # Can be extended to include sources
            }
            
        except Exception as e:
            # Log error and raise HTTP exception
            error_msg = f"LLM API call failed: {str(e)}"
            print(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)
    
    try:
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
            raise HTTPException(status_code=429, detail=result["error"])
        
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
        
        return QueryResponse(
            answer=response["answer"],
            sources=response.get("sources", []),
            uncertain=response.get("uncertain", False),
            suggestions=response.get("suggestions"),
            memories_used=response.get("memories", []),
            warning=response.get("warning"),
            cost=response.get("cost")
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ============================================================================
# Budget Status Endpoint
# ============================================================================

@app.get("/budget/status")
async def get_budget_status(user_id: str):
    """
    Get budget status for a user.
    
    Returns:
        Dict with budget utilization for text tokens, audio minutes, and dollars.
    """
    status = cost_tracker.get_daily_status(user_id)
    return {
        "user_id": user_id,
        "text_tokens": {
            "used": status.get("tokens_used", 0),
            "limit": status.get("tokens_limit", 500000),
            "utilization": status.get("tokens_used", 0) / max(status.get("tokens_limit", 500000), 1)
        },
        "audio_minutes": {
            "used": status.get("audio_minutes_used", 0.0),
            "limit": status.get("audio_minutes_limit", 60.0),
            "utilization": status.get("audio_minutes_used", 0.0) / max(status.get("audio_minutes_limit", 60.0), 1)
        },
        "dollars": {
            "used": status.get("dollars_used", 0.0),
            "limit": status.get("dollars_limit", 10.0),
            "utilization": status.get("dollars_used", 0.0) / max(status.get("dollars_limit", 10.0), 1)
        }
    }


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )


# ============================================================================
# Startup/Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    print("🚀 Jarvis RAG API starting up...")
    print(f"✅ Memory storage initialized")
    print(f"✅ Budget enforcer initialized")
    print(f"✅ Cost tracker initialized")
    print(f"✅ All routers loaded")
    print("🎉 API ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("🛑 Jarvis RAG API shutting down...")
    # Add any cleanup logic here

