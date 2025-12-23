"""
Unit tests for CostTracker
"""

import unittest
import sys
import os
from datetime import date

# Add parent directory to path to import rag-api modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../rag-api'))
from cost import CostTracker


class TestCostTracker(unittest.TestCase):
    
    def setUp(self):
        self.tracker = CostTracker()
        # Clear any existing budgets
        self.tracker.user_budgets = {}
    
    def test_estimate_cost(self):
        """Test cost estimation"""
        cost = self.tracker.estimate_cost(1000000)  # 1M tokens
        self.assertGreater(cost, 0)
        self.assertLess(cost, 10)  # Should be around $6.25
    
    def test_check_daily_budget_within_limit(self):
        """Test budget check when within limit"""
        result = self.tracker.check_daily_budget("test_user", 1000, 0.01)
        self.assertTrue(result["within_budget"])
        self.assertFalse(result.get("warning", False))
    
    def test_check_daily_budget_warning(self):
        """Test budget warning at 80%"""
        # Use 80% of token limit
        result = self.tracker.check_daily_budget("test_user", 400000, 8.0)
        self.assertTrue(result["within_budget"])
        self.assertTrue(result.get("warning", False))
    
    def test_check_daily_budget_exceeded(self):
        """Test budget check when exceeded"""
        result = self.tracker.check_daily_budget("test_user", 600000, 12.0)
        self.assertFalse(result["within_budget"])
        self.assertEqual(result["action"], "reject")
    
    def test_update_budget(self):
        """Test budget update"""
        self.tracker.update_budget("test_user", 1000, 0.01)
        today = date.today().isoformat()
        self.assertIn("test_user", self.tracker.user_budgets)
        self.assertIn(today, self.tracker.user_budgets["test_user"])
        self.assertEqual(self.tracker.user_budgets["test_user"][today]["tokens_used"], 1000)


if __name__ == "__main__":
    unittest.main()

