"""
LS1A Router

FastAPI router for LS1A WebSocket endpoint.
"""

from fastapi import APIRouter, WebSocket, Query
from .ls1a_websocket import ls1a_websocket_endpoint

router = APIRouter(tags=["ls1a"])


@router.websocket("/ws/{session_id}")
async def ls1a_websocket(
    websocket: WebSocket,
    session_id: str,
    user_id: str = Query(..., description="User ID for ownership validation")
):
    """
    WebSocket endpoint for LS1A audio pipeline.
    
    Usage:
        WS /ls1a/ws/{session_id}?user_id={user_id}
    
    Message Types (from client):
        - audio_chunk (binary): PCM audio data (16-bit, 16kHz, mono)
        - pause (text JSON): {"type": "pause"} - Pause session
        - resume (text JSON): {"type": "resume"} - Resume session
        - close (text JSON): {"type": "close"} - Close session
    
    Response Types (to client):
        - ready: {"type": "ready", "session_id": "...", "message": "..."}
        - transcript: {"type": "transcript", "text": "...", "is_final": bool}
        - audio_chunk: {"type": "audio_chunk", "data": "base64...", "format": "mp3"}
        - budget_warning: {"type": "budget_warning", "utilization": 0.85, "message": "..."}
        - session_paused: {"type": "session_paused", "reason": "budget_exhausted"}
        - error: {"type": "error", "message": "..."}
    """
    await ls1a_websocket_endpoint(websocket, session_id, user_id)

