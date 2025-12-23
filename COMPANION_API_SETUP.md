# Companion API Connection Issues - Setup Guide

## 🔍 Current Issue

When clicking "Start Session" in Jarvis Companion, you see "Error" but no details.

## ✅ What I Fixed

1. **Better Error Messages**: Now shows actual error details
2. **Health Check**: Tests connection before attempting WebSocket
3. **API URL Display**: Shows which API URL is being used
4. **Troubleshooting Info**: Provides guidance in error messages

## 🚨 Root Cause

The **companion-api** service is a **separate service** that needs to be:
1. **Running** (either locally or deployed)
2. **Accessible** from the frontend
3. **Configured** with correct URL

## 📋 Setup Options

### Option 1: Deploy Companion-API Separately (Recommended)

1. **Deploy companion-api to Railway/Vercel**:
   ```bash
   cd companion-api
   # Deploy to Railway or Vercel
   ```

2. **Set Environment Variable**:
   - In Vercel: Add `NEXT_PUBLIC_COMPANION_API_BASE=https://your-companion-api.railway.app`
   - Or in `.env.local`: `NEXT_PUBLIC_COMPANION_API_BASE=https://your-companion-api.railway.app`

### Option 2: Run Locally (Development)

1. **Start companion-api locally**:
   ```bash
   cd companion-api
   python main.py
   # Runs on http://localhost:8081
   ```

2. **Frontend will auto-detect** `http://localhost:8081` in development

### Option 3: Integrate into rag-api (Alternative)

If you want companion endpoints in rag-api:

1. **Copy companion endpoints** from `companion-api/main.py` to `rag-api/app.py`
2. **Update frontend** to use rag-api URL for companion endpoints
3. **Deploy rag-api** with companion functionality

## 🔧 Current Configuration

The frontend tries to detect companion-api URL:
- **Production**: Tries `companion.jarvisb.app` or same domain as rag-api
- **Development**: Defaults to `http://localhost:8081`
- **Override**: Set `NEXT_PUBLIC_COMPANION_API_BASE` environment variable

## 🐛 Debugging Steps

1. **Check Browser Console**:
   - Open DevTools (F12)
   - Look for connection errors
   - Check Network tab for failed requests

2. **Check Error Message**:
   - The UI now shows the actual error
   - Look for messages like:
     - "Cannot reach companion API at..."
     - "Companion API health check failed..."
     - "WebSocket connection error..."

3. **Test Health Endpoint**:
   - Try: `https://your-companion-api.com/health`
   - Should return: `{"status": "healthy", ...}`

4. **Check API URL**:
   - The UI shows the API URL being used
   - Verify it's correct

## ✅ Quick Fix

**If companion-api is not deployed yet:**

1. **Set environment variable** in Vercel:
   ```
   NEXT_PUBLIC_COMPANION_API_BASE=https://api.jarvisb.app
   ```

2. **Or run locally**:
   ```bash
   cd companion-api
   python main.py
   ```

3. **Then try connecting again**

## 📝 Next Steps

1. **Deploy companion-api** to Railway or Vercel
2. **Set `NEXT_PUBLIC_COMPANION_API_BASE`** in Vercel environment variables
3. **Redeploy frontend** to pick up the new URL
4. **Test connection** - should work now!

## 🎯 Summary

- ✅ Error messages now show actual problems
- ✅ Health check prevents silent failures  
- ✅ API URL displayed for debugging
- ⚠️ **Companion-api service must be running and accessible**

The frontend is now much better at telling you what's wrong!

