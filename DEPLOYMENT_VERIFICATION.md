# Deployment Verification Checklist

This guide helps verify that both frontend and backend are deploying correctly after code changes.

## ✅ Step 1: Verify Code is Pushed to GitHub

```bash
# Check git status
git status

# Should show: "Your branch is up to date with 'origin/main'"
# If not, push changes:
git add .
git commit -m "Your commit message"
git push origin main
```

## ✅ Step 2: Verify Railway Backend Deployment

### Check Railway Dashboard:
1. Go to: https://railway.app
2. Navigate to your project → `rag-api` service
3. Check **Deployments** tab:
   - Latest deployment should show your recent commit
   - Status should be "Active" or "Building"
   - Build logs should show successful build

### Verify Backend is Live:
```bash
# Test health endpoint
curl https://railway-rag-api-production.up.railway.app/health

# Should return: {"status": "healthy"}
```

### Check Railway Configuration:
- ✅ **Root Directory**: Set to `rag-api`
- ✅ **Environment Variables**: 
  - `OPENAI_API_KEY` is set
  - `CHROMADB_PATH=/app/rag_knowledge_base`
- ✅ **Auto-deploy**: Enabled (deploys on git push)

## ✅ Step 3: Verify Vercel Frontend Deployment

### Check Vercel Dashboard:
1. Go to: https://vercel.com
2. Navigate to your project → `next-holo-ui`
3. Check **Deployments** tab:
   - Latest deployment should show your recent commit
   - Status should be "Ready" or "Building"
   - Build logs should show successful build

### Verify Frontend is Live:
1. Open your Vercel URL (e.g., `https://next-holo-ui.vercel.app`)
2. Open browser DevTools → Console
3. Check for errors
4. Test API connection by using the app

### Check Vercel Configuration:
- ✅ **Root Directory**: Set to `next-holo-ui`
- ✅ **Framework**: Next.js (auto-detected)
- ✅ **Environment Variables**:
  - `NEXT_PUBLIC_API_BASE` is set to Railway URL
  - Applied to: Production, Preview, Development
- ✅ **Auto-deploy**: Enabled (deploys on git push)

## ✅ Step 4: Verify Auto-Deploy is Enabled

### Railway:
1. Railway Dashboard → Service → Settings → Source
2. Verify: **Auto Deploy** is enabled
3. Verify: **Branch** is set to `main`

### Vercel:
1. Vercel Dashboard → Project → Settings → Git
2. Verify: **Production Branch** is `main`
3. Verify: **Auto Deploy** is enabled

## ✅ Step 5: Test End-to-End

1. **Backend Health Check**:
   ```bash
   curl https://railway-rag-api-production.up.railway.app/health
   ```

2. **Frontend Loads**:
   - Open Vercel URL
   - Page should load without errors

3. **API Connection**:
   - Use the frontend to make a query
   - Check browser Network tab
   - API calls should go to Railway URL
   - Should receive successful responses

## 🔧 Troubleshooting

### Changes Not Appearing

1. **Check if code is pushed**:
   ```bash
   git log --oneline -5
   git status
   ```

2. **Check deployment status**:
   - Railway: Dashboard → Deployments → Check latest build logs
   - Vercel: Dashboard → Deployments → Check latest build logs

3. **Force redeploy**:
   - **Railway**: Dashboard → Service → Deployments → Click "Redeploy"
   - **Vercel**: Dashboard → Project → Deployments → Click "Redeploy"

### Build Failures

1. **Check build logs**:
   - Railway: Dashboard → Service → Deployments → View Logs
   - Vercel: Dashboard → Project → Deployments → View Logs

2. **Common issues**:
   - Missing dependencies in `package.json` or `requirements.txt`
   - Environment variables not set
   - Root directory misconfigured
   - Build command errors

### API Connection Issues

1. **Check CORS**:
   - Verify Railway CORS allows Vercel domain
   - Check `rag-api/app.py` CORS configuration

2. **Check environment variables**:
   - Vercel: `NEXT_PUBLIC_API_BASE` must match Railway URL
   - Railway: API keys must be set

3. **Test API directly**:
   ```bash
   curl https://railway-rag-api-production.up.railway.app/health
   ```

## 📋 Quick Deployment Checklist

After making changes:

- [ ] Commit changes: `git add . && git commit -m "message"`
- [ ] Push to GitHub: `git push origin main`
- [ ] Wait 2-3 minutes for auto-deploy
- [ ] Check Railway deployment status
- [ ] Check Vercel deployment status
- [ ] Test backend health endpoint
- [ ] Test frontend in browser
- [ ] Verify API connection works

## 🚀 Manual Deployment (If Auto-Deploy Fails)

### Railway:
1. Dashboard → Service → Deployments
2. Click "Redeploy" on latest deployment
3. Or: Click "New Deployment" → Select branch `main`

### Vercel:
1. Dashboard → Project → Deployments
2. Click "Redeploy" on latest deployment
3. Or: Push empty commit: `git commit --allow-empty -m "Redeploy" && git push`

## 📊 Monitoring

### Railway:
- **Logs**: Dashboard → Service → Deployments → View Logs
- **Metrics**: Dashboard → Service → Metrics
- **Alerts**: Configure in Settings

### Vercel:
- **Logs**: Dashboard → Project → Deployments → View Logs
- **Analytics**: Dashboard → Project → Analytics
- **Real-time**: Dashboard → Project → Real-time Logs

---

**Last Updated**: 2025-01-XX  
**Status**: Active

