"""
Unit tests for UncertaintyChecker
"""

import unittest
import sys
import os

# Add parent directory to path to import rag-api modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../rag-api'))
from uncertainty import UncertaintyChecker


class TestUncertaintyChecker(unittest.TestCase):
    
    def setUp(self):
        self.checker = UncertaintyChecker(threshold=0.6)
    
    def test_empty_retrieval(self):
        """Test that empty retrieval triggers uncertainty"""
        result = self.checker.check_retrieval([])
        self.assertTrue(result["uncertain"])
        self.assertEqual(result["reason"], "empty_retrieval")
    
    def test_low_confidence(self):
        """Test that low confidence triggers uncertainty"""
        docs = [{"score": 0.5, "text": "Some text"}]
        result = self.checker.check_retrieval(docs)
        self.assertTrue(result["uncertain"])
        self.assertEqual(result["reason"], "low_confidence")
    
    def test_high_confidence(self):
        """Test that high confidence does not trigger uncertainty"""
        docs = [{"score": 0.8, "text": "Some text"}]
        result = self.checker.check_retrieval(docs)
        self.assertFalse(result["uncertain"])
    
    def test_generate_uncertain_response(self):
        """Test uncertain response generation"""
        response = self.checker.generate_uncertain_response("test question", "empty_retrieval")
        self.assertTrue(response["uncertain"])
        self.assertEqual(response["reason"], "empty_retrieval")
        self.assertIn("suggestions", response)
        self.assertEqual(len(response["suggestions"]), 3)


if __name__ == "__main__":
    unittest.main()

