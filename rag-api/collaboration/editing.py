"""
Collaborative Editing

Real-time document editing with conflict resolution.
"""
from typing import Dict, List, Optional
from datetime import datetime
import json


class CollaborativeEditor:
    """Manages collaborative document editing"""
    
    def __init__(self, document_id: str):
        """
        Initialize collaborative editor for a document.
        
        Args:
            document_id: Document identifier
        """
        self.document_id = document_id
        self.content = ""
        self.cursors: Dict[str, Dict] = {}  # {user_id: {position: int, selection: tuple}}
        self.change_history: List[Dict] = []
        self.version = 0
    
    def apply_change(
        self,
        user_id: str,
        change_type: str,  # insert, delete, format
        position: int,
        content: Optional[str] = None,
        length: Optional[int] = None
    ) -> Dict:
        """
        Apply change to document.
        
        Args:
            user_id: User making the change
            change_type: Type of change
            position: Position in document
            content: Content to insert (for insert)
            length: Length to delete (for delete)
            
        Returns:
            Dict with change result and new version
        """
        if change_type == "insert" and content:
            self.content = self.content[:position] + content + self.content[position:]
            self.version += 1
        elif change_type == "delete" and length:
            self.content = self.content[:position] + self.content[position + length:]
            self.version += 1
        
        change_record = {
            "user_id": user_id,
            "change_type": change_type,
            "position": position,
            "content": content,
            "length": length,
            "version": self.version,
            "timestamp": datetime.now().isoformat()
        }
        
        self.change_history.append(change_record)
        
        return {
            "success": True,
            "version": self.version,
            "change": change_record
        }
    
    def update_cursor(self, user_id: str, position: int, selection: Optional[tuple] = None):
        """Update user cursor position"""
        self.cursors[user_id] = {
            "position": position,
            "selection": selection,
            "updated_at": datetime.now().isoformat()
        }
    
    def get_cursors(self) -> Dict[str, Dict]:
        """Get all user cursors"""
        return self.cursors.copy()
    
    def get_content(self) -> str:
        """Get current document content"""
        return self.content


# In-memory storage for collaborative editors
collaborative_editors: Dict[str, CollaborativeEditor] = {}


def get_editor(document_id: str) -> CollaborativeEditor:
    """Get or create collaborative editor for document"""
    if document_id not in collaborative_editors:
        collaborative_editors[document_id] = CollaborativeEditor(document_id)
    return collaborative_editors[document_id]

