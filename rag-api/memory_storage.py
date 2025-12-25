"""
Memory Storage Interface

Abstract base class for memory storage implementations.
Supports ChromaDB and can be extended for Firestore/BigQuery.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
import chromadb
from chromadb.config import Settings

from .models import MemoryItem


class MemoryStorage(ABC):
    """
    Abstract base class for memory storage.
    
    Implementations should provide:
    - ChromaDB-based storage (default)
    - Firestore-based storage (optional)
    - BigQuery-based storage (optional)
    """
    
    @abstractmethod
    def create(self, memory: MemoryItem) -> MemoryItem:
        """
        Create a new memory item.
        
        Args:
            memory: Memory item to create
            
        Returns:
            Created memory item with generated ID
        """
        pass
    
    @abstractmethod
    def get(self, memory_id: str, user_id: str) -> Optional[MemoryItem]:
        """
        Get a memory item by ID.
        
        Args:
            memory_id: Memory item ID
            user_id: User ID (for ownership validation)
            
        Returns:
            Memory item if found, None otherwise
        """
        pass
    
    @abstractmethod
    def list(
        self,
        user_id: str,
        project_id: Optional[str] = None,
        memory_type: Optional[str] = None,
        limit: int = 100
    ) -> List[MemoryItem]:
        """
        List memory items for a user.
        
        Args:
            user_id: User ID
            project_id: Optional project filter (None = global + project)
            memory_type: Optional type filter
            limit: Maximum number of items to return
            
        Returns:
            List of memory items
        """
        pass
    
    @abstractmethod
    def update(self, memory_id: str, user_id: str, updates: dict) -> Optional[MemoryItem]:
        """
        Update a memory item.
        
        Args:
            memory_id: Memory item ID
            user_id: User ID (for ownership validation)
            updates: Dictionary of fields to update
            
        Returns:
            Updated memory item if found, None otherwise
        """
        pass
    
    @abstractmethod
    def delete(self, memory_id: str, user_id: str) -> bool:
        """
        Delete a memory item.
        
        Args:
            memory_id: Memory item ID
            user_id: User ID (for ownership validation)
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    def search(
        self,
        user_id: str,
        query: str,
        project_id: Optional[str] = None,
        memory_type: Optional[str] = None,
        limit: int = 10
    ) -> List[MemoryItem]:
        """
        Search memories using semantic search.
        
        Args:
            user_id: User ID
            query: Search query text
            project_id: Optional project filter
            memory_type: Optional type filter
            limit: Maximum number of results
            
        Returns:
            List of memory items sorted by relevance
        """
        pass


class ChromaDBMemoryStorage(MemoryStorage):
    """
    ChromaDB-based memory storage implementation.
    
    Uses ChromaDB for vector storage and semantic search.
    """
    
    def __init__(self, collection_name: str = "memories", persist_directory: str = "./memory_db"):
        """
        Initialize ChromaDB memory storage.
        
        Args:
            collection_name: ChromaDB collection name
            persist_directory: Directory to persist ChromaDB data
        """
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    def create(self, memory: MemoryItem) -> MemoryItem:
        """Create a new memory item."""
        # Update timestamps
        memory.created_at = datetime.utcnow()
        memory.updated_at = datetime.utcnow()
        
        # Store in ChromaDB
        self.collection.add(
            ids=[memory.id],
            documents=[memory.content],
            metadatas=[{
                "user_id": memory.user_id,
                "project_id": memory.project_id or "",
                "memory_type": memory.memory_type,
                "created_at": memory.created_at.isoformat(),
                "updated_at": memory.updated_at.isoformat()
            }]
        )
        
        return memory
    
    def get(self, memory_id: str, user_id: str) -> Optional[MemoryItem]:
        """Get a memory item by ID."""
        try:
            results = self.collection.get(
                ids=[memory_id],
                include=["documents", "metadatas"]
            )
            
            if not results["ids"]:
                return None
            
            metadata = results["metadatas"][0]
            
            # Verify ownership
            if metadata["user_id"] != user_id:
                return None
            
            return MemoryItem(
                id=memory_id,
                user_id=metadata["user_id"],
                project_id=metadata["project_id"] or None,
                content=results["documents"][0],
                memory_type=metadata["memory_type"],
                created_at=datetime.fromisoformat(metadata["created_at"]),
                updated_at=datetime.fromisoformat(metadata["updated_at"])
            )
        except Exception:
            return None
    
    def list(
        self,
        user_id: str,
        project_id: Optional[str] = None,
        memory_type: Optional[str] = None,
        limit: int = 100
    ) -> List[MemoryItem]:
        """List memory items for a user."""
        # Build where clause
        where = {"user_id": user_id}
        if project_id is not None:
            where["project_id"] = project_id
        if memory_type is not None:
            where["memory_type"] = memory_type
        
        try:
            results = self.collection.get(
                where=where,
                limit=limit,
                include=["documents", "metadatas"]
            )
            
            memories = []
            for i, memory_id in enumerate(results["ids"]):
                metadata = results["metadatas"][i]
                memories.append(MemoryItem(
                    id=memory_id,
                    user_id=metadata["user_id"],
                    project_id=metadata["project_id"] or None,
                    content=results["documents"][i],
                    memory_type=metadata["memory_type"],
                    created_at=datetime.fromisoformat(metadata["created_at"]),
                    updated_at=datetime.fromisoformat(metadata["updated_at"])
                ))
            
            return memories
        except Exception:
            return []
    
    def update(self, memory_id: str, user_id: str, updates: dict) -> Optional[MemoryItem]:
        """Update a memory item."""
        # Get existing memory
        memory = self.get(memory_id, user_id)
        if not memory:
            return None
        
        # Apply updates
        if "content" in updates:
            memory.content = updates["content"]
        if "memory_type" in updates:
            memory.memory_type = updates["memory_type"]
        if "project_id" in updates:
            memory.project_id = updates["project_id"]
        
        memory.updated_at = datetime.utcnow()
        
        # Update in ChromaDB
        self.collection.update(
            ids=[memory_id],
            documents=[memory.content],
            metadatas=[{
                "user_id": memory.user_id,
                "project_id": memory.project_id or "",
                "memory_type": memory.memory_type,
                "created_at": memory.created_at.isoformat(),
                "updated_at": memory.updated_at.isoformat()
            }]
        )
        
        return memory
    
    def delete(self, memory_id: str, user_id: str) -> bool:
        """Delete a memory item."""
        # Verify ownership
        memory = self.get(memory_id, user_id)
        if not memory:
            return False
        
        # Delete from ChromaDB
        self.collection.delete(ids=[memory_id])
        return True
    
    def search(
        self,
        user_id: str,
        query: str,
        project_id: Optional[str] = None,
        memory_type: Optional[str] = None,
        limit: int = 10
    ) -> List[MemoryItem]:
        """Search memories using semantic search."""
        # Build where clause
        where = {"user_id": user_id}
        if project_id is not None:
            where["project_id"] = project_id
        if memory_type is not None:
            where["memory_type"] = memory_type
        
        try:
            results = self.collection.query(
                query_texts=[query],
                where=where,
                n_results=limit,
                include=["documents", "metadatas", "distances"]
            )
            
            memories = []
            if results["ids"] and len(results["ids"][0]) > 0:
                for i, memory_id in enumerate(results["ids"][0]):
                    metadata = results["metadatas"][0][i]
                    memories.append(MemoryItem(
                        id=memory_id,
                        user_id=metadata["user_id"],
                        project_id=metadata["project_id"] or None,
                        content=results["documents"][0][i],
                        memory_type=metadata["memory_type"],
                        created_at=datetime.fromisoformat(metadata["created_at"]),
                        updated_at=datetime.fromisoformat(metadata["updated_at"])
                    ))
            
            return memories
        except Exception:
            return []

