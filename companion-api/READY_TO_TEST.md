# ✅ Ready to Test!

## API Keys Configured

All three required API keys have been set up in the `.env` file:

- ✅ **OpenAI API Key**: Configured (for GPT-4o and embeddings)
- ✅ **Deepgram API Key**: Configured (for speech-to-text)
- ✅ **ElevenLabs API Key**: Configured (for text-to-speech)

## Next Steps

### 1. Test Locally (Backend)

**Windows:**
```bash
cd companion-api
run_local.bat
```

**Linux/macOS:**
```bash
cd companion-api
./run_local.sh
```

This will:
- Create virtual environment (if needed)
- Install dependencies (including pipwin for PyAudio on Windows)
- Start the FastAPI server on `http://localhost:8080`

### 2. Test the Health Endpoint

Once the server is running, open:
```
http://localhost:8080/health
```

You should see:
```json
{
  "status": "healthy",
  "service": "real-time-ai-companion",
  "active_sessions": 0
}
```

### 3. Test with Frontend

1. Make sure the Next.js frontend is running:
   ```bash
   cd next-holo-ui
   npm run dev
   ```

2. Open `http://localhost:3000` in your browser

3. Go to Settings and configure:
   - **Companion API Base URL**: `http://localhost:8080`
   - **Deepgram API Key**: (same as in .env)
   - **ElevenLabs API Key**: (same as in .env)
   - **ElevenLabs Voice ID**: `uju3wxzG5OhpWcoi3SMy` (Michael) or your custom voice

4. Click "Start Session" in the Companion Voice panel

### 4. Expected Behavior

- ✅ Backend connects to Deepgram
- ✅ Browser captures microphone audio
- ✅ Audio streams to backend → Deepgram
- ✅ Transcripts appear in real-time
- ✅ AI generates response (GPT-4o)
- ✅ ElevenLabs streams audio back
- ✅ You hear the AI companion speaking

## Troubleshooting

### "ModuleNotFoundError: No module named 'dotenv'"
- Run `pip install python-dotenv` in your virtual environment

### "DEEPGRAM_API_KEY environment variable is required"
- Make sure `.env` file exists in `companion-api/` directory
- Check that keys are on separate lines (no spaces around `=`)

### "Failed to connect to Deepgram"
- Verify Deepgram API key is correct
- Check internet connection
- Try testing Deepgram API directly

### "OpenAI API error"
- Verify OpenAI API key is correct
- Check your OpenAI account has credits/quota

### "ElevenLabs error"
- Verify ElevenLabs API key is correct
- Check your ElevenLabs account has credits

## Security Reminder

⚠️ The `.env` file contains your API keys and is in `.gitignore`. 
**DO NOT** commit it to version control or share it publicly.

## Ready! 🚀

Everything is configured and ready for testing. Start the backend server and begin testing the real-time AI companion!

