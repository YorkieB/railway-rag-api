"""
Context Budget Enforcement

This module enforces context budget limits to prevent token overruns.
Tracks tokens per component (system, history, RAG docs, memory) and
truncates/summarizes when over budget.
"""

from typing import List, Dict, Optional


class ContextBudgetEnforcer:
    """Enforces context budget limits and manages token allocation"""
    
    def __init__(self, max_tokens: int = 100000, warn_threshold: float = 0.8):
        """
        Initialize context budget enforcer
        
        Args:
            max_tokens: Maximum total tokens allowed in context (default: 100000)
            warn_threshold: Utilization threshold for warnings (0.0-1.0, default: 0.8 = 80%)
        """
        self.max_tokens = max_tokens
        self.warn_threshold = warn_threshold
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count from text
        
        Rough estimation: 1 token ≈ 4 characters
        More accurate estimation would use tiktoken library
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count
        """
        if not text:
            return 0
        # Rough estimate: 1 token ≈ 4 characters
        return len(text) // 4
    
    def check_budget(
        self, 
        system_tokens: int, 
        history_tokens: int, 
        rag_tokens: int, 
        memory_tokens: int = 0
    ) -> Dict:
        """
        Check if context is within budget
        
        Args:
            system_tokens: Tokens used by system prompt
            history_tokens: Tokens used by conversation history
            rag_tokens: Tokens used by RAG documents
            memory_tokens: Tokens used by memory context (default: 0)
            
        Returns:
            Dict with budget status, utilization, and action required
        """
        total = system_tokens + history_tokens + rag_tokens + memory_tokens
        utilization = total / self.max_tokens if self.max_tokens > 0 else 0.0
        
        if total > self.max_tokens:
            return {
                "over_budget": True,
                "total": total,
                "max": self.max_tokens,
                "utilization": utilization,
                "action": "truncate"
            }
        
        if utilization >= self.warn_threshold:
            return {
                "over_budget": False,
                "total": total,
                "max": self.max_tokens,
                "utilization": utilization,
                "warning": True
            }
        
        return {
            "over_budget": False,
            "total": total,
            "max": self.max_tokens,
            "utilization": utilization,
            "warning": False
        }
    
    def truncate_history(self, messages: List[Dict], max_history_tokens: int) -> List[Dict]:
        """
        Truncate conversation history to fit budget
        
        Keeps system message (if present) and removes oldest user/assistant pairs
        until history fits within max_history_tokens
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
            max_history_tokens: Maximum tokens allowed for history
            
        Returns:
            Truncated list of messages
        """
        if not messages:
            return []
        
        # Separate system message (keep it)
        system_messages = [msg for msg in messages if msg.get('role') == 'system']
        conversation_messages = [msg for msg in messages if msg.get('role') != 'system']
        
        # Calculate tokens for conversation messages
        total_tokens = sum([self.estimate_tokens(msg.get('content', '')) for msg in conversation_messages])
        
        # If already under budget, return as-is
        if total_tokens <= max_history_tokens:
            return messages
        
        # Remove oldest messages until under budget
        truncated = conversation_messages.copy()
        while total_tokens > max_history_tokens and len(truncated) > 0:
            # Remove oldest message (first in list)
            removed_msg = truncated.pop(0)
            total_tokens -= self.estimate_tokens(removed_msg.get('content', ''))
        
        # Combine system messages with truncated conversation
        return system_messages + truncated

