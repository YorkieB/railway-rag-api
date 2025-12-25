# LS1A Audio Pipeline Integration Guide

**Sprint 2.1: LS1A Audio Pipeline**

This guide explains how to integrate the LS1A audio pipeline into your FastAPI application.

---

## Overview

The LS1A pipeline provides real-time voice interactions with:
- **Deepgram** for Speech-to-Text (STT)
- **OpenAI** for streaming LLM responses
- **ElevenLabs** for Text-to-Speech (TTS)
- **Barge-in detection** (<50ms response)
- **Budget enforcement** (audio minutes tracking)
- **Sub-1000ms latency** (target)

---

## Components

### 1. LS1APipeline (`rag-api/ls1a_pipeline.py`)
- Core audio processing pipeline
- Handles Deepgram, OpenAI, and ElevenLabs integration
- Manages barge-in detection
- Tracks audio minutes for budget

### 2. LS1AWebSocketHandler (`rag-api/ls1a_websocket.py`)
- WebSocket connection management
- Session state transitions
- Message routing

### 3. LS1A Router (`rag-api/ls1a_router.py`)
- FastAPI router for WebSocket endpoint

---

## Integration Steps

### Step 1: Install Dependencies

```bash
pip install -r rag-api/requirements-ls1a.txt
```

Or install individually:
```bash
pip install deepgram-sdk openai elevenlabs websockets
```

### Step 2: Set Environment Variables

```bash
export DEEPGRAM_API_KEY="your-deepgram-api-key"
export OPENAI_API_KEY="your-openai-api-key"
export ELEVENLABS_API_KEY="your-elevenlabs-api-key"
export ELEVENLABS_VOICE_ID="21m00Tcm4TlvDq8ikWAM"  # Optional, default voice
```

### Step 3: Include Router in app.py

```python
from fastapi import FastAPI
from rag_api.ls1a_router import router as ls1a_router
from rag_api.live_session_api import router as live_session_router

app = FastAPI()

# Include routers
app.include_router(live_session_router)  # For session management
app.include_router(ls1a_router, prefix="/ls1a")  # For WebSocket
```

### Step 4: Create Session Before Connecting

```python
# Client-side (JavaScript example)
const response = await fetch('/live-sessions', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_id: 'user123',
    mode: 'LS1A',
    recording_consent: false
  })
});

const { session } = await response.json();
const sessionId = session.id;

// Connect WebSocket
const ws = new WebSocket(`ws://localhost:8000/ls1a/ws/${sessionId}?user_id=user123`);
```

---

## WebSocket Protocol

### Client → Server Messages

#### Audio Chunk (Binary)
```
Raw PCM audio bytes (16-bit, 16kHz, mono)
```

#### Control Messages (Text JSON)
```json
// Pause session
{"type": "pause"}

// Resume session
{"type": "resume"}

// Close session
{"type": "close"}
```

### Server → Client Messages

#### Ready
```json
{
  "type": "ready",
  "session_id": "session-uuid",
  "message": "LS1A pipeline ready"
}
```

#### Transcript (Partial)
```json
{
  "type": "transcript",
  "text": "Hello, how are",
  "is_final": false
}
```

#### Transcript (Final)
```json
{
  "type": "transcript",
  "text": "Hello, how are you?",
  "is_final": true
}
```

#### Audio Chunk (TTS)
```json
{
  "type": "audio_chunk",
  "data": "base64-encoded-mp3-audio",
  "format": "mp3"
}
```

#### Budget Warning
```json
{
  "type": "budget_warning",
  "utilization": 0.85,
  "message": "Audio budget at 85.0%"
}
```

#### Session Paused
```json
{
  "type": "session_paused",
  "reason": "budget_exhausted"
}
```

#### Error
```json
{
  "type": "error",
  "message": "Error description"
}
```

---

## Client Implementation Example

### JavaScript/TypeScript

```typescript
class LS1AClient {
  private ws: WebSocket | null = null;
  private sessionId: string;
  private userId: string;
  private audioContext: AudioContext;
  private mediaStream: MediaStream | null = null;

  constructor(sessionId: string, userId: string) {
    this.sessionId = sessionId;
    this.userId = userId;
    this.audioContext = new AudioContext({ sampleRate: 16000 });
  }

  async connect(): Promise<void> {
    const url = `ws://localhost:8000/ls1a/ws/${this.sessionId}?user_id=${this.userId}`;
    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      console.log('LS1A WebSocket connected');
      this.startAudioCapture();
    };

    this.ws.onmessage = (event) => {
      if (typeof event.data === 'string') {
        this.handleTextMessage(JSON.parse(event.data));
      } else {
        // Binary audio (if needed)
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.ws.onclose = () => {
      console.log('WebSocket closed');
      this.stopAudioCapture();
    };
  }

  private handleTextMessage(message: any): void {
    switch (message.type) {
      case 'ready':
        console.log('Pipeline ready');
        break;
      
      case 'transcript':
        this.onTranscript(message.text, message.is_final);
        break;
      
      case 'audio_chunk':
        this.playAudio(message.data);
        break;
      
      case 'budget_warning':
        console.warn('Budget warning:', message.message);
        break;
      
      case 'session_paused':
        console.log('Session paused:', message.reason);
        break;
      
      case 'error':
        console.error('Error:', message.message);
        break;
    }
  }

  private async startAudioCapture(): Promise<void> {
    try {
      this.mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true
        }
      });

      const source = this.audioContext.createMediaStreamSource(this.mediaStream);
      const processor = this.audioContext.createScriptProcessor(4096, 1, 1);

      processor.onaudioprocess = (event) => {
        const inputData = event.inputBuffer.getChannelData(0);
        const pcmData = this.floatTo16BitPCM(inputData);
        
        // Send audio chunk to server
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
          this.ws.send(pcmData);
        }
      };

      source.connect(processor);
      processor.connect(this.audioContext.destination);
    } catch (error) {
      console.error('Error capturing audio:', error);
    }
  }

  private stopAudioCapture(): void {
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach(track => track.stop());
      this.mediaStream = null;
    }
  }

  private floatTo16BitPCM(float32Array: Float32Array): ArrayBuffer {
    const buffer = new ArrayBuffer(float32Array.length * 2);
    const view = new DataView(buffer);
    let offset = 0;
    for (let i = 0; i < float32Array.length; i++, offset += 2) {
      const s = Math.max(-1, Math.min(1, float32Array[i]));
      view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
    }
    return buffer;
  }

  private playAudio(base64Data: string): void {
    const audio = new Audio(`data:audio/mp3;base64,${base64Data}`);
    audio.play().catch(error => {
      console.error('Error playing audio:', error);
    });
  }

  private onTranscript(text: string, isFinal: boolean): void {
    // Update UI with transcript
    console.log(`Transcript (${isFinal ? 'final' : 'partial'}):`, text);
  }

  pause(): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: 'pause' }));
    }
  }

  resume(): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: 'resume' }));
    }
  }

  close(): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: 'close' }));
      this.ws.close();
    }
    this.stopAudioCapture();
  }
}
```

---

## Budget Enforcement

The pipeline automatically:
1. **Tracks audio minutes** during TTS playback
2. **Updates session** with `audio_minutes_used`
3. **Checks budget** via CostTracker
4. **Sends warnings** at 80% utilization
5. **Auto-pauses** at 100% utilization

### Budget Status

Check budget status via REST API:
```http
GET /budget/status?user_id={user_id}
```

Or via LiveSession:
```http
GET /live-sessions/{session_id}?user_id={user_id}
```

---

## Barge-In Detection

Barge-in is automatically handled:
1. **Deepgram VAD** detects when user starts speaking
2. **Pipeline cancels** TTS playback immediately
3. **Clears TTS queue** to prevent delayed audio
4. **Processes new transcript** from user

Target response time: **<50ms**

---

## Error Handling

The pipeline handles:
- **Deepgram connection errors** → Reconnect or notify client
- **OpenAI API errors** → Return error message to client
- **ElevenLabs errors** → Skip TTS, continue with text
- **Budget exhaustion** → Auto-pause session
- **WebSocket disconnects** → Cleanup and end session

---

## Performance Targets

- **STT Latency**: 300-600ms (partial text as user speaks)
- **LLM TTFT**: <500ms (time to first token)
- **TTS Latency**: 75-100ms (ElevenLabs Flash v2.5)
- **Total TTFT**: <1000ms (user finishes → audio starts)
- **Barge-in Response**: <50ms

---

## Next Steps

1. **Test with real audio** from browser
2. **Monitor latency** and optimize
3. **Add logging** for debugging
4. **Implement reconnection** logic
5. **Add metrics** collection

---

**Status:** ✅ Ready for integration and testing

