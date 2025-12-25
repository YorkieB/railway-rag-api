"""
Unit Tests for ContextBudgetEnforcer
"""

import pytest
from rag_api.budget import ContextBudgetEnforcer, TokenBreakdown


class TestTokenBreakdown:
    """Test TokenBreakdown dataclass."""
    
    def test_total_calculation(self):
        """Test total token calculation."""
        breakdown = TokenBreakdown(
            system=1000,
            history=2000,
            rag_docs=3000,
            memory=500
        )
        assert breakdown.total == 6500
    
    def test_utilization_calculation(self):
        """Test utilization calculation."""
        breakdown = TokenBreakdown(
            system=1000,
            history=2000,
            rag_docs=3000,
            memory=500
        )
        # With default MAX_CONTEXT_TOKENS=100000
        assert breakdown.utilization == 6500 / 100000
    
    def test_is_over_budget(self):
        """Test over budget detection."""
        # Create breakdown that exceeds default limit
        breakdown = TokenBreakdown(
            system=50000,
            history=30000,
            rag_docs=30000,
            memory=1000
        )
        assert breakdown.is_over_budget == True
    
    def test_should_warn(self):
        """Test warning threshold detection."""
        # Create breakdown at 80% utilization
        breakdown = TokenBreakdown(
            system=20000,
            history=20000,
            rag_docs=20000,
            memory=20000
        )
        assert breakdown.should_warn == True


class TestContextBudgetEnforcer:
    """Test ContextBudgetEnforcer class."""
    
    def test_estimate_tokens(self):
        """Test token estimation."""
        enforcer = ContextBudgetEnforcer()
        # Simple approximation: ~4 chars per token
        assert enforcer.estimate_tokens("test") == 1
        assert enforcer.estimate_tokens("test " * 4) == 4
    
    def test_track_components(self):
        """Test component tracking."""
        enforcer = ContextBudgetEnforcer()
        
        breakdown = enforcer.track_components(
            system_prompt="System prompt",
            history=[
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there"}
            ],
            rag_docs=["Document 1", "Document 2"],
            memory_items=["Memory 1"]
        )
        
        assert breakdown.system > 0
        assert breakdown.history > 0
        assert breakdown.rag_docs > 0
        assert breakdown.memory > 0
    
    def test_truncate_history(self):
        """Test history truncation."""
        enforcer = ContextBudgetEnforcer(max_tokens=1000, warn_threshold=0.8)
        
        # Create long history
        history = [
            {"role": "user", "content": "Message " + str(i) * 100}
            for i in range(20)
        ]
        
        truncated, removed = enforcer.truncate_history(history, target_tokens=500)
        
        assert len(truncated) < len(history)
        assert removed > 0
    
    def test_enforce_budget_under_limit(self):
        """Test budget enforcement when under limit."""
        enforcer = ContextBudgetEnforcer(max_tokens=100000)
        
        history, rag_docs, warning = enforcer.enforce_budget(
            system_prompt="System",
            history=[{"role": "user", "content": "Hello"}],
            rag_docs=["Doc 1"],
            memory_items=[]
        )
        
        assert len(history) == 1
        assert len(rag_docs) == 1
        assert warning is None
    
    def test_enforce_budget_over_limit(self):
        """Test budget enforcement when over limit."""
        enforcer = ContextBudgetEnforcer(max_tokens=100)
        
        # Create content that exceeds limit
        long_history = [
            {"role": "user", "content": "x" * 1000}
            for _ in range(10)
        ]
        
        history, rag_docs, warning = enforcer.enforce_budget(
            system_prompt="System prompt",
            history=long_history,
            rag_docs=["Document " * 100],
            memory_items=[]
        )
        
        # Should truncate
        assert len(history) < len(long_history) or len(rag_docs) < 1
    
    def test_warning_at_threshold(self):
        """Test warning at 80% threshold."""
        enforcer = ContextBudgetEnforcer(max_tokens=1000, warn_threshold=0.8)
        
        # Create content at 85% utilization
        large_content = "x" * 3400  # ~850 tokens
        
        history, rag_docs, warning = enforcer.enforce_budget(
            system_prompt="",
            history=[{"role": "user", "content": large_content}],
            rag_docs=[],
            memory_items=[]
        )
        
        assert warning is not None
        assert "80%" in warning or "85%" in warning or "utilization" in warning.lower()
    
    def test_get_budget_status(self):
        """Test budget status generation."""
        enforcer = ContextBudgetEnforcer()
        
        breakdown = TokenBreakdown(
            system=1000,
            history=2000,
            rag_docs=3000,
            memory=500
        )
        
        status = enforcer.get_budget_status(breakdown)
        
        assert "total_tokens" in status
        assert "utilization" in status
        assert "breakdown" in status
        assert status["total_tokens"] == 6500

