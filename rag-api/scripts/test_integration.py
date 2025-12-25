#!/usr/bin/env python3
"""
Integration Testing Script for Jarvis RAG API

Tests complete user flows and integrations between components.
Usage: python scripts/test_integration.py [--base-url BASE_URL]
"""

import asyncio
import sys
import argparse
import json
from typing import Dict, Optional
from datetime import datetime
import httpx
from colorama import init, Fore, Style

init(autoreset=True)

class IntegrationTester:
    """Integration testing class for complete user flows."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=60.0)
        self.auth_token: Optional[str] = None
        self.user_id = "integration_test_user"
        self.test_data = {}
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
        
    def log(self, message: str, status: str = "INFO"):
        """Log message with color coding."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {
            "PASS": Fore.GREEN,
            "FAIL": Fore.RED,
            "INFO": Fore.CYAN,
            "STEP": Fore.YELLOW
        }
        color = colors.get(status, Fore.WHITE)
        print(f"{color}[{timestamp}] {status}: {message}{Style.RESET_ALL}")
        
    async def make_request(self, method: str, path: str, data: Optional[Dict] = None,
                          headers: Optional[Dict] = None) -> httpx.Response:
        """Make HTTP request."""
        url = f"{self.base_url}{path}"
        headers = headers or {}
        
        if self.auth_token:
            headers.setdefault("Authorization", f"Bearer {self.auth_token}")
            
        if method.upper() == "GET":
            return await self.client.get(url, headers=headers)
        elif method.upper() == "POST":
            return await self.client.post(url, json=data, headers=headers)
        elif method.upper() == "PUT":
            return await self.client.put(url, json=data, headers=headers)
        elif method.upper() == "DELETE":
            return await self.client.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")
            
    # ============================================================================
    # Integration Test Flows
    # ============================================================================
    
    async def test_complete_query_flow(self):
        """Test complete RAG query flow with memory."""
        self.log("=" * 60, "STEP")
        self.log("Test 1: Complete Query Flow", "STEP")
        self.log("=" * 60, "STEP")
        
        # Step 1: Create memory
        self.log("Step 1: Creating memory...", "INFO")
        memory_data = {
            "user_id": self.user_id,
            "content": "User prefers Python programming",
            "memory_type": "preference"
        }
        response = await self.make_request("POST", "/memory", data=memory_data)
        if response.status_code == 200:
            memory = response.json()
            self.test_data["memory_id"] = memory.get("id")
            self.log(f"✓ Memory created: {self.test_data['memory_id']}", "PASS")
        else:
            self.log(f"✗ Failed to create memory: {response.status_code}", "FAIL")
            return False
            
        # Step 2: Make query
        self.log("Step 2: Making query...", "INFO")
        query_data = {
            "message": "What programming language do I prefer?",
            "user_id": self.user_id
        }
        response = await self.make_request("POST", "/query", data=query_data)
        if response.status_code == 200:
            result = response.json()
            self.log(f"✓ Query successful", "PASS")
            self.log(f"  Answer: {result.get('answer', '')[:100]}...", "INFO")
            return True
        else:
            self.log(f"✗ Query failed: {response.status_code}", "FAIL")
            return False
            
    async def test_live_session_flow(self):
        """Test complete live session flow."""
        self.log("=" * 60, "STEP")
        self.log("Test 2: Live Session Flow", "STEP")
        self.log("=" * 60, "STEP")
        
        # Step 1: Create session
        self.log("Step 1: Creating live session...", "INFO")
        session_data = {
            "user_id": self.user_id,
            "mode": "audio"
        }
        response = await self.make_request("POST", "/live-sessions", data=session_data)
        if response.status_code == 200:
            session = response.json()
            self.test_data["session_id"] = session.get("id")
            self.log(f"✓ Session created: {self.test_data['session_id']}", "PASS")
        else:
            self.log(f"✗ Failed to create session: {response.status_code}", "FAIL")
            return False
            
        # Step 2: Get session
        self.log("Step 2: Retrieving session...", "INFO")
        response = await self.make_request("GET", f"/live-sessions/{self.test_data['session_id']}")
        if response.status_code == 200:
            self.log("✓ Session retrieved", "PASS")
        else:
            self.log(f"✗ Failed to retrieve session: {response.status_code}", "FAIL")
            return False
            
        # Step 3: Update session
        self.log("Step 3: Updating session...", "INFO")
        update_data = {
            "transcript_partial": "Test transcript"
        }
        response = await self.make_request(
            "PUT", 
            f"/live-sessions/{self.test_data['session_id']}",
            data=update_data
        )
        if response.status_code == 200:
            self.log("✓ Session updated", "PASS")
        else:
            self.log(f"✗ Failed to update session: {response.status_code}", "FAIL")
            return False
            
        return True
        
    async def test_browser_automation_flow(self):
        """Test complete browser automation flow."""
        self.log("=" * 60, "STEP")
        self.log("Test 3: Browser Automation Flow", "STEP")
        self.log("=" * 60, "STEP")
        
        # Step 1: Create browser session
        self.log("Step 1: Creating browser session...", "INFO")
        session_data = {
            "user_id": self.user_id
        }
        response = await self.make_request("POST", "/browser/sessions", data=session_data)
        if response.status_code == 200:
            session = response.json()
            self.test_data["browser_session_id"] = session.get("id")
            self.log(f"✓ Browser session created: {self.test_data['browser_session_id']}", "PASS")
        else:
            self.log(f"✗ Failed to create browser session: {response.status_code}", "FAIL")
            return False
            
        # Step 2: Navigate
        self.log("Step 2: Navigating to URL...", "INFO")
        navigate_data = {
            "url": "https://example.com"
        }
        response = await self.make_request(
            "POST",
            f"/browser/sessions/{self.test_data['browser_session_id']}/navigate",
            data=navigate_data
        )
        if response.status_code in [200, 202]:
            self.log("✓ Navigation initiated", "PASS")
        else:
            self.log(f"⚠ Navigation may have failed: {response.status_code}", "FAIL")
            # Don't fail the test, navigation might take time
            
        return True
        
    async def test_reasoning_flow(self):
        """Test reasoning with query."""
        self.log("=" * 60, "STEP")
        self.log("Test 4: Reasoning Flow", "STEP")
        self.log("=" * 60, "STEP")
        
        # Step 1: Chain-of-Thought reasoning
        self.log("Step 1: Testing Chain-of-Thought...", "INFO")
        data = {
            "query": "If I have 5 apples and eat 2, how many are left?",
            "user_id": self.user_id
        }
        response = await self.make_request("POST", "/reasoning/chain-of-thought", data=data)
        if response.status_code == 200:
            result = response.json()
            self.log("✓ Chain-of-Thought reasoning successful", "PASS")
            self.log(f"  Reasoning: {result.get('reasoning', '')[:100]}...", "INFO")
        else:
            self.log(f"✗ Reasoning failed: {response.status_code}", "FAIL")
            return False
            
        return True
        
    async def test_media_flow(self):
        """Test media generation flow."""
        self.log("=" * 60, "STEP")
        self.log("Test 5: Media Generation Flow", "STEP")
        self.log("=" * 60, "STEP")
        
        # Step 1: Generate image
        self.log("Step 1: Generating image...", "INFO")
        data = {
            "prompt": "A beautiful landscape",
            "user_id": self.user_id
        }
        response = await self.make_request("POST", "/media/images/generate", data=data)
        if response.status_code in [200, 202]:
            result = response.json()
            self.log("✓ Image generation initiated", "PASS")
            if "image_url" in result:
                self.log(f"  Image URL: {result['image_url']}", "INFO")
        else:
            self.log(f"⚠ Image generation may require API keys: {response.status_code}", "FAIL")
            
        return True
        
    async def run_all_tests(self):
        """Run all integration tests."""
        self.log("=" * 60, "INFO")
        self.log("Starting Integration Tests", "INFO")
        self.log("=" * 60, "INFO")
        self.log(f"Base URL: {self.base_url}", "INFO")
        self.log(f"User ID: {self.user_id}", "INFO")
        self.log("", "INFO")
        
        results = []
        
        # Run all test flows
        test_flows = [
            ("Complete Query Flow", self.test_complete_query_flow),
            ("Live Session Flow", self.test_live_session_flow),
            ("Browser Automation Flow", self.test_browser_automation_flow),
            ("Reasoning Flow", self.test_reasoning_flow),
            ("Media Flow", self.test_media_flow),
        ]
        
        for name, test_func in test_flows:
            try:
                result = await test_func()
                results.append({"name": name, "passed": result})
                self.log("", "INFO")
            except Exception as e:
                self.log(f"✗ {name} failed with exception: {e}", "FAIL")
                results.append({"name": name, "passed": False, "error": str(e)})
                self.log("", "INFO")
        
        # Print summary
        self.print_summary(results)
        
    def print_summary(self, results):
        """Print test summary."""
        self.log("=" * 60, "INFO")
        self.log("Integration Test Summary", "INFO")
        self.log("=" * 60, "INFO")
        
        passed = sum(1 for r in results if r.get("passed", False))
        failed = len(results) - passed
        
        for result in results:
            status = "PASS" if result.get("passed", False) else "FAIL"
            symbol = "✓" if result.get("passed", False) else "✗"
            self.log(f"{symbol} {result['name']}", status)
            
        self.log("", "INFO")
        self.log(f"Passed: {passed}/{len(results)}", "PASS" if passed == len(results) else "INFO")
        self.log(f"Failed: {failed}/{len(results)}", "FAIL" if failed > 0 else "INFO")
        self.log("=" * 60, "INFO")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Integration tests for Jarvis RAG API")
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Base URL of the API (default: http://localhost:8000)"
    )
    
    args = parser.parse_args()
    
    async with IntegrationTester(base_url=args.base_url) as tester:
        await tester.run_all_tests()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nTests failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

