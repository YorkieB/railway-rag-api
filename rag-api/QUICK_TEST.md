# Quick Testing Guide

## Step 1: Test Backend API Locally

### Prerequisites Check
```powershell
# Check Python is installed
python --version

# Check pip is available
pip --version

# Navigate to backend directory
cd rag-api
```

### Install Dependencies
```powershell
pip install -r requirements.txt
```

### Set Environment Variables
```powershell
# Set your API keys (replace with actual values)
$env:OPENAI_API_KEY = "your_openai_api_key"
$env:CHROMADB_PATH = "./rag_knowledge_base"  # Optional

# Verify it's set
echo $env:OPENAI_API_KEY
```

### Start the Backend Server
```powershell
python -m uvicorn app:app --host 0.0.0.0 --port 8080
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080
```

### Test the Health Endpoint
Open a new terminal and run:
```powershell
# Test health endpoint
curl http://localhost:8080/

# Or use PowerShell
Invoke-WebRequest -Uri http://localhost:8080/ -Method GET
```

Expected response:
```json
{"message": "RAG Knowledge Base API - ChromaDB Edition", "endpoints": {...}}
```

### Test List Documents (should be empty initially)
```powershell
curl http://localhost:8080/documents
# Or
Invoke-WebRequest -Uri http://localhost:8080/documents -Method GET
```

### Test Upload Endpoint
```powershell
# Using the test document
python test_upload.py test_document.txt "Test Document"

# Or using curl
curl -X POST http://localhost:8080/upload `
  -F "file=@test_document.txt" `
  -F "document_name=Test Document"
```

Expected response:
```json
{
  "status": "success",
  "message": "Document 'Test Document' uploaded successfully",
  "document_name": "Test Document",
  "chunks_created": 2,
  "total_chars": 450
}
```

### Verify Upload Worked
```powershell
# List documents again
curl http://localhost:8080/documents
```

You should see your uploaded document!

### Test Query Endpoint
```powershell
# Query the knowledge base
curl -X POST http://localhost:8080/query `
  -H "Content-Type: application/json" `
  -d '{\"question\": \"What does the test document contain?\"}'
```

---

## Step 2: Test Streamlit UI Locally

### Open a New Terminal
Keep the backend running in the first terminal.

### Navigate to UI Directory
```powershell
cd ..\knowledge-base-ui
```

### Install Dependencies
```powershell
pip install -r requirements.txt
```

### Set Environment Variable (Optional)
```powershell
# If testing locally, point to localhost
$env:RAG_API_URL = "http://localhost:8080"
```

### Start Streamlit
```powershell
streamlit run app.py
```

Streamlit will automatically open your browser at `http://localhost:8501`

### Test the UI

1. **Upload Documents Tab:**
   - Click "Upload Documents" tab
   - Click "Choose a file to upload"
   - Select `test_document.txt` (or any PDF/DOCX/TXT/MD file)
   - Optionally enter a document name
   - Click "Upload Document"
   - Wait for success message

2. **Manage Documents Tab:**
   - Click "Manage Documents" tab
   - Click "Refresh Document List"
   - You should see your uploaded document(s)
   - Try deleting a document (optional)

3. **Ask Questions Tab:**
   - Click "Ask Questions" tab
   - Enter a question like "What does the test document contain?"
   - Click "Search"
   - You should see an answer with sources

---

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (need 3.8+)
- Check dependencies: `pip list`
- Check environment variables are set (OPENAI_API_KEY)
- Check ChromaDB path is writable

### Upload fails
- Check file format is supported (PDF, DOCX, TXT, MD)
- Check file isn't corrupted
- Check OpenAI API key is valid (for embeddings)
- Check OpenAI API key is valid (for embeddings and answer generation)

### UI can't connect to backend
- Make sure backend is running on port 8080
- Check `RAG_API_URL` environment variable
- Try `http://localhost:8080` instead of the Cloud Run URL

### No documents found
- Upload a document first
- Check ChromaDB collection exists (created automatically)
- Check documents were actually inserted

---

## Success Indicators

✅ Backend starts without errors
✅ Health endpoint returns 200 OK
✅ Upload endpoint accepts files and returns success
✅ Documents appear in list endpoint
✅ Query endpoint returns answers with sources
✅ Streamlit UI loads and connects to backend
✅ Can upload files through UI
✅ Can query through UI and get answers


