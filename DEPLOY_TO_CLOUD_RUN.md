# Deploy JARVIS to Google Cloud Run

This guide will help you deploy both the **RAG API Backend** and **Streamlit Frontend** to Google Cloud Run.

## Prerequisites

1. **Google Cloud Account** with billing enabled
2. **Google Cloud SDK (gcloud)** installed: https://cloud.google.com/sdk/docs/install
3. **Docker** installed (for local testing): https://www.docker.com/get-started
4. **Project ID**: `gen-lang-client-0118945483` (already configured)

## Step 1: Initial Setup

### 1.1 Authenticate with Google Cloud

```bash
gcloud auth login
gcloud config set project gen-lang-client-0118945483
```

### 1.2 Enable Required APIs

```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable bigquery.googleapis.com
```

## Step 2: Deploy RAG API Backend

### 2.1 Navigate to Backend Directory

```bash
cd rag-api
```

### 2.2 Set Environment Variables

Create a `.env` file or set these in Cloud Run:

```bash
# Required environment variables
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json  # Optional if using service account
```

### 2.3 Build and Deploy Backend

**Option A: Deploy from Source (Recommended)**

```bash
# Build and deploy in one command
gcloud run deploy rag-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --timeout 300 \
  --set-env-vars GEMINI_API_KEY=your_gemini_api_key_here \
  --service-account your-service-account@gen-lang-client-0118945483.iam.gserviceaccount.com
```

**Option B: Build Docker Image First**

```bash
# Build the image
gcloud builds submit --tag gcr.io/gen-lang-client-0118945483/rag-api

# Deploy the image
gcloud run deploy rag-api \
  --image gcr.io/gen-lang-client-0118945483/rag-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --timeout 300 \
  --set-env-vars GEMINI_API_KEY=your_gemini_api_key_here
```

### 2.4 Get Backend URL

After deployment, note the service URL:
```bash
gcloud run services describe rag-api --region us-central1 --format 'value(status.url)'
```

Example output: `https://rag-api-xxxxx-uc.a.run.app`

## Step 3: Deploy Streamlit Frontend

### 3.1 Navigate to Frontend Directory

```bash
cd ../knowledge-base-ui
```

### 3.2 Update API URL in Code (if needed)

The frontend uses `RAG_API_URL` environment variable. Update `app.py` line 17 if you want to hardcode it, or set it as an environment variable.

### 3.3 Build and Deploy Frontend

**Option A: Deploy from Source**

```bash
gcloud run deploy jarvis-ui \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 1Gi \
  --timeout 300 \
  --set-env-vars RAG_API_URL=https://rag-api-xxxxx-uc.a.run.app
```

**Option B: Build Docker Image First**

```bash
# Build the image
gcloud builds submit --tag gcr.io/gen-lang-client-0118945483/jarvis-ui

# Deploy the image
gcloud run deploy jarvis-ui \
  --image gcr.io/gen-lang-client-0118945483/jarvis-ui \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 1Gi \
  --timeout 300 \
  --set-env-vars RAG_API_URL=https://rag-api-xxxxx-uc.a.run.app
```

### 3.4 Get Frontend URL

```bash
gcloud run services describe jarvis-ui --region us-central1 --format 'value(status.url)'
```

## Step 4: Service Account Setup (for BigQuery Access)

### 4.1 Create Service Account (if not exists)

```bash
gcloud iam service-accounts create jarvis-sa \
  --display-name="JARVIS Service Account" \
  --description="Service account for JARVIS RAG system"
```

### 4.2 Grant BigQuery Permissions

```bash
gcloud projects add-iam-policy-binding gen-lang-client-0118945483 \
  --member="serviceAccount:jarvis-sa@gen-lang-client-0118945483.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding gen-lang-client-0118945483 \
  --member="serviceAccount:jarvis-sa@gen-lang-client-0118945483.iam.gserviceaccount.com" \
  --role="roles/bigquery.jobUser"
```

### 4.3 Update Backend Deployment with Service Account

```bash
gcloud run services update rag-api \
  --service-account=jarvis-sa@gen-lang-client-0118945483.iam.gserviceaccount.com \
  --region us-central1
```

## Step 5: Verify Deployment

### 5.1 Test Backend

```bash
# Get the backend URL
BACKEND_URL=$(gcloud run services describe rag-api --region us-central1 --format 'value(status.url)')

# Test health endpoint
curl $BACKEND_URL/

# Test query endpoint
curl -X POST $BACKEND_URL/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this system?"}'
```

### 5.2 Test Frontend

Open the frontend URL in your browser:
```bash
FRONTEND_URL=$(gcloud run services describe jarvis-ui --region us-central1 --format 'value(status.url)')
echo "Frontend URL: $FRONTEND_URL"
```

## Step 6: Update Frontend with Backend URL

After deploying the backend, update the frontend's `RAG_API_URL`:

```bash
gcloud run services update jarvis-ui \
  --set-env-vars RAG_API_URL=https://rag-api-xxxxx-uc.a.run.app \
  --region us-central1
```

## Quick Deployment Script

Save this as `deploy.sh`:

```bash
#!/bin/bash

# Set your variables
PROJECT_ID="gen-lang-client-0118945483"
REGION="us-central1"
GEMINI_API_KEY="your_gemini_api_key_here"

# Enable APIs
gcloud services enable cloudbuild.googleapis.com run.googleapis.com bigquery.googleapis.com --project=$PROJECT_ID

# Deploy Backend
echo "Deploying RAG API Backend..."
cd rag-api
gcloud run deploy rag-api \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --timeout 300 \
  --set-env-vars GEMINI_API_KEY=$GEMINI_API_KEY \
  --project=$PROJECT_ID

# Get Backend URL
BACKEND_URL=$(gcloud run services describe rag-api --region $REGION --format 'value(status.url)' --project=$PROJECT_ID)
echo "Backend URL: $BACKEND_URL"

# Deploy Frontend
echo "Deploying JARVIS UI..."
cd ../knowledge-base-ui
gcloud run deploy jarvis-ui \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8080 \
  --memory 1Gi \
  --timeout 300 \
  --set-env-vars RAG_API_URL=$BACKEND_URL \
  --project=$PROJECT_ID

# Get Frontend URL
FRONTEND_URL=$(gcloud run services describe jarvis-ui --region $REGION --format 'value(status.url)' --project=$PROJECT_ID)
echo "Frontend URL: $FRONTEND_URL"
echo "Deployment complete!"
```

Make it executable and run:
```bash
chmod +x deploy.sh
./deploy.sh
```

## Troubleshooting

### Common Issues

1. **Build fails**: Check Dockerfile syntax and requirements.txt
2. **Service won't start**: Check logs: `gcloud run services logs read rag-api --region us-central1`
3. **BigQuery access denied**: Verify service account permissions
4. **CORS errors**: Backend CORS is configured, but verify frontend URL is allowed
5. **API calls fail**: Check `RAG_API_URL` environment variable in frontend

### View Logs

```bash
# Backend logs
gcloud run services logs read rag-api --region us-central1 --limit 50

# Frontend logs
gcloud run services logs read jarvis-ui --region us-central1 --limit 50
```

### Update Services

```bash
# Update backend
cd rag-api
gcloud run deploy rag-api --source . --region us-central1

# Update frontend
cd ../knowledge-base-ui
gcloud run deploy jarvis-ui --source . --region us-central1
```

## Cost Optimization

- Use **min instances = 0** to scale to zero when not in use
- Set **max instances** based on expected traffic
- Use **CPU allocation** only when processing requests

```bash
gcloud run services update rag-api \
  --min-instances 0 \
  --max-instances 10 \
  --cpu-throttling \
  --region us-central1
```

## Security Notes

1. **API Keys**: Store in Secret Manager, not environment variables
2. **Authentication**: Consider requiring authentication for production
3. **CORS**: Restrict CORS origins to your frontend domain
4. **Service Account**: Use least-privilege IAM roles

## Next Steps

1. Set up custom domain (optional)
2. Configure Cloud CDN for faster global access
3. Set up monitoring and alerts
4. Configure auto-scaling policies
5. Set up CI/CD pipeline for automatic deployments

