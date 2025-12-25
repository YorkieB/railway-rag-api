#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick API Test - Simple version to verify API is working
"""

import asyncio
import httpx
import sys
import os
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

async def test_endpoint(client, method, url, data=None, expected=200):
    """Test a single endpoint."""
    try:
        if method == "GET":
            response = await client.get(url)
        elif method == "POST":
            response = await client.post(url, json=data)
        else:
            return False, f"Unsupported method: {method}"
            
        if response.status_code == expected:
            return True, f"[PASS] {method} {url} - {response.status_code}"
        else:
            return False, f"[FAIL] {method} {url} - Expected {expected}, got {response.status_code}"
    except Exception as e:
        return False, f"[FAIL] {method} {url} - Error: {str(e)}"

async def main():
    """Run quick tests."""
    base_url = "http://localhost:8000"
    
    print("=" * 60)
    print("Quick API Test")
    print("=" * 60)
    print(f"Testing: {base_url}")
    print()
    
    # Check if API is running
    print("Checking if API is running...")
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                print("[PASS] API is running!")
            else:
                print(f"[FAIL] API returned status {response.status_code}")
                return 1
    except Exception as e:
        print(f"[FAIL] API is not running: {e}")
        print()
        print("Please start the API first:")
        print("  cd rag-api")
        print("  uvicorn app:app --reload")
        return 1
    
    print()
    print("Running tests...")
    print()
    
    results = []
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Core endpoints
        success, msg = await test_endpoint(client, "GET", f"{base_url}/")
        print(msg)
        results.append(success)
        
        success, msg = await test_endpoint(client, "GET", f"{base_url}/health")
        print(msg)
        results.append(success)
        
        success, msg = await test_endpoint(client, "GET", f"{base_url}/metrics")
        print(msg)
        results.append(success)
        
        # Memory API
        success, msg = await test_endpoint(
            client, "GET", 
            f"{base_url}/memory?user_id=test"
        )
        print(msg)
        results.append(success)
        
        # Query endpoint
        success, msg = await test_endpoint(
            client, "POST",
            f"{base_url}/query",
            data={"message": "Hello", "user_id": "test"}
        )
        print(msg)
        results.append(success)
    
    print()
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest interrupted")
        sys.exit(1)

