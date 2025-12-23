"""
Cost Tracking

This module tracks API costs and enforces daily budget limits per user.
Tracks tokens and dollars spent, warns at 80% utilization, and halts at 100%.
"""

from typing import Dict, Optional
from datetime import datetime, date
import os


class CostTracker:
    """Tracks API costs and enforces daily budget limits"""
    
    def __init__(self):
        """
        Initialize cost tracker
        
        Uses in-memory storage for MVP. Future: ChromaDB or Firestore for persistence.
        """
        # In-memory storage: {user_id: {date: {tokens: int, dollars: float}}}
        self.user_budgets = {}
    
    def estimate_cost(self, tokens: int, model: str = "gpt-4o") -> float:
        """
        Estimate cost based on token count and model
        
        GPT-4o pricing (as of 2024):
        - Input: $2.50 per 1M tokens
        - Output: $10.00 per 1M tokens
        
        Rough estimate: assume 50/50 input/output split for average cost
        
        Args:
            tokens: Total token count (input + output)
            model: Model name (default: "gpt-4o")
            
        Returns:
            Estimated cost in dollars
        """
        if model == "gpt-4o":
            # Average cost: (2.50 + 10.00) / 2 = 6.25 per 1M tokens
            cost_per_million = 6.25
        else:
            # Default to GPT-4o pricing for unknown models
            cost_per_million = 6.25
        
        return (tokens / 1_000_000) * cost_per_million
    
    def check_daily_budget(self, user_id: str, tokens: int, dollars: float) -> Dict:
        """
        Check if user is within daily budget
        
        Args:
            user_id: User identifier
            tokens: Tokens to be used in this request
            dollars: Dollars to be spent in this request
            
        Returns:
            Dict with budget status, utilization, and action required
        """
        today = date.today().isoformat()
        
        # Get or initialize user's daily budget
        if user_id not in self.user_budgets:
            self.user_budgets[user_id] = {}
        
        if today not in self.user_budgets[user_id]:
            self.user_budgets[user_id][today] = {
                "tokens_used": 0,
                "dollars_used": 0.0,
                "tokens_limit": 500_000,  # 500K tokens per day
                "dollars_limit": 10.0  # $10 per day
            }
        
        user_budget = self.user_budgets[user_id][today]
        
        # Calculate new totals
        new_tokens = user_budget["tokens_used"] + tokens
        new_dollars = user_budget["dollars_used"] + dollars
        
        # Calculate utilization
        tokens_utilization = new_tokens / user_budget["tokens_limit"] if user_budget["tokens_limit"] > 0 else 0.0
        dollars_utilization = new_dollars / user_budget["dollars_limit"] if user_budget["dollars_limit"] > 0 else 0.0
        
        # Check if over budget
        if new_tokens >= user_budget["tokens_limit"] or new_dollars >= user_budget["dollars_limit"]:
            return {
                "within_budget": False,
                "tokens_used": new_tokens,
                "dollars_used": new_dollars,
                "tokens_limit": user_budget["tokens_limit"],
                "dollars_limit": user_budget["dollars_limit"],
                "tokens_utilization": tokens_utilization,
                "dollars_utilization": dollars_utilization,
                "action": "reject"
            }
        
        # Check if warning threshold reached (80%)
        if tokens_utilization >= 0.8 or dollars_utilization >= 0.8:
            return {
                "within_budget": True,
                "tokens_used": new_tokens,
                "dollars_used": new_dollars,
                "tokens_limit": user_budget["tokens_limit"],
                "dollars_limit": user_budget["dollars_limit"],
                "tokens_utilization": tokens_utilization,
                "dollars_utilization": dollars_utilization,
                "warning": True,
                "utilization": max(tokens_utilization, dollars_utilization)
            }
        
        return {
            "within_budget": True,
            "tokens_used": new_tokens,
            "dollars_used": new_dollars,
            "tokens_limit": user_budget["tokens_limit"],
            "dollars_limit": user_budget["dollars_limit"],
            "tokens_utilization": tokens_utilization,
            "dollars_utilization": dollars_utilization,
            "warning": False
        }
    
    def update_budget(self, user_id: str, tokens: int, dollars: float):
        """
        Update user's daily budget after request
        
        Args:
            user_id: User identifier
            tokens: Tokens used in request
            dollars: Dollars spent in request
        """
        today = date.today().isoformat()
        
        if user_id not in self.user_budgets:
            self.user_budgets[user_id] = {}
        
        if today not in self.user_budgets[user_id]:
            self.user_budgets[user_id][today] = {
                "tokens_used": 0,
                "dollars_used": 0.0,
                "tokens_limit": 500_000,
                "dollars_limit": 10.0
            }
        
        self.user_budgets[user_id][today]["tokens_used"] += tokens
        self.user_budgets[user_id][today]["dollars_used"] += dollars
    
    def get_budget_status(self, user_id: str) -> Optional[Dict]:
        """
        Get current budget status for user
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict with current budget status or None if user not found
        """
        today = date.today().isoformat()
        
        if user_id not in self.user_budgets or today not in self.user_budgets[user_id]:
            return None
        
        budget = self.user_budgets[user_id][today]
        tokens_utilization = budget["tokens_used"] / budget["tokens_limit"] if budget["tokens_limit"] > 0 else 0.0
        dollars_utilization = budget["dollars_used"] / budget["dollars_limit"] if budget["dollars_limit"] > 0 else 0.0
        
        return {
            "tokens_used": budget["tokens_used"],
            "tokens_limit": budget["tokens_limit"],
            "tokens_utilization": tokens_utilization,
            "dollars_used": budget["dollars_used"],
            "dollars_limit": budget["dollars_limit"],
            "dollars_utilization": dollars_utilization,
            "warning": tokens_utilization >= 0.8 or dollars_utilization >= 0.8
        }

