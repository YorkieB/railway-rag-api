"""
RAG Pipeline Integration

Helper functions for integrating memory and budget enforcement into RAG queries.
"""

from typing import List, Dict, Optional, Tuple
from .budget import ContextBudgetEnforcer, TokenBreakdown
from .memory_storage import MemoryStorage
from .models import MemoryItem


class RAGPipeline:
    """
    Enhanced RAG pipeline with memory and budget enforcement.
    
    Integrates:
    - Memory retrieval and injection
    - Context budget enforcement
    - Token tracking
    """
    
    def __init__(
        self,
        budget_enforcer: ContextBudgetEnforcer,
        memory_storage: MemoryStorage
    ):
        """
        Initialize RAG pipeline.
        
        Args:
            budget_enforcer: ContextBudgetEnforcer instance
            memory_storage: MemoryStorage instance
        """
        self.budget_enforcer = budget_enforcer
        self.memory_storage = memory_storage
    
    def prepare_context(
        self,
        system_prompt: str,
        user_query: str,
        history: List[Dict[str, str]],
        rag_docs: List[str],
        user_id: str,
        project_id: Optional[str] = None
    ) -> Tuple[List[Dict[str, str]], List[str], List[MemoryItem], Optional[str], Dict]:
        """
        Prepare context for LLM with memory retrieval and budget enforcement.
        
        Args:
            system_prompt: System prompt text
            user_query: Current user query
            history: Conversation history
            rag_docs: RAG document chunks
            user_id: User ID for memory retrieval
            project_id: Optional project ID for memory filtering
            
        Returns:
            Tuple of:
            - Prepared history (truncated if needed)
            - Prepared RAG docs (truncated if needed)
            - Relevant memories
            - Warning message (if budget warning)
            - Budget status dict
        """
        # Step 1: Retrieve relevant memories
        memories = self._retrieve_memories(user_query, user_id, project_id)
        memory_contents = [mem.content for mem in memories]
        
        # Step 2: Track token usage
        breakdown = self.budget_enforcer.track_components(
            system_prompt=system_prompt,
            history=history,
            rag_docs=rag_docs,
            memory_items=memory_contents
        )
        
        # Step 3: Enforce budget (truncate if needed)
        truncated_history, truncated_rag, warning = self.budget_enforcer.enforce_budget(
            system_prompt=system_prompt,
            history=history,
            rag_docs=rag_docs,
            memory_items=memory_contents
        )
        
        # Step 4: Get budget status
        budget_status = self.budget_enforcer.get_budget_status(breakdown)
        
        return truncated_history, truncated_rag, memories, warning, budget_status
    
    def _retrieve_memories(
        self,
        query: str,
        user_id: str,
        project_id: Optional[str] = None,
        limit: int = 5
    ) -> List[MemoryItem]:
        """
        Retrieve relevant memories for a query.
        
        Args:
            query: User query
            user_id: User ID
            project_id: Optional project ID
            limit: Maximum number of memories to retrieve
            
        Returns:
            List of relevant memory items
        """
        try:
            # Search for relevant memories
            memories = self.memory_storage.search(
                user_id=user_id,
                query=query,
                project_id=project_id,
                limit=limit
            )
            return memories
        except Exception:
            # If search fails, return empty list
            return []
    
    def format_memory_context(self, memories: List[MemoryItem]) -> str:
        """
        Format memories for injection into LLM context.
        
        Args:
            memories: List of memory items
            
        Returns:
            Formatted memory context string
        """
        if not memories:
            return ""
        
        memory_lines = []
        for mem in memories:
            memory_lines.append(
                f"[{mem.memory_type.upper()}] {mem.content}"
            )
        
        return "\n".join(memory_lines)
    
    def build_enhanced_system_prompt(
        self,
        base_system_prompt: str,
        memories: List[MemoryItem]
    ) -> str:
        """
        Build enhanced system prompt with memory context.
        
        Args:
            base_system_prompt: Base system prompt
            memories: Relevant memory items
            
        Returns:
            Enhanced system prompt with memory context
        """
        if not memories:
            return base_system_prompt
        
        memory_context = self.format_memory_context(memories)
        
        enhanced = f"""{base_system_prompt}

## User Context & Preferences
{memory_context}

When answering, consider the user's preferences and past decisions mentioned above.
If a memory is relevant to the query, you may reference it in your response.
"""
        
        return enhanced
    
    def format_response_with_memories(
        self,
        answer: str,
        sources: List[Dict],
        memories: List[MemoryItem],
        uncertain: bool = False
    ) -> Dict:
        """
        Format RAG response with memory citations.
        
        Args:
            answer: LLM answer text
            sources: RAG document sources
            memories: Memories used in context
            uncertain: Whether response is uncertain
            
        Returns:
            Formatted response dictionary
        """
        response = {
            "answer": answer,
            "sources": sources,
            "uncertain": uncertain
        }
        
        # Add memory citations if memories were used
        if memories:
            response["memories_used"] = [
                {
                    "id": mem.id,
                    "content": mem.content,
                    "type": mem.memory_type
                }
                for mem in memories
            ]
        
        return response


def integrate_memory_into_query(
    query: str,
    user_id: str,
    project_id: Optional[str],
    history: List[Dict[str, str]],
    rag_docs: List[str],
    system_prompt: str,
    budget_enforcer: ContextBudgetEnforcer,
    memory_storage: MemoryStorage,
    private_session: bool = False
) -> Dict:
    """
    Helper function to integrate memory and budget into a RAG query.
    
    This function demonstrates how to use the RAGPipeline in a query endpoint.
    
    Args:
        query: User query
        user_id: User ID
        project_id: Optional project ID
        history: Conversation history
        rag_docs: RAG document chunks
        system_prompt: System prompt
        budget_enforcer: ContextBudgetEnforcer instance
        memory_storage: MemoryStorage instance
        private_session: Whether this is a private session (no memory writes)
        
    Returns:
        Dictionary with:
        - prepared_history: Truncated history
        - prepared_rag_docs: Truncated RAG docs
        - memories: Relevant memories
        - enhanced_system_prompt: System prompt with memory context
        - warning: Budget warning (if any)
        - budget_status: Budget status information
    """
    # Initialize pipeline
    pipeline = RAGPipeline(budget_enforcer, memory_storage)
    
    # Prepare context (retrieve memories, enforce budget)
    prepared_history, prepared_rag, memories, warning, budget_status = pipeline.prepare_context(
        system_prompt=system_prompt,
        user_query=query,
        history=history,
        rag_docs=rag_docs,
        user_id=user_id,
        project_id=project_id
    )
    
    # Build enhanced system prompt with memory context
    enhanced_system_prompt = pipeline.build_enhanced_system_prompt(
        base_system_prompt=system_prompt,
        memories=memories
    )
    
    return {
        "prepared_history": prepared_history,
        "prepared_rag_docs": prepared_rag,
        "memories": memories,
        "enhanced_system_prompt": enhanced_system_prompt,
        "warning": warning,
        "budget_status": budget_status
    }

