# V1 Deployment Checklist

## Pre-Deployment Steps

### 1. Install Dependencies

**Backend (rag-api):**
```bash
cd rag-api
pip install -r requirements.txt
playwright install chromium
```

**Frontend (next-holo-ui):**
```bash
cd next-holo-ui
npm install
```

### 2. Environment Variables

**Backend (rag-api):**
- `OPENAI_API_KEY` - Required for LLM, embeddings, and vision
- `COMPANION_API_URL` - Optional, defaults to `http://localhost:8081`
- `CHROMADB_PATH` - Optional, defaults to `./rag_knowledge_base`

**Companion-API:**
- `DEEPGRAM_API_KEY` - Required for STT
- `ELEVENLABS_API_KEY` - Required for TTS
- `OPENAI_API_KEY` - Required for LLM
- `ELEVENLABS_VOICE_ID` - Optional, defaults to `uju3wxzG5OhpWcoi3SMy`
- `ELEVENLABS_MODEL` - Optional, defaults to `eleven_flash_v2_5`

**Frontend (next-holo-ui):**
- `NEXT_PUBLIC_API_BASE` - Backend API URL (defaults to `http://localhost:8080`)
- `NEXT_PUBLIC_COMPANION_API_BASE` - Companion API URL (defaults to `http://localhost:8081`)

### 3. Start Services

**Backend (rag-api):**
```bash
cd rag-api
uvicorn app:app --host 0.0.0.0 --port 8080
```

**Companion-API:**
```bash
cd companion-api
uvicorn main:app --host 0.0.0.0 --port 8081
```

**Frontend (next-holo-ui):**
```bash
cd next-holo-ui
npm run dev
```

### 4. Verify Services

- [ ] Backend health check: `GET http://localhost:8080/health`
- [ ] Companion-API health check: `GET http://localhost:8081/health`
- [ ] Companion-API health via backend: `GET http://localhost:8080/companion-api/health`
- [ ] Frontend loads at `http://localhost:3000`

## Feature Testing

### Companion-API (Sprint 2.1)
- [ ] Create session: `POST /companion/session/create`
- [ ] WebSocket connection works
- [ ] Audio capture works
- [ ] STT transcription works
- [ ] TTS audio playback works
- [ ] Barge-in works
- [ ] Memory persistence works

### Screen Share Assist (Sprint 2.2)
- [ ] Create LS3 session: `POST /live-sessions` with `mode: "LS3"`
- [ ] WebSocket connection works
- [ ] Frame capture works
- [ ] Secret detection works
- [ ] Vision analysis works
- [ ] Budget tracking works
- [ ] Pause/resume works

### Browser Automation (Sprint 2.3-2.4)
- [ ] Create browser session: `POST /browser/sessions`
- [ ] Navigate works: `POST /browser/sessions/{id}/navigate`
- [ ] AX Tree extraction works: `GET /browser/sessions/{id}/ax-tree`
- [ ] Screenshot works: `GET /browser/sessions/{id}/screenshot`
- [ ] Click action works: `POST /browser/sessions/{id}/actions/click`
- [ ] Type action works: `POST /browser/sessions/{id}/actions/type`
- [ ] Extract action works: `POST /browser/sessions/{id}/actions/extract`
- [ ] Plan-execute works: `POST /browser/sessions/{id}/actions/plan-execute`
- [ ] Safety guardrails block restricted domains
- [ ] Uncertainty protocol triggers correctly

### PDF Export (Sprint 2.6)
- [ ] Export conversation: `POST /export/conversation`
- [ ] Export query results: `POST /export/query-results`
- [ ] PDFs download correctly
- [ ] PDFs contain all expected content

## Frontend Testing

- [ ] CompanionVoice component loads
- [ ] ScreenSharePanel component loads
- [ ] BrowserPanel component loads
- [ ] ExportPanel component loads
- [ ] All components integrated in main page
- [ ] WebSocket connections work
- [ ] Error handling works
- [ ] Loading states display correctly

## Production Deployment

### Backend (Railway/Container)
- [ ] Set environment variables
- [ ] Install Playwright browsers in container
- [ ] Configure CORS for production domains
- [ ] Set up persistent storage for ChromaDB
- [ ] Configure health check endpoints

### Frontend (Vercel/Next.js Host)
- [ ] Set `NEXT_PUBLIC_API_BASE` environment variable
- [ ] Set `NEXT_PUBLIC_COMPANION_API_BASE` environment variable
- [ ] Build succeeds: `npm run build`
- [ ] Deploy to production

### Companion-API (Separate Service)
- [ ] Deploy as separate service
- [ ] Set all required environment variables
- [ ] Configure CORS
- [ ] Set up persistent storage for ChromaDB memory

## Post-Deployment

- [ ] All endpoints accessible
- [ ] WebSocket connections work
- [ ] No CORS errors
- [ ] All features functional
- [ ] Performance acceptable
- [ ] Error handling works
- [ ] Logging configured

## Known Limitations

1. **Playwright Browsers**: Must be installed separately (`playwright install chromium`)
2. **Companion-API**: Requires separate deployment/service
3. **Memory Storage**: In-memory for MVP (sessions don't persist across restarts)
4. **Secret Detection**: Basic regex-based (full OCR-based detection deferred)
5. **Vision Budget**: Default 50K tokens/day (configurable per session)

## Troubleshooting

### Playwright Issues
- Ensure Chromium is installed: `playwright install chromium`
- Check browser path in container/environment

### WebSocket Issues
- Verify CORS is configured correctly
- Check WebSocket URL format (ws:// vs wss://)
- Verify firewall/network allows WebSocket connections

### Vision API Issues
- Check OpenAI API key is set
- Verify API quota/billing
- Check vision token budget limits

### Companion-API Issues
- Verify all API keys are set (Deepgram, ElevenLabs, OpenAI)
- Check WebSocket connection
- Verify audio permissions in browser

