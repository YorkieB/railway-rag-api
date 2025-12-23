"""
Memory Storage Implementation

Memory system using ChromaDB for persistent storage and semantic search.
Memories are stored with embeddings for relevance-based retrieval.
"""

import chromadb
from chromadb.utils import embedding_functions
from typing import List, Optional, Dict
import os
from datetime import datetime
from models import MemoryItem


class MemoryStorage:
    """ChromaDB-based memory storage with semantic search"""
    
    def __init__(self, chromadb_path: str = "./rag_knowledge_base"):
        """
        Initialize memory storage
        
        Args:
            chromadb_path: Path to ChromaDB storage (default: same as RAG documents)
        """
        self.chromadb_path = chromadb_path
        self.client = chromadb.PersistentClient(path=chromadb_path)
        
        # Create embedding function using OpenAI
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise Exception("OPENAI_API_KEY environment variable is required for memory embeddings")
        
        self.embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
            api_key=openai_api_key,
            model_name="text-embedding-3-small"
        )
        
        # Get or create memories collection
        self.collection = self.client.get_or_create_collection(
            name="memories",
            embedding_function=self.embedding_fn
        )
    
    def create(self, memory: MemoryItem) -> MemoryItem:
        """
        Store memory in ChromaDB
        
        Args:
            memory: MemoryItem to store
            
        Returns:
            Stored MemoryItem
        """
        self.collection.add(
            documents=[memory.content],
            metadatas=[{
                "id": memory.id,
                "user_id": memory.user_id,
                "project_id": memory.project_id or "",
                "memory_type": memory.memory_type,
                "created_at": memory.created_at.isoformat(),
                "updated_at": memory.updated_at.isoformat()
            }],
            ids=[memory.id]
        )
        return memory
    
    def get(self, memory_id: str, user_id: str) -> Optional[MemoryItem]:
        """
        Get memory by ID
        
        Args:
            memory_id: Memory identifier
            user_id: User identifier (for security)
            
        Returns:
            MemoryItem if found, None otherwise
        """
        try:
            results = self.collection.get(
                ids=[memory_id],
                where={"user_id": user_id}
            )
            
            if not results['ids'] or len(results['ids']) == 0:
                return None
            
            # Parse metadata
            metadata = results['metadatas'][0] if results['metadatas'] else {}
            document = results['documents'][0] if results['documents'] else ""
            
            return MemoryItem(
                id=metadata.get("id", memory_id),
                user_id=metadata.get("user_id", user_id),
                project_id=metadata.get("project_id") or None,
                content=document,
                memory_type=metadata.get("memory_type", "fact"),
                created_at=datetime.fromisoformat(metadata.get("created_at", datetime.now().isoformat())),
                updated_at=datetime.fromisoformat(metadata.get("updated_at", datetime.now().isoformat()))
            )
        except Exception as e:
            print(f"Error getting memory {memory_id}: {e}")
            return None
    
    def update(self, memory: MemoryItem) -> Optional[MemoryItem]:
        """
        Update memory in ChromaDB
        
        Args:
            memory: Updated MemoryItem
            
        Returns:
            Updated MemoryItem if successful, None otherwise
        """
        try:
            # Update metadata
            memory.updated_at = datetime.now()
            
            # ChromaDB doesn't have direct update, so we delete and re-add
            self.collection.delete(ids=[memory.id])
            
            self.collection.add(
                documents=[memory.content],
                metadatas=[{
                    "id": memory.id,
                    "user_id": memory.user_id,
                    "project_id": memory.project_id or "",
                    "memory_type": memory.memory_type,
                    "created_at": memory.created_at.isoformat(),
                    "updated_at": memory.updated_at.isoformat()
                }],
                ids=[memory.id]
            )
            return memory
        except Exception as e:
            print(f"Error updating memory {memory.id}: {e}")
            return None
    
    def delete(self, memory_id: str, user_id: str) -> bool:
        """
        Delete memory by ID
        
        Args:
            memory_id: Memory identifier
            user_id: User identifier (for security)
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            # Verify memory belongs to user
            memory = self.get(memory_id, user_id)
            if not memory:
                return False
            
            self.collection.delete(ids=[memory_id])
            return True
        except Exception as e:
            print(f"Error deleting memory {memory_id}: {e}")
            return False
    
    def list(self, user_id: str, project_id: Optional[str] = None) -> List[MemoryItem]:
        """
        List all memories for user (optionally filtered by project)
        
        Args:
            user_id: User identifier
            project_id: Optional project identifier (None = all memories including global)
            
        Returns:
            List of MemoryItem objects
        """
        try:
            where_clause = {"user_id": user_id}
            
            # Get all memories for user
            results = self.collection.get(where=where_clause)
            
            memories = []
            if results['ids']:
                for i, memory_id in enumerate(results['ids']):
                    metadata = results['metadatas'][i] if results['metadatas'] else {}
                    document = results['documents'][i] if results['documents'] else ""
                    
                    # Filter by project_id if specified
                    mem_project_id = metadata.get("project_id") or None
                    if project_id is not None:
                        # If project_id specified, only return memories for that project or global (None)
                        if mem_project_id != project_id and mem_project_id is not None:
                            continue
                    
                    memory = MemoryItem(
                        id=memory_id,
                        user_id=metadata.get("user_id", user_id),
                        project_id=mem_project_id,
                        content=document,
                        memory_type=metadata.get("memory_type", "fact"),
                        created_at=datetime.fromisoformat(metadata.get("created_at", datetime.now().isoformat())),
                        updated_at=datetime.fromisoformat(metadata.get("updated_at", datetime.now().isoformat()))
                    )
                    memories.append(memory)
            
            return memories
        except Exception as e:
            print(f"Error listing memories: {e}")
            return []
    
    def search(
        self, 
        user_id: str, 
        query: str, 
        project_id: Optional[str] = None, 
        top_k: int = 5
    ) -> List[MemoryItem]:
        """
        Search memories by relevance using semantic search
        
        Args:
            user_id: User identifier
            query: Search query text
            project_id: Optional project identifier (None = search all memories including global)
            top_k: Number of results to return
            
        Returns:
            List of MemoryItem objects sorted by relevance
        """
        try:
            where_clause = {"user_id": user_id}
            
            # Query ChromaDB for relevant memories
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k * 2,  # Get more results to filter by project
                where=where_clause
            )
            
            memories = []
            if results['ids'] and len(results['ids']) > 0:
                ids = results['ids'][0]
                metadatas = results['metadatas'][0] if results['metadatas'] else [{}] * len(ids)
                documents = results['documents'][0] if results['documents'] else [""] * len(ids)
                distances = results['distances'][0] if results['distances'] else [1.0] * len(ids)
                
                for i, memory_id in enumerate(ids):
                    metadata = metadatas[i]
                    document = documents[i]
                    distance = distances[i]
                    
                    # Filter by project_id if specified
                    mem_project_id = metadata.get("project_id") or None
                    if project_id is not None:
                        # If project_id specified, only return memories for that project or global (None)
                        if mem_project_id != project_id and mem_project_id is not None:
                            continue
                    
                    # Convert distance to similarity score
                    score = 1.0 - distance if distance <= 1.0 else 0.0
                    
                    memory = MemoryItem(
                        id=memory_id,
                        user_id=metadata.get("user_id", user_id),
                        project_id=mem_project_id,
                        content=document,
                        memory_type=metadata.get("memory_type", "fact"),
                        created_at=datetime.fromisoformat(metadata.get("created_at", datetime.now().isoformat())),
                        updated_at=datetime.fromisoformat(metadata.get("updated_at", datetime.now().isoformat()))
                    )
                    memories.append(memory)
                    
                    # Stop if we have enough results
                    if len(memories) >= top_k:
                        break
            
            return memories
        except Exception as e:
            print(f"Error searching memories: {e}")
            return []

