"""
Live Session REST API

FastAPI endpoints for managing live sessions.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Literal, Dict
from pydantic import BaseModel
from .models import LiveSession
from .live_session_storage import LiveSessionStorage, InMemoryLiveSessionStorage
from uuid import uuid4
from datetime import datetime
import os

router = APIRouter(prefix="/live-sessions", tags=["live-sessions"])


# Global storage instance (set by app.py)
_session_storage: Optional[LiveSessionStorage] = None

def set_session_storage(storage: LiveSessionStorage):
    """Set the global session storage instance."""
    global _session_storage
    _session_storage = storage

def get_session_storage() -> LiveSessionStorage:
    """
    Dependency to get session storage instance.
    
    Uses the global instance set by app.py, or falls back to in-memory.
    """
    global _session_storage
    if _session_storage is None:
        _session_storage = InMemoryLiveSessionStorage()
    return _session_storage


# Request/Response Models
class LiveSessionCreate(BaseModel):
    """Request model for creating a live session."""
    user_id: str
    mode: Optional[Literal["LS1A", "LS1B", "LS1C", "LS2", "LS3"]] = "LS1A"
    recording_consent: bool = False
    secrets_blurred: Optional[List[str]] = None


class LiveSessionUpdate(BaseModel):
    """Request model for updating a live session."""
    state: Optional[Literal["IDLE", "CONNECTING", "LIVE", "PAUSED", "ENDED"]] = None
    transcript_partial: Optional[str] = None
    audio_minutes_used: Optional[float] = None
    frames_processed: Optional[int] = None
    daily_budget_remaining: Optional[Dict[str, float]] = None


class LiveSessionResponse(BaseModel):
    """Response model for live session."""
    session: LiveSession


class LiveSessionListResponse(BaseModel):
    """Response model for listing live sessions."""
    sessions: List[LiveSession]
    total: int


# Endpoints
@router.post("", response_model=LiveSessionResponse, status_code=201)
async def create_session(
    session_data: LiveSessionCreate,
    storage: LiveSessionStorage = Depends(get_session_storage)
):
    """
    Create a new live session.
    
    Returns:
        Created session in CONNECTING state
    """
    # Create new session
    session = LiveSession(
        id=str(uuid4()),
        user_id=session_data.user_id,
        mode=session_data.mode,
        state="IDLE",  # Will transition to CONNECTING on create
        recording_consent=session_data.recording_consent,
        secrets_blurred=session_data.secrets_blurred or []
    )
    
    # Create in storage (will transition to CONNECTING)
    created = storage.create(session)
    
    return LiveSessionResponse(session=created)


@router.get("/{session_id}", response_model=LiveSessionResponse)
async def get_session(
    session_id: str,
    user_id: str = Query(..., description="User ID for ownership validation"),
    storage: LiveSessionStorage = Depends(get_session_storage)
):
    """
    Get a live session by ID.
    
    Returns:
        Session if found and owned by user
    """
    session = storage.get(session_id, user_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found or access denied"
        )
    
    return LiveSessionResponse(session=session)


@router.get("", response_model=LiveSessionListResponse)
async def list_sessions(
    user_id: str = Query(..., description="User ID"),
    state: Optional[str] = Query(None, description="Filter by state"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of sessions"),
    storage: LiveSessionStorage = Depends(get_session_storage)
):
    """
    List live sessions for a user.
    
    Returns:
        List of sessions, optionally filtered by state
    """
    sessions = storage.list(user_id=user_id, state=state, limit=limit)
    
    return LiveSessionListResponse(sessions=sessions, total=len(sessions))


@router.put("/{session_id}/pause", response_model=LiveSessionResponse)
async def pause_session(
    session_id: str,
    user_id: str = Query(..., description="User ID for ownership validation"),
    storage: LiveSessionStorage = Depends(get_session_storage)
):
    """
    Pause a live session.
    
    Valid transitions:
    - LIVE → PAUSED
    - PAUSED → PAUSED (no-op)
    
    Returns:
        Updated session
    """
    session = storage.get(session_id, user_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found or access denied"
        )
    
    # Attempt state transition
    if session.state == "LIVE":
        updated = storage.update(session_id, user_id, {"state": "PAUSED"})
        if not updated:
            raise HTTPException(
                status_code=400,
                detail="Cannot pause session in current state"
            )
    elif session.state == "PAUSED":
        # Already paused, no-op
        updated = session
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot pause session in {session.state} state"
        )
    
    return LiveSessionResponse(session=updated)


@router.put("/{session_id}/resume", response_model=LiveSessionResponse)
async def resume_session(
    session_id: str,
    user_id: str = Query(..., description="User ID for ownership validation"),
    storage: LiveSessionStorage = Depends(get_session_storage)
):
    """
    Resume a paused live session.
    
    Valid transitions:
    - PAUSED → LIVE
    - LIVE → LIVE (no-op)
    
    Returns:
        Updated session
    """
    session = storage.get(session_id, user_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found or access denied"
        )
    
    # Attempt state transition
    if session.state == "PAUSED":
        updated = storage.update(session_id, user_id, {"state": "LIVE"})
        if not updated:
            raise HTTPException(
                status_code=400,
                detail="Cannot resume session in current state"
            )
    elif session.state == "LIVE":
        # Already live, no-op
        updated = session
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot resume session in {session.state} state"
        )
    
    return LiveSessionResponse(session=updated)


@router.delete("/{session_id}", status_code=204)
async def end_session(
    session_id: str,
    user_id: str = Query(..., description="User ID for ownership validation"),
    storage: LiveSessionStorage = Depends(get_session_storage)
):
    """
    End a live session.
    
    Valid transitions:
    - LIVE → ENDED
    - PAUSED → ENDED
    - ENDED → ENDED (no-op)
    
    Returns:
        204 No Content on success
    """
    session = storage.get(session_id, user_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found or access denied"
        )
    
    # Transition to ENDED if not already ended
    if session.state != "ENDED":
        storage.update(session_id, user_id, {"state": "ENDED"})
    
    # Delete session (or keep for history - adjust based on requirements)
    storage.delete(session_id, user_id)
    
    return None


@router.put("/{session_id}", response_model=LiveSessionResponse)
async def update_session(
    session_id: str,
    updates: LiveSessionUpdate,
    user_id: str = Query(..., description="User ID for ownership validation"),
    storage: LiveSessionStorage = Depends(get_session_storage)
):
    """
    Update a live session.
    
    Can update:
    - transcript_partial
    - audio_minutes_used
    - frames_processed
    - daily_budget_remaining
    - state (with validation)
    
    Returns:
        Updated session
    """
    session = storage.get(session_id, user_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found or access denied"
        )
    
    # Prepare update dict (exclude None values)
    update_dict = {k: v for k, v in updates.dict().items() if v is not None}
    
    if not update_dict:
        raise HTTPException(
            status_code=400,
            detail="No updates provided"
        )
    
    # Update session
    updated = storage.update(session_id, user_id, update_dict)
    if not updated:
        raise HTTPException(
            status_code=400,
            detail="Update failed (invalid state transition or other error)"
        )
    
    return LiveSessionResponse(session=updated)

