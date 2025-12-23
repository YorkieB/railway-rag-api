"""
App Launch/Switch
Handles Windows application launch and switching with safety guardrails.
"""
import subprocess
import os
from typing import Optional, List, Dict
# Note: browser_safety is in browser.safety, not windows.safety


class AppManager:
    """
    Manages Windows application launch and switching.
    
    Safety Rules (CC1):
    - App launch: ✅ Allowed (except blocklist)
    - Blocklist: Password managers, system tools
    - System tools require explicit approval
    """
    
    def __init__(self):
        """Initialize app manager."""
        # Default blocklist (password managers, system tools)
        self.blocklist = [
            "credential", "password", "keeper", "lastpass", "1password",
            "bitwarden", "dashlane", "enpass", "roboform",
            "regedit", "gpedit", "msconfig", "services.msc",
            "taskmgr", "cmd", "powershell", "wsl"
        ]
    
    def is_blocked(self, app_name: str) -> bool:
        """
        Check if app is in blocklist.
        
        Args:
            app_name: Application name or path
            
        Returns:
            True if blocked
        """
        app_lower = app_name.lower()
        return any(blocked in app_lower for blocked in self.blocklist)
    
    def launch_app(self, app_path: str, arguments: Optional[List[str]] = None) -> Dict:
        """
        Launch a Windows application.
        
        Args:
            app_path: Path to executable or app name
            arguments: Optional command-line arguments
            
        Returns:
            Dict with launch result
        """
        # Check blocklist
        if self.is_blocked(app_path):
            return {
                "success": False,
                "error": "Application is blocked for security reasons",
                "app_path": app_path,
                "blocked": True
            }
        
        try:
            # Launch application
            if arguments:
                process = subprocess.Popen([app_path] + arguments, shell=False)
            else:
                process = subprocess.Popen(app_path, shell=False)
            
            return {
                "success": True,
                "app_path": app_path,
                "process_id": process.pid,
                "message": "Application launched successfully"
            }
        except FileNotFoundError:
            return {
                "success": False,
                "error": "Application not found",
                "app_path": app_path
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to launch application: {str(e)}",
                "app_path": app_path
            }
    
    def switch_to_app(self, window_title: str, timeout_seconds: float = 5.0) -> Dict:
        """
        Switch to an existing application window.
        
        Args:
            window_title: Window title or partial match
            timeout_seconds: Maximum time to spend searching for window (default: 5.0)
            
        Returns:
            Dict with switch result
        """
        try:
            import win32gui
            import win32con
            import threading
            import time
            
            windows = []
            enumeration_complete = threading.Event()
            enumeration_error = [None]
            
            def enum_windows_callback(hwnd, windows_list):
                """Callback for window enumeration with error handling."""
                try:
                    if win32gui.IsWindowVisible(hwnd):
                        title = win32gui.GetWindowText(hwnd)
                        if window_title.lower() in title.lower():
                            windows_list.append((hwnd, title))
                except Exception as e:
                    enumeration_error[0] = str(e)
            
            def enumerate_windows():
                """Run enumeration in separate thread to allow timeout."""
                try:
                    win32gui.EnumWindows(enum_windows_callback, windows)
                except Exception as e:
                    enumeration_error[0] = str(e)
                finally:
                    enumeration_complete.set()
            
            # Start enumeration in background thread
            enum_thread = threading.Thread(target=enumerate_windows, daemon=True)
            enum_thread.start()
            
            # Wait for completion or timeout
            if enumeration_complete.wait(timeout=timeout_seconds):
                # Enumeration completed
                if enumeration_error[0]:
                    return {
                        "success": False,
                        "error": f"Error during window enumeration: {enumeration_error[0]}",
                        "window_title": window_title
                    }
                
                if windows:
                    hwnd, title = windows[0]
                    try:
                        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                        win32gui.SetForegroundWindow(hwnd)
                        
                        return {
                            "success": True,
                            "window_title": title,
                            "message": "Switched to application window"
                        }
                    except Exception as e:
                        return {
                            "success": False,
                            "error": f"Failed to switch to window: {str(e)}",
                            "window_title": window_title
                        }
                else:
                    return {
                        "success": False,
                        "error": "Window not found",
                        "window_title": window_title
                    }
            else:
                # Timeout occurred
                return {
                    "success": False,
                    "error": f"Window search timed out after {timeout_seconds}s",
                    "window_title": window_title
                }
        except ImportError:
            return {
                "success": False,
                "error": "win32gui not available (install pywin32)",
                "window_title": window_title
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to switch to application: {str(e)}",
                "window_title": window_title
            }
    
    def list_running_apps(self, timeout_seconds: float = 5.0) -> List[Dict]:
        """
        List currently running applications.
        
        Args:
            timeout_seconds: Maximum time to spend enumerating windows (default: 5.0)
        
        Returns:
            List of running app info (may be partial if timeout occurs)
        """
        try:
            import win32gui
            import win32process
            import threading
            import time
            
            apps = []
            enumeration_complete = threading.Event()
            enumeration_error = [None]
            
            def enum_windows_callback(hwnd, apps_list):
                """Callback for window enumeration with error handling."""
                try:
                    if win32gui.IsWindowVisible(hwnd):
                        title = win32gui.GetWindowText(hwnd)
                        if title:
                            try:
                                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                                apps_list.append({
                                    "window_title": title,
                                    "process_id": pid,
                                    "hwnd": hwnd
                                })
                            except Exception:
                                pass
                except Exception as e:
                    # Log but don't stop enumeration
                    enumeration_error[0] = str(e)
            
            def enumerate_windows():
                """Run enumeration in separate thread to allow timeout."""
                try:
                    win32gui.EnumWindows(enum_windows_callback, apps)
                except Exception as e:
                    enumeration_error[0] = str(e)
                finally:
                    enumeration_complete.set()
            
            # Start enumeration in background thread
            enum_thread = threading.Thread(target=enumerate_windows, daemon=True)
            enum_thread.start()
            
            # Wait for completion or timeout
            if enumeration_complete.wait(timeout=timeout_seconds):
                # Enumeration completed
                if enumeration_error[0]:
                    print(f"Warning: Error during window enumeration: {enumeration_error[0]}")
                return apps
            else:
                # Timeout occurred - return partial results
                print(f"Warning: Window enumeration timed out after {timeout_seconds}s. Returning {len(apps)} windows found so far.")
                return apps
            
        except ImportError:
            return []
        except Exception as e:
            print(f"Error listing running apps: {e}")
            return []


# Global app manager instance
app_manager = AppManager()

