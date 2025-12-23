"""
Integration tests for Windows Companion APIs
"""
import pytest
import requests
import os
import time


# Test configuration
API_BASE = os.getenv("API_BASE", "http://localhost:8080")
TEST_DEVICE_ID = None
TEST_CREDENTIAL_NAME = "test_integration_credential"


@pytest.fixture(scope="module")
def api_base():
    """Get API base URL."""
    return API_BASE


@pytest.fixture(scope="module")
def registered_device(api_base):
    """Register a test device."""
    global TEST_DEVICE_ID
    
    response = requests.post(f"{api_base}/windows/device/register")
    assert response.status_code == 200
    
    data = response.json()
    TEST_DEVICE_ID = data["device_id"]
    
    yield data
    
    # Cleanup: Revoke device
    if TEST_DEVICE_ID:
        try:
            requests.post(f"{api_base}/windows/device/{TEST_DEVICE_ID}/revoke")
        except Exception:
            pass


class TestDevicePairingAPI:
    """Test device pairing API endpoints."""
    
    def test_register_device(self, api_base):
        """Test device registration endpoint."""
        response = requests.post(f"{api_base}/windows/device/register")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "device_id" in data
        assert "certificate" in data
        assert "status" in data
        assert data["status"] == "registered"
        
        # Cleanup
        device_id = data["device_id"]
        requests.post(f"{api_base}/windows/device/{device_id}/revoke")
    
    def test_get_device_status(self, api_base, registered_device):
        """Test device status endpoint."""
        device_id = registered_device["device_id"]
        
        response = requests.get(f"{api_base}/windows/device/{device_id}/status")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["device_id"] == device_id
        assert "status" in data
        assert "revoked" in data
        assert data["revoked"] is False
    
    def test_get_nonexistent_device_status(self, api_base):
        """Test getting status of non-existent device."""
        response = requests.get(f"{api_base}/windows/device/nonexistent-device-123/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "not_found"
    
    def test_revoke_device(self, api_base):
        """Test device revocation endpoint."""
        # Register device first
        register_response = requests.post(f"{api_base}/windows/device/register")
        device_id = register_response.json()["device_id"]
        
        # Revoke device
        response = requests.post(f"{api_base}/windows/device/{device_id}/revoke")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "revoked"
        assert data["device_id"] == device_id
        
        # Verify revoked
        status_response = requests.get(f"{api_base}/windows/device/{device_id}/status")
        status_data = status_response.json()
        assert status_data["revoked"] is True


class TestCredentialManagementAPI:
    """Test credential management API endpoints."""
    
    def test_store_credential(self, api_base):
        """Test storing credential endpoint."""
        params = {
            "credential_name": TEST_CREDENTIAL_NAME,
            "username": "test_user",
            "password": "test_password_123",
            "description": "Test credential for integration tests"
        }
        
        response = requests.post(f"{api_base}/windows/credentials", params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "stored"
        assert data["credential_name"] == TEST_CREDENTIAL_NAME
        
        # Cleanup
        requests.delete(f"{api_base}/windows/credentials/{TEST_CREDENTIAL_NAME}")
    
    def test_get_credential(self, api_base):
        """Test getting credential endpoint."""
        # Store first
        params = {
            "credential_name": TEST_CREDENTIAL_NAME,
            "username": "test_user",
            "password": "test_password_123"
        }
        requests.post(f"{api_base}/windows/credentials", params=params)
        
        # Get credential
        response = requests.get(f"{api_base}/windows/credentials/{TEST_CREDENTIAL_NAME}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["credential_name"] == TEST_CREDENTIAL_NAME
        assert data["username"] == "test_user"
        assert data["exists"] is True
        # Password should NOT be in response
        assert "password" not in data
        
        # Cleanup
        requests.delete(f"{api_base}/windows/credentials/{TEST_CREDENTIAL_NAME}")
    
    def test_get_nonexistent_credential(self, api_base):
        """Test getting non-existent credential."""
        response = requests.get(f"{api_base}/windows/credentials/nonexistent_credential")
        
        assert response.status_code == 404
    
    def test_delete_credential(self, api_base):
        """Test deleting credential endpoint."""
        # Store first
        params = {
            "credential_name": TEST_CREDENTIAL_NAME,
            "username": "test_user",
            "password": "test_password_123"
        }
        requests.post(f"{api_base}/windows/credentials", params=params)
        
        # Delete credential
        response = requests.delete(f"{api_base}/windows/credentials/{TEST_CREDENTIAL_NAME}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "deleted"
        
        # Verify deleted
        get_response = requests.get(f"{api_base}/windows/credentials/{TEST_CREDENTIAL_NAME}")
        assert get_response.status_code == 404
    
    def test_list_credentials(self, api_base):
        """Test listing credentials endpoint."""
        # Store a test credential
        params = {
            "credential_name": TEST_CREDENTIAL_NAME,
            "username": "test_user",
            "password": "test_password_123"
        }
        requests.post(f"{api_base}/windows/credentials", params=params)
        
        # List credentials
        response = requests.get(f"{api_base}/windows/credentials")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "credentials" in data
        assert "total" in data
        assert isinstance(data["credentials"], list)
        assert TEST_CREDENTIAL_NAME in data["credentials"]
        
        # Cleanup
        requests.delete(f"{api_base}/windows/credentials/{TEST_CREDENTIAL_NAME}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

