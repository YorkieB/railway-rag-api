#!/usr/bin/env python3
"""
Comprehensive API Testing Script for Jarvis RAG API

Tests all endpoints, integrations, and features.
Usage: python scripts/test_api.py [--base-url BASE_URL]
"""

import asyncio
import sys
import argparse
import json
from typing import Dict, List, Optional
from datetime import datetime
import httpx
from colorama import init, Fore, Style

# Initialize colorama for Windows
init(autoreset=True)

# Fix Windows console encoding for Unicode characters
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

class APITester:
    """Comprehensive API testing class."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=30.0)
        self.results = {
            "passed": [],
            "failed": [],
            "skipped": [],
            "total": 0
        }
        self.auth_token: Optional[str] = None
        self.api_key: Optional[str] = None
        
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
            "SKIP": Fore.YELLOW,
            "INFO": Fore.CYAN
        }
        color = colors.get(status, Fore.WHITE)
        print(f"{color}[{timestamp}] {status}: {message}{Style.RESET_ALL}")
        
    async def test_endpoint(self, method: str, path: str, expected_status: int = 200,
                          data: Optional[Dict] = None, headers: Optional[Dict] = None,
                          description: str = "") -> bool:
        """Test a single endpoint."""
        self.results["total"] += 1
        url = f"{self.base_url}{path}"
        
        try:
            if method.upper() == "GET":
                response = await self.client.get(url, headers=headers)
            elif method.upper() == "POST":
                response = await self.client.post(url, json=data, headers=headers)
            elif method.upper() == "PUT":
                response = await self.client.put(url, json=data, headers=headers)
            elif method.upper() == "DELETE":
                response = await self.client.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            if response.status_code == expected_status:
                self.log(f"✓ {description or path} - Status: {response.status_code}", "PASS")
                self.results["passed"].append({
                    "method": method,
                    "path": path,
                    "status": response.status_code,
                    "description": description
                })
                return True
            else:
                self.log(f"✗ {description or path} - Expected {expected_status}, got {response.status_code}", "FAIL")
                self.log(f"  Response: {response.text[:200]}", "FAIL")
                self.results["failed"].append({
                    "method": method,
                    "path": path,
                    "expected": expected_status,
                    "actual": response.status_code,
                    "response": response.text[:500],
                    "description": description
                })
                return False
        except Exception as e:
            self.log(f"✗ {description or path} - Error: {str(e)}", "FAIL")
            self.results["failed"].append({
                "method": method,
                "path": path,
                "error": str(e),
                "description": description
            })
            return False
            
    # ============================================================================
    # Core Endpoints
    # ============================================================================
    
    async def test_root(self):
        """Test root endpoint."""
        await self.test_endpoint("GET", "/", description="Root endpoint")
        
    async def test_health(self):
        """Test health check."""
        await self.test_endpoint("GET", "/health", description="Health check")
        
    async def test_metrics(self):
        """Test metrics endpoint."""
        await self.test_endpoint("GET", "/metrics", description="Metrics endpoint")
        
    # ============================================================================
    # Authentication
    # ============================================================================
    
    async def test_auth_login(self):
        """Test authentication login."""
        login_data = {
            "username": "test_user",
            "password": "test_password"
        }
        success = await self.test_endpoint(
            "POST", "/auth/login", 
            data=login_data,
            expected_status=200,
            description="Authentication login"
        )
        
        if success:
            # Try to extract token from response
            try:
                response = await self.client.post(
                    f"{self.base_url}/auth/login",
                    json=login_data
                )
                if response.status_code == 200:
                    data = response.json()
                    self.auth_token = data.get("access_token")
                    if self.auth_token:
                        self.log(f"  Token obtained: {self.auth_token[:20]}...", "PASS")
            except:
                pass
                
    async def test_auth_me(self):
        """Test get current user."""
        headers = {}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        await self.test_endpoint(
            "GET", "/auth/me",
            headers=headers if headers else None,
            description="Get current user"
        )
        
    # ============================================================================
    # Memory API
    # ============================================================================
    
    async def test_memory_create(self):
        """Test memory creation."""
        memory_data = {
            "user_id": "test_user",
            "content": "Test memory content",
            "memory_type": "fact"
        }
        await self.test_endpoint(
            "POST", "/memory",
            data=memory_data,
            description="Create memory"
        )
        
    async def test_memory_list(self):
        """Test memory listing."""
        await self.test_endpoint(
            "GET", "/memory?user_id=test_user",
            description="List memories"
        )
        
    # ============================================================================
    # Live Sessions
    # ============================================================================
    
    async def test_live_session_create(self):
        """Test live session creation."""
        session_data = {
            "user_id": "test_user",
            "mode": "audio"
        }
        await self.test_endpoint(
            "POST", "/live-sessions",
            data=session_data,
            description="Create live session"
        )
        
    async def test_live_session_list(self):
        """Test live session listing."""
        await self.test_endpoint(
            "GET", "/live-sessions?user_id=test_user",
            description="List live sessions"
        )
        
    # ============================================================================
    # Browser Automation
    # ============================================================================
    
    async def test_browser_session_create(self):
        """Test browser session creation."""
        session_data = {
            "user_id": "test_user"
        }
        await self.test_endpoint(
            "POST", "/browser/sessions",
            data=session_data,
            description="Create browser session"
        )
        
    async def test_browser_session_list(self):
        """Test browser session listing."""
        await self.test_endpoint(
            "GET", "/browser/sessions?user_id=test_user",
            description="List browser sessions"
        )
        
    # ============================================================================
    # Reasoning API
    # ============================================================================
    
    async def test_reasoning_cot(self):
        """Test Chain-of-Thought reasoning."""
        data = {
            "query": "What is 2+2?",
            "user_id": "test_user"
        }
        await self.test_endpoint(
            "POST", "/reasoning/chain-of-thought",
            data=data,
            description="Chain-of-Thought reasoning"
        )
        
    async def test_reasoning_reflection(self):
        """Test Reflection reasoning."""
        data = {
            "query": "Explain quantum computing",
            "user_id": "test_user"
        }
        await self.test_endpoint(
            "POST", "/reasoning/reflection",
            data=data,
            description="Reflection reasoning"
        )
        
    # ============================================================================
    # Indexing API
    # ============================================================================
    
    async def test_indexing_search(self):
        """Test universal search."""
        await self.test_endpoint(
            "GET", "/indexing/search?query=test&user_id=test_user",
            description="Universal search"
        )
        
    # ============================================================================
    # Media API
    # ============================================================================
    
    async def test_media_image_generate(self):
        """Test image generation."""
        data = {
            "prompt": "A beautiful sunset",
            "user_id": "test_user"
        }
        await self.test_endpoint(
            "POST", "/media/images/generate",
            data=data,
            description="Image generation"
        )
        
    async def test_media_spotify_search(self):
        """Test Spotify search."""
        await self.test_endpoint(
            "GET", "/media/spotify/search?q=test&user_id=test_user",
            description="Spotify search"
        )
        
    # ============================================================================
    # Word Processor API
    # ============================================================================
    
    async def test_word_processor_create(self):
        """Test word processor document creation."""
        data = {
            "title": "Test Document",
            "content": "Test content",
            "user_id": "test_user"
        }
        await self.test_endpoint(
            "POST", "/word-processor/documents",
            data=data,
            description="Create word processor document"
        )
        
    # ============================================================================
    # Query Endpoint
    # ============================================================================
    
    async def test_query(self):
        """Test main query endpoint."""
        data = {
            "message": "Hello, what can you do?",
            "user_id": "test_user"
        }
        await self.test_endpoint(
            "POST", "/query",
            data=data,
            description="Main query endpoint"
        )
        
    # ============================================================================
    # Rate Limiting Test
    # ============================================================================
    
    async def test_rate_limiting(self):
        """Test rate limiting."""
        self.log("Testing rate limiting (sending 20 rapid requests)...", "INFO")
        success_count = 0
        rate_limited = False
        
        for i in range(20):
            response = await self.client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                success_count += 1
            elif response.status_code == 429:
                rate_limited = True
                break
                
        if rate_limited:
            self.log("✓ Rate limiting is working", "PASS")
            self.results["passed"].append({"test": "rate_limiting", "status": "working"})
        else:
            self.log("⚠ Rate limiting may not be configured", "SKIP")
            self.results["skipped"].append({"test": "rate_limiting"})
            
    # ============================================================================
    # Run All Tests
    # ============================================================================
    
    async def run_all_tests(self):
        """Run all test suites."""
        self.log("=" * 60, "INFO")
        self.log("Starting Comprehensive API Tests", "INFO")
        self.log("=" * 60, "INFO")
        self.log(f"Base URL: {self.base_url}", "INFO")
        self.log("", "INFO")
        
        # Core endpoints
        self.log("Testing Core Endpoints...", "INFO")
        await self.test_root()
        await self.test_health()
        await self.test_metrics()
        self.log("", "INFO")
        
        # Authentication
        self.log("Testing Authentication...", "INFO")
        await self.test_auth_login()
        await self.test_auth_me()
        self.log("", "INFO")
        
        # Memory API
        self.log("Testing Memory API...", "INFO")
        await self.test_memory_create()
        await self.test_memory_list()
        self.log("", "INFO")
        
        # Live Sessions
        self.log("Testing Live Sessions...", "INFO")
        await self.test_live_session_create()
        await self.test_live_session_list()
        self.log("", "INFO")
        
        # Browser Automation
        self.log("Testing Browser Automation...", "INFO")
        await self.test_browser_session_create()
        await self.test_browser_session_list()
        self.log("", "INFO")
        
        # Reasoning
        self.log("Testing Reasoning API...", "INFO")
        await self.test_reasoning_cot()
        await self.test_reasoning_reflection()
        self.log("", "INFO")
        
        # Indexing
        self.log("Testing Indexing API...", "INFO")
        await self.test_indexing_search()
        self.log("", "INFO")
        
        # Media
        self.log("Testing Media API...", "INFO")
        await self.test_media_image_generate()
        await self.test_media_spotify_search()
        self.log("", "INFO")
        
        # Word Processor
        self.log("Testing Word Processor API...", "INFO")
        await self.test_word_processor_create()
        self.log("", "INFO")
        
        # Query
        self.log("Testing Query Endpoint...", "INFO")
        await self.test_query()
        self.log("", "INFO")
        
        # Rate Limiting
        self.log("Testing Rate Limiting...", "INFO")
        await self.test_rate_limiting()
        self.log("", "INFO")
        
        # Print summary
        self.print_summary()
        
    def print_summary(self):
        """Print test summary."""
        self.log("=" * 60, "INFO")
        self.log("Test Summary", "INFO")
        self.log("=" * 60, "INFO")
        
        total = self.results["total"]
        passed = len(self.results["passed"])
        failed = len(self.results["failed"])
        skipped = len(self.results["skipped"])
        
        self.log(f"Total Tests: {total}", "INFO")
        self.log(f"Passed: {passed} {Fore.GREEN}✓{Style.RESET_ALL}", "PASS" if passed > 0 else "INFO")
        self.log(f"Failed: {failed} {Fore.RED}✗{Style.RESET_ALL}", "FAIL" if failed > 0 else "INFO")
        self.log(f"Skipped: {skipped} {Fore.YELLOW}⚠{Style.RESET_ALL}", "SKIP" if skipped > 0 else "INFO")
        
        if failed > 0:
            self.log("", "INFO")
            self.log("Failed Tests:", "FAIL")
            for test in self.results["failed"]:
                self.log(f"  - {test.get('description', test.get('path', 'Unknown'))}", "FAIL")
                if "error" in test:
                    self.log(f"    Error: {test['error']}", "FAIL")
                elif "actual" in test:
                    self.log(f"    Expected: {test['expected']}, Got: {test['actual']}", "FAIL")
        
        self.log("=" * 60, "INFO")
        
        # Save results to file
        results_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2)
        self.log(f"Results saved to: {results_file}", "INFO")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Test Jarvis RAG API")
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Base URL of the API (default: http://localhost:8000)"
    )
    
    args = parser.parse_args()
    
    async with APITester(base_url=args.base_url) as tester:
        await tester.run_all_tests()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nTest failed with error: {e}")
        sys.exit(1)

