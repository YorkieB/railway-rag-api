"""
Enhanced RAG Integration with Uncertainty and Cost Tracking

Complete integration of budget, memory, uncertainty, and cost tracking.
"""

from typing import List, Dict, Optional, Tuple
from .budget import ContextBudgetEnforcer
from .memory_storage import MemoryStorage
from .uncertainty import UncertaintyChecker, RetrievalResult, create_retrieval_result
from .cost import CostTracker
from .models import MemoryItem


class EnhancedRAGPipeline:
    """
    Complete RAG pipeline with all Sprint 1.1 and 1.2 features.
    
    Integrates:
    - Memory retrieval and injection
    - Context budget enforcement
    - Uncertainty protocol
    - Cost tracking
    """
    
    def __init__(
        self,
        budget_enforcer: ContextBudgetEnforcer,
        memory_storage: MemoryStorage,
        uncertainty_checker: UncertaintyChecker,
        cost_tracker: CostTracker
    ):
        """
        Initialize enhanced RAG pipeline.
        
        Args:
            budget_enforcer: ContextBudgetEnforcer instance
            memory_storage: MemoryStorage instance
            uncertainty_checker: UncertaintyChecker instance
            cost_tracker: CostTracker instance
        """
        self.budget_enforcer = budget_enforcer
        self.memory_storage = memory_storage
        self.uncertainty_checker = uncertainty_checker
        self.cost_tracker = cost_tracker
    
    def process_query(
        self,
        query: str,
        user_id: str,
        system_prompt: str,
        history: List[Dict[str, str]],
        rag_chunks: List[Dict[str, any]],
        rag_scores: Optional[List[float]] = None,
        project_id: Optional[str] = None,
        private_session: bool = False
    ) -> Dict:
        """
        Process RAG query with full pipeline.
        
        Args:
            query: User query
            user_id: User ID
            system_prompt: System prompt
            history: Conversation history
            rag_chunks: RAG document chunks
            rag_scores: Optional relevance scores
            project_id: Optional project ID
            private_session: Whether this is a private session
            
        Returns:
            Dictionary with:
            - prepared_context: Context for LLM
            - uncertain_response: UncertainResponse if uncertain, None otherwise
            - budget_warning: Budget warning if needed
            - cost_info: Cost tracking information
            - budget_status: Budget status
            - memories: Relevant memories
        """
        # Step 1: Check cost budget (pre-query)
        estimated_tokens = self.budget_enforcer.estimate_tokens(query)
        is_allowed, error_msg, budget = self.cost_tracker.check_budget(
            user_id=user_id,
            estimated_text_tokens=estimated_tokens
        )
        
        if not is_allowed:
            return {
                "error": error_msg,
                "code": "BUDGET_EXCEEDED",
                "budget_status": self.cost_tracker.get_budget_status(user_id)
            }
        
        # Step 2: Retrieve relevant memories
        memories = []
        if not private_session:
            memories = self.memory_storage.search(
                user_id=user_id,
                query=query,
                project_id=project_id,
                limit=5
            )
        memory_contents = [mem.content for mem in memories]
        
        # Step 3: Check uncertainty protocol
        retrieval_result = create_retrieval_result(rag_chunks, rag_scores)
        uncertain_response = self.uncertainty_checker.check_retrieval(
            retrieval_result=retrieval_result,
            query=query
        )
        
        # If uncertain, return uncertain response (no LLM call needed)
        if uncertain_response:
            return {
                "uncertain_response": uncertain_response.to_dict(),
                "memories": [self._memory_to_dict(mem) for mem in memories],
                "budget_status": self.cost_tracker.get_budget_status(user_id)
            }
        
        # Step 4: Prepare context with budget enforcement
        rag_docs = [chunk.get("text", chunk.get("content", "")) for chunk in rag_chunks]
        truncated_history, truncated_rag, budget_warning = self.budget_enforcer.enforce_budget(
            system_prompt=system_prompt,
            history=history,
            rag_docs=rag_docs,
            memory_items=memory_contents
        )
        
        # Step 5: Build enhanced system prompt
        enhanced_system = self._build_enhanced_system_prompt(system_prompt, memories)
        
        # Step 6: Prepare context for LLM
        prepared_context = {
            "system_prompt": enhanced_system,
            "history": truncated_history,
            "rag_docs": truncated_rag,
            "memories": memories
        }
        
        # Step 7: Estimate final token count for cost tracking
        final_tokens = self.budget_enforcer.track_components(
            system_prompt=enhanced_system,
            history=truncated_history,
            rag_docs=truncated_rag,
            memory_items=memory_contents
        ).total
        
        # Step 8: Track cost (will be updated after LLM call with actual usage)
        budget, cost_info = self.cost_tracker.track_usage(
            user_id=user_id,
            text_tokens=final_tokens
        )
        
        return {
            "prepared_context": prepared_context,
            "uncertain_response": None,
            "budget_warning": budget_warning,
            "cost_info": cost_info,
            "budget_status": self.cost_tracker.get_budget_status(user_id),
            "memories": [self._memory_to_dict(mem) for mem in memories]
        }
    
    def _build_enhanced_system_prompt(
        self,
        base_system_prompt: str,
        memories: List[MemoryItem]
    ) -> str:
        """Build enhanced system prompt with memory context."""
        if not memories:
            return base_system_prompt
        
        memory_context = "\n".join([
            f"[{mem.memory_type.upper()}] {mem.content}"
            for mem in memories
        ])
        
        return f"""{base_system_prompt}

## User Context & Preferences
{memory_context}

When answering, consider the user's preferences and past decisions mentioned above.
If a memory is relevant to the query, you may reference it in your response.
"""
    
    def _memory_to_dict(self, memory: MemoryItem) -> Dict:
        """Convert memory to dictionary."""
        return {
            "id": memory.id,
            "content": memory.content,
            "type": memory.memory_type
        }
    
    def format_response(
        self,
        llm_answer: str,
        sources: List[Dict],
        memories: List[MemoryItem],
        uncertain: bool = False,
        budget_warning: Optional[str] = None,
        cost_info: Optional[Dict] = None
    ) -> Dict:
        """
        Format final response with all metadata.
        
        Args:
            llm_answer: LLM answer text
            sources: RAG document sources
            memories: Memories used
            uncertain: Whether response is uncertain
            budget_warning: Budget warning if any
            cost_info: Cost tracking information
            
        Returns:
            Formatted response dictionary
        """
        response = {
            "answer": llm_answer,
            "sources": sources,
            "uncertain": uncertain
        }
        
        # Add memory citations
        if memories:
            response["memories_used"] = [
                self._memory_to_dict(mem) for mem in memories
            ]
        
        # Add budget warning
        if budget_warning:
            response["warning"] = budget_warning
        
        # Add cost information
        if cost_info:
            response["cost"] = {
                "tokens": cost_info.get("text_tokens", 0),
                "dollars": cost_info.get("total_cost", 0)
            }
        
        return response

