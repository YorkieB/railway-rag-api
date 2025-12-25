#!/usr/bin/env python3
"""
Quick test runner - checks if API is running and runs tests
"""

import sys
import subprocess
import asyncio
import httpx
from pathlib import Path

async def check_api_running(base_url: str = "http://localhost:8000") -> bool:
    """Check if API is running."""
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"{base_url}/health")
            return response.status_code == 200
    except:
        return False

def main():
    """Main entry point."""
    print("=" * 60)
    print("Jarvis API Test Runner")
    print("=" * 60)
    print()
    
    # Check if API is running
    print("Checking if API is running...")
    try:
        result = asyncio.run(check_api_running())
        if result:
            print("✓ API is running!")
            print()
        else:
            print("✗ API is not running!")
            print()
            print("Please start the API first:")
            print("  cd rag-api")
            print("  uvicorn app:app --reload")
            print()
            print("Or in a separate terminal, run:")
            print("  python -m uvicorn rag-api.app:app --reload")
            print()
            return 1
    except Exception as e:
        print(f"✗ Error checking API: {e}")
        print()
        return 1
    
    # Run API tests
    print("Running API tests...")
    print()
    script_path = Path(__file__).parent / "scripts" / "test_api.py"
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=Path(__file__).parent
        )
        return result.returncode
    except Exception as e:
        print(f"✗ Error running tests: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

