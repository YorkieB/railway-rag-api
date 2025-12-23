"""
Platform Abstraction

Provides unified interface for OS automation across platforms.
"""
import platform
import sys
from typing import Optional, Dict, List


def get_platform() -> str:
    """Get current platform name"""
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system == "linux":
        return "linux"
    elif system == "darwin":
        return "macos"
    else:
        return "unknown"


def get_platform_module():
    """Get platform-specific module"""
    current_platform = get_platform()
    
    if current_platform == "windows":
        from windows import apps as apps_module
        from windows import files as files_module
        return apps_module, files_module
    elif current_platform == "linux":
        # Future: import linux modules
        raise NotImplementedError("Linux automation not yet implemented")
    elif current_platform == "macos":
        # Future: import macOS modules
        raise NotImplementedError("macOS automation not yet implemented")
    else:
        raise Exception(f"Unsupported platform: {current_platform}")


class PlatformAppManager:
    """Platform-agnostic app manager"""
    
    def __init__(self):
        """Initialize platform-specific app manager"""
        self.platform = get_platform()
        apps_module, _ = get_platform_module()
        self.app_manager = apps_module.app_manager
    
    def list_running_apps(self, timeout_seconds: float = 5.0) -> List[Dict]:
        """List running applications"""
        return self.app_manager.list_running_apps(timeout_seconds=timeout_seconds)
    
    def launch_app(self, app_name: str) -> Dict:
        """Launch application"""
        return self.app_manager.launch_app(app_name)
    
    def switch_to_app(self, app_name: str, timeout_seconds: float = 5.0) -> Dict:
        """Switch to application"""
        return self.app_manager.switch_to_app(app_name, timeout_seconds=timeout_seconds)


# Global platform app manager
platform_app_manager = PlatformAppManager()

