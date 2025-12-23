# Testing Guide - Real-Time AI Companion

## Manual Testing Checklist

### 1. Environment Setup
- [ ] All API keys configured in `.env`
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Server starts without errors

### 2. Health Check
```bash
curl http://localhost:8080/health
```
Expected: `{"status": "healthy", "service": "real-time-ai-companion", "active_sessions": 0}`

### 3. Session Creation
```bash
curl -X POST http://localhost:8080/companion/session/create
```
Expected: JSON with `session_id` and `status: "created"`

### 4. WebSocket Connection
- Open browser console
- Connect to `ws://localhost:8080/companion/ws/{session_id}`
- Should receive `{"type": "session_ready", "status": "connected"}`

### 5. Audio Streaming Test
- Grant microphone permissions
- Start session in UI
- Speak into microphone
- Verify:
  - [ ] Transcripts appear in real-time
  - [ ] AI response is generated
  - [ ] Audio playback works
  - [ ] Latency is displayed

### 6. Interruption Test
- Start a conversation
- While AI is speaking, interrupt by speaking again
- Verify:
  - [ ] AI stops speaking immediately
  - [ ] Interruption indicator appears
  - [ ] New response starts after interruption

### 7. Memory Persistence Test
- Have a conversation
- Stop and restart session
- Reference previous conversation topic
- Verify:
  - [ ] AI remembers previous conversation
  - [ ] Memory context is retrieved

### 8. Latency Measurement
- Monitor TTFT (Time to First Token)
- Target: < 800ms
- Verify latency metrics display correctly

## Automated Testing

### Unit Tests (To be implemented)
```bash
pytest tests/
```

### Integration Tests
```bash
pytest tests/integration/
```

## Performance Benchmarks

### Target Metrics
- **TTFT**: < 800ms
- **Total Response Time**: < 3s for short responses
- **Memory Retrieval**: < 100ms
- **Audio Streaming Latency**: < 50ms per chunk

### Measuring Latency

1. **TTFT (Time to First Token)**
   - Measure from user speech end to first LLM token
   - Logged in backend and displayed in UI

2. **Total Response Time**
   - Measure from user speech end to audio playback complete
   - Includes: STT + LLM + TTS + network

3. **Memory Retrieval Time**
   - Measure ChromaDB query time
   - Should be < 100ms for typical queries

## Load Testing

### WebSocket Connections
```bash
# Test with multiple concurrent connections
for i in {1..10}; do
  curl -X POST http://localhost:8080/companion/session/create &
done
```

### Stress Test
- Use tools like `k6` or `artillery` for WebSocket load testing
- Monitor:
  - Connection stability
  - Memory usage
  - CPU usage
  - Error rates

## Error Scenarios

### Test Cases
1. **API Key Invalid**
   - Remove or invalidate API key
   - Verify graceful error handling

2. **Network Interruption**
   - Disconnect network during conversation
   - Verify reconnection logic

3. **Microphone Permission Denied**
   - Deny microphone access
   - Verify error message

4. **Backend Unavailable**
   - Stop backend server
   - Verify frontend error handling

5. **WebSocket Disconnect**
   - Force disconnect WebSocket
   - Verify cleanup and reconnection

## Debugging

### Enable Debug Logging
Set environment variable:
```bash
export DEBUG=1
```

### View Logs
```bash
# Backend logs
tail -f logs/companion.log

# Or if using uvicorn
uvicorn main:app --log-level debug
```

### Common Issues

1. **"Deepgram connection failed"**
   - Check API key
   - Verify network connectivity
   - Check Deepgram service status

2. **"OpenAI API error"**
   - Verify API key and quota
   - Check rate limits
   - Verify model availability

3. **"ElevenLabs streaming error"**
   - Check API key
   - Verify voice ID exists
   - Check model availability

4. **"ChromaDB error"**
   - Check write permissions
   - Verify disk space
   - Check OpenAI embedding API key

## Test Data

### Sample Conversations
1. **Greeting**: "Hello, how are you?"
2. **Question**: "What's the weather like?"
3. **Memory Test**: "Remember that I like coffee" → later: "What do I like?"
4. **Interruption**: Start speaking while AI is responding

