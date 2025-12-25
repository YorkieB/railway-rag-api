"""
Firestore-based Live Session Storage

Production-ready storage implementation using Google Cloud Firestore.
"""

from typing import List, Optional
from datetime import datetime
import os

try:
    from google.cloud import firestore
    FIRESTORE_AVAILABLE = True
except ImportError:
    FIRESTORE_AVAILABLE = False
    firestore = None

from ..models import LiveSession
from ..live_session_storage import LiveSessionStorage


class FirestoreLiveSessionStorage(LiveSessionStorage):
    """
    Firestore-based live session storage.
    
    Requires:
    - google-cloud-firestore package
    - GOOGLE_APPLICATION_CREDENTIALS environment variable (or default credentials)
    - Firestore project ID
    """
    
    def __init__(self, project_id: Optional[str] = None, collection_name: str = "live_sessions"):
        """
        Initialize Firestore storage.
        
        Args:
            project_id: GCP project ID (defaults to env var or default credentials)
            collection_name: Firestore collection name
        """
        if not FIRESTORE_AVAILABLE:
            raise ImportError(
                "google-cloud-firestore is required. Install with: pip install google-cloud-firestore"
            )
        
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.collection_name = collection_name
        
        # Initialize Firestore client
        if self.project_id:
            self.db = firestore.Client(project=self.project_id)
        else:
            self.db = firestore.Client()  # Uses default credentials
        
        self.collection = self.db.collection(collection_name)
    
    def create(self, session: LiveSession) -> LiveSession:
        """Create a new live session in Firestore."""
        # Convert session to dict
        session_dict = {
            "id": session.id,
            "user_id": session.user_id,
            "mode": session.mode,
            "state": session.state,
            "started_at": session.started_at,
            "paused_at": session.paused_at,
            "ended_at": session.ended_at,
            "transcript_partial": session.transcript_partial,
            "transcript_final": session.transcript_final,
            "audio_minutes_used": session.audio_minutes_used,
            "frames_processed": session.frames_processed,
            "daily_budget_remaining": session.daily_budget_remaining,
            "recording_consent": session.recording_consent,
            "secrets_blurred": session.secrets_blurred,
            "transcript_url": session.transcript_url,
            "recording_url": session.recording_url,
        }
        
        # Add to Firestore
        doc_ref = self.collection.document(session.id)
        doc_ref.set(session_dict)
        
        return session
    
    def get(self, session_id: str, user_id: str) -> Optional[LiveSession]:
        """Get a live session by ID."""
        doc_ref = self.collection.document(session_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return None
        
        data = doc.to_dict()
        
        # Verify ownership
        if data.get("user_id") != user_id:
            return None
        
        return self._dict_to_session(data)
    
    def list(
        self,
        user_id: str,
        state: Optional[str] = None,
        limit: int = 100
    ) -> List[LiveSession]:
        """List live sessions for a user."""
        query = self.collection.where("user_id", "==", user_id)
        
        if state:
            query = query.where("state", "==", state)
        
        query = query.limit(limit)
        docs = query.stream()
        
        sessions = []
        for doc in docs:
            data = doc.to_dict()
            sessions.append(self._dict_to_session(data))
        
        return sessions
    
    def update(self, session_id: str, user_id: str, updates: dict) -> Optional[LiveSession]:
        """Update a live session."""
        doc_ref = self.collection.document(session_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return None
        
        data = doc.to_dict()
        if data.get("user_id") != user_id:
            return None
        
        # Update fields
        doc_ref.update(updates)
        
        # Return updated session
        updated_doc = doc_ref.get()
        return self._dict_to_session(updated_doc.to_dict())
    
    def delete(self, session_id: str, user_id: str) -> bool:
        """Delete a live session."""
        doc_ref = self.collection.document(session_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return False
        
        # Verify ownership
        if doc.to_dict().get("user_id") != user_id:
            return False
        
        doc_ref.delete()
        return True
    
    def _dict_to_session(self, data: dict) -> LiveSession:
        """Convert Firestore document to LiveSession."""
        # Handle datetime conversion
        def parse_datetime(value):
            if value is None:
                return None
            if isinstance(value, datetime):
                return value
            if isinstance(value, str):
                try:
                    return datetime.fromisoformat(value.replace('Z', '+00:00'))
                except:
                    return datetime.utcnow()
            return value
        
        return LiveSession(
            id=data["id"],
            user_id=data["user_id"],
            mode=data.get("mode", "LS1A"),
            state=data.get("state", "IDLE"),
            started_at=parse_datetime(data.get("started_at")),
            paused_at=parse_datetime(data.get("paused_at")),
            ended_at=parse_datetime(data.get("ended_at")),
            transcript_partial=data.get("transcript_partial", ""),
            transcript_final=data.get("transcript_final"),
            audio_minutes_used=data.get("audio_minutes_used", 0.0),
            frames_processed=data.get("frames_processed", 0),
            daily_budget_remaining=data.get("daily_budget_remaining", {
                "audioMin": 60.0,
                "videoTokens": 50000.0,
                "screenTokens": 50000.0
            }),
            recording_consent=data.get("recording_consent", False),
            secrets_blurred=data.get("secrets_blurred", []),
            transcript_url=data.get("transcript_url"),
            recording_url=data.get("recording_url"),
        )

