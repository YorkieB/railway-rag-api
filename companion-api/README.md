# Real-Time AI Companion API

A real-time conversational AI companion built following the guidance document "Building a Real-Time AI Companion.txt".

## Features

- **Sub-800ms latency** from speech to response
- **Streaming TTS** with ElevenLabs Flash v2.5
- **Real-time STT** with Deepgram Nova-2
- **Persistent memory** with ChromaDB
- **Interruption handling** (barge-in support)
- **WebSocket API** for browser integration

## Setup

1. **Install system dependencies:**
   - **Windows**: `pip install pipwin && pipwin install pyaudio` (recommended)
   - **macOS**: `brew install portaudio`
   - **Linux**: `sudo apt-get install portaudio19-dev libasound2-dev`

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   **Note for Windows**: PyAudio should be installed via pipwin (see above) before installing other dependencies.

2. **Configure environment variables:**
   Create a `.env` file:
   ```
   OPENAI_API_KEY=sk-proj-...
   DEEPGRAM_API_KEY=...
   ELEVENLABS_API_KEY=...
   ```

3. **Run locally:**
   ```bash
   python main.py
   ```
   Or with uvicorn:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8080
   ```

## API Endpoints

### WebSocket
- `ws://localhost:8080/companion/ws/{session_id}` - Real-time companion interaction

### REST
- `POST /companion/session/create` - Create new session
- `GET /companion/memories?session_id={id}` - Get conversation memories
- `DELETE /companion/memories/{memory_id}?session_id={id}` - Delete memory
- `POST /companion/config` - Update configuration
- `GET /health` - Health check

## Architecture

- **AudioManager**: PyAudio input/output handling
- **MemoryManager**: ChromaDB vector storage
- **WebCompanion**: Browser-compatible companion orchestrator
- **main.py**: FastAPI WebSocket server

## Deployment

See `Dockerfile` for containerized deployment to Cloud Run.

## Notes

- For local microphone use, see `companion.py` (standalone script)
- For browser integration, use `companion_web.py` via WebSocket

