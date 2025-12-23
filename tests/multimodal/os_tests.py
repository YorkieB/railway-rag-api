"""
OS Automation Tests
Tests for Windows OS automation functionality.
"""
import requests
from typing import Dict, List


class OSAutomationTestSuite:
    """
    Test suite for OS automation.
    
    Tests:
    - App launch
    - App switching
    - File operations
    - Screenshot capture
    - ROC (Region-of-Control) management
    """
    
    def __init__(self, api_base: str = "http://localhost:8080"):
        """
        Initialize OS test suite.
        
        Args:
            api_base: API base URL
        """
        self.api_base = api_base
    
    def test_app_launch(self) -> Dict:
        """
        Test app launch functionality.
        
        Returns:
            Test result
        """
        try:
            # Test launching a safe app (Notepad)
            response = requests.post(
                f"{self.api_base}/windows/apps/launch",
                json={"app_path": "notepad.exe"}
            )
            if response.status_code == 200:
                return {
                    "test_id": "os_1",
                    "test_name": "App Launch",
                    "status": "passed"
                }
            else:
                return {
                    "test_id": "os_1",
                    "test_name": "App Launch",
                    "status": "failed",
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                "test_id": "os_1",
                "test_name": "App Launch",
                "status": "failed",
                "error": str(e)
            }
    
    def test_list_running_apps(self) -> Dict:
        """
        Test listing running applications.
        
        Returns:
            Test result
        """
        try:
            response = requests.get(f"{self.api_base}/windows/apps/running")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data.get("apps"), list):
                    return {
                        "test_id": "os_2",
                        "test_name": "List Running Apps",
                        "status": "passed",
                        "app_count": len(data.get("apps", []))
                    }
                else:
                    return {
                        "test_id": "os_2",
                        "test_name": "List Running Apps",
                        "status": "failed",
                        "error": "Invalid response format"
                    }
            else:
                return {
                    "test_id": "os_2",
                    "test_name": "List Running Apps",
                    "status": "failed",
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                "test_id": "os_2",
                "test_name": "List Running Apps",
                "status": "failed",
                "error": str(e)
            }
    
    def test_screenshot_capture(self) -> Dict:
        """
        Test screenshot capture.
        
        Returns:
            Test result
        """
        try:
            response = requests.post(
                f"{self.api_base}/windows/vision/capture"
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("screenshot"):
                    return {
                        "test_id": "os_3",
                        "test_name": "Screenshot Capture",
                        "status": "passed"
                    }
                else:
                    return {
                        "test_id": "os_3",
                        "test_name": "Screenshot Capture",
                        "status": "failed",
                        "error": "No screenshot in response"
                    }
            else:
                return {
                    "test_id": "os_3",
                    "test_name": "Screenshot Capture",
                    "status": "failed",
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                "test_id": "os_3",
                "test_name": "Screenshot Capture",
                "status": "failed",
                "error": str(e)
            }
    
    def test_roc_management(self) -> Dict:
        """
        Test Region-of-Control management.
        
        Returns:
            Test result
        """
        try:
            # Test setting ROC
            response = requests.post(
                f"{self.api_base}/windows/roc/set",
                json={
                    "window_title": "Test Window",
                    "bounds": {"x": 0, "y": 0, "width": 800, "height": 600}
                }
            )
            if response.status_code == 200:
                # Test getting ROC
                get_response = requests.get(f"{self.api_base}/windows/roc")
                if get_response.status_code == 200:
                    return {
                        "test_id": "os_4",
                        "test_name": "ROC Management",
                        "status": "passed"
                    }
                else:
                    return {
                        "test_id": "os_4",
                        "test_name": "ROC Management",
                        "status": "failed",
                        "error": "Failed to get ROC"
                    }
            else:
                return {
                    "test_id": "os_4",
                    "test_name": "ROC Management",
                    "status": "failed",
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                "test_id": "os_4",
                "test_name": "ROC Management",
                "status": "failed",
                "error": str(e)
            }
    
    def run_all(self) -> List[Dict]:
        """
        Run all OS automation tests.
        
        Returns:
            List of test results
        """
        return [
            self.test_app_launch(),
            self.test_list_running_apps(),
            self.test_screenshot_capture(),
            self.test_roc_management()
        ]


if __name__ == "__main__":
    suite = OSAutomationTestSuite()
    results = suite.run_all()
    
    print("OS Automation Test Results:")
    for result in results:
        status = result.get("status", "unknown")
        print(f"  {result.get('test_name')}: {status}")
        if result.get("error"):
            print(f"    Error: {result['error']}")

