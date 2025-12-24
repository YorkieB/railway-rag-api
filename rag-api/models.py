"""
Data Models for RAG API

Pydantic models for request/response validation and data structures.
"""

from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
import uuid


class MemoryItem(BaseModel):
    """Memory item model for persistent conversation memory"""
    
    id: str
    user_id: str
    project_id: Optional[str] = None  # None = global memory (accessible across projects)
    content: str
    memory_type: str  # "fact", "preference", "decision"
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def create(
        cls, 
        user_id: str, 
        content: str, 
        memory_type: str, 
        project_id: Optional[str] = None
    ) -> "MemoryItem":
        """
        Create new memory item
        
        Args:
            user_id: User identifier
            content: Memory content
            memory_type: Type of memory ("fact", "preference", "decision")
            project_id: Optional project identifier (None = global memory)
            
        Returns:
            New MemoryItem instance
        """
        now = datetime.now()
        return cls(
            id=str(uuid.uuid4()),
            user_id=user_id,
            project_id=project_id,
            content=content,
            memory_type=memory_type,
            created_at=now,
            updated_at=now
        )
    
    def update(self, content: Optional[str] = None, memory_type: Optional[str] = None):
        """
        Update memory item
        
        Args:
            content: New content (optional)
            memory_type: New memory type (optional)
        """
        if content is not None:
            self.content = content
        if memory_type is not None:
            self.memory_type = memory_type
        self.updated_at = datetime.now()


class MemoryCreateRequest(BaseModel):
    """Request model for creating a memory"""
    user_id: str
    content: str
    memory_type: str  # "fact", "preference", "decision"
    project_id: Optional[str] = None


class MemoryUpdateRequest(BaseModel):
    """Request model for updating a memory"""
    content: Optional[str] = None
    memory_type: Optional[str] = None


class MemorySearchRequest(BaseModel):
    """Request model for searching memories"""
    user_id: str
    query: str
    project_id: Optional[str] = None
    top_k: int = 5


class MemoryListRequest(BaseModel):
    """Request model for listing memories"""
    user_id: str
    project_id: Optional[str] = None


class LiveSession(BaseModel):
    """Live session model with state machine and mode support"""
    
    session_id: str
    user_id: str
    state: str = "IDLE"  # IDLE, CONNECTING, LIVE, PAUSED, ENDED
    mode: str = "LS1A"  # LS1A, LS1B, LS1C, LS2, LS3
    created_at: datetime
    updated_at: datetime
    
    # Session metrics
    audio_minutes_used: float = 0.0
    frames_processed: int = 0
    daily_budget_remaining: Optional[float] = None
    recording_consent: bool = False
    
    # LS3-specific fields
    frame_sampling_rate: float = 1.0  # fps (default 1fps)
    vision_tokens_used: int = 0
    daily_vision_tokens_limit: int = 50000  # 50K tokens default
    
    def transition_to(self, new_state: str):
        """Transition session to new state"""
        valid_transitions = {
            "IDLE": ["CONNECTING"],
            "CONNECTING": ["LIVE", "ENDED"],
            "LIVE": ["PAUSED", "ENDED"],
            "PAUSED": ["LIVE", "ENDED"],
            "ENDED": []  # Terminal state
        }
        
        if new_state not in valid_transitions.get(self.state, []):
            raise ValueError(f"Invalid state transition from {self.state} to {new_state}")
        
        self.state = new_state
        self.updated_at = datetime.now()
    
    @classmethod
    def create(
        cls,
        session_id: str,
        user_id: str,
        mode: str = "LS1A",
        recording_consent: bool = False
    ) -> "LiveSession":
        """Create new live session"""
        now = datetime.now()
        return cls(
            session_id=session_id,
            user_id=user_id,
            state="IDLE",
            mode=mode,
            created_at=now,
            updated_at=now,
            recording_consent=recording_consent
        )


class LiveSessionCreateRequest(BaseModel):
    """Request model for creating a live session"""
    user_id: str
    mode: str = "LS1A"  # LS1A, LS1B, LS1C, LS2, LS3
    recording_consent: bool = False
    frame_sampling_rate: Optional[float] = None


class ImageGenerationRequest(BaseModel):
    """Request model for image generation"""
    prompt: str
    size: str = "1024x1024"  # 1024x1024, 1792x1024, 1024x1792
    quality: str = "standard"  # standard, hd
    style: str = "vivid"  # vivid, natural
    n: int = 1  # Number of images (DALL-E 3 only supports 1)


class ImageEditRequest(BaseModel):
    """Request model for image editing"""
    image_id: str
    prompt: str
    mask_path: Optional[str] = None
    size: str = "1024x1024"
    n: int = 1


class ImageVariationsRequest(BaseModel):
    """Request model for image variations"""
    image_id: str
    n: int = 1
    size: str = "1024x1024"


class ImageAnalysisRequest(BaseModel):
    """Request model for image analysis"""
    image_id: str
    prompt: Optional[str] = None


class VideoGenerationRequest(BaseModel):
    """Request model for video generation"""
    prompt: str
    duration: int = 5  # seconds
    resolution: str = "720p"  # 720p, 1080p
    fps: int = 24


class ChartGenerationRequest(BaseModel):
    """Request model for chart generation"""
    chart_type: str  # line, bar, pie, scatter, area, heatmap
    data: Dict  # Chart data
    title: str
    x_label: Optional[str] = None
    y_label: Optional[str] = None
    options: Optional[Dict] = None


class SpotifyPlaylistCreateRequest(BaseModel):
    """Request model for creating Spotify playlist"""
    name: str
    description: Optional[str] = None
    public: bool = False
    tracks: List[str] = []  # Spotify track URIs


class SmartPlaylistRequest(BaseModel):
    """Request model for AI-powered playlist creation"""
    description: str  # Natural language description
    track_count: int = 20
    include_genres: Optional[List[str]] = None
    exclude_genres: Optional[List[str]] = None




class ForgotPasswordRequest(BaseModel):
    """Request model for forgot password"""
    email: str


class ResetPasswordRequest(BaseModel):
    """Request model for reset password"""
    token: str
    new_password: str


class CreateUserRequest(BaseModel):
    """Request model for creating user (admin only)"""
    email: str
    password: str
    username: Optional[str] = None
    is_admin: bool = False


class UpdateUserRequest(BaseModel):
    """Request model for updating user (admin only)"""
    email: Optional[str] = None
    username: Optional[str] = None


class ResetUserPasswordRequest(BaseModel):
    """Request model for resetting user password (admin only)"""
    new_password: str


class SetAdminRequest(BaseModel):
    """Request model for setting admin status (admin only)"""
    is_admin: bool


class ProjectShareRequest(BaseModel):
    """Request model for sharing project"""
    user_id: str
    permission: str  # "read", "write", "admin"
    user_id: str
    mode: str = "LS1A"  # LS1A, LS1B, LS1C, LS2, LS3
    recording_consent: bool = False
    frame_sampling_rate: Optional[float] = None  # For LS3 mode

