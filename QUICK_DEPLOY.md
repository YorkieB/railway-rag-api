# Quick Deploy to Google Cloud Run

## Option 1: Install Google Cloud SDK (Recommended)

### Install:
1. Download: https://cloud.google.com/sdk/docs/install
2. Run installer
3. Restart terminal

### Then run these commands:

```powershell
# 1. Login
gcloud auth login

# 2. Set project
gcloud config set project gen-lang-client-0118945483

# 3. Deploy Backend
cd rag-api
gcloud run deploy rag-api --source . --region us-central1 --allow-unauthenticated --port 8080 --memory 2Gi --set-env-vars GEMINI_API_KEY=YOUR_KEY_HERE

# 4. Get Backend URL (copy this!)
gcloud run services describe rag-api --region us-central1 --format 'value(status.url)'

# 5. Deploy Frontend (replace BACKEND_URL with the URL from step 4)
cd ..\knowledge-base-ui
gcloud run deploy jarvis-ui --source . --region us-central1 --allow-unauthenticated --port 8080 --memory 1Gi --set-env-vars RAG_API_URL=BACKEND_URL
```

## Option 2: Use Google Cloud Console (Web Interface)

### No installation needed!

1. **Go to Cloud Run Console:**
   https://console.cloud.google.com/run?project=gen-lang-client-0118945483

2. **Deploy Backend:**
   - Click "CREATE SERVICE"
   - Choose "Deploy one revision from a source repository"
   - Or upload your `rag-api` folder
   - Set environment variable: `GEMINI_API_KEY=your_key`
   - Click "CREATE"

3. **Deploy Frontend:**
   - Click "CREATE SERVICE" again
   - Upload `knowledge-base-ui` folder
   - Set environment variable: `RAG_API_URL=https://rag-api-xxxxx-uc.a.run.app`
   - Click "CREATE"

## Option 3: Use GitHub + Cloud Build (CI/CD)

1. Push code to GitHub
2. Connect Cloud Build to your repo
3. Auto-deploy on push

## What You Need:

- ✅ Your Gemini API Key
- ✅ Google Cloud account with billing enabled
- ✅ Project: `gen-lang-client-0118945483`

## Files Ready:
- ✅ `rag-api/Dockerfile` (fixed to use app_bigquery.py)
- ✅ `knowledge-base-ui/Dockerfile`
- ✅ Both `requirements.txt` files

