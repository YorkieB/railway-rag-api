"""
Unit tests for Windows Credential Management
"""
import pytest
import os
import sys
import tempfile
import shutil

# Add parent directory to path to import rag-api modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../rag-api'))
from windows.credentials import CredentialManager


class TestCredentialManager:
    """Test credential management functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.cred_manager = CredentialManager()
        self.test_credential_name = "test_credential"
        self.test_username = "test_user"
        self.test_password = "test_password_123"
    
    def teardown_method(self):
        """Clean up test fixtures."""
        # Clean up test credentials
        try:
            self.cred_manager.delete_credential(self.test_credential_name)
        except Exception:
            pass
    
    def test_store_credential(self):
        """Test storing a credential."""
        success = self.cred_manager.store_credential(
            self.test_credential_name,
            self.test_username,
            self.test_password,
            "Test credential"
        )
        
        assert success is True
    
    def test_retrieve_credential(self):
        """Test retrieving a credential."""
        # Store first
        self.cred_manager.store_credential(
            self.test_credential_name,
            self.test_username,
            self.test_password
        )
        
        # Retrieve
        credential = self.cred_manager.retrieve_credential(self.test_credential_name)
        
        assert credential is not None
        assert credential["username"] == self.test_username
        assert credential["password"] == self.test_password
    
    def test_retrieve_nonexistent_credential(self):
        """Test retrieving non-existent credential."""
        credential = self.cred_manager.retrieve_credential("nonexistent_credential")
        assert credential is None
    
    def test_delete_credential(self):
        """Test deleting a credential."""
        # Store first
        self.cred_manager.store_credential(
            self.test_credential_name,
            self.test_username,
            self.test_password
        )
        
        # Verify exists
        credential = self.cred_manager.retrieve_credential(self.test_credential_name)
        assert credential is not None
        
        # Delete
        success = self.cred_manager.delete_credential(self.test_credential_name)
        assert success is True
        
        # Verify deleted
        credential = self.cred_manager.retrieve_credential(self.test_credential_name)
        assert credential is None
    
    def test_list_credentials(self):
        """Test listing credentials."""
        # Store a few credentials
        self.cred_manager.store_credential("cred1", "user1", "pass1")
        self.cred_manager.store_credential("cred2", "user2", "pass2")
        
        # List
        credentials = self.cred_manager.list_credentials()
        
        assert isinstance(credentials, list)
        assert "cred1" in credentials or "cred2" in credentials
        
        # Cleanup
        self.cred_manager.delete_credential("cred1")
        self.cred_manager.delete_credential("cred2")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

