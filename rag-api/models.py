"""
Data Models for Jarvis RAG API

Defines Pydantic models for MemoryItem and LiveSession.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Literal, Dict, List
from datetime import datetime
from uuid import uuid4


class MemoryItem(BaseModel):
    """
    Memory item model for storing user preferences, facts, and decisions.
    
    Attributes:
        id: Unique identifier (UUID)
        user_id: User who owns this memory
        project_id: Optional project scope (None = global memory)
        content: Memory content text
        memory_type: Type of memory ("fact", "preference", "decision")
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    project_id: Optional[str] = None  # None = global memory
    content: str
    memory_type: Literal["fact", "preference", "decision"] = "fact"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('content')
    def content_not_empty(cls, v):
        """Validate content is not empty."""
        if not v or not v.strip():
            raise ValueError("Memory content cannot be empty")
        return v.strip()
    
    @validator('memory_type')
    def validate_memory_type(cls, v):
        """Validate memory type is one of allowed values."""
        allowed = ["fact", "preference", "decision"]
        if v not in allowed:
            raise ValueError(f"memory_type must be one of {allowed}")
        return v
    
    class Config:
        """Pydantic config."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MemoryCreateRequest(BaseModel):
    """Request model for creating a memory."""
    user_id: str
    project_id: Optional[str] = None
    content: str
    memory_type: Literal["fact", "preference", "decision"] = "fact"


class MemoryUpdateRequest(BaseModel):
    """Request model for updating a memory."""
    content: Optional[str] = None
    memory_type: Optional[Literal["fact", "preference", "decision"]] = None
    project_id: Optional[str] = None


class MemorySearchRequest(BaseModel):
    """Request model for searching memories."""
    user_id: str
    query: str
    project_id: Optional[str] = None
    memory_type: Optional[Literal["fact", "preference", "decision"]] = None
    limit: int = Field(default=10, ge=1, le=50)


class MemoryListResponse(BaseModel):
    """Response model for listing memories."""
    memories: List[MemoryItem]
    total: int


class MemorySearchResponse(BaseModel):
    """Response model for memory search."""
    memories: List[MemoryItem]
    query: str
    total: int


class LiveSession(BaseModel):
    """
    Live session model for tracking real-time AI interactions.
    
    Attributes:
        id: Unique session identifier
        user_id: User who owns this session
        state: Current session state
        mode: Session mode (LS1A, LS1B, LS1C, LS2, LS3)
        started_at: Session start timestamp
        paused_at: Optional pause timestamp
        ended_at: Optional end timestamp
        transcript_partial: Real-time transcript (during LIVE/PAUSED)
        transcript_final: Finalized transcript (on ENDED)
        audio_minutes_used: Cumulative audio minutes consumed
        frames_processed: Number of video frames processed (for LS2/LS3)
        daily_budget_remaining: Remaining daily budget by resource type
        recording_consent: Whether raw AV is stored
        secrets_blurred: List of regex patterns for blurred secrets
        transcript_url: GCS URL for transcript storage
        recording_url: GCS URL for recording storage (if consented)
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    state: Literal["IDLE", "CONNECTING", "LIVE", "PAUSED", "ENDED"] = "IDLE"
    mode: Literal["LS1A", "LS1B", "LS1C", "LS2", "LS3"] = "LS1A"
    started_at: datetime = Field(default_factory=datetime.utcnow)
    paused_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    transcript_partial: str = ""
    transcript_final: Optional[str] = None
    audio_minutes_used: float = 0.0
    frames_processed: int = 0
    daily_budget_remaining: Dict[str, float] = Field(default_factory=lambda: {
        "audioMin": 60.0,
        "videoTokens": 50000.0,
        "screenTokens": 50000.0
    })
    recording_consent: bool = False
    secrets_blurred: List[str] = Field(default_factory=list)
    transcript_url: Optional[str] = None
    recording_url: Optional[str] = None
    
    def can_transition_to(self, new_state: str) -> bool:
        """
        Check if state transition is valid.
        
        Valid transitions:
        - IDLE → CONNECTING
        - CONNECTING → LIVE
        - LIVE → PAUSED
        - PAUSED → LIVE
        - LIVE/PAUSED → ENDED
        - ENDED: Terminal (no transitions)
        """
        transitions = {
            "IDLE": ["CONNECTING"],
            "CONNECTING": ["LIVE"],
            "LIVE": ["PAUSED", "ENDED"],
            "PAUSED": ["LIVE", "ENDED"],
            "ENDED": []  # Terminal state
        }
        return new_state in transitions.get(self.state, [])
    
    def transition_to(self, new_state: str) -> bool:
        """
        Attempt to transition to new state.
        
        Returns:
            True if transition successful, False otherwise
        """
        if not self.can_transition_to(new_state):
            return False
        
        old_state = self.state
        self.state = new_state
        
        # Update timestamps based on state
        if new_state == "LIVE" and old_state == "CONNECTING":
            self.started_at = datetime.utcnow()
        elif new_state == "PAUSED":
            self.paused_at = datetime.utcnow()
        elif new_state == "ENDED":
            self.ended_at = datetime.utcnow()
            if self.transcript_partial and not self.transcript_final:
                self.transcript_final = self.transcript_partial
        
        return True
    
    class Config:
        """Pydantic config."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

