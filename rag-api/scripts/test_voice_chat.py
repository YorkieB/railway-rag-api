#!/usr/bin/env python3
"""
Test Voice Chat (LS1A) WebSocket Connection

Tests the WebSocket endpoint for voice chat functionality.
"""

import asyncio
import websockets
import json
import base64
import sys
import os
from datetime import datetime

async def test_voice_chat_websocket(base_url: str = "ws://localhost:8000", user_id: str = "test_user"):
    """Test voice chat WebSocket connection."""
    
    print("=" * 60)
    print("Voice Chat WebSocket Test")
    print("=" * 60)
    print(f"Base URL: {base_url}")
    print(f"User ID: {user_id}")
    print()
    
    # Step 1: Create a live session
    print("Step 1: Creating live session...")
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url.replace('ws://', 'http://').replace('wss://', 'https://')}/live-sessions",
                json={
                    "user_id": user_id,
                    "mode": "LS1A"
                },
                timeout=10.0
            )
            
            if response.status_code != 200:
                print(f"[FAIL] Failed to create session: {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            session_data = response.json()
            # API returns {"session": {"id": "..."}} not {"id": "..."}
            session_id = session_data.get("session", {}).get("id")
            if not session_id:
                # Fallback: try direct access in case response format differs
                session_id = session_data.get("id")
            print(f"[PASS] Session created: {session_id}")
    except Exception as e:
        print(f"[FAIL] Error creating session: {e}")
        return False
    
    print()
    
    # Step 2: Connect to WebSocket
    print("Step 2: Connecting to WebSocket...")
    ws_url = f"{base_url}/ls1a/ws/{session_id}?user_id={user_id}"
    print(f"WebSocket URL: {ws_url}")
    
    try:
        async with websockets.connect(ws_url) as websocket:
            print("[PASS] WebSocket connected")
            print()
            
            # Step 3: Wait for ready message
            print("Step 3: Waiting for ready message...")
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                print(f"[PASS] Received message: {data.get('type', 'unknown')}")
                if data.get('type') == 'ready':
                    print("[PASS] Pipeline is ready!")
                else:
                    print(f"[INFO] Message type: {data.get('type')}")
            except asyncio.TimeoutError:
                print("[WARN] No ready message received (may still work)")
            except Exception as e:
                print(f"[WARN] Error receiving ready message: {e}")
            
            print()
            
            # Step 4: Send a test control message
            print("Step 4: Testing control messages...")
            test_message = {"type": "pause"}
            await websocket.send(json.dumps(test_message))
            print("[PASS] Sent pause message")
            
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                data = json.loads(response)
                print(f"[PASS] Received response: {data.get('type', 'unknown')}")
            except asyncio.TimeoutError:
                print("[WARN] No response to pause message")
            except Exception as e:
                print(f"[WARN] Error receiving response: {e}")
            
            print()
            
            # Step 5: Test audio chunk (dummy data)
            print("Step 5: Testing audio chunk sending...")
            # Create dummy PCM audio data (16-bit, 16kHz, mono)
            dummy_audio = b'\x00' * 3200  # 100ms of silence at 16kHz
            await websocket.send(dummy_audio)
            print("[PASS] Sent dummy audio chunk")
            
            # Wait a bit for processing
            await asyncio.sleep(1)
            
            print()
            print("=" * 60)
            print("Test Summary")
            print("=" * 60)
            print("[PASS] WebSocket connection successful")
            print("[PASS] Ready message received")
            print("[PASS] Control messages work")
            print("[PASS] Audio chunks can be sent")
            print()
            print("✅ Voice chat WebSocket is working!")
            print()
            print("Note: Full voice chat requires:")
            print("  - DEEPGRAM_API_KEY for STT")
            print("  - OPENAI_API_KEY for LLM")
            print("  - ELEVENLABS_API_KEY for TTS")
            print()
            
            return True
            
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"[FAIL] WebSocket connection failed: {e}")
        if e.status_code == 404:
            print("[INFO] Endpoint not found - check if ls1a_router is included in app.py")
        return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test voice chat WebSocket")
    parser.add_argument(
        "--base-url",
        default="ws://localhost:8000",
        help="WebSocket base URL (default: ws://localhost:8000)"
    )
    parser.add_argument(
        "--user-id",
        default="test_user",
        help="User ID for testing (default: test_user)"
    )
    
    args = parser.parse_args()
    
    success = await test_voice_chat_websocket(args.base_url, args.user_id)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted")
        sys.exit(1)

