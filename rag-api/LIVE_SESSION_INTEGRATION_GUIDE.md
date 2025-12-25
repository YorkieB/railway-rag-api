# Live Session Integration Guide

**Sprint 2.1: Enhanced Live Sessions**

This guide explains how to integrate the LiveSession API into your FastAPI application.

---

## Overview

The LiveSession API provides:
- Session lifecycle management (create, pause, resume, end)
- State machine with validated transitions
- Budget tracking per session
- Transcript management (partial and final)

---

## Components

### 1. LiveSession Model (`rag-api/models.py`)
- Already exists with state machine logic
- Fields: id, user_id, state, mode, timestamps, transcripts, budgets, etc.

### 2. LiveSessionStorage (`rag-api/live_session_storage.py`)
- Abstract interface for storage
- `InMemoryLiveSessionStorage` - Development/testing
- Can be extended with `FirestoreLiveSessionStorage` or `BigQueryLiveSessionStorage`

### 3. LiveSession API (`rag-api/live_session_api.py`)
- REST endpoints for session management
- FastAPI router ready to include

---

## Integration Steps

### Step 1: Include the Router

Add to your `app.py`:

```python
from fastapi import FastAPI
from rag_api.live_session_api import router as live_session_router

app = FastAPI()

# Include live session router
app.include_router(live_session_router)
```

### Step 2: Configure Storage (Optional)

For production, replace the default in-memory storage:

```python
from rag_api.live_session_storage import LiveSessionStorage
from rag_api.live_session_api import get_session_storage

# Create custom storage instance
class FirestoreLiveSessionStorage(LiveSessionStorage):
    # ... implement Firestore storage ...

# Override dependency
app.dependency_overrides[get_session_storage] = lambda: FirestoreLiveSessionStorage()
```

### Step 3: Use in Your WebSocket Handler

Example WebSocket integration:

```python
from fastapi import WebSocket, WebSocketDisconnect
from rag_api.live_session_storage import InMemoryLiveSessionStorage

storage = InMemoryLiveSessionStorage()

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
    # Get session (assume user_id from auth)
    user_id = "user123"  # Get from auth token
    session = storage.get(session_id, user_id)
    
    if not session:
        await websocket.close(code=1008, reason="Session not found")
        return
    
    # Transition to LIVE if in CONNECTING
    if session.state == "CONNECTING":
        storage.update(session_id, user_id, {"state": "LIVE"})
    
    try:
        while True:
            data = await websocket.receive_text()
            # Process audio/data
            # Update transcript_partial as needed
            storage.update(session_id, user_id, {
                "transcript_partial": updated_transcript
            })
    except WebSocketDisconnect:
        # End session
        storage.update(session_id, user_id, {"state": "ENDED"})
```

---

## API Endpoints

### POST `/live-sessions`
Create a new session.

**Request:**
```json
{
  "user_id": "user123",
  "mode": "LS1A",
  "recording_consent": false,
  "secrets_blurred": []
}
```

**Response:**
```json
{
  "session": {
    "id": "session-uuid",
    "user_id": "user123",
    "state": "CONNECTING",
    "mode": "LS1A",
    "started_at": "2025-12-25T10:00:00Z",
    ...
  }
}
```

### GET `/live-sessions/{session_id}?user_id={user_id}`
Get session status.

### GET `/live-sessions?user_id={user_id}&state={state}&limit={limit}`
List user sessions (optionally filtered by state).

### PUT `/live-sessions/{session_id}/pause?user_id={user_id}`
Pause a LIVE session.

### PUT `/live-sessions/{session_id}/resume?user_id={user_id}`
Resume a PAUSED session.

### PUT `/live-sessions/{session_id}?user_id={user_id}`
Update session fields (transcript, budget, etc.).

**Request:**
```json
{
  "transcript_partial": "Updated transcript...",
  "audio_minutes_used": 5.5,
  "daily_budget_remaining": {
    "audioMin": 54.5
  }
}
```

### DELETE `/live-sessions/{session_id}?user_id={user_id}`
End and delete a session.

---

## State Machine

### Valid Transitions
- `IDLE` → `CONNECTING` (on create)
- `CONNECTING` → `LIVE` (when WebSocket ready)
- `LIVE` → `PAUSED` (user pause or budget exhausted)
- `PAUSED` → `LIVE` (user resume)
- `LIVE`/`PAUSED` → `ENDED` (session termination)
- `ENDED` - Terminal (no transitions)

### State Transition Example
```python
session = storage.get(session_id, user_id)

# Check if transition is valid
if session.can_transition_to("LIVE"):
    # Perform transition
    if session.transition_to("LIVE"):
        # Save updated session
        storage.update(session_id, user_id, {"state": "LIVE"})
```

---

## Budget Integration

### Track Audio Minutes
```python
# During session, update audio minutes
current_minutes = session.audio_minutes_used + delta_minutes
remaining = session.daily_budget_remaining["audioMin"] - delta_minutes

storage.update(session_id, user_id, {
    "audio_minutes_used": current_minutes,
    "daily_budget_remaining": {
        "audioMin": remaining,
        "videoTokens": session.daily_budget_remaining["videoTokens"],
        "screenTokens": session.daily_budget_remaining["screenTokens"]
    }
})

# Check if budget exhausted
if remaining <= 0:
    # Auto-pause session
    storage.update(session_id, user_id, {"state": "PAUSED"})
```

### Budget Warnings
```python
# Check if at 80% threshold
budget_used = 1.0 - (remaining / initial_budget)
if budget_used >= 0.8:
    # Send warning via WebSocket
    await websocket.send_json({
        "type": "budget_warning",
        "message": f"Audio budget at {budget_used:.1%}"
    })
```

---

## Integration with Cost Tracker

Combine with Sprint 1.2 CostTracker:

```python
from rag_api.cost import CostTracker
from rag_api.live_session_storage import InMemoryLiveSessionStorage

cost_tracker = CostTracker()
session_storage = InMemoryLiveSessionStorage()

# During session
session = session_storage.get(session_id, user_id)
audio_minutes_used = calculate_audio_minutes()

# Track cost
cost_tracker.track_usage(
    user_id=session.user_id,
    audio_minutes=audio_minutes_used
)

# Update session
session_storage.update(session_id, user_id, {
    "audio_minutes_used": session.audio_minutes_used + audio_minutes_used,
    "daily_budget_remaining": {
        "audioMin": cost_tracker.get_budget_status(session.user_id)["audio_minutes"]["remaining"]
    }
})
```

---

## Example: Complete WebSocket Handler

```python
from fastapi import WebSocket, WebSocketDisconnect
from rag_api.live_session_storage import InMemoryLiveSessionStorage
from rag_api.cost import CostTracker

storage = InMemoryLiveSessionStorage()
cost_tracker = CostTracker()

@app.websocket("/live/ws/{session_id}")
async def live_session_websocket(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
    # Get user_id from auth (simplified)
    user_id = extract_user_id(websocket)
    
    # Get session
    session = storage.get(session_id, user_id)
    if not session:
        await websocket.close(code=1008, reason="Session not found")
        return
    
    # Transition to LIVE
    if session.state == "CONNECTING":
        storage.update(session_id, user_id, {"state": "LIVE"})
        await websocket.send_json({"type": "session_started", "session_id": session_id})
    
    try:
        while True:
            # Receive audio/data
            data = await websocket.receive()
            
            # Process audio (STT, LLM, TTS)
            # ... your audio pipeline ...
            
            # Update transcript
            if transcript_update:
                storage.update(session_id, user_id, {
                    "transcript_partial": transcript_update
                })
            
            # Track audio minutes
            audio_delta = calculate_audio_minutes()
            if audio_delta > 0:
                cost_tracker.track_usage(user_id, audio_minutes=audio_delta)
                session = storage.get(session_id, user_id)
                storage.update(session_id, user_id, {
                    "audio_minutes_used": session.audio_minutes_used + audio_delta
                })
                
                # Check budget
                budget_status = cost_tracker.get_budget_status(user_id)
                if budget_status["audio_minutes"]["utilization"] >= 0.8:
                    await websocket.send_json({
                        "type": "budget_warning",
                        "utilization": budget_status["audio_minutes"]["utilization"]
                    })
                
                if budget_status["audio_minutes"]["utilization"] >= 1.0:
                    storage.update(session_id, user_id, {"state": "PAUSED"})
                    await websocket.send_json({
                        "type": "session_paused",
                        "reason": "budget_exhausted"
                    })
                    break
            
    except WebSocketDisconnect:
        # End session
        storage.update(session_id, user_id, {"state": "ENDED"})
```

---

## Next Steps

1. **LS1A Audio Pipeline** (Sprint 2.1 continuation)
   - Integrate Deepgram WebSocket
   - Integrate OpenAI streaming LLM
   - Integrate ElevenLabs streaming TTS
   - Implement barge-in detection

2. **Production Storage**
   - Implement FirestoreLiveSessionStorage
   - Or BigQueryLiveSessionStorage
   - Add indexes for user_id and state

3. **WebSocket Enhancement**
   - Update existing WebSocket endpoints to use LiveSession
   - Handle state transitions
   - Send budget warnings

---

**Status:** ✅ Ready for integration

