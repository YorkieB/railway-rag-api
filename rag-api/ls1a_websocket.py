"""
LS1A WebSocket Handler

WebSocket endpoint for LS1A audio pipeline with LiveSession integration.
"""

from fastapi import WebSocket, WebSocketDisconnect, HTTPException, Query
from typing import Optional
import asyncio
import json
import base64
from .models import LiveSession
from .live_session_storage import LiveSessionStorage, InMemoryLiveSessionStorage
from .cost import CostTracker
from .ls1a_pipeline import LS1APipeline


class LS1AWebSocketHandler:
    """
    WebSocket handler for LS1A audio pipeline.
    
    Handles:
    - WebSocket connection management
    - Audio chunk processing
    - Session state transitions
    - Budget warnings
    """
    
    def __init__(
        self,
        session_storage: Optional[LiveSessionStorage] = None,
        cost_tracker: Optional[CostTracker] = None
    ):
        """
        Initialize WebSocket handler.
        
        Args:
            session_storage: LiveSessionStorage instance (defaults to InMemory)
            cost_tracker: CostTracker instance (defaults to new instance)
        """
        self.session_storage = session_storage or InMemoryLiveSessionStorage()
        self.cost_tracker = cost_tracker or CostTracker()
        self.active_pipelines: dict[str, LS1APipeline] = {}
    
    async def handle_websocket(
        self,
        websocket: WebSocket,
        session_id: str,
        user_id: str
    ):
        """
        Handle WebSocket connection for LS1A session.
        
        Args:
            websocket: WebSocket connection
            session_id: LiveSession ID
            user_id: User ID for ownership validation
        """
        await websocket.accept()
        
        # Get session
        session = self.session_storage.get(session_id, user_id)
        if not session:
            await websocket.close(code=1008, reason="Session not found")
            return
        
        # Validate mode
        if session.mode != "LS1A":
            await websocket.close(code=1008, reason="Session is not LS1A mode")
            return
        
        # Transition to LIVE if in CONNECTING
        if session.state == "CONNECTING":
            updated = self.session_storage.update(session_id, user_id, {"state": "LIVE"})
            if updated:
                session = updated
                await websocket.send_json({
                    "type": "session_started",
                    "session_id": session_id,
                    "state": "LIVE"
                })
            else:
                await websocket.close(code=1008, reason="Failed to start session")
                return
        
        # Check if already LIVE
        if session.state != "LIVE":
            await websocket.close(code=1008, reason=f"Session is in {session.state} state")
            return
        
        # Initialize pipeline
        try:
            pipeline = LS1APipeline(
                session=session,
                session_storage=self.session_storage,
                cost_tracker=self.cost_tracker
            )
            
            # Set up callbacks
            pipeline.on_transcript = lambda text, is_final: asyncio.create_task(
                self._send_transcript(websocket, text, is_final)
            )
            pipeline.on_audio_chunk = lambda audio_bytes: asyncio.create_task(
                self._send_audio_chunk(websocket, audio_bytes)
            )
            pipeline.on_budget_warning = lambda utilization: asyncio.create_task(
                self._send_budget_warning(websocket, utilization)
            )
            pipeline.on_error = lambda error: asyncio.create_task(
                self._send_error(websocket, error)
            )
            
            # Connect to Deepgram
            deepgram_connection = await pipeline.connect_deepgram()
            
            # Store pipeline
            self.active_pipelines[session_id] = pipeline
            
            # Send ready message
            await websocket.send_json({
                "type": "ready",
                "session_id": session_id,
                "message": "LS1A pipeline ready"
            })
            
            # Main loop
            try:
                while True:
                    # Receive message
                    message = await websocket.receive()
                    
                    if "text" in message:
                        # Text message (control)
                        data = json.loads(message["text"])
                        await self._handle_control_message(websocket, pipeline, data)
                    
                    elif "bytes" in message:
                        # Binary message (audio chunk)
                        audio_data = message["bytes"]
                        await self._handle_audio_chunk(pipeline, audio_data)
                    
            except WebSocketDisconnect:
                print(f"[LS1A] WebSocket disconnected for session {session_id}")
            finally:
                # Cleanup
                await pipeline.close()
                if session_id in self.active_pipelines:
                    del self.active_pipelines[session_id]
                
                # End session
                self.session_storage.update(session_id, user_id, {"state": "ENDED"})
        
        except Exception as e:
            print(f"[LS1A] Pipeline error: {e}")
            await websocket.close(code=1011, reason=f"Pipeline error: {str(e)}")
    
    async def _handle_control_message(
        self,
        websocket: WebSocket,
        pipeline: LS1APipeline,
        data: dict
    ):
        """Handle control messages from client."""
        msg_type = data.get("type")
        
        if msg_type == "pause":
            # Pause session
            self.session_storage.update(
                pipeline.session.id,
                pipeline.session.user_id,
                {"state": "PAUSED"}
            )
            await websocket.send_json({"type": "session_paused"})
        
        elif msg_type == "resume":
            # Resume session
            self.session_storage.update(
                pipeline.session.id,
                pipeline.session.user_id,
                {"state": "LIVE"}
            )
            await websocket.send_json({"type": "session_resumed"})
        
        elif msg_type == "close":
            # Close session
            await pipeline.close()
            await websocket.close(code=1000, reason="Session closed by client")
    
    async def _handle_audio_chunk(self, pipeline: LS1APipeline, audio_data: bytes):
        """Handle audio chunk from client."""
        # Decode if base64 (common in WebSocket)
        try:
            # Try base64 decode
            audio_bytes = base64.b64decode(audio_data)
        except:
            # Assume raw bytes
            audio_bytes = audio_data
        
        # Send to Deepgram
        await pipeline.send_audio(audio_bytes)
    
    async def _send_transcript(self, websocket: WebSocket, text: str, is_final: bool):
        """Send transcript to client."""
        try:
            await websocket.send_json({
                "type": "transcript",
                "text": text,
                "is_final": is_final
            })
        except:
            pass  # WebSocket may be closed
    
    async def _send_audio_chunk(self, websocket: WebSocket, audio_bytes: bytes):
        """Send audio chunk to client."""
        try:
            # Encode as base64 for JSON
            audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
            await websocket.send_json({
                "type": "audio_chunk",
                "data": audio_b64,
                "format": "mp3"  # ElevenLabs returns MP3
            })
        except:
            pass  # WebSocket may be closed
    
    async def _send_budget_warning(self, websocket: WebSocket, utilization: float):
        """Send budget warning to client."""
        try:
            await websocket.send_json({
                "type": "budget_warning",
                "utilization": utilization,
                "message": f"Audio budget at {utilization:.1%}"
            })
            
            if utilization >= 1.0:
                await websocket.send_json({
                    "type": "session_paused",
                    "reason": "budget_exhausted"
                })
        except:
            pass  # WebSocket may be closed
    
    async def _send_error(self, websocket: WebSocket, error: Exception):
        """Send error to client."""
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(error)
            })
        except:
            pass  # WebSocket may be closed


# Global handler instance
_handler = LS1AWebSocketHandler()


async def ls1a_websocket_endpoint(
    websocket: WebSocket,
    session_id: str = Query(..., description="LiveSession ID"),
    user_id: str = Query(..., description="User ID for ownership validation")
):
    """
    WebSocket endpoint for LS1A audio pipeline.
    
    Usage:
        WS /ls1a/ws/{session_id}?user_id={user_id}
    
    Message Types:
        - audio_chunk (binary): PCM audio data (16-bit, 16kHz, mono)
        - pause (text): Pause session
        - resume (text): Resume session
        - close (text): Close session
    
    Response Types:
        - ready: Pipeline ready
        - transcript: Transcript update (partial or final)
        - audio_chunk: TTS audio chunk (base64 MP3)
        - budget_warning: Budget utilization warning
        - session_paused: Session paused (budget or manual)
        - error: Error message
    """
    await _handler.handle_websocket(websocket, session_id, user_id)

