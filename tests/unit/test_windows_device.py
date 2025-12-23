"""
Unit tests for Windows Device Pairing
"""
import pytest
import os
import sys
import tempfile
import shutil

# Add parent directory to path to import rag-api modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../rag-api'))
from windows.device import DevicePairing


class TestDevicePairing:
    """Test device pairing functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.pairing = DevicePairing(storage_path=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_generate_device_keypair(self):
        """Test Ed25519 keypair generation."""
        private_key, public_key = self.pairing.generate_device_keypair()
        
        assert private_key is not None
        assert public_key is not None
        assert len(private_key) > 0
        assert len(public_key) > 0
        assert b"BEGIN PRIVATE KEY" in private_key
        assert b"BEGIN PUBLIC KEY" in public_key
    
    def test_register_device(self):
        """Test device registration."""
        result = self.pairing.register_device()
        
        assert "device_id" in result
        assert "certificate" in result
        assert "status" in result
        assert result["status"] == "registered"
        assert result["certificate"]["status"] == "active"
        
        # Verify device key was stored
        device_id = result["device_id"]
        key = self.pairing.load_device_key(device_id)
        assert key is not None
    
    def test_register_device_with_id(self):
        """Test device registration with specific ID."""
        device_id = "test-device-123"
        result = self.pairing.register_device(device_id=device_id)
        
        assert result["device_id"] == device_id
    
    def test_check_device_status(self):
        """Test device status checking."""
        # Register device first
        result = self.pairing.register_device()
        device_id = result["device_id"]
        
        # Check status
        status = self.pairing.check_device_status(device_id)
        
        assert status["device_id"] == device_id
        assert status["status"] == "active"
        assert status["revoked"] is False
    
    def test_check_nonexistent_device(self):
        """Test checking status of non-existent device."""
        status = self.pairing.check_device_status("nonexistent-device")
        
        assert status["status"] == "not_found"
        assert status["revoked"] is False
    
    def test_revoke_device(self):
        """Test device revocation."""
        # Register device first
        result = self.pairing.register_device()
        device_id = result["device_id"]
        
        # Revoke device
        success = self.pairing.revoke_device(device_id)
        assert success is True
        
        # Check status
        status = self.pairing.check_device_status(device_id)
        assert status["revoked"] is True
        assert status["status"] == "revoked"
    
    def test_revoke_nonexistent_device(self):
        """Test revoking non-existent device."""
        success = self.pairing.revoke_device("nonexistent-device")
        assert success is False
    
    def test_clear_device_credentials(self):
        """Test clearing device credentials on revocation."""
        # Register device first
        result = self.pairing.register_device()
        device_id = result["device_id"]
        
        # Verify key exists
        key = self.pairing.load_device_key(device_id)
        assert key is not None
        
        # Clear credentials
        success = self.pairing.clear_device_credentials(device_id)
        assert success is True
        
        # Verify key is deleted
        key = self.pairing.load_device_key(device_id)
        assert key is None
        
        # Verify device removed from registry
        status = self.pairing.check_device_status(device_id)
        assert status["status"] == "not_found"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

