"""
MemoryManager: Handles ChromaDB for persistent conversation memory.
Based on the guidance document: Building a Real-Time AI Companion.txt
"""
import os
import time
from typing import Optional, List
import chromadb
from chromadb.utils import embedding_functions

from config import CHROMADB_PATH, COLLECTION_NAME, EMBEDDING_MODEL, MEMORY_RETRIEVAL_K


class MemoryManager:
    """
    Handles the Vector Database (ChromaDB) for long-term memory.
    Stores conversation turns as vector embeddings for semantic retrieval.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize ChromaDB client and collection.
        
        Args:
            db_path: Path to ChromaDB persistence directory (defaults to config value)
        """
        path = db_path or CHROMADB_PATH
        
        # Create a persistent client that saves data to disk
        self.client = chromadb.PersistentClient(path=path)
        
        # Use OpenAI's embedding model to convert text to vectors
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            raise ValueError("OPENAI_API_KEY environment variable is required for embeddings")
        
        self.embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
            api_key=openai_key,
            model_name=EMBEDDING_MODEL
        )
        
        # Get or create the collection
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=self.embedding_fn
        )
    
    def add_memory(self, user_text: str, ai_text: str):
        """
        Stores a turn of conversation as a memory.
        
        Args:
            user_text: User's input text
            ai_text: AI's response text
        """
        interaction = f"User: {user_text} | AI: {ai_text}"
        timestamp = str(time.time())
        
        try:
            self.collection.add(
                documents=[interaction],
                metadatas=[{
                    "timestamp": timestamp,
                    "role": "dialogue",
                    "user_text": user_text[:200],  # Truncate for metadata
                    "ai_text": ai_text[:200]
                }],
                ids=[timestamp]
            )
        except Exception as e:
            print(f"Error adding memory: {e}")
    
    def get_relevant_context(self, query_text: str, n_results: int = None) -> str:
        """
        Retrieves the top-k most relevant past interactions.
        
        Args:
            query_text: Current user query to find relevant memories for
            n_results: Number of memories to retrieve (defaults to config value)
        
        Returns:
            Concatenated string of relevant memories, or empty string if none found
        """
        k = n_results or MEMORY_RETRIEVAL_K
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=k
            )
            if results['documents'] and len(results['documents']) > 0:
                # Join all relevant memories with newlines
                return "\n".join(results['documents'][0])
        except Exception as e:
            print(f"Error retrieving context: {e}")
        return ""
    
    def get_all_memories(self, limit: int = 100) -> List[dict]:
        """
        Retrieves all stored memories (for UI display/debugging).
        
        Args:
            limit: Maximum number of memories to retrieve
        
        Returns:
            List of memory dictionaries with id, document, and metadata
        """
        try:
            results = self.collection.get(limit=limit)
            memories = []
            for i, doc_id in enumerate(results['ids']):
                memories.append({
                    'id': doc_id,
                    'document': results['documents'][i] if i < len(results['documents']) else '',
                    'metadata': results['metadatas'][i] if i < len(results['metadatas']) else {}
                })
            return memories
        except Exception as e:
            print(f"Error retrieving all memories: {e}")
            return []
    
    def delete_memory(self, memory_id: str) -> bool:
        """
        Deletes a specific memory by ID.
        
        Args:
            memory_id: ID of the memory to delete
        
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            self.collection.delete(ids=[memory_id])
            return True
        except Exception as e:
            print(f"Error deleting memory: {e}")
            return False
    
    def clear_all_memories(self):
        """Clears all stored memories (use with caution)."""
        try:
            # Delete the collection and recreate it
            self.client.delete_collection(name=COLLECTION_NAME)
            self.collection = self.client.get_or_create_collection(
                name=COLLECTION_NAME,
                embedding_function=self.embedding_fn
            )
        except Exception as e:
            print(f"Error clearing memories: {e}")

