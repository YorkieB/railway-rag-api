# Install Google Cloud SDK and Deploy

## Step 1: Install Google Cloud SDK

### Windows Installation:

1. **Download Google Cloud SDK:**
   - Go to: https://cloud.google.com/sdk/docs/install
   - Download the Windows installer
   - Run the installer and follow the prompts

2. **Or use PowerShell (if you have Chocolatey):**
   ```powershell
   choco install gcloudsdk
   ```

3. **After installation, restart your terminal/PowerShell**

## Step 2: Authenticate and Setup

```powershell
# Login to Google Cloud
gcloud auth login

# Set your project
gcloud config set project gen-lang-client-0118945483

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable bigquery.googleapis.com
```

## Step 3: Deploy Backend

```powershell
cd rag-api

# Deploy (replace YOUR_GEMINI_API_KEY with your actual key)
gcloud run deploy rag-api `
  --source . `
  --platform managed `
  --region us-central1 `
  --allow-unauthenticated `
  --port 8080 `
  --memory 2Gi `
  --timeout 300 `
  --set-env-vars GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

## Step 4: Get Backend URL and Deploy Frontend

```powershell
# Get the backend URL (save this!)
$BACKEND_URL = gcloud run services describe rag-api --region us-central1 --format 'value(status.url)'
Write-Host "Backend URL: $BACKEND_URL"

# Deploy frontend
cd ..\knowledge-base-ui

gcloud run deploy jarvis-ui `
  --source . `
  --platform managed `
  --region us-central1 `
  --allow-unauthenticated `
  --port 8080 `
  --memory 1Gi `
  --timeout 300 `
  --set-env-vars RAG_API_URL=$BACKEND_URL
```

## Alternative: Use Google Cloud Console (No SDK Needed)

If you prefer not to install the SDK, you can deploy via the web interface:

1. Go to: https://console.cloud.google.com/run
2. Click "Create Service"
3. Select "Deploy one revision from a source repository" or "Deploy from container image"
4. Follow the wizard

