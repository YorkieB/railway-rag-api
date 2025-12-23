"""
Comprehensive Test Suite for Jarvis RAG API
Tests all endpoints including V3 features
"""
import requests
import json
import sys
import os
import io
from typing import Dict, Optional

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE_URL = os.getenv("API_BASE_URL", "https://railway-rag-api-production.up.railway.app")
test_results = []
passed = 0
failed = 0


def test_endpoint(
    name: str,
    method: str,
    path: str,
    body: Optional[Dict] = None,
    params: Optional[Dict] = None,
    expected_status: int = 200
) -> bool:
    """Test an API endpoint"""
    global passed, failed
    
    print(f"Testing: {name} [{method} {path}]", end="")
    
    try:
        url = f"{BASE_URL}{path}"
        
        if method == "GET":
            response = requests.get(url, params=params, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=body, params=params, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json=body, params=params, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, params=params, timeout=10)
        else:
            print(f"  ❌ FAILED: Unknown method {method}")
            failed += 1
            return False
        
        if response.status_code == expected_status or (expected_status == 200 and 200 <= response.status_code < 300):
            print(f"  ✅ PASSED")
            passed += 1
            test_results.append({
                "name": name,
                "status": "PASSED",
                "status_code": response.status_code
            })
            return True
        else:
            print(f"  ❌ FAILED (Expected {expected_status}, got {response.status_code})")
            failed += 1
            test_results.append({
                "name": name,
                "status": "FAILED",
                "status_code": response.status_code,
                "expected": expected_status
            })
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"  ❌ FAILED: Cannot connect to server")
        failed += 1
        test_results.append({
            "name": name,
            "status": "FAILED",
            "error": "Connection refused"
        })
        return False
    except Exception as e:
        print(f"  ❌ FAILED: {str(e)}")
        failed += 1
        test_results.append({
            "name": name,
            "status": "FAILED",
            "error": str(e)
        })
        return False


def main():
    """Run comprehensive test suite"""
    global passed, failed
    
    print("=" * 50)
    print("  JARVIS RAG API - FULL TEST SUITE")
    print("=" * 50)
    print()
    
    # Check if server is running
    print("Checking server status...", end="")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(" ✅ Server is running")
        print()
    except:
        print(" ❌ Server is not running!")
        print()
        print("Please start the server first:")
        print("  cd rag-api")
        print("  uvicorn app:app --reload --port 8080")
        print()
        sys.exit(1)
    
    print("Starting comprehensive tests...")
    print()
    
    # ============================================
    # CORE API TESTS
    # ============================================
    print("=== CORE API ===")
    test_endpoint("Health Check", "GET", "/health")
    test_endpoint("Root Endpoint", "GET", "/")
    test_endpoint("List Documents", "GET", "/documents")
    print()
    
    # ============================================
    # V3 FEATURES - INTEGRATIONS
    # ============================================
    print("=== V3: INTEGRATIONS ===")
    test_endpoint("List Integrations", "GET", "/integrations")
    test_endpoint("Zapier Status", "GET", "/integrations/zapier/status")
    test_endpoint("Slack Status", "GET", "/integrations/slack/status")
    test_endpoint("Email Status", "GET", "/integrations/email/status")
    test_endpoint("Spotify Status", "GET", "/integrations/spotify/status")
    print()
    
    # ============================================
    # V3 FEATURES - MEMORY
    # ============================================
    print("=== V3: MEMORY FEATURES ===")
    test_endpoint("List Memory Templates", "GET", "/memory/templates")
    test_endpoint("List Memories", "GET", "/memory", params={"user_id": "test_user"})
    test_endpoint("Memory Clustering", "POST", "/memory/cluster", params={"user_id": "test_user"})
    test_endpoint("Memory Conflicts", "GET", "/memory/conflicts", params={"user_id": "test_user"})
    print()
    
    # ============================================
    # V3 FEATURES - COLLABORATION
    # ============================================
    print("=== V3: COLLABORATION ===")
    session_created = test_endpoint(
        "Create Collaboration Session",
        "POST",
        "/collaboration/sessions",
        body={
            "owner_id": "test_user",
            "session_type": "browser",
            "target_id": "test_session"
        }
    )
    
    if session_created:
        try:
            response = requests.post(
                f"{BASE_URL}/collaboration/sessions",
                json={
                    "owner_id": "test_user",
                    "session_type": "browser",
                    "target_id": "test_session"
                }
            )
            session_data = response.json()
            session_id = session_data.get("session_id")
            if session_id:
                test_endpoint("Get Collaboration Session", "GET", f"/collaboration/sessions/{session_id}")
                test_endpoint("List Collaboration Sessions", "GET", "/collaboration/sessions", params={"user_id": "test_user"})
        except:
            pass
    print()
    
    # ============================================
    # V3 FEATURES - AGENTS
    # ============================================
    print("=== V3: AGENTS ===")
    test_endpoint("Agent Marketplace", "GET", "/agents/marketplace")
    test_endpoint("Agent Status", "GET", "/agents/status")
    test_endpoint(
        "Agent Learning",
        "POST",
        "/agents/test_agent/learn",
        body={
            "feedback": "Good job",
            "pattern": {
                "agent_type": "browser",
                "success": True
            }
        }
    )
    test_endpoint("Agent Improvement", "POST", "/agents/test_agent/improve")
    print()
    
    # ============================================
    # V3 FEATURES - ANALYTICS
    # ============================================
    print("=== V3: ANALYTICS ===")
    test_endpoint("Usage Statistics", "GET", "/analytics/usage", params={"user_id": "test_user", "days": 30})
    test_endpoint("Cost Analysis", "GET", "/analytics/cost", params={"user_id": "test_user", "days": 30})
    test_endpoint("Performance Metrics", "GET", "/analytics/performance", params={"user_id": "test_user", "days": 30})
    print()
    
    # ============================================
    # V3 FEATURES - DOCUMENT PROCESSING
    # ============================================
    print("=== V3: DOCUMENT PROCESSING ===")
    test_endpoint(
        "Document Categorization",
        "POST",
        "/documents/categorize",
        params={
            "text": "This is a meeting note about project planning and deadlines.",
            "user_id": "test_user"
        }
    )
    test_endpoint(
        "Document Summarization",
        "POST",
        "/documents/summarize",
        params={
            "text": "This is a long document about various topics that need to be summarized into a shorter version.",
            "max_length": 100,
            "user_id": "test_user"
        }
    )
    print()
    
    # ============================================
    # EXISTING FEATURES - MEMORY API
    # ============================================
    print("=== EXISTING: MEMORY API ===")
    test_endpoint(
        "Search Memories",
        "POST",
        "/memory/search",
        body={
            "user_id": "test_user",
            "query": "test query",
            "top_k": 5
        }
    )
    print()
    
    # ============================================
    # EXISTING FEATURES - BROWSER AUTOMATION
    # ============================================
    print("=== EXISTING: BROWSER AUTOMATION ===")
    browser_session_created = test_endpoint("Create Browser Session", "POST", "/browser/sessions", params={"user_id": "test_user"})
    if browser_session_created:
        try:
            response = requests.post(f"{BASE_URL}/browser/sessions", params={"user_id": "test_user"})
            browser_data = response.json()
            browser_session_id = browser_data.get("session_id")
            if browser_session_id:
                test_endpoint("Get AX Tree", "GET", f"/browser/sessions/{browser_session_id}/ax-tree")
        except:
            pass
    print()
    
    # ============================================
    # SUMMARY
    # ============================================
    print("=" * 50)
    print("  TEST SUMMARY")
    print("=" * 50)
    print()
    print(f"Total Tests: {passed + failed}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print()
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        print()
        print("Failed tests:")
        for result in test_results:
            if result.get("status") == "FAILED":
                print(f"  - {result['name']}")
                if "error" in result:
                    print(f"    Error: {result['error']}")
    
    print()
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

