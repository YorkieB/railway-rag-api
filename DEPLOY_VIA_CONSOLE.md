# Deploy JARVIS via Google Cloud Console (Web Interface)

## Step-by-Step Guide

### Prerequisites Checklist
- [ ] Google Cloud account with billing enabled
- [ ] Access to project: `gen-lang-client-0118945483`
- [ ] Your Gemini API Key ready
- [ ] Both folders ready: `rag-api` and `knowledge-base-ui`

---

## PART 1: Deploy Backend (RAG API)

### Step 1: Open Cloud Run Console
1. Go to: **https://console.cloud.google.com/run?project=gen-lang-client-0118945483**
2. Make sure you're in the correct project (top dropdown should show `gen-lang-client-0118945483`)

### Step 2: Create Backend Service
1. Click the **"CREATE SERVICE"** button (top of the page)
2. Choose **"Deploy one revision from a source repository"** or **"Deploy from container image"**

### Step 3: Configure Backend Deployment

**If using "Deploy from source":**
- **Service name:** `rag-api`
- **Region:** `us-central1` (or your preferred region)
- **Authentication:** Select **"Allow unauthenticated invocations"** (for now)
- **Source:** Upload the `rag-api` folder or connect to a repository

**If using "Deploy from container image":**
- You'll need to build the image first (see alternative method below)

### Step 4: Configure Backend Settings
1. Click **"Container, Variables & Secrets, Connections, Security"** to expand
2. **Container:**
   - Port: `8080`
   - Memory: `2 GiB`
   - CPU: `2` (or 1 for cost savings)
   - Timeout: `300 seconds`
   - Max instances: `10` (or adjust as needed)
   - Min instances: `0` (to save costs)

3. **Variables & Secrets:**
   - Click **"ADD VARIABLE"**
   - Name: `GEMINI_API_KEY`
   - Value: `your_actual_gemini_api_key_here`
   - Click **"ADD"**

### Step 5: Deploy Backend
1. Click **"CREATE"** button at the bottom
2. Wait for deployment (2-5 minutes)
3. **IMPORTANT:** Copy the service URL (e.g., `https://rag-api-xxxxx-uc.a.run.app`)
   - You'll need this for the frontend!

---

## PART 2: Deploy Frontend (JARVIS UI)

### Step 6: Create Frontend Service
1. Still in Cloud Run console, click **"CREATE SERVICE"** again
2. Choose **"Deploy one revision from a source repository"**

### Step 7: Configure Frontend Deployment
- **Service name:** `jarvis-ui`
- **Region:** `us-central1` (same as backend)
- **Authentication:** Select **"Allow unauthenticated invocations"**
- **Source:** Upload the `knowledge-base-ui` folder

### Step 8: Configure Frontend Settings
1. Click **"Container, Variables & Secrets, Connections, Security"** to expand
2. **Container:**
   - Port: `8080`
   - Memory: `1 GiB`
   - CPU: `1`
   - Timeout: `300 seconds`
   - Max instances: `10`
   - Min instances: `0`

3. **Variables & Secrets:**
   - Click **"ADD VARIABLE"**
   - Name: `RAG_API_URL`
   - Value: `https://rag-api-xxxxx-uc.a.run.app` (use the URL from Step 5!)
   - Click **"ADD"**

### Step 9: Deploy Frontend
1. Click **"CREATE"** button
2. Wait for deployment (2-5 minutes)
3. **Copy the frontend URL** - this is your JARVIS app!

---

## PART 3: Verify Deployment

### Step 10: Test Backend
1. In Cloud Run console, click on `rag-api` service
2. Click the **URL** at the top to open it
3. You should see: `{"message":"RAG Knowledge Base API - BigQuery Edition"}`

### Step 11: Test Frontend
1. In Cloud Run console, click on `jarvis-ui` service
2. Click the **URL** at the top
3. You should see the JARVIS interface!

### Step 12: Test Full Flow
1. Open the frontend URL
2. Try uploading a document
3. Try asking a question
4. Verify it connects to the backend

---

## Troubleshooting

### If Backend Deployment Fails:
- Check that `Dockerfile` exists in `rag-api` folder
- Verify `requirements.txt` is present
- Check logs: Click on service → "LOGS" tab

### If Frontend Can't Connect to Backend:
- Verify `RAG_API_URL` environment variable is set correctly
- Check backend URL is accessible (open in browser)
- Ensure backend allows unauthenticated access

### If You See CORS Errors:
- Backend already has CORS configured
- Verify frontend URL is in allowed origins (if you restricted CORS)

### View Logs:
1. Click on service name in Cloud Run console
2. Click **"LOGS"** tab
3. See real-time logs and errors

---

## Updating Services Later

### To Update Backend:
1. Go to Cloud Run → `rag-api` service
2. Click **"EDIT & DEPLOY NEW REVISION"**
3. Upload new code or connect to updated repository
4. Click **"DEPLOY"**

### To Update Frontend:
1. Go to Cloud Run → `jarvis-ui` service
2. Click **"EDIT & DEPLOY NEW REVISION"**
3. Upload new code
4. Click **"DEPLOY"**

---

## Important URLs to Save

After deployment, save these URLs:
- **Backend URL:** `https://rag-api-xxxxx-uc.a.run.app`
- **Frontend URL:** `https://jarvis-ui-xxxxx-uc.a.run.app`

You can find them anytime in the Cloud Run console by clicking on each service.

---

## Cost Optimization Tips

1. **Set Min Instances to 0:** Services scale to zero when not in use
2. **Adjust Memory:** Start with recommended values, reduce if needed
3. **Set Max Instances:** Limit to prevent unexpected costs
4. **Use CPU Throttling:** Enable to save costs during idle periods

---

## Next Steps After Deployment

1. ✅ Test all features
2. ✅ Set up custom domain (optional)
3. ✅ Configure monitoring and alerts
4. ✅ Set up CI/CD for automatic updates
5. ✅ Review security settings

---

## Quick Reference

**Backend Service:**
- Name: `rag-api`
- Port: `8080`
- Memory: `2 GiB`
- Env Var: `GEMINI_API_KEY`

**Frontend Service:**
- Name: `jarvis-ui`
- Port: `8080`
- Memory: `1 GiB`
- Env Var: `RAG_API_URL`

**Project:** `gen-lang-client-0118945483`
**Region:** `us-central1`

