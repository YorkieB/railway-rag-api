# Personal Knowledge Base with RAG

## Overview
A complete Google Cloud-native RAG (Retrieval-Augmented Generation) system with:
- BigQuery Vector Search for document retrieval
- OpenAI GPT-4o for web search fallback
- Gemini for embeddings and answers
- Streamlit web interface

## Project Structure
```
project-backup/
├── rag-api/              # FastAPI backend service
│   ├── app.py           # Main API application
│   ├── Dockerfile       # Container configuration
│   └── requirements.txt # Python dependencies
└── knowledge-base-ui/   # Streamlit frontend
    ├── app.py          # Web interface
    ├── Dockerfile      # Container configuration  
    └── requirements.txt # Python dependencies
```

## Services
- **rag-api**: https://rag-api-883324649002.us-central1.run.app
- **knowledge-base-ui**: https://knowledge-base-ui-883324649002.us-central1.run.app

## Environment Variables

### For rag-api:
```bash
GEMINI_API_KEY=your_gemini_api_key
GCP_PROJECT=gen-lang-client-0118945483
OPENAI_API_KEY=your_openai_api_key
```

### For knowledge-base-ui:
```bash
RAG_API_URL=https://rag-api-883324649002.us-central1.run.app
```

## Local Development

### rag-api
```bash
cd rag-api
pip install -r requirements.txt
export GEMINI_API_KEY=your_key
export OPENAI_API_KEY=your_key
export GCP_PROJECT=gen-lang-client-0118945483
python app.py
```

### knowledge-base-ui
```bash
cd knowledge-base-ui
pip install -r requirements.txt
export RAG_API_URL=http://localhost:8080
streamlit run app.py
```

## Deployment to Cloud Run

### Deploy rag-api:
```bash
cd rag-api
gcloud run deploy rag-api \
  --source . \
  --region=us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=xxx,OPENAI_API_KEY=xxx,GCP_PROJECT=gen-lang-client-0118945483
```

### Deploy knowledge-base-ui:
```bash
cd knowledge-base-ui
gcloud run deploy knowledge-base-ui \
  --source . \
  --region=us-central1 \
  --allow-unauthenticated \
  --port=8080
```

## Features
- Hybrid search: Knowledge base + web search
- Vector similarity search using BigQuery
- Automatic fallback to GPT-4o for web queries
- Clean Streamlit UI with source citations
- Fully serverless on Google Cloud Run

## Database
BigQuery dataset: `gen-lang-client-0118945483.knowledge_base.documents`

Created: December 18, 2025
