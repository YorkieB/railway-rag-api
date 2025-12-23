"""
Unit tests for Windows App Management
"""
import pytest
import os
import sys

# Add parent directory to path to import rag-api modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../rag-api'))
from windows.apps import AppManager


class TestAppManager:
    """Test app management functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.app_manager = AppManager()
    
    def test_is_blocked_password_manager(self):
        """Test that password managers are blocked."""
        assert self.app_manager.is_blocked("lastpass.exe") is True
        assert self.app_manager.is_blocked("1password") is True
        assert self.app_manager.is_blocked("bitwarden") is True
    
    def test_is_blocked_system_tool(self):
        """Test that system tools are blocked."""
        assert self.app_manager.is_blocked("regedit.exe") is True
        assert self.app_manager.is_blocked("taskmgr") is True
        assert self.app_manager.is_blocked("cmd.exe") is True
    
    def test_is_not_blocked_normal_app(self):
        """Test that normal apps are not blocked."""
        assert self.app_manager.is_blocked("notepad.exe") is False
        assert self.app_manager.is_blocked("chrome.exe") is False
        assert self.app_manager.is_blocked("code.exe") is False
    
    def test_launch_app_blocked(self):
        """Test launching a blocked app."""
        result = self.app_manager.launch_app("regedit.exe")
        
        assert result["success"] is False
        assert result["blocked"] is True
        assert "blocked" in result["error"].lower()
    
    def test_launch_app_not_found(self):
        """Test launching a non-existent app."""
        result = self.app_manager.launch_app("nonexistent_app_12345.exe")
        
        assert result["success"] is False
        assert "not found" in result["error"].lower()
    
    @pytest.mark.timeout(10)  # 10 second test timeout as safety net
    def test_list_running_apps(self):
        """Test listing running apps with timeout protection."""
        # Use shorter timeout for test (2 seconds)
        apps = self.app_manager.list_running_apps(timeout_seconds=2.0)
        
        assert isinstance(apps, list)
        # Should return list (may be empty if win32gui not available or timeout occurs)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

