"""
Context Budget Enforcer

Tracks tokens per component (system, history, RAG docs, memory) and enforces
context window limits with truncation/summarization when over budget.
"""

import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# Configuration
MAX_CONTEXT_TOKENS = int(os.getenv("MAX_CONTEXT_TOKENS", "100000"))
WARN_THRESHOLD = float(os.getenv("WARN_THRESHOLD", "0.8"))


@dataclass
class TokenBreakdown:
    """Token usage breakdown by component."""
    system: int = 0
    history: int = 0
    rag_docs: int = 0
    memory: int = 0
    
    @property
    def total(self) -> int:
        """Total token count."""
        return self.system + self.history + self.rag_docs + self.memory
    
    @property
    def utilization(self) -> float:
        """Utilization as fraction of max (0.0 to 1.0)."""
        return self.total / MAX_CONTEXT_TOKENS if MAX_CONTEXT_TOKENS > 0 else 0.0
    
    @property
    def is_over_budget(self) -> bool:
        """Check if over budget."""
        return self.total > MAX_CONTEXT_TOKENS
    
    @property
    def should_warn(self) -> bool:
        """Check if should warn (at 80% threshold)."""
        return self.utilization >= WARN_THRESHOLD


class ContextBudgetEnforcer:
    """
    Enforces context budget by tracking tokens and truncating when needed.
    
    Configuration:
    - MAX_CONTEXT_TOKENS: Maximum context window size (default: 100000)
    - WARN_THRESHOLD: Warning threshold as fraction (default: 0.8 = 80%)
    """
    
    def __init__(self, max_tokens: Optional[int] = None, warn_threshold: Optional[float] = None):
        """
        Initialize budget enforcer.
        
        Args:
            max_tokens: Maximum context tokens (defaults to MAX_CONTEXT_TOKENS env var)
            warn_threshold: Warning threshold as fraction (defaults to WARN_THRESHOLD env var)
        """
        self.max_tokens = max_tokens or MAX_CONTEXT_TOKENS
        self.warn_threshold = warn_threshold or WARN_THRESHOLD
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        
        Uses simple approximation: ~4 characters per token.
        For production, consider using tiktoken or similar.
        
        Args:
            text: Text to estimate tokens for
            
        Returns:
            Estimated token count
        """
        # Simple approximation: ~4 chars per token
        # For production, use tiktoken: len(encoding.encode(text))
        return len(text) // 4
    
    def track_components(
        self,
        system_prompt: str = "",
        history: List[Dict[str, str]] = None,
        rag_docs: List[str] = None,
        memory_items: List[str] = None
    ) -> TokenBreakdown:
        """
        Track token usage across all components.
        
        Args:
            system_prompt: System prompt text
            history: Conversation history (list of {"role": "...", "content": "..."})
            rag_docs: RAG document chunks (list of text strings)
            memory_items: Memory item contents (list of text strings)
            
        Returns:
            TokenBreakdown with token counts per component
        """
        history = history or []
        rag_docs = rag_docs or []
        memory_items = memory_items or []
        
        # Estimate tokens for each component
        system_tokens = self.estimate_tokens(system_prompt)
        
        history_tokens = sum(
            self.estimate_tokens(msg.get("content", ""))
            for msg in history
        )
        
        rag_tokens = sum(
            self.estimate_tokens(doc)
            for doc in rag_docs
        )
        
        memory_tokens = sum(
            self.estimate_tokens(mem)
            for mem in memory_items
        )
        
        return TokenBreakdown(
            system=system_tokens,
            history=history_tokens,
            rag_docs=rag_tokens,
            memory=memory_tokens
        )
    
    def truncate_history(
        self,
        history: List[Dict[str, str]],
        target_tokens: int,
        keep_system: bool = True
    ) -> Tuple[List[Dict[str, str]], int]:
        """
        Truncate conversation history to fit within target token budget.
        
        Keeps most recent messages and removes oldest ones.
        
        Args:
            history: Conversation history (list of {"role": "...", "content": "..."})
            target_tokens: Target token count to fit within
            keep_system: Whether to keep system messages (default: True)
            
        Returns:
            Tuple of (truncated_history, tokens_removed)
        """
        if not history:
            return [], 0
        
        # Estimate tokens for each message
        message_tokens = [
            (msg, self.estimate_tokens(msg.get("content", "")))
            for msg in history
        ]
        
        # Keep system messages if requested
        if keep_system:
            system_messages = [
                (msg, tokens) for msg, tokens in message_tokens
                if msg.get("role") == "system"
            ]
            other_messages = [
                (msg, tokens) for msg, tokens in message_tokens
                if msg.get("role") != "system"
            ]
        else:
            system_messages = []
            other_messages = message_tokens
        
        # Calculate tokens for system messages
        system_tokens = sum(tokens for _, tokens in system_messages)
        remaining_budget = target_tokens - system_tokens
        
        # Keep most recent messages that fit
        truncated = []
        current_tokens = 0
        tokens_removed = 0
        
        # Add messages from newest to oldest until budget is reached
        for msg, tokens in reversed(other_messages):
            if current_tokens + tokens <= remaining_budget:
                truncated.insert(0, msg)
                current_tokens += tokens
            else:
                tokens_removed += tokens
        
        # Add system messages back
        truncated = [msg for msg, _ in system_messages] + truncated
        
        return truncated, tokens_removed
    
    def enforce_budget(
        self,
        system_prompt: str,
        history: List[Dict[str, str]],
        rag_docs: List[str],
        memory_items: List[str] = None
    ) -> Tuple[List[Dict[str, str]], List[str], Optional[str]]:
        """
        Enforce context budget by truncating components as needed.
        
        Priority order for truncation:
        1. History (oldest messages first)
        2. RAG docs (lowest relevance first - requires scores)
        3. Memory items (oldest first)
        
        Args:
            system_prompt: System prompt text
            history: Conversation history
            rag_docs: RAG document chunks
            memory_items: Memory item contents
            
        Returns:
            Tuple of (truncated_history, truncated_rag_docs, warning_message)
            warning_message is None if no warning needed, otherwise contains warning text
        """
        memory_items = memory_items or []
        
        # Track current usage
        breakdown = self.track_components(
            system_prompt=system_prompt,
            history=history,
            rag_docs=rag_docs,
            memory_items=memory_items
        )
        
        warning = None
        
        # Check if warning needed (80% threshold)
        if breakdown.should_warn:
            warning = (
                f"Context usage at {breakdown.utilization:.1%} "
                f"({breakdown.total:,}/{self.max_tokens:,} tokens). "
                "Consider starting a new conversation."
            )
        
        # If over budget, truncate
        if breakdown.is_over_budget:
            # Calculate how much to reduce
            overage = breakdown.total - self.max_tokens
            
            # Reserve space for system prompt and some RAG/memory
            system_tokens = breakdown.system
            reserved_for_rag = min(breakdown.rag_docs, self.max_tokens // 4)  # Reserve 25% for RAG
            reserved_for_memory = min(breakdown.memory, self.max_tokens // 10)  # Reserve 10% for memory
            
            # Target for history
            history_budget = self.max_tokens - system_tokens - reserved_for_rag - reserved_for_memory
            
            # Truncate history
            truncated_history, _ = self.truncate_history(history, history_budget)
            
            # If still over budget, truncate RAG docs (simple: keep first N)
            remaining_tokens = (
                self.track_components(
                    system_prompt=system_prompt,
                    history=truncated_history,
                    rag_docs=rag_docs,
                    memory_items=memory_items
                ).total
            )
            
            truncated_rag = rag_docs
            if remaining_tokens > self.max_tokens:
                # Remove RAG docs until under budget
                rag_tokens_per_doc = [self.estimate_tokens(doc) for doc in rag_docs]
                total_rag_tokens = sum(rag_tokens_per_doc)
                excess = remaining_tokens - self.max_tokens
                
                # Remove docs from end (assuming they're sorted by relevance)
                removed_tokens = 0
                truncated_rag = []
                for i, (doc, tokens) in enumerate(zip(rag_docs, rag_tokens_per_doc)):
                    if removed_tokens + tokens <= excess:
                        removed_tokens += tokens
                    else:
                        truncated_rag = rag_docs[i:]
                        break
            
            return truncated_history, truncated_rag, warning
        
        # Under budget, no truncation needed
        return history, rag_docs, warning
    
    def get_budget_status(self, breakdown: TokenBreakdown) -> Dict[str, any]:
        """
        Get budget status information.
        
        Args:
            breakdown: Token breakdown
            
        Returns:
            Dictionary with budget status information
        """
        return {
            "total_tokens": breakdown.total,
            "max_tokens": self.max_tokens,
            "utilization": breakdown.utilization,
            "utilization_percent": breakdown.utilization * 100,
            "is_over_budget": breakdown.is_over_budget,
            "should_warn": breakdown.should_warn,
            "breakdown": {
                "system": breakdown.system,
                "history": breakdown.history,
                "rag_docs": breakdown.rag_docs,
                "memory": breakdown.memory
            }
        }

