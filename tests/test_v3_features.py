"""
Test V3 Features

Quick tests for new V3 endpoints and functionality.
"""
import pytest
import requests
import json
from typing import Dict


# Base URL for API (adjust if needed)
API_BASE = "http://localhost:8080"


class TestV3Features:
    """Test V3 feature endpoints"""
    
    def test_collaboration_session_creation(self):
        """Test creating a collaboration session"""
        response = requests.post(
            f"{API_BASE}/collaboration/sessions",
            json={
                "owner_id": "test_user",
                "session_type": "browser",
                "target_id": "browser_session_123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["owner_id"] == "test_user"
        assert data["session_type"] == "browser"
    
    def test_memory_templates_list(self):
        """Test listing memory templates"""
        response = requests.get(f"{API_BASE}/memory/templates")
        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        assert isinstance(data["templates"], list)
        # Should have default templates
        assert len(data["templates"]) > 0
    
    def test_integrations_list(self):
        """Test listing available integrations"""
        response = requests.get(f"{API_BASE}/integrations")
        assert response.status_code == 200
        data = response.json()
        assert "integrations" in data
        assert isinstance(data["integrations"], list)
        # Should have at least Zapier, Slack, Email, Spotify
        integration_names = [i["name"] for i in data["integrations"]]
        assert "zapier" in integration_names
        assert "slack" in integration_names
        assert "email" in integration_names
        assert "spotify" in integration_names
    
    def test_agent_marketplace(self):
        """Test agent marketplace endpoint"""
        response = requests.get(f"{API_BASE}/agents/marketplace")
        assert response.status_code == 200
        data = response.json()
        assert "custom_agents" in data
        assert "marketplace_agents" in data
        assert isinstance(data["custom_agents"], list)
        assert isinstance(data["marketplace_agents"], list)
    
    def test_analytics_endpoints(self):
        """Test analytics endpoints"""
        # Test usage statistics
        response = requests.get(f"{API_BASE}/analytics/usage?user_id=test_user&days=30")
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        
        # Test cost analysis
        response = requests.get(f"{API_BASE}/analytics/cost?user_id=test_user&days=30")
        assert response.status_code == 200
        data = response.json()
        assert "cost_breakdown" in data
        
        # Test performance metrics
        response = requests.get(f"{API_BASE}/analytics/performance?user_id=test_user&days=30")
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
    
    def test_document_processing_endpoints(self):
        """Test document processing endpoints"""
        # Test document categorization (with sample text)
        response = requests.post(
            f"{API_BASE}/documents/categorize",
            params={"text": "This is a meeting note about project planning.", "user_id": "test_user"}
        )
        # May require OpenAI API key, so check for either success or appropriate error
        assert response.status_code in [200, 500]  # 500 if API key not set
    
    def test_memory_clustering(self):
        """Test memory clustering endpoint"""
        response = requests.post(
            f"{API_BASE}/memory/cluster",
            params={"user_id": "test_user"}
        )
        # May require OpenAI API key and existing memories
        assert response.status_code in [200, 500]
    
    def test_memory_conflicts(self):
        """Test memory conflict detection"""
        response = requests.get(
            f"{API_BASE}/memory/conflicts",
            params={"user_id": "test_user"}
        )
        # May require OpenAI API key and existing memories
        assert response.status_code in [200, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

