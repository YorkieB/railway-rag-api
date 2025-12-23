"""
Region-of-Control (ROC)
Manages user-selected automation boundaries.
Automation is limited to the selected window's bounds.
"""
import os
from typing import Optional, Dict, Tuple
try:
    import win32gui
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False


class RegionOfControl:
    """
    Manages Region-of-Control (ROC) boundaries.
    
    ROC Rules:
    - User selects specific window before automation
    - Automation canvas limited to that window's bounds
    - Any detected UI element outside ROC is ignored
    - Never click outside Region-of-Control
    """
    
    def __init__(self):
        """Initialize ROC manager."""
        self.active_roc: Optional[Dict] = None
    
    def set_roc(self, window_title: str) -> Dict:
        """
        Set Region-of-Control to a specific window.
        
        Args:
            window_title: Window title or partial match
            
        Returns:
            Dict with ROC bounds
        """
        if not WIN32_AVAILABLE:
            return {
                "success": False,
                "error": "win32gui not available (install pywin32)"
            }
        
        try:
            # Find window
            hwnd = win32gui.FindWindow(None, window_title)
            if not hwnd:
                # Try partial match
                def enum_windows_callback(hwnd_param, windows):
                    if win32gui.IsWindowVisible(hwnd_param):
                        title = win32gui.GetWindowText(hwnd_param)
                        if window_title.lower() in title.lower():
                            windows.append((hwnd_param, title))
                
                windows = []
                win32gui.EnumWindows(enum_windows_callback, windows)
                
                if not windows:
                    return {
                        "success": False,
                        "error": "Window not found",
                        "window_title": window_title
                    }
                
                hwnd, actual_title = windows[0]
            else:
                actual_title = win32gui.GetWindowText(hwnd)
            
            # Get window bounds
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            
            roc = {
                "window_title": actual_title,
                "hwnd": hwnd,
                "bounds": {
                    "x": left,
                    "y": top,
                    "width": right - left,
                    "height": bottom - top
                }
            }
            
            self.active_roc = roc
            
            return {
                "success": True,
                "roc": roc,
                "message": f"ROC set to window: {actual_title}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to set ROC: {str(e)}",
                "window_title": window_title
            }
    
    def clear_roc(self) -> Dict:
        """
        Clear active ROC.
        
        Returns:
            Dict with result
        """
        self.active_roc = None
        return {
            "success": True,
            "message": "ROC cleared"
        }
    
    def get_roc(self) -> Optional[Dict]:
        """
        Get active ROC.
        
        Returns:
            Active ROC dict or None
        """
        return self.active_roc
    
    def is_within_roc(self, x: int, y: int) -> bool:
        """
        Check if coordinates are within active ROC.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            True if coordinates are within ROC
        """
        if not self.active_roc:
            return True  # No ROC set, allow all
        
        bounds = self.active_roc["bounds"]
        return (
            bounds["x"] <= x <= bounds["x"] + bounds["width"] and
            bounds["y"] <= y <= bounds["y"] + bounds["height"]
        )
    
    def filter_elements_by_roc(self, elements: list[Dict]) -> list[Dict]:
        """
        Filter elements to only those within ROC.
        
        Args:
            elements: List of element dicts with x, y coordinates
            
        Returns:
            Filtered list of elements within ROC
        """
        if not self.active_roc:
            return elements  # No ROC set, return all
        
        filtered = []
        for element in elements:
            x = element.get("x", 0)
            y = element.get("y", 0)
            if self.is_within_roc(x, y):
                filtered.append(element)
        
        return filtered
    
    def list_windows(self) -> list[Dict]:
        """
        List all visible windows.
        
        Returns:
            List of window info dicts
        """
        if not WIN32_AVAILABLE:
            return []
        
        windows = []
        
        def enum_windows_callback(hwnd, windows_list):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                    windows_list.append({
                        "title": title,
                        "hwnd": hwnd,
                        "bounds": {
                            "x": left,
                            "y": top,
                            "width": right - left,
                            "height": bottom - top
                        }
                    })
        
        try:
            win32gui.EnumWindows(enum_windows_callback, windows)
        except Exception as e:
            print(f"Error listing windows: {e}")
        
        return windows


# Global ROC instance
roc = RegionOfControl()

