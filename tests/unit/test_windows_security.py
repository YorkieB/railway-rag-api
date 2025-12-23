"""
Unit tests for Windows Trust Boundaries
"""
import pytest
import os
import sys
import tempfile
import shutil

# Add parent directory to path to import rag-api modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../rag-api'))
from windows.security import TrustBoundaries


class TestTrustBoundaries:
    """Test trust boundaries functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.trust = TrustBoundaries()
    
    def test_create_session_key(self):
        """Test creating session key."""
        session_id = "test_session_123"
        key = self.trust.create_session_key(session_id)
        
        assert key is not None
        assert len(key) == 32  # 32 bytes = 256 bits
    
    def test_get_session_key(self):
        """Test retrieving session key."""
        session_id = "test_session_123"
        key1 = self.trust.create_session_key(session_id)
        key2 = self.trust.get_session_key(session_id)
        
        assert key1 == key2
    
    def test_get_nonexistent_session_key(self):
        """Test retrieving non-existent session key."""
        key = self.trust.get_session_key("nonexistent_session")
        assert key is None
    
    def test_clear_session_key(self):
        """Test clearing session key."""
        session_id = "test_session_123"
        self.trust.create_session_key(session_id)
        
        # Verify exists
        key = self.trust.get_session_key(session_id)
        assert key is not None
        
        # Clear
        success = self.trust.clear_session_key(session_id)
        assert success is True
        
        # Verify cleared
        key = self.trust.get_session_key(session_id)
        assert key is None
    
    def test_clear_all_session_keys(self):
        """Test clearing all session keys."""
        self.trust.create_session_key("session1")
        self.trust.create_session_key("session2")
        
        # Verify exist
        assert self.trust.get_session_key("session1") is not None
        assert self.trust.get_session_key("session2") is not None
        
        # Clear all
        self.trust.clear_all_session_keys()
        
        # Verify cleared
        assert self.trust.get_session_key("session1") is None
        assert self.trust.get_session_key("session2") is None
    
    def test_create_temp_file(self):
        """Test creating temporary file."""
        content = b"test file content"
        filepath = self.trust.create_temp_file("test.txt", content)
        
        assert os.path.exists(filepath)
        with open(filepath, "rb") as f:
            assert f.read() == content
    
    def test_should_send_to_cloud_credentials(self):
        """Test cloud send policy for credentials."""
        # Credentials should never be sent
        assert self.trust.should_send_to_cloud("credentials", user_consent=True) is False
        assert self.trust.should_send_to_cloud("passwords", user_consent=True) is False
        assert self.trust.should_send_to_cloud("api_keys", user_consent=True) is False
    
    def test_should_send_to_cloud_session_keys(self):
        """Test cloud send policy for session keys."""
        # Session keys should never be sent
        assert self.trust.should_send_to_cloud("session_keys", user_consent=True) is False
    
    def test_should_send_to_cloud_screenshots(self):
        """Test cloud send policy for screenshots."""
        # Screenshots only with user consent
        assert self.trust.should_send_to_cloud("screenshots", user_consent=False) is False
        assert self.trust.should_send_to_cloud("screenshots", user_consent=True) is True
    
    def test_redact_sensitive_data(self):
        """Test sensitive data redaction."""
        # API key
        data = "My API key is sk-proj-abc123xyz"
        redacted = self.trust.redact_sensitive_data(data)
        assert "[API_KEY_REDACTED]" in redacted
        assert "sk-proj-abc123xyz" not in redacted
        
        # Credit card
        data = "Card number: 1234-5678-9012-3456"
        redacted = self.trust.redact_sensitive_data(data)
        assert "[CARD_REDACTED]" in redacted
        assert "1234-5678-9012-3456" not in redacted
        
        # SSN
        data = "SSN: 123-45-6789"
        redacted = self.trust.redact_sensitive_data(data)
        assert "[SSN_REDACTED]" in redacted
        assert "123-45-6789" not in redacted
        
        # Password
        data = "password: secret123"
        redacted = self.trust.redact_sensitive_data(data)
        assert "[REDACTED]" in redacted
        assert "secret123" not in redacted


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

