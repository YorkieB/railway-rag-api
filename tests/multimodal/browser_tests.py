"""
Browser Automation Tests
Tests for Playwright browser automation functionality.
"""
import requests
from typing import Dict, List


class BrowserAutomationTestSuite:
    """
    Test suite for browser automation.
    
    Tests:
    - Browser session creation
    - Navigation
    - AX Tree extraction
    - Element clicking
    - Form filling
    - Screenshot capture
    """
    
    def __init__(self, api_base: str = "http://localhost:8080"):
        """
        Initialize browser test suite.
        
        Args:
            api_base: API base URL
        """
        self.api_base = api_base
        self.session_id = None
    
    def test_create_session(self) -> Dict:
        """
        Test browser session creation.
        
        Returns:
            Test result
        """
        try:
            response = requests.post(f"{self.api_base}/browser/sessions")
            if response.status_code == 200:
                data = response.json()
                self.session_id = data.get("session_id")
                return {
                    "test_id": "browser_1",
                    "test_name": "Create Browser Session",
                    "status": "passed",
                    "session_id": self.session_id
                }
            else:
                return {
                    "test_id": "browser_1",
                    "test_name": "Create Browser Session",
                    "status": "failed",
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                "test_id": "browser_1",
                "test_name": "Create Browser Session",
                "status": "failed",
                "error": str(e)
            }
    
    def test_navigation(self) -> Dict:
        """
        Test browser navigation.
        
        Returns:
            Test result
        """
        if not self.session_id:
            return {
                "test_id": "browser_2",
                "test_name": "Navigation",
                "status": "skipped",
                "message": "No session created"
            }
        
        try:
            response = requests.post(
                f"{self.api_base}/browser/sessions/{self.session_id}/navigate",
                json={"url": "https://example.com"}
            )
            if response.status_code == 200:
                return {
                    "test_id": "browser_2",
                    "test_name": "Navigation",
                    "status": "passed"
                }
            else:
                return {
                    "test_id": "browser_2",
                    "test_name": "Navigation",
                    "status": "failed",
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                "test_id": "browser_2",
                "test_name": "Navigation",
                "status": "failed",
                "error": str(e)
            }
    
    def test_ax_tree_extraction(self) -> Dict:
        """
        Test AX Tree extraction.
        
        Returns:
            Test result
        """
        if not self.session_id:
            return {
                "test_id": "browser_3",
                "test_name": "AX Tree Extraction",
                "status": "skipped",
                "message": "No session created"
            }
        
        try:
            response = requests.get(
                f"{self.api_base}/browser/sessions/{self.session_id}/ax-tree"
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("ax_tree"):
                    return {
                        "test_id": "browser_3",
                        "test_name": "AX Tree Extraction",
                        "status": "passed"
                    }
                else:
                    return {
                        "test_id": "browser_3",
                        "test_name": "AX Tree Extraction",
                        "status": "failed",
                        "error": "No AX tree in response"
                    }
            else:
                return {
                    "test_id": "browser_3",
                    "test_name": "AX Tree Extraction",
                    "status": "failed",
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                "test_id": "browser_3",
                "test_name": "AX Tree Extraction",
                "status": "failed",
                "error": str(e)
            }
    
    def test_screenshot(self) -> Dict:
        """
        Test screenshot capture.
        
        Returns:
            Test result
        """
        if not self.session_id:
            return {
                "test_id": "browser_4",
                "test_name": "Screenshot",
                "status": "skipped",
                "message": "No session created"
            }
        
        try:
            response = requests.get(
                f"{self.api_base}/browser/sessions/{self.session_id}/screenshot"
            )
            if response.status_code == 200:
                return {
                    "test_id": "browser_4",
                    "test_name": "Screenshot",
                    "status": "passed"
                }
            else:
                return {
                    "test_id": "browser_4",
                    "test_name": "Screenshot",
                    "status": "failed",
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                "test_id": "browser_4",
                "test_name": "Screenshot",
                "status": "failed",
                "error": str(e)
            }
    
    def run_all(self) -> List[Dict]:
        """
        Run all browser automation tests.
        
        Returns:
            List of test results
        """
        # Create session first
        session_result = self.test_create_session()
        results = [session_result]
        
        if session_result.get("status") == "passed":
            # Run other tests
            results.extend([
                self.test_navigation(),
                self.test_ax_tree_extraction(),
                self.test_screenshot()
            ])
        
        return results


if __name__ == "__main__":
    suite = BrowserAutomationTestSuite()
    results = suite.run_all()
    
    print("Browser Automation Test Results:")
    for result in results:
        status = result.get("status", "unknown")
        print(f"  {result.get('test_name')}: {status}")
        if result.get("error"):
            print(f"    Error: {result['error']}")

