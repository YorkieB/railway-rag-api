"""
Unit Tests for CostTracker
"""

import pytest
from rag_api.cost import CostTracker, DailyBudget, InMemoryBudgetStorage


class TestDailyBudget:
    """Test DailyBudget dataclass."""
    
    def test_utilization_calculations(self):
        """Test utilization calculations."""
        budget = DailyBudget(
            user_id="test_user",
            date="2025-12-25",
            text_tokens_used=400000,
            text_tokens_limit=500000
        )
        
        assert budget.text_tokens_utilization == 0.8
        assert budget.should_warn == True
    
    def test_is_exceeded(self):
        """Test exceeded detection."""
        budget = DailyBudget(
            user_id="test_user",
            date="2025-12-25",
            text_tokens_used=500000,
            text_tokens_limit=500000
        )
        
        assert budget.is_exceeded == True
    
    def test_get_warnings(self):
        """Test warning generation."""
        budget = DailyBudget(
            user_id="test_user",
            date="2025-12-25",
            text_tokens_used=450000,  # 90% utilization
            text_tokens_limit=500000
        )
        
        warnings = budget.get_warnings()
        assert len(warnings) > 0
        assert "Text tokens" in warnings[0]


class TestCostTracker:
    """Test CostTracker class."""
    
    def test_estimate_text_cost(self):
        """Test text cost estimation."""
        tracker = CostTracker()
        
        cost = tracker.estimate_text_cost(1000)
        assert cost > 0
        assert cost == (1000 / 1000) * tracker.COST_PER_1K_TOKENS
    
    def test_check_budget_allowed(self):
        """Test budget check when allowed."""
        tracker = CostTracker()
        
        is_allowed, error, budget = tracker.check_budget(
            user_id="test_user",
            estimated_text_tokens=1000
        )
        
        assert is_allowed == True
        assert error is None
        assert budget is not None
    
    def test_check_budget_exceeded(self):
        """Test budget check when exceeded."""
        tracker = CostTracker()
        
        # Use up all budget
        budget, _ = tracker.track_usage(
            user_id="test_user",
            text_tokens=500000  # Use all default limit
        )
        
        # Try to use more
        is_allowed, error, _ = tracker.check_budget(
            user_id="test_user",
            estimated_text_tokens=1000
        )
        
        assert is_allowed == False
        assert error is not None
        assert "limit reached" in error.lower()
    
    def test_track_usage(self):
        """Test usage tracking."""
        tracker = CostTracker()
        
        budget, cost_info = tracker.track_usage(
            user_id="test_user",
            text_tokens=1000
        )
        
        assert budget.text_tokens_used == 1000
        assert cost_info["text_tokens"] == 1000
        assert cost_info["total_cost"] > 0
    
    def test_get_budget_status(self):
        """Test budget status retrieval."""
        tracker = CostTracker()
        
        # Track some usage
        tracker.track_usage(user_id="test_user", text_tokens=1000)
        
        status = tracker.get_budget_status("test_user")
        
        assert status["user_id"] == "test_user"
        assert "text_tokens" in status
        assert "dollars" in status
        assert status["text_tokens"]["used"] == 1000

