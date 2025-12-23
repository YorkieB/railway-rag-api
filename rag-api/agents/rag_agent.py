"""
RAG Agent for CrewAI
Specialized agent for document search and retrieval.
"""
from typing import Dict, Any, Optional, List
from crewai import Agent
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class RAGAgent:
    """
    RAG (Retrieval-Augmented Generation) agent for CrewAI.
    
    Capabilities:
    - Search documents
    - Answer questions based on documents
    - Retrieve relevant information
    - Cite sources
    """
    
    def __init__(self, llm=None, chromadb_path: Optional[str] = None):
        """
        Initialize RAG agent.
        
        Args:
            llm: Optional LLM instance for CrewAI
            chromadb_path: Path to ChromaDB storage
        """
        self.llm = llm
        self.chromadb_path = chromadb_path or os.getenv("CHROMADB_PATH", "./rag_knowledge_base")
        self.agent = None
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize CrewAI agent."""
        try:
            from crewai import Agent
            
            # Try to create agent, but handle LLM initialization failures gracefully
            try:
                self.agent = Agent(
                    role="Document Search and Retrieval Specialist",
                    goal="Find and retrieve relevant information from documents",
                    backstory="""You are an expert at searching through documents and
                    retrieving relevant information. You use semantic search to find
                    documents that match user queries, and you always cite your sources.
                    You follow the uncertainty protocol - if you can't find relevant
                    information, you explicitly state that.""",
                    verbose=False,  # Set to False to reduce initialization overhead
                    allow_delegation=False,
                    llm=self.llm
                )
            except Exception as e:
                # LLM initialization failed (e.g., missing API key)
                # This is acceptable - agent can still be used for non-LLM tasks
                import warnings
                warnings.warn(f"CrewAI Agent created without LLM: {e}")
                self.agent = None
        except ImportError:
            # CrewAI not available - use fallback
            self.agent = None
    
    def execute_task(self, query: str, top_k: int = 3, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a RAG search task.
        
        Args:
            query: Search query
            top_k: Number of results to return
            project_id: Optional project ID for filtering
            
        Returns:
            Dict with search results
        """
        try:
            # Import search function from app
            from app import search_chromadb
            
            # Search documents
            results = search_chromadb(
                query_text=query,
                top_k=top_k,
                use_hybrid=True,
                project_id=project_id
            )
            
            # Format results
            formatted_results = []
            for doc in results:
                formatted_results.append({
                    "content": doc.get("document", ""),
                    "source": doc.get("metadata", {}).get("document_name", "Unknown"),
                    "score": doc.get("score", 0.0),
                    "metadata": doc.get("metadata", {})
                })
            
            return {
                "success": True,
                "query": query,
                "results": formatted_results,
                "count": len(formatted_results),
                "agent_type": "rag"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent_type": "rag"
            }
    
    def get_agent(self):
        """Get CrewAI agent instance."""
        return self.agent

