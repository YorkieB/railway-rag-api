# Railway Environment Variable Troubleshooting

## Issue: DEEPGRAM_API_KEY Not Found

If you're getting "Missing required API keys: DEEPGRAM_API_KEY" even after adding variables to Railway, follow these steps:

## Step 1: Verify Variables Are in Correct Service

**CRITICAL**: The companion functionality runs in the `rag-api` service, NOT a separate `companion-api` service.

1. Go to https://railway.app
2. Select your project
3. **Select the `railway-rag-api` service** (this is the main backend service)
4. Click on **Variables** tab
5. Verify these exact variable names exist (case-sensitive, underscore not hyphen):

```
DEEPGRAM_API_KEY
ELEVENLABS_API_KEY
OPENAI_API_KEY
```

## Step 2: Check Variable Names for Typos

Common mistakes:
- ❌ `DEEPGRAM_API-KEY` (hyphen) → ✅ `DEEPGRAM_API_KEY` (underscore)
- ❌ `deepgram_api_key` (lowercase) → ✅ `DEEPGRAM_API_KEY` (uppercase)
- ❌ `DEEPGRAM_API_KEY ` (trailing space) → ✅ `DEEPGRAM_API_KEY` (no spaces)

## Step 3: Verify Variable Values

1. Click on each variable to edit
2. Ensure:
   - No quotes around the value (Railway adds quotes automatically if needed)
   - No leading/trailing spaces
   - Value is complete (not truncated)
   - Value matches exactly what you copied

## Step 4: Force Redeploy

**IMPORTANT**: Railway should auto-redeploy when you add variables, but sometimes it doesn't. Force a redeploy:

1. In Railway dashboard → `railway-rag-api` service
2. Go to **Deployments** tab
3. Click **"Redeploy"** on the latest deployment
4. Wait 2-3 minutes for deployment to complete
5. Check deployment logs to ensure it started successfully

## Step 5: Test Diagnostic Endpoint

After redeploy, test the diagnostic endpoint:

```bash
# Replace with your Railway URL
curl https://railway-rag-api-production.up.railway.app/companion/check-keys
```

Or open in browser:
```
https://railway-rag-api-production.up.railway.app/companion/check-keys
```

Expected response (if keys are set):
```json
{
  "status": "ok",
  "keys": {
    "DEEPGRAM_API_KEY": "set",
    "ELEVENLABS_API_KEY": "set",
    "OPENAI_API_KEY": "set"
  },
  "companion_available": true,
  "message": "All keys set"
}
```

If keys are missing:
```json
{
  "status": "missing_keys",
  "keys": {
    "DEEPGRAM_API_KEY": "missing",
    "ELEVENLABS_API_KEY": "set",
    "OPENAI_API_KEY": "set"
  },
  "companion_available": true,
  "message": "Missing keys: DEEPGRAM_API_KEY"
}
```

## Step 6: Check Railway Logs

1. In Railway dashboard → `railway-rag-api` service
2. Go to **Deployments** tab
3. Click on the latest deployment
4. Click **"View Logs"**
5. Look for:
   - Any errors about missing environment variables
   - Confirmation that the service started successfully
   - Any import errors related to companion modules

## Step 7: Verify Service is Running

1. Test the health endpoint:
   ```bash
   curl https://railway-rag-api-production.up.railway.app/health
   ```

2. Should return:
   ```json
   {"status": "healthy", "service": "rag-api"}
   ```

## Common Issues

### Issue 1: Variables in Wrong Service
- **Symptom**: Variables exist but service can't find them
- **Solution**: Ensure variables are in `railway-rag-api` service, not a separate `companion-api` service

### Issue 2: Service Not Redeployed
- **Symptom**: Variables added but still getting error
- **Solution**: Manually trigger redeploy in Railway dashboard

### Issue 3: Variable Name Typo
- **Symptom**: Variable exists but code can't find it
- **Solution**: Double-check exact spelling: `DEEPGRAM_API_KEY` (underscore, uppercase)

### Issue 4: Variables Not Saved
- **Symptom**: Added variables but they disappeared
- **Solution**: Make sure to click "Add" or "Save" after entering each variable

## Quick Checklist

- [ ] Variables are in `railway-rag-api` service (not companion-api)
- [ ] Variable names are exact: `DEEPGRAM_API_KEY`, `ELEVENLABS_API_KEY`, `OPENAI_API_KEY`
- [ ] No typos (underscore not hyphen, uppercase)
- [ ] Values are complete (no truncation)
- [ ] Service has been redeployed after adding variables
- [ ] Diagnostic endpoint `/companion/check-keys` shows keys as "set"
- [ ] Health endpoint `/health` returns 200 OK

## Still Not Working?

If after following all steps the diagnostic endpoint still shows keys as "missing":

1. **Double-check Railway Variables Tab**: 
   - Take a screenshot of your Variables tab
   - Verify variable names match exactly

2. **Check Deployment Logs**:
   - Look for any errors during startup
   - Check if environment variables are being loaded

3. **Try Deleting and Re-adding Variables**:
   - Delete the variable
   - Add it again with exact name
   - Redeploy service

4. **Contact Support**:
   - Share the output from `/companion/check-keys` endpoint
   - Share a screenshot of your Railway Variables tab (hide values)

