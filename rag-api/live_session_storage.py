"""
Live Session Storage Interface

Abstract base class for live session storage implementations.
Supports in-memory (for development) and can be extended for Firestore/BigQuery.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from .models import LiveSession


class LiveSessionStorage(ABC):
    """
    Abstract base class for live session storage.
    
    Implementations should provide:
    - In-memory storage (default, for development)
    - Firestore-based storage (optional)
    - BigQuery-based storage (optional)
    """
    
    @abstractmethod
    def create(self, session: LiveSession) -> LiveSession:
        """
        Create a new live session.
        
        Args:
            session: Live session to create
            
        Returns:
            Created session with generated ID
        """
        pass
    
    @abstractmethod
    def get(self, session_id: str, user_id: str) -> Optional[LiveSession]:
        """
        Get a live session by ID.
        
        Args:
            session_id: Session ID
            user_id: User ID (for ownership validation)
            
        Returns:
            Live session if found, None otherwise
        """
        pass
    
    @abstractmethod
    def list(
        self,
        user_id: str,
        state: Optional[str] = None,
        limit: int = 100
    ) -> List[LiveSession]:
        """
        List live sessions for a user.
        
        Args:
            user_id: User ID
            state: Optional state filter (None = all states)
            limit: Maximum number of sessions to return
            
        Returns:
            List of live sessions
        """
        pass
    
    @abstractmethod
    def update(self, session_id: str, user_id: str, updates: dict) -> Optional[LiveSession]:
        """
        Update a live session.
        
        Args:
            session_id: Session ID
            user_id: User ID (for ownership validation)
            updates: Dictionary of fields to update
            
        Returns:
            Updated session if found, None otherwise
        """
        pass
    
    @abstractmethod
    def delete(self, session_id: str, user_id: str) -> bool:
        """
        Delete a live session.
        
        Args:
            session_id: Session ID
            user_id: User ID (for ownership validation)
            
        Returns:
            True if deleted, False otherwise
        """
        pass


class InMemoryLiveSessionStorage(LiveSessionStorage):
    """
    In-memory storage for live sessions (development/testing).
    
    For production, implement FirestoreLiveSessionStorage or BigQueryLiveSessionStorage.
    """
    
    def __init__(self):
        """Initialize in-memory storage."""
        self._sessions: dict[str, LiveSession] = {}
        self._user_sessions: dict[str, list[str]] = {}  # user_id -> [session_ids]
    
    def create(self, session: LiveSession) -> LiveSession:
        """Create a new live session."""
        # Ensure session is in CONNECTING state initially
        if session.state == "IDLE":
            session.transition_to("CONNECTING")
        
        self._sessions[session.id] = session
        
        # Track by user
        if session.user_id not in self._user_sessions:
            self._user_sessions[session.user_id] = []
        if session.id not in self._user_sessions[session.user_id]:
            self._user_sessions[session.user_id].append(session.id)
        
        return session
    
    def get(self, session_id: str, user_id: str) -> Optional[LiveSession]:
        """Get a live session by ID."""
        session = self._sessions.get(session_id)
        if session and session.user_id == user_id:
            return session
        return None
    
    def list(
        self,
        user_id: str,
        state: Optional[str] = None,
        limit: int = 100
    ) -> List[LiveSession]:
        """List live sessions for a user."""
        session_ids = self._user_sessions.get(user_id, [])
        sessions = [self._sessions[sid] for sid in session_ids if sid in self._sessions]
        
        # Filter by state if provided
        if state:
            sessions = [s for s in sessions if s.state == state]
        
        # Sort by started_at (newest first)
        sessions.sort(key=lambda s: s.started_at, reverse=True)
        
        return sessions[:limit]
    
    def update(self, session_id: str, user_id: str, updates: dict) -> Optional[LiveSession]:
        """Update a live session."""
        session = self.get(session_id, user_id)
        if not session:
            return None
        
        # Update fields
        for key, value in updates.items():
            if hasattr(session, key):
                # Handle state transitions
                if key == "state" and isinstance(value, str):
                    if session.transition_to(value):
                        # State transition successful, timestamp updated automatically
                        pass
                    else:
                        # Invalid transition, revert
                        return None
                else:
                    setattr(session, key, value)
        
        # Update updated_at if it exists
        if hasattr(session, "updated_at"):
            session.updated_at = datetime.utcnow()
        
        self._sessions[session_id] = session
        return session
    
    def delete(self, session_id: str, user_id: str) -> bool:
        """Delete a live session."""
        session = self.get(session_id, user_id)
        if not session:
            return False
        
        # Remove from storage
        del self._sessions[session_id]
        
        # Remove from user tracking
        if user_id in self._user_sessions:
            if session_id in self._user_sessions[user_id]:
                self._user_sessions[user_id].remove(session_id)
        
        return True

