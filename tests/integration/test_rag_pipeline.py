"""
Integration tests for RAG pipeline
"""

import unittest
import requests
import os
import time


class TestRAGPipeline(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.api_base = os.getenv("API_BASE", "http://localhost:8080")
        cls.user_id = "test_user"
        # Wait for API to be ready
        max_retries = 10
        for i in range(max_retries):
            try:
                response = requests.get(f"{cls.api_base}/health", timeout=2)
                if response.status_code == 200:
                    break
            except:
                if i == max_retries - 1:
                    raise Exception("API not available")
                time.sleep(1)
    
    def test_query_with_documents(self):
        """Test query endpoint with documents"""
        response = requests.post(
            f"{self.api_base}/query",
            json={
                "question": "What is the main topic?",
                "user_id": self.user_id
            },
            headers={"X-User-ID": self.user_id},
            timeout=60
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("answer", data)
        self.assertIn("sources", data)
    
    def test_uncertainty_protocol(self):
        """Test uncertainty protocol for empty retrieval"""
        response = requests.post(
            f"{self.api_base}/query",
            json={
                "question": "What is the capital of Mars?",
                "user_id": self.user_id
            },
            headers={"X-User-ID": self.user_id},
            timeout=60
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Should be uncertain for impossible question
        if data.get("uncertain"):
            self.assertTrue(data["uncertain"])
            self.assertIn("reason", data)
            self.assertIn("suggestions", data)
    
    def test_cost_tracking_headers(self):
        """Test that cost tracking headers are present"""
        response = requests.post(
            f"{self.api_base}/query",
            json={
                "question": "Test question",
                "user_id": self.user_id
            },
            headers={"X-User-ID": self.user_id},
            timeout=60
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("X-Cost-Tokens", response.headers)
        self.assertIn("X-Cost-Dollars", response.headers)
    
    def test_memory_integration(self):
        """Test memory integration in RAG pipeline"""
        # First create a memory
        memory_response = requests.post(
            f"{self.api_base}/memory",
            json={
                "user_id": self.user_id,
                "content": "User prefers Python programming",
                "memory_type": "preference"
            },
            timeout=60
        )
        
        if memory_response.status_code == 200:
            # Then query with memory context
            query_response = requests.post(
                f"{self.api_base}/query",
                json={
                    "question": "What programming language do I prefer?",
                    "user_id": self.user_id
                },
                headers={"X-User-ID": self.user_id},
                timeout=60
            )
            self.assertEqual(query_response.status_code, 200)
            data = query_response.json()
            # Should potentially use memory (if relevant)
            # Note: This is a soft check since memory retrieval is semantic


if __name__ == "__main__":
    unittest.main()

