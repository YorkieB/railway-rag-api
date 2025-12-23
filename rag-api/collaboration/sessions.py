"""
Collaboration Sessions

Manages shared browser sessions, document editing, and real-time collaboration.
"""
from typing import Dict, List, Optional
from datetime import datetime
import uuid


class CollaborationSession:
    """Manages a shared collaboration session"""
    
    def __init__(
        self,
        session_id: str,
        owner_id: str,
        session_type: str = "browser"  # browser, document, automation
    ):
        """
        Initialize collaboration session.
        
        Args:
            session_id: Unique session identifier
            owner_id: User ID of session owner
            session_type: Type of session (browser, document, automation)
        """
        self.session_id = session_id
        self.owner_id = owner_id
        self.session_type = session_type
        self.members: Dict[str, Dict] = {owner_id: {"role": "owner", "joined_at": datetime.now()}}
        self.created_at = datetime.now()
        self.state = "active"  # active, paused, ended
    
    def add_member(self, user_id: str, role: str = "viewer") -> bool:
        """
        Add member to collaboration session.
        
        Args:
            user_id: User ID to add
            role: Member role (owner, editor, viewer)
            
        Returns:
            True if added successfully
        """
        if user_id not in self.members:
            self.members[user_id] = {
                "role": role,
                "joined_at": datetime.now()
            }
            return True
        return False
    
    def remove_member(self, user_id: str) -> bool:
        """Remove member from session"""
        if user_id in self.members and user_id != self.owner_id:
            del self.members[user_id]
            return True
        return False
    
    def update_member_role(self, user_id: str, role: str) -> bool:
        """Update member role"""
        if user_id in self.members:
            self.members[user_id]["role"] = role
            return True
        return False
    
    def get_members(self) -> List[Dict]:
        """Get list of all members"""
        return [
            {
                "user_id": uid,
                "role": info["role"],
                "joined_at": info["joined_at"].isoformat()
            }
            for uid, info in self.members.items()
        ]


# In-memory storage for collaboration sessions
collaboration_sessions: Dict[str, CollaborationSession] = {}


class CollaborationManager:
    """Manages collaboration sessions"""
    
    def create_session(
        self,
        owner_id: str,
        session_type: str = "browser",
        target_id: Optional[str] = None  # browser_session_id, document_id, etc.
    ) -> Dict:
        """
        Create new collaboration session.
        
        Args:
            owner_id: User ID of session owner
            session_type: Type of session
            target_id: ID of target resource (browser session, document, etc.)
            
        Returns:
            Dict with session_id and details
        """
        session_id = str(uuid.uuid4())
        session = CollaborationSession(session_id, owner_id, session_type)
        session.target_id = target_id
        collaboration_sessions[session_id] = session
        
        return {
            "session_id": session_id,
            "owner_id": owner_id,
            "session_type": session_type,
            "target_id": target_id,
            "created_at": session.created_at.isoformat()
        }
    
    def get_session(self, session_id: str) -> Optional[CollaborationSession]:
        """Get collaboration session by ID"""
        return collaboration_sessions.get(session_id)
    
    def list_user_sessions(self, user_id: str) -> List[Dict]:
        """List all sessions user is part of"""
        user_sessions = []
        for session_id, session in collaboration_sessions.items():
            if user_id in session.members:
                user_sessions.append({
                    "session_id": session_id,
                    "owner_id": session.owner_id,
                    "session_type": session.session_type,
                    "role": session.members[user_id]["role"],
                    "member_count": len(session.members)
                })
        return user_sessions


# Global collaboration manager
collaboration_manager = CollaborationManager()

