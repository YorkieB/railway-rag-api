# Setup Guide - Real-Time AI Companion

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Docker (for containerized deployment)

## Local Development Setup

### 1. Install System Dependencies

**Windows:**
- **Recommended**: Use pipwin (easier, no Visual Studio required):
  ```bash
  pip install pipwin
  pipwin install pyaudio
  ```
- **Alternative**: Install Visual Studio C++ Build Tools (for compiling PyAudio from source)

**macOS:**
```bash
brew install portaudio
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install -y portaudio19-dev libasound2-dev libportaudio2 libportaudiocpp0 ffmpeg
```

### 2. Create Virtual Environment

```bash
cd companion-api
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
- `OPENAI_API_KEY` - Get from https://platform.openai.com/api-keys
- `DEEPGRAM_API_KEY` - Get from https://console.deepgram.com/
- `ELEVENLABS_API_KEY` - Get from https://elevenlabs.io/app/settings/api-keys

### 5. Run the Server

```bash
# Development mode
uvicorn main:app --host 0.0.0.0 --port 8080 --reload

# Or production mode
uvicorn main:app --host 0.0.0.0 --port 8080
```

The API will be available at `http://localhost:8080`

### 6. Test the API

```bash
# Health check
curl http://localhost:8080/health

# Create a session
curl -X POST http://localhost:8080/companion/session/create
```

## Docker Deployment

### Build Docker Image

```bash
docker build -t companion-api .
```

### Run Container

```bash
docker run -p 8080:8080 \
  -e OPENAI_API_KEY=your_key \
  -e DEEPGRAM_API_KEY=your_key \
  -e ELEVENLABS_API_KEY=your_key \
  companion-api
```

### Or use docker-compose

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  companion-api:
    build: .
    ports:
      - "8080:8080"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DEEPGRAM_API_KEY=${DEEPGRAM_API_KEY}
      - ELEVENLABS_API_KEY=${ELEVENLABS_API_KEY}
    volumes:
      - ./companion_memory:/app/companion_memory
```

Run:
```bash
docker-compose up
```

## Cloud Run Deployment

1. Build and push to Google Container Registry:
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/companion-api
```

2. Deploy to Cloud Run:
```bash
gcloud run deploy companion-api \
  --image gcr.io/YOUR_PROJECT_ID/companion-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=your_key,DEEPGRAM_API_KEY=your_key,ELEVENLABS_API_KEY=your_key \
  --port 8080
```

## Troubleshooting

### PyAudio Installation Issues

**Windows (Recommended Method):**
```bash
# Install pipwin first
pip install pipwin

# Then install pyaudio using pipwin (uses pre-built wheels, no compilation needed)
pipwin install pyaudio
```

**Windows (Alternative - Requires Visual Studio):**
```bash
# Install Visual Studio C++ Build Tools first, then:
pip install pyaudio
```

**macOS:**
```bash
brew install portaudio
pip install pyaudio
```

**Linux:**
```bash
sudo apt-get install portaudio19-dev
pip install pyaudio
```

### WebSocket Connection Issues

- Ensure Cloud Run is configured for WebSocket support
- Check firewall rules allow WebSocket connections
- Verify CORS settings in `main.py`

### Memory Issues

- ChromaDB data is stored in `./companion_memory/` by default
- Ensure write permissions for the directory
- For production, consider using a persistent volume

## Testing

See `TESTING.md` for detailed testing instructions.

