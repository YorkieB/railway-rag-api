# Testing Guide for Upload Functionality

## Prerequisites

1. Make sure the backend API is running:
   ```bash
   cd rag-api
   pip install -r requirements.txt
   python app.py
   ```

2. Set environment variables:
   ```bash
   export OPENAI_API_KEY=your_key  # Required: For embeddings and answer generation
   export CHROMADB_PATH=./rag_knowledge_base  # Optional
   ```

## Testing the Upload Endpoint

### Option 1: Using the Test Script

```bash
# Test health check and list documents
python test_upload.py

# Test uploading a file
python test_upload.py path/to/your/document.pdf "My Document Name"
```

### Option 2: Using curl

```bash
# List all documents
curl http://localhost:8080/documents

# Upload a document
curl -X POST http://localhost:8080/upload \
  -F "file=@your_document.pdf" \
  -F "document_name=My Research Paper"

# Delete a document
curl -X DELETE "http://localhost:8080/documents/My%20Research%20Paper"
```

### Option 3: Using Python requests

```python
import requests

# Upload a file
with open('document.pdf', 'rb') as f:
    files = {'file': ('document.pdf', f, 'application/pdf')}
    data = {'document_name': 'My Document'}
    response = requests.post('http://localhost:8080/upload', files=files, data=data)
    print(response.json())
```

## Testing the Streamlit UI

1. Start the Next.js frontend:
   ```bash
   cd next-holo-ui
   npm install
   npm run dev
   ```

2. Navigate to `http://localhost:8501`

3. Use the tabs:
   - **Ask Questions**: Query your knowledge base
   - **Upload Documents**: Upload new files
   - **Manage Documents**: View and delete documents

## Supported File Formats

- PDF (`.pdf`)
- Word Documents (`.docx`)
- Text Files (`.txt`)
- Markdown (`.md`, `.markdown`)

## Troubleshooting

### Error: "ChromaDB client not initialized"
- Make sure `OPENAI_API_KEY` environment variable is set (required for embeddings)
- Check that ChromaDB path is writable
- Try deleting the ChromaDB directory and recreating it

### Error: "OpenAI client initialization failed"
- Make sure `OPENAI_API_KEY` environment variable is set (required for embeddings and answer generation)

### Error: "Unsupported file type"
- Check that your file extension is supported
- Try renaming the file with a proper extension

### Upload takes too long
- Large documents are chunked and embedded, which takes time
- Check the API logs for progress
- Consider breaking large documents into smaller files


