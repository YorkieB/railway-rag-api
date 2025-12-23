"""
Integration tests for OS Automation APIs
"""
import pytest
import requests
import os
import tempfile
import shutil


# Test configuration
API_BASE = os.getenv("API_BASE", "http://localhost:8080")
TEST_FILE_PATH = None
TEST_DIR = None


@pytest.fixture(scope="module")
def api_base():
    """Get API base URL."""
    return API_BASE


@pytest.fixture(scope="module")
def test_file(api_base):
    """Create a test file for file operations."""
    global TEST_DIR, TEST_FILE_PATH
    
    TEST_DIR = tempfile.mkdtemp()
    TEST_FILE_PATH = os.path.join(TEST_DIR, "test_integration.txt")
    
    with open(TEST_FILE_PATH, 'w') as f:
        f.write("Test content for integration testing")
    
    yield TEST_FILE_PATH
    
    # Cleanup
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)


class TestAppManagementAPI:
    """Test app management API endpoints."""
    
    def test_list_running_apps(self, api_base):
        """Test listing running apps endpoint."""
        response = requests.get(f"{api_base}/windows/apps/running")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "apps" in data
        assert "total" in data
        assert isinstance(data["apps"], list)
    
    def test_launch_app_blocked(self, api_base):
        """Test launching a blocked app."""
        response = requests.post(
            f"{api_base}/windows/apps/launch",
            params={"app_path": "regedit.exe"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "blocked" in data.get("detail", "").lower() or "blocked" in str(data).lower()


class TestFileOperationsAPI:
    """Test file operations API endpoints."""
    
    def test_read_file(self, api_base, test_file):
        """Test reading file endpoint."""
        allow_dir = os.path.dirname(test_file)
        
        # FastAPI expects list query params as multiple params with same name
        # Use params with list to create multiple query params
        response = requests.get(
            f"{api_base}/windows/files/read",
            params=[("file_path", test_file), ("allow_list", allow_dir)]
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "content" in data
        assert data["content"] == "Test content for integration testing"
    
    def test_read_file_system_directory(self, api_base):
        """Test reading file in system directory (should be blocked)."""
        response = requests.get(
            f"{api_base}/windows/files/read",
            params={"file_path": "C:\\Windows\\System32\\config\\sam"}
        )
        
        assert response.status_code == 403
        data = response.json()
        assert "system directory" in data.get("detail", "").lower()
    
    def test_write_file_requires_approval(self, api_base, test_file):
        """Test that file write requires approval."""
        response = requests.post(
            f"{api_base}/windows/files/write",
            params={
                "file_path": test_file,
                "content": "New content",
                "require_approval": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is False
        assert data["requires_approval"] is True
    
    def test_list_directory(self, api_base, test_file):
        """Test listing directory endpoint."""
        dir_path = os.path.dirname(test_file)
        allow_dir = dir_path
        
        # FastAPI expects list query params as multiple params with same name
        # Use params with list to create multiple query params
        response = requests.get(
            f"{api_base}/windows/files/list",
            params=[("dir_path", dir_path), ("allow_list", allow_dir)]
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "items" in data
        assert "count" in data
        assert isinstance(data["items"], list)


class TestVisionAPI:
    """Test vision/screenshot API endpoints."""
    
    def test_capture_screenshot(self, api_base):
        """Test capturing screenshot endpoint."""
        response = requests.post(
            f"{api_base}/windows/vision/capture",
            json={}
        )
        
        # May fail if win32gui not available, but should return proper error
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
            assert "screenshot" in data
        else:
            # Expected if win32gui not available
            assert response.status_code in [500, 503]


class TestROCAPI:
    """Test Region-of-Control API endpoints."""
    
    def test_get_roc_none(self, api_base):
        """Test getting ROC when none is set."""
        response = requests.get(f"{api_base}/windows/roc")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is False
        assert "No active ROC" in data.get("message", "")
    
    def test_list_windows(self, api_base):
        """Test listing windows endpoint."""
        response = requests.get(f"{api_base}/windows/roc/windows")
        
        # May fail if win32gui not available
        if response.status_code == 200:
            data = response.json()
            assert "windows" in data
            assert "total" in data
            assert isinstance(data["windows"], list)
        else:
            # Expected if win32gui not available
            assert response.status_code in [500, 503]
    
    def test_clear_roc(self, api_base):
        """Test clearing ROC endpoint."""
        response = requests.delete(f"{api_base}/windows/roc")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

