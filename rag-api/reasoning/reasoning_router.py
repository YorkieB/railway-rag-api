"""
Reasoning REST API Router
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any

from .reasoning_engine import ReasoningEngine
from .models import ReasoningResult, ReasoningTrace

router = APIRouter(prefix="/reasoning", tags=["reasoning"])

# Initialize reasoning engine (singleton)
_reasoning_engine: Optional[ReasoningEngine] = None

def get_reasoning_engine() -> ReasoningEngine:
    """Get reasoning engine instance."""
    global _reasoning_engine
    if _reasoning_engine is None:
        _reasoning_engine = ReasoningEngine()
    return _reasoning_engine

# Request/Response Models
class ReasoningRequest(BaseModel):
    query: str
    method: str = "cot"  # "cot", "reflection", "self_consistency", "tot", "react"
    context: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None

class ReasoningResponse(BaseModel):
    answer: str
    confidence: float
    method: str
    trace_id: str
    steps_count: int

# Endpoints
@router.post("/reason", response_model=ReasoningResponse)
async def reason(request: ReasoningRequest, engine: ReasoningEngine = Depends(get_reasoning_engine)):
    """Perform reasoning on a query."""
    try:
        result = await engine.reason(
            query=request.query,
            method=request.method,
            context=request.context,
            **(request.parameters or {})
        )
        
        return ReasoningResponse(
            answer=result.answer,
            confidence=result.confidence,
            method=request.method,
            trace_id=result.trace.id,
            steps_count=len(result.trace.steps)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/traces/{trace_id}")
async def get_trace(trace_id: str, engine: ReasoningEngine = Depends(get_reasoning_engine)):
    """Get reasoning trace by ID."""
    # In production, store traces in database
    # For now, return error
    raise HTTPException(status_code=501, detail="Trace storage not yet implemented")

@router.get("/methods")
async def list_methods():
    """List available reasoning methods."""
    return {
        "methods": [
            {
                "id": "cot",
                "name": "Chain-of-Thought",
                "description": "Step-by-step reasoning"
            },
            {
                "id": "reflection",
                "name": "Reflection",
                "description": "Self-critique and refinement"
            },
            {
                "id": "self_consistency",
                "name": "Self-Consistency",
                "description": "Multiple paths, consensus answer"
            },
            {
                "id": "tot",
                "name": "Tree of Thoughts",
                "description": "Explore multiple branches"
            },
            {
                "id": "react",
                "name": "ReAct",
                "description": "Reasoning + Acting with tools"
            }
        ]
    }

