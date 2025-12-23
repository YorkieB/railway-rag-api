# Vercel Deployment Guide for next-holo-ui

## Step 1: Update Environment Variable

First, update the `env.example` file with your Railway API URL:

```env
NEXT_PUBLIC_API_BASE=https://railway-rag-api-production.up.railway.app
```

## Step 2: Deploy to Vercel

### Option A: Via Vercel Dashboard (Recommended)

1. **Go to Vercel**: https://vercel.com
2. **Sign in** with your GitHub account
3. **Click "Add New"** → **"Project"**
4. **Import Git Repository**:
   - Select `YorkieB/railway-rag-api` (or your repo)
   - Vercel will auto-detect Next.js
5. **Configure Project**:
   - **Framework Preset**: Next.js (auto-detected)
   - **Root Directory**: `next-holo-ui` ⚠️ **IMPORTANT**
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `.next` (auto-detected)
   - **Install Command**: `npm install` (auto-detected)
6. **Set Environment Variables**:
   - Click "Environment Variables"
   - Add:
     ```
     NEXT_PUBLIC_API_BASE=https://railway-rag-api-production.up.railway.app
     ```
   - Select "Production", "Preview", and "Development"
7. **Deploy**:
   - Click "Deploy"
   - Wait for build to complete (~2-3 minutes)

### Option B: Via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Navigate to frontend directory
cd next-holo-ui

# Deploy
vercel --prod

# When prompted:
# - Set up and deploy? Yes
# - Which scope? (select your account)
# - Link to existing project? No (first time) or Yes (if updating)
# - What's your project's name? next-holo-ui
# - In which directory is your code located? ./
# - Want to override settings? No

# Set environment variable
vercel env add NEXT_PUBLIC_API_BASE production
# Enter: https://railway-rag-api-production.up.railway.app

# Redeploy with new env var
vercel --prod
```

## Step 3: Verify Deployment

After deployment, you'll get a URL like:
- `https://next-holo-ui.vercel.app` (or your custom domain)

**Test the deployment**:
1. Open the Vercel URL in your browser
2. Check browser console for any errors
3. Test a query to verify API connection
4. Check that API calls are going to Railway URL

## Step 4: Update CORS (if needed)

If you see CORS errors, update `rag-api/app.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://next-holo-ui.vercel.app",  # Your Vercel URL
        "https://your-custom-domain.vercel.app",  # If using custom domain
        "http://localhost:3000",  # Local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then redeploy Railway service.

## Troubleshooting

### Build Fails
- Check Vercel build logs
- Verify `package.json` has correct scripts
- Ensure Node.js version is compatible (requires >=18)

### API Connection Fails
- Verify `NEXT_PUBLIC_API_BASE` is set correctly
- Check Railway API is accessible
- Verify CORS is configured correctly
- Check browser console for errors

### Environment Variables Not Working
- Ensure variable name starts with `NEXT_PUBLIC_` for client-side access
- Redeploy after adding environment variables
- Check Vercel dashboard → Project → Settings → Environment Variables

## Next Steps

After successful deployment:
1. ✅ Test all features in production
2. ✅ Set up custom domain (optional)
3. ✅ Configure monitoring
4. ✅ Update documentation with production URLs

