"""
Cost Tracking and Budget Management

Tracks per-user daily budgets for tokens, vision tokens, audio minutes, and dollars.
Implements pre-query cost estimation, warnings at 80%, and hard halts at 100%.
"""

import os
from typing import Dict, Optional, Tuple, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

# Configuration
DEFAULT_DAILY_BUDGETS = {
    "text_tokens": 500000,      # 500K tokens/day
    "vision_tokens": 50000,     # 50K tokens/day
    "audio_minutes": 60.0,      # 60 minutes/day
    "dollars": 10.0             # $10/day
}

WARN_THRESHOLD = 0.8  # Warn at 80%


@dataclass
class DailyBudget:
    """Daily budget tracking for a user."""
    user_id: str
    date: str  # YYYY-MM-DD format
    text_tokens_used: int = 0
    vision_tokens_used: int = 0
    audio_minutes_used: float = 0.0
    dollars_used: float = 0.0
    
    # Budget limits (configurable per user)
    text_tokens_limit: int = DEFAULT_DAILY_BUDGETS["text_tokens"]
    vision_tokens_limit: int = DEFAULT_DAILY_BUDGETS["vision_tokens"]
    audio_minutes_limit: float = DEFAULT_DAILY_BUDGETS["audio_minutes"]
    dollars_limit: float = DEFAULT_DAILY_BUDGETS["dollars"]
    
    @property
    def text_tokens_utilization(self) -> float:
        """Text tokens utilization (0.0 to 1.0)."""
        return self.text_tokens_used / self.text_tokens_limit if self.text_tokens_limit > 0 else 0.0
    
    @property
    def vision_tokens_utilization(self) -> float:
        """Vision tokens utilization (0.0 to 1.0)."""
        return self.vision_tokens_used / self.vision_tokens_limit if self.vision_tokens_limit > 0 else 0.0
    
    @property
    def audio_minutes_utilization(self) -> float:
        """Audio minutes utilization (0.0 to 1.0)."""
        return self.audio_minutes_used / self.audio_minutes_limit if self.audio_minutes_limit > 0 else 0.0
    
    @property
    def dollars_utilization(self) -> float:
        """Dollars utilization (0.0 to 1.0)."""
        return self.dollars_used / self.dollars_limit if self.dollars_limit > 0 else 0.0
    
    @property
    def should_warn(self) -> bool:
        """Check if any budget is at warning threshold (80%)."""
        return (
            self.text_tokens_utilization >= WARN_THRESHOLD or
            self.vision_tokens_utilization >= WARN_THRESHOLD or
            self.audio_minutes_utilization >= WARN_THRESHOLD or
            self.dollars_utilization >= WARN_THRESHOLD
        )
    
    @property
    def is_exceeded(self) -> bool:
        """Check if any budget is exceeded (100%)."""
        return (
            self.text_tokens_used >= self.text_tokens_limit or
            self.vision_tokens_used >= self.vision_tokens_limit or
            self.audio_minutes_used >= self.audio_minutes_limit or
            self.dollars_used >= self.dollars_limit
        )
    
    def get_warnings(self) -> List[str]:
        """Get warning messages for budgets at threshold."""
        warnings = []
        
        if self.text_tokens_utilization >= WARN_THRESHOLD:
            warnings.append(
                f"Text tokens: {self.text_tokens_utilization:.1%} used "
                f"({self.text_tokens_used:,}/{self.text_tokens_limit:,})"
            )
        
        if self.vision_tokens_utilization >= WARN_THRESHOLD:
            warnings.append(
                f"Vision tokens: {self.vision_tokens_utilization:.1%} used "
                f"({self.vision_tokens_used:,}/{self.vision_tokens_limit:,})"
            )
        
        if self.audio_minutes_utilization >= WARN_THRESHOLD:
            warnings.append(
                f"Audio minutes: {self.audio_minutes_utilization:.1%} used "
                f"({self.audio_minutes_used:.1f}/{self.audio_minutes_limit:.1f})"
            )
        
        if self.dollars_utilization >= WARN_THRESHOLD:
            warnings.append(
                f"Cost: {self.dollars_utilization:.1%} used "
                f"(${self.dollars_used:.2f}/${self.dollars_limit:.2f})"
            )
        
        return warnings


class BudgetStorage(ABC):
    """Abstract base class for budget storage."""
    
    @abstractmethod
    def get_daily_budget(self, user_id: str, date: str) -> Optional[DailyBudget]:
        """Get daily budget for user and date."""
        pass
    
    @abstractmethod
    def save_daily_budget(self, budget: DailyBudget) -> None:
        """Save daily budget."""
        pass


class InMemoryBudgetStorage(BudgetStorage):
    """In-memory budget storage (for development/testing)."""
    
    def __init__(self):
        """Initialize in-memory storage."""
        self._budgets: Dict[Tuple[str, str], DailyBudget] = {}
    
    def get_daily_budget(self, user_id: str, date: str) -> Optional[DailyBudget]:
        """Get daily budget from memory."""
        key = (user_id, date)
        return self._budgets.get(key)
    
    def save_daily_budget(self, budget: DailyBudget) -> None:
        """Save daily budget to memory."""
        key = (budget.user_id, budget.date)
        self._budgets[key] = budget


class CostTracker:
    """
    Tracks and enforces per-user daily budgets.
    
    Features:
    - Pre-query cost estimation
    - Post-query cost tracking
    - Warnings at 80% utilization
    - Hard halts at 100% utilization
    - Response headers with cost information
    """
    
    # Cost per token (approximate, adjust based on actual API costs)
    COST_PER_1K_TOKENS = 0.01  # $0.01 per 1K tokens (adjust for your model)
    COST_PER_VISION_TOKEN = 0.00001  # $0.00001 per vision token
    COST_PER_AUDIO_MINUTE = 0.15  # $0.15 per audio minute
    
    def __init__(self, storage: Optional[BudgetStorage] = None):
        """
        Initialize cost tracker.
        
        Args:
            storage: Budget storage implementation (defaults to in-memory)
        """
        self.storage = storage or InMemoryBudgetStorage()
    
    def _get_today(self) -> str:
        """Get today's date in YYYY-MM-DD format."""
        return datetime.utcnow().strftime("%Y-%m-%d")
    
    def _get_or_create_budget(self, user_id: str, date: Optional[str] = None) -> DailyBudget:
        """
        Get or create daily budget for user.
        
        Args:
            user_id: User ID
            date: Date string (YYYY-MM-DD), defaults to today
            
        Returns:
            DailyBudget instance
        """
        date = date or self._get_today()
        
        budget = self.storage.get_daily_budget(user_id, date)
        if budget is None:
            budget = DailyBudget(user_id=user_id, date=date)
            self.storage.save_daily_budget(budget)
        
        return budget
    
    def estimate_text_cost(self, tokens: int) -> float:
        """
        Estimate cost for text tokens.
        
        Args:
            tokens: Number of tokens
            
        Returns:
            Estimated cost in dollars
        """
        return (tokens / 1000) * self.COST_PER_1K_TOKENS
    
    def estimate_vision_cost(self, tokens: int) -> float:
        """
        Estimate cost for vision tokens.
        
        Args:
            tokens: Number of vision tokens
            
        Returns:
            Estimated cost in dollars
        """
        return tokens * self.COST_PER_VISION_TOKEN
    
    def estimate_audio_cost(self, minutes: float) -> float:
        """
        Estimate cost for audio minutes.
        
        Args:
            minutes: Number of audio minutes
            
        Returns:
            Estimated cost in dollars
        """
        return minutes * self.COST_PER_AUDIO_MINUTE
    
    def check_budget(
        self,
        user_id: str,
        estimated_text_tokens: int = 0,
        estimated_vision_tokens: int = 0,
        estimated_audio_minutes: float = 0.0
    ) -> Tuple[bool, Optional[str], DailyBudget]:
        """
        Check if request is within budget.
        
        Args:
            user_id: User ID
            estimated_text_tokens: Estimated text tokens for request
            estimated_vision_tokens: Estimated vision tokens for request
            estimated_audio_minutes: Estimated audio minutes for request
            
        Returns:
            Tuple of (is_allowed, error_message, budget)
            is_allowed: True if within budget, False if exceeded
            error_message: Error message if not allowed, None otherwise
            budget: DailyBudget instance
        """
        budget = self._get_or_create_budget(user_id)
        
        # Check if already exceeded
        if budget.is_exceeded:
            return False, "Daily budget limit reached. Please try again tomorrow.", budget
        
        # Check if estimated usage would exceed budget
        if (
            budget.text_tokens_used + estimated_text_tokens >= budget.text_tokens_limit or
            budget.vision_tokens_used + estimated_vision_tokens >= budget.vision_tokens_limit or
            budget.audio_minutes_used + estimated_audio_minutes >= budget.audio_minutes_limit
        ):
            return False, "Estimated usage would exceed daily budget limit.", budget
        
        return True, None, budget
    
    def track_usage(
        self,
        user_id: str,
        text_tokens: int = 0,
        vision_tokens: int = 0,
        audio_minutes: float = 0.0
    ) -> Tuple[DailyBudget, Dict[str, float]]:
        """
        Track actual usage and update budget.
        
        Args:
            user_id: User ID
            text_tokens: Actual text tokens used
            vision_tokens: Actual vision tokens used
            audio_minutes: Actual audio minutes used
            
        Returns:
            Tuple of (updated_budget, cost_info)
            cost_info: Dictionary with cost breakdown
        """
        budget = self._get_or_create_budget(user_id)
        
        # Calculate costs
        text_cost = self.estimate_text_cost(text_tokens)
        vision_cost = self.estimate_vision_cost(vision_tokens)
        audio_cost = self.estimate_audio_cost(audio_minutes)
        total_cost = text_cost + vision_cost + audio_cost
        
        # Update budget
        budget.text_tokens_used += text_tokens
        budget.vision_tokens_used += vision_tokens
        budget.audio_minutes_used += audio_minutes
        budget.dollars_used += total_cost
        
        # Save updated budget
        self.storage.save_daily_budget(budget)
        
        # Build cost info
        cost_info = {
            "text_tokens": text_tokens,
            "vision_tokens": vision_tokens,
            "audio_minutes": audio_minutes,
            "text_cost": text_cost,
            "vision_cost": vision_cost,
            "audio_cost": audio_cost,
            "total_cost": total_cost
        }
        
        return budget, cost_info
    
    def get_budget_status(self, user_id: str) -> Dict[str, any]:
        """
        Get current budget status for user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with budget status information
        """
        budget = self._get_or_create_budget(user_id)
        
        return {
            "user_id": user_id,
            "date": budget.date,
            "text_tokens": {
                "used": budget.text_tokens_used,
                "limit": budget.text_tokens_limit,
                "remaining": budget.text_tokens_limit - budget.text_tokens_used,
                "utilization": budget.text_tokens_utilization
            },
            "vision_tokens": {
                "used": budget.vision_tokens_used,
                "limit": budget.vision_tokens_limit,
                "remaining": budget.vision_tokens_limit - budget.vision_tokens_used,
                "utilization": budget.vision_tokens_utilization
            },
            "audio_minutes": {
                "used": budget.audio_minutes_used,
                "limit": budget.audio_minutes_limit,
                "remaining": budget.audio_minutes_limit - budget.audio_minutes_used,
                "utilization": budget.audio_minutes_utilization
            },
            "dollars": {
                "used": budget.dollars_used,
                "limit": budget.dollars_limit,
                "remaining": budget.dollars_limit - budget.dollars_used,
                "utilization": budget.dollars_utilization
            },
            "warnings": budget.get_warnings(),
            "is_exceeded": budget.is_exceeded,
            "should_warn": budget.should_warn
        }

