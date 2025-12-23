# Deployment Guide - Railway + Vercel

This guide covers deploying all three services of the Jarvis project using Railway (backend) and Vercel (frontend).

---

## Overview

**Deployment Strategy:**
- **Backend Services** (rag-api, companion-api) → **Railway**
- **Frontend** (next-holo-ui) → **Vercel**

**Why This Stack?**
- ✅ Zero vendor lock-in (ChromaDB is platform-agnostic)
- ✅ Simple deployment (GitHub → Auto-deploy)
- ✅ Cost-effective (~$25-40/month total)
- ✅ Better developer experience
- ✅ Automatic HTTPS and CDN

---

## Prerequisites

1. **GitHub Account** (for repository)
2. **Railway Account** - Sign up at https://railway.app
3. **Vercel Account** - Sign up at https://vercel.com
4. **API Keys Ready:**
   - Gemini API key
   - OpenAI API key
   - Deepgram API key (for companion-api)
   - ElevenLabs API key (for companion-api)

---

## Step 1: Deploy rag-api to Railway

### 1.1 Push Code to GitHub

```bash
# If not already in a repo
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### 1.2 Create Railway Project

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Authorize Railway to access your GitHub
5. Select your repository

### 1.3 Configure rag-api Service

1. Railway will detect the repository
2. Click "Add Service" → "GitHub Repo"
3. Select your repository
4. **Set Root Directory**: `rag-api` (important for monorepo)
   - Service Settings → Source → Root Directory → `rag-api`

### 1.4 Set Environment Variables

In Railway dashboard → rag-api service → Variables:

```
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
CHROMADB_PATH=/app/rag_knowledge_base
```

### 1.5 Deploy

Railway will automatically:
- Detect the Dockerfile
- Build the Docker image
- Deploy to a live URL
- Your service will be at: `https://rag-api-production-XXXX.up.railway.app`

### 1.6 Get Service URL

1. In Railway dashboard → rag-api service
2. Click "Settings" → "Generate Domain"
3. Copy the URL (e.g., `https://rag-api-production-XXXX.up.railway.app`)

---

## Step 2: Deploy companion-api to Railway

### 2.1 Add Second Service

1. In the same Railway project
2. Click "Add Service" → "GitHub Repo"
3. Select the same repository
4. **Set Root Directory**: `companion-api`

### 2.2 Set Environment Variables

```
OPENAI_API_KEY=your_openai_api_key
DEEPGRAM_API_KEY=your_deepgram_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_VOICE_ID=uju3wxzG5OhpWcoi3SMy
CHROMADB_PATH=/app/companion_memory
```

### 2.3 Deploy

Railway will automatically deploy. Get the URL from Settings → Generate Domain.

---

## Step 3: Deploy next-holo-ui to Vercel

### 3.1 Import Repository

1. Go to https://vercel.com
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Vercel will auto-detect Next.js

### 3.2 Configure Build Settings

Vercel auto-detects Next.js, but verify:
- **Framework Preset**: Next.js
- **Root Directory**: `next-holo-ui`
- **Build Command**: `npm run build` (auto-detected)
- **Output Directory**: `.next` (auto-detected)

### 3.3 Set Environment Variables

In Vercel dashboard → Project Settings → Environment Variables:

```
NEXT_PUBLIC_API_BASE=https://rag-api-production-XXXX.up.railway.app
```

**Important:** Replace with your actual Railway URL from Step 1.6.

### 3.4 Deploy

Click "Deploy". Vercel will:
- Build the Next.js app
- Deploy to a live URL
- Your app will be at: `https://your-project.vercel.app`

---

## Step 4: Configure CORS (if needed)

If you encounter CORS errors:

### rag-api CORS Configuration

Update `rag-api/app.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-project.vercel.app",  # Your Vercel URL
        "http://localhost:3000",  # Local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### companion-api CORS Configuration

Update `companion-api/main.py` similarly.

---

## Step 5: Verify Deployment

### 5.1 Test rag-api

```bash
# Health check
curl https://rag-api-production-XXXX.up.railway.app/health

# API docs
open https://rag-api-production-XXXX.up.railway.app/docs
```

### 5.2 Test companion-api

```bash
# Health check
curl https://companion-api-production-XXXX.up.railway.app/health
```

### 5.3 Test Frontend

1. Open your Vercel URL: `https://your-project.vercel.app`
2. Test document upload
3. Test RAG query
4. Test Gemini Live (if implemented)

---

## Persistent Storage

### ChromaDB on Railway

Railway automatically provides persistent volumes. ChromaDB data persists across deployments.

**Storage Paths:**
- rag-api: `/app/rag_knowledge_base`
- companion-api: `/app/companion_memory`

**No additional configuration needed** - Railway handles persistence automatically.

---

## Environment Variables Reference

### rag-api

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Gemini API key for answer generation |
| `OPENAI_API_KEY` | Yes | OpenAI API key for embeddings |
| `CHROMADB_PATH` | No | ChromaDB storage path (default: `/app/rag_knowledge_base`) |
| `PORT` | No | Port number (Railway sets automatically) |

### companion-api

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for LLM |
| `DEEPGRAM_API_KEY` | Yes | Deepgram API key for STT |
| `ELEVENLABS_API_KEY` | Yes | ElevenLabs API key for TTS |
| `ELEVENLABS_VOICE_ID` | No | Voice ID (default: `uju3wxzG5OhpWcoi3SMy`) |
| `ELEVENLABS_MODEL` | No | Model ID (default: `eleven_flash_v2_5`) |
| `CHROMADB_PATH` | No | ChromaDB storage path (default: `/app/companion_memory`) |
| `PORT` | No | Port number (Railway sets automatically) |

### next-holo-ui

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_API_BASE` | Yes | Backend API URL (Railway URL) |

---

## Monitoring & Logs

### Railway

- **Logs**: Railway dashboard → Service → Deployments → View Logs
- **Metrics**: Railway dashboard → Service → Metrics
- **Alerts**: Configure in Railway dashboard → Service → Settings

### Vercel

- **Logs**: Vercel dashboard → Project → Deployments → View Logs
- **Analytics**: Vercel dashboard → Project → Analytics
- **Real-time**: Vercel dashboard → Project → Real-time Logs

---

## Troubleshooting

### Build Fails on Railway

1. Check Dockerfile syntax
2. Verify all dependencies in `requirements.txt`
3. Check build logs in Railway dashboard
4. Ensure root directory is set correctly (`rag-api` or `companion-api`)

### Service Won't Start

1. Verify environment variables are set
2. Check that application uses `PORT` environment variable (Railway sets this)
3. Review application logs in Railway dashboard
4. Test locally first: `uvicorn app:app --host 0.0.0.0 --port $PORT`

### CORS Errors

1. Update CORS configuration in backend services
2. Add Vercel URL to `allow_origins` list
3. Redeploy backend services

### ChromaDB Not Persisting

1. Verify `CHROMADB_PATH` is set correctly
2. Railway volumes persist by default, but check path
3. Check logs for ChromaDB initialization errors

### Frontend Can't Connect to Backend

1. Verify `NEXT_PUBLIC_API_BASE` is set correctly
2. Check Railway service URLs are accessible
3. Test backend endpoints directly with `curl`
4. Check CORS configuration

---

## Cost Estimates

### Railway

- **Free Tier**: $5 credit/month
- **Hobby**: $5/month (after free tier)
- **Pro**: $20/month (for production)
- **Usage-based**: Additional charges for high traffic

### Vercel

- **Hobby**: Free (for personal projects)
- **Pro**: $20/month (for team projects)
- **Enterprise**: Custom pricing

**Total Estimated Cost**: ~$25-40/month for both services

---

## Next Steps

1. ✅ All services deployed
2. ✅ Environment variables configured
3. ✅ CORS configured (if needed)
4. 🚧 Set up custom domains (optional)
5. 🚧 Configure monitoring and alerts
6. 🚧 Set up CI/CD (optional - Railway/Vercel auto-deploy on push)

---

## Custom Domains (Optional)

### Railway Custom Domain

1. Railway dashboard → Service → Settings → Domains
2. Add custom domain
3. Configure DNS as instructed
4. Railway automatically provisions SSL certificate

### Vercel Custom Domain

1. Vercel dashboard → Project → Settings → Domains
2. Add custom domain
3. Configure DNS as instructed
4. Vercel automatically provisions SSL certificate

---

## CI/CD (Automatic Deployments)

Both Railway and Vercel automatically deploy on git push:

1. **Push to GitHub** → Automatic deployment
2. **Railway**: Detects changes, rebuilds, redeploys
3. **Vercel**: Detects changes, rebuilds, redeploys

**No additional configuration needed** - works out of the box!

---

## Rollback

### Railway

1. Railway dashboard → Service → Deployments
2. Find previous deployment
3. Click "Redeploy"

### Vercel

1. Vercel dashboard → Project → Deployments
2. Find previous deployment
3. Click "..." → "Promote to Production"

---

**Last Updated**: 2025-01-XX  
**Status**: Production Ready

