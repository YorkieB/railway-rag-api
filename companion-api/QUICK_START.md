# Quick Start Guide

## 1. Get API Keys

You need three API keys:
- **OpenAI**: https://platform.openai.com/api-keys (for GPT-4o)
- **Deepgram**: https://console.deepgram.com/ (for speech-to-text)
- **ElevenLabs**: https://elevenlabs.io/app/settings/api-keys (for text-to-speech)

## 2. Setup Environment

```bash
cd companion-api
cp .env.example .env
# Edit .env and add your API keys
```

## 3. Install & Run

**Windows:**
```bash
run_local.bat
```

**macOS/Linux:**
```bash
chmod +x run_local.sh
./run_local.sh
```

**Manual:**
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

## 4. Test

Open browser to your Next.js frontend (or test WebSocket directly):
```bash
# Health check
curl http://localhost:8080/health

# Create session
curl -X POST http://localhost:8080/companion/session/create
```

## 5. Frontend

Update `next-holo-ui` to point to your backend:
- Set `NEXT_PUBLIC_API_BASE=http://localhost:8080` in `.env.local`
- Or update Settings in UI

## Troubleshooting

- **PyAudio issues (Windows)**: 
  ```bash
  pip install pipwin
  pipwin install pyaudio
  ```
  See SETUP.md for more details
- **API errors**: Verify all keys are correct in `.env`
- **WebSocket errors**: Ensure backend is running and accessible

For detailed setup, see `SETUP.md`

