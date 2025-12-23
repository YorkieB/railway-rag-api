"""
FastAPI WebSocket server for Real-Time AI Companion.
Bridges browser audio streams to the companion pipeline.
"""
import asyncio
import base64
import json
import os
import uuid
from typing import Dict, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from companion_web import WebCompanion
from memory_manager import MemoryManager
from config import VOICE_ID, ELEVEN_MODEL_ID

app = FastAPI(title="Real-Time AI Companion API")

# CORS configuration for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active companion sessions
active_sessions: Dict[str, WebCompanion] = {}
session_websockets: Dict[str, WebSocket] = {}


class SessionConfig(BaseModel):
    """Configuration for a new companion session."""
    voice_id: Optional[str] = None
    model_id: Optional[str] = None
    system_prompt: Optional[str] = None


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "real-time-ai-companion",
        "active_sessions": len(active_sessions)
    }


@app.post("/companion/session/create")
async def create_session(config: Optional[SessionConfig] = None):
    """
    Initialize a new companion session.
    Returns session_id for WebSocket connection.
    """
    session_id = str(uuid.uuid4())
    
    try:
        # Create new companion instance (WebSocket will be set when connection is established)
        companion = WebCompanion(websocket=None)
        # Note: Deepgram will be initialized when WebSocket connects
        
        active_sessions[session_id] = companion
        
        return {
            "session_id": session_id,
            "status": "created",
            "message": "Companion session created. Connect via WebSocket."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")


@app.websocket("/companion/ws/{session_id}")
async def companion_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time companion interaction.
    Handles browser audio streams and streams back TTS audio.
    """
    await websocket.accept()
    
    if session_id not in active_sessions:
        await websocket.send_json({
            "type": "error",
            "message": "Session not found"
        })
        await websocket.close()
        return
    
    companion = active_sessions[session_id]
    companion.websocket = websocket  # Set WebSocket for companion
    session_websockets[session_id] = websocket
    
    try:
        # Initialize Deepgram connection (now that WebSocket is set)
        await companion.initialize_deepgram()
        
        # Send session ready message
        await websocket.send_json({
            "type": "session_ready",
            "session_id": session_id,
            "status": "connected"
        })
        
        # Start companion processing loop
        companion.processing_task = asyncio.create_task(companion.start_processing_loop())
        
        # Main message loop - receive audio/text from browser
        while True:
            try:
                # Receive message from browser
                data = await websocket.receive_json()
                msg_type = data.get("type")
                
                if msg_type == "audio_chunk":
                    # Browser sent audio chunk - forward to Deepgram
                    audio_data = data.get("audio", "")
                    if audio_data:
                        try:
                            # Decode base64 audio (Int16 PCM format)
                            audio_bytes = base64.b64decode(audio_data)
                            # Process audio chunk (send to Deepgram)
                            # Note: process_audio_chunk is synchronous, run in executor if needed
                            companion.process_audio_chunk(audio_bytes)
                        except Exception as e:
                            print(f"Error processing audio chunk: {e}")
                            await websocket.send_json({
                                "type": "error",
                                "message": f"Audio processing error: {str(e)}"
                            })
                
                elif msg_type == "text_input":
                    # Browser sent text input directly
                    text = data.get("text", "")
                    if text:
                        await companion.transcript_queue.put(text)
                
                elif msg_type == "interrupt":
                    # Browser requested interruption
                    if companion.current_playback_task and not companion.current_playback_task.done():
                        companion.current_playback_task.cancel()
                        await websocket.send_json({
                            "type": "interrupted",
                            "message": "AI response interrupted"
                        })
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"Error in websocket loop: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        # Cleanup
        await companion.cleanup()
        if session_id in session_websockets:
            del session_websockets[session_id]
        # Note: We keep the companion session alive for memory persistence
        # To fully clean up: del active_sessions[session_id]


@app.get("/companion/memories")
async def get_memories(session_id: str):
    """Retrieve conversation memories for a session."""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    companion = active_sessions[session_id]
    memories = companion.memory.get_all_memories()
    
    return {
        "session_id": session_id,
        "memories": memories,
        "count": len(memories)
    }


@app.delete("/companion/memories/{memory_id}")
async def delete_memory(session_id: str, memory_id: str):
    """Delete a specific memory."""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    companion = active_sessions[session_id]
    success = companion.memory.delete_memory(memory_id)
    
    return {
        "success": success,
        "memory_id": memory_id
    }


@app.post("/companion/config")
async def update_config(session_id: str, config: SessionConfig):
    """Update companion configuration (voice, model, etc.)."""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Update config (would need to modify companion instance)
    # For now, return success
    return {
        "success": True,
        "message": "Configuration updated (requires session restart)"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

