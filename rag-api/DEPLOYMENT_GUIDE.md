# Railway.app Deployment Guide for rag-api

## Quick Start - Deploy to Railway in 5 minutes

### Prerequisites

- GitHub account (recommended) or Railway CLI
- Railway account at https://railway.app
- API keys ready:
  - `OPENAI_API_KEY` - OpenAI API key (for embeddings and answer generation)

### Option 1: Deploy via GitHub (Recommended)

1. **Push Code to GitHub**
   ```bash
   # If not already in a repo
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

2. **Deploy to Railway**
   - Go to https://railway.app
   - Click "New Project" → "Deploy from GitHub"
   - Authorize Railway and select your repository
   - Railway will automatically:
     - Detect the Dockerfile in `rag-api/` directory
     - Build the Docker image
     - Deploy to a live URL
   - Your app will be live at: `https://YOUR_APP_NAME.railway.app`

3. **Configure Environment Variables**
   - In Railway dashboard → Service → Variables
   - Add required variables:
     - `OPENAI_API_KEY` - Your OpenAI API key (for embeddings and answer generation)
     - `CHROMADB_PATH` - Optional (default: `/app/rag_knowledge_base`)
   - Railway will automatically redeploy when variables are added

4. **Configure Root Directory (if needed)**
   - If deploying from monorepo, set root directory:
   - Service Settings → Source → Root Directory → `rag-api`

### Option 2: Deploy via Railway CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Link to existing service or create new
railway link

# Deploy
railway up
```

### Option 3: Deploy from Local Directory

1. Go to https://railway.app
2. Create new project → "Empty Project"
3. Add service → "GitHub Repo" or "Empty Service"
4. If empty service, use Railway CLI to deploy:
   ```bash
   railway up
   ```

## Environment Variables

### Required

- `OPENAI_API_KEY` - OpenAI API key (for embeddings and answer generation)

### Optional

- `CHROMADB_PATH` - ChromaDB storage path (default: `/app/rag_knowledge_base`)
- `PORT` - Port number (Railway sets this automatically via `$PORT`)

## Persistent Storage

Railway automatically provides persistent volumes for your service. ChromaDB data will persist across deployments.

**Storage Location:**
- Default: `/app/rag_knowledge_base` (inside container)
- Railway volumes persist data between deployments
- No additional configuration needed

## Application Files

- `app.py` - FastAPI application (main entry point)
- `requirements.txt` - Python dependencies
- `Dockerfile` - Docker configuration
- `.dockerignore` - Files to exclude from Docker build (optional)

## Deployment Status

After deployment, your FastAPI app will be accessible at:
- **URL**: `https://YOUR_SERVICE_NAME.railway.app`
- **Health Check**: `https://YOUR_SERVICE_NAME.railway.app/health`
- **API Docs**: `https://YOUR_SERVICE_NAME.railway.app/docs`
- **Port**: Automatically assigned by Railway (use `$PORT` env var)

## Custom Domain (Optional)

1. In Railway dashboard → Service → Settings → Domains
2. Add custom domain
3. Configure DNS as instructed
4. Railway automatically provisions SSL certificate

## Monitoring & Logs

- **Logs**: Railway dashboard → Service → Deployments → View Logs
- **Metrics**: Railway dashboard → Service → Metrics
- **Alerts**: Configure in Railway dashboard → Service → Settings

## Troubleshooting

### Build Fails

- Check Dockerfile syntax
- Verify all dependencies in `requirements.txt`
- Check build logs in Railway dashboard

### Service Won't Start

- Verify environment variables are set
- Check that `PORT` environment variable is used (Railway sets this)
- Review application logs in Railway dashboard

### ChromaDB Not Persisting

- Ensure `CHROMADB_PATH` points to a persistent location
- Railway volumes persist by default, but verify path is correct

## Next Steps

1. Deploy `companion-api` to Railway (same project, different service)
2. Deploy `next-holo-ui` to Vercel
3. Update `NEXT_PUBLIC_API_BASE` in Vercel to point to Railway URL
4. Test all endpoints

## Cost

Railway pricing:
- **Free tier**: $5 credit/month
- **Hobby**: $5/month (after free tier)
- **Pro**: $20/month (for production)

See https://railway.app/pricing for current pricing.

