"""
Screen-Based Fallback
Handles screenshot capture, vision analysis, and coordinate-based clicking.
Used when AX Tree is insufficient (canvas, remote desktop, custom UI frameworks).
"""
import base64
import io
from typing import Optional, Dict, Tuple
from PIL import Image
import numpy as np
from openai import OpenAI
import os


class ScreenVision:
    """
    Screen-based vision fallback for complex UIs.
    
    Workflow:
    1. Capture screenshot of target window
    2. Send to vision model: "Find the [element] in this screenshot"
    3. Model returns bounding box + confidence
    4. Show overlay: green rectangle around detected element
    5. User can drag to adjust bounding box if needed
    6. On approval, click center of bounding box
    """
    
    def __init__(self):
        """Initialize screen vision."""
        self.openai_client = None
        self._initialize_openai()
    
    def _initialize_openai(self):
        """Initialize OpenAI client for vision."""
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.openai_client = OpenAI(api_key=api_key)
    
    def capture_screenshot(self, window_title: Optional[str] = None) -> Optional[bytes]:
        """
        Capture screenshot of specific window or entire screen.
        
        Args:
            window_title: Optional window title to capture (None = entire screen)
            
        Returns:
            Screenshot bytes (PNG format) or None if failed
        """
        try:
            from PIL import ImageGrab
            import win32gui
            import win32ui
            import win32con
            
            if window_title:
                # Find window by title
                hwnd = win32gui.FindWindow(None, window_title)
                if not hwnd:
                    return None
                
                # Get window rectangle
                left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                width = right - left
                height = bottom - top
                
                # Capture window
                hwndDC = win32gui.GetWindowDC(hwnd)
                mfcDC = win32ui.CreateDCFromHandle(hwndDC)
                saveDC = mfcDC.CreateCompatibleDC()
                
                bitmap = win32ui.CreateBitmap()
                bitmap.CreateCompatibleBitmap(mfcDC, width, height)
                saveDC.SelectObject(bitmap)
                
                saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)
                
                # Convert to PIL Image
                bmpinfo = bitmap.GetInfo()
                bmpstr = bitmap.GetBitmapBits(True)
                img = Image.frombuffer(
                    'RGB',
                    (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                    bmpstr, 'raw', 'BGRX', 0, 1
                )
                
                # Cleanup
                win32gui.DeleteObject(bitmap.GetHandle())
                saveDC.DeleteDC()
                mfcDC.DeleteDC()
                win32gui.ReleaseDC(hwnd, hwndDC)
            else:
                # Capture entire screen
                img = ImageGrab.grab()
            
            # Convert to bytes
            output = io.BytesIO()
            img.save(output, format='PNG')
            return output.getvalue()
            
        except ImportError:
            # Fallback: Use PIL ImageGrab only
            try:
                from PIL import ImageGrab
                img = ImageGrab.grab()
                output = io.BytesIO()
                img.save(output, format='PNG')
                return output.getvalue()
            except Exception as e:
                print(f"Error capturing screenshot: {e}")
                return None
        except Exception as e:
            print(f"Error capturing screenshot: {e}")
            return None
    
    def find_element_in_screenshot(
        self,
        screenshot_bytes: bytes,
        element_description: str,
        query: Optional[str] = None
    ) -> Dict:
        """
        Find element in screenshot using vision model.
        
        Args:
            screenshot_bytes: Screenshot image bytes
            element_description: Description of element to find
            query: Optional additional context
            
        Returns:
            Dict with bounding box, confidence, and coordinates
        """
        if not self.openai_client:
            return {
                "success": False,
                "error": "OpenAI client not initialized"
            }
        
        try:
            # Encode screenshot to base64
            screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            
            # Create vision prompt
            vision_prompt = f"""Look at this screenshot and find the element described as: "{element_description}".

Return the bounding box coordinates in JSON format:
{{
    "x": <left coordinate>,
    "y": <top coordinate>,
    "width": <width in pixels>,
    "height": <height in pixels>,
    "confidence": <confidence 0.0-1.0>,
    "description": "<what you found>"
}}

The coordinates should be relative to the screenshot (0,0 is top-left).
Only return the JSON, no other text."""
            
            if query:
                vision_prompt = f"{vision_prompt}\n\nAdditional context: {query}"
            
            # Call OpenAI Vision API
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": vision_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{screenshot_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=200,
                timeout=30.0
            )
            
            # Parse response
            response_text = response.choices[0].message.content or "{}"
            
            # Extract JSON from response
            import json
            import re
            
            # Try to find JSON in response
            json_match = re.search(r'\{[^}]+\}', response_text)
            if json_match:
                result = json.loads(json_match.group())
            else:
                # Fallback: try parsing entire response
                result = json.loads(response_text)
            
            return {
                "success": True,
                "bounds": {
                    "x": result.get("x", 0),
                    "y": result.get("y", 0),
                    "width": result.get("width", 0),
                    "height": result.get("height", 0)
                },
                "confidence": result.get("confidence", 0.0),
                "description": result.get("description", ""),
                "center": {
                    "x": result.get("x", 0) + result.get("width", 0) // 2,
                    "y": result.get("y", 0) + result.get("height", 0) // 2
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Vision analysis failed: {str(e)}"
            }
    
    def click_coordinate(self, x: int, y: int) -> Dict:
        """
        Click at specific screen coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Dict with click result
        """
        try:
            import win32api
            import win32con
            
            # Move mouse to coordinate
            win32api.SetCursorPos((x, y))
            
            # Click
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
            
            return {
                "success": True,
                "x": x,
                "y": y,
                "message": "Click executed successfully"
            }
        except ImportError:
            return {
                "success": False,
                "error": "win32api not available (install pywin32)"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to click coordinate: {str(e)}"
            }


# Global screen vision instance
screen_vision = ScreenVision()

