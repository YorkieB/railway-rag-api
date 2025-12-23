"""
Unit tests for ContextBudgetEnforcer
"""

import unittest
import sys
import os

# Add parent directory to path to import rag-api modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../rag-api'))
from budget import ContextBudgetEnforcer


class TestContextBudgetEnforcer(unittest.TestCase):
    
    def setUp(self):
        self.enforcer = ContextBudgetEnforcer(max_tokens=100000, warn_threshold=0.8)
    
    def test_estimate_tokens(self):
        """Test token estimation"""
        text = "This is a test" * 100  # ~1400 characters
        tokens = self.enforcer.estimate_tokens(text)
        self.assertGreater(tokens, 0)
        self.assertLess(tokens, 1000)  # Should be reasonable
    
    def test_check_budget_under_limit(self):
        """Test budget check when under limit"""
        result = self.enforcer.check_budget(
            system_tokens=1000,
            history_tokens=5000,
            rag_tokens=10000,
            memory_tokens=0
        )
        self.assertFalse(result["over_budget"])
        self.assertFalse(result.get("warning", False))
    
    def test_check_budget_warning(self):
        """Test budget warning at 80%"""
        result = self.enforcer.check_budget(
            system_tokens=1000,
            history_tokens=50000,
            rag_tokens=30000,
            memory_tokens=0
        )
        self.assertFalse(result["over_budget"])
        self.assertTrue(result.get("warning", False))
    
    def test_check_budget_over_limit(self):
        """Test budget check when over limit"""
        result = self.enforcer.check_budget(
            system_tokens=1000,
            history_tokens=50000,
            rag_tokens=60000,
            memory_tokens=0
        )
        self.assertTrue(result["over_budget"])
        self.assertEqual(result["action"], "truncate")
    
    def test_truncate_history(self):
        """Test history truncation"""
        messages = [
            {"role": "system", "content": "System prompt"},
            {"role": "user", "content": "Message 1" * 1000},
            {"role": "assistant", "content": "Response 1" * 1000},
            {"role": "user", "content": "Message 2" * 1000},
            {"role": "assistant", "content": "Response 2" * 1000},
        ]
        
        truncated = self.enforcer.truncate_history(messages, max_history_tokens=1000)
        self.assertLessEqual(len(truncated), len(messages))
        # System message should be kept
        self.assertEqual(truncated[0]["role"], "system")


if __name__ == "__main__":
    unittest.main()

