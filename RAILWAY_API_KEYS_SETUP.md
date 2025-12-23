# 🔑 Setting Up API Keys in Railway

## Error Message
You're seeing: `DEEPGRAM_API_KEY environment variable is required`

This means the companion functionality needs API keys to work. Here's how to add them:

## 📋 Required API Keys

For full companion functionality, you need these environment variables in Railway:

1. **DEEPGRAM_API_KEY** - For speech-to-text (STT)
2. **ELEVENLABS_API_KEY** - For text-to-speech (TTS)
3. **OPENAI_API_KEY** - Already set ✅
4. **ELEVENLABS_VOICE_ID** - Optional (has default)

## 🚀 How to Add API Keys to Railway

### Step 1: Get Your API Keys

1. **Deepgram API Key**:
   - Go to https://console.deepgram.com/
   - Sign up or log in
   - Navigate to API Keys
   - Create a new API key
   - Copy the key

2. **ElevenLabs API Key**:
   - Go to https://elevenlabs.io/
   - Sign up or log in
   - Go to Profile → API Keys
   - Create a new API key
   - Copy the key

3. **ElevenLabs Voice ID** (Optional):
   - Go to https://elevenlabs.io/
   - Navigate to Voices
   - Choose a voice
   - Copy the Voice ID (or use default: `uju3wxzG5OhpWcoi3SMy`)

### Step 2: Add to Railway

1. **Go to Railway Dashboard**:
   - Visit https://railway.app/
   - Log in
   - Select your project: `wonderful-energy`
   - Select your service: `railway-rag-api`

2. **Add Environment Variables**:
   - Click on the service
   - Go to the **Variables** tab
   - Click **+ New Variable**
   - Add each variable:

   ```
   DEEPGRAM_API_KEY = your_deepgram_key_here
   ELEVENLABS_API_KEY = your_elevenlabs_key_here
   ELEVENLABS_VOICE_ID = uju3wxzG5OhpWcoi3SMy (optional)
   ```

3. **Save and Redeploy**:
   - Railway will automatically redeploy when you add variables
   - Wait 5-10 minutes for deployment to complete

### Step 3: Verify

1. **Check Deployment**:
   - Go to Railway → Deployments
   - Wait for latest deployment to show "Active"

2. **Test Connection**:
   - Go to https://jarvisb.app
   - Open Settings → Diagnostics
   - Click "Run Health Checks"
   - Try connecting to Jarvis Companion

## ✅ After Adding Keys

Once the keys are added and Railway redeploys:

1. The error message will disappear
2. You can create companion sessions
3. Voice conversation will work
4. Web access will be available

## 🔍 Troubleshooting

**Still seeing errors?**
- Check Railway deployment logs for any issues
- Verify API keys are correct (no extra spaces)
- Make sure Railway has redeployed after adding variables
- Check Diagnostics panel in Settings for detailed error messages

**API Key Issues?**
- Deepgram: Make sure you have credits/quota
- ElevenLabs: Check your subscription tier
- OpenAI: Already configured ✅

## 📝 Quick Reference

**Railway Service**: `railway-rag-api`  
**Project**: `wonderful-energy`  
**Required Variables**:
- `DEEPGRAM_API_KEY` ⚠️ Required
- `ELEVENLABS_API_KEY` ⚠️ Required
- `ELEVENLABS_VOICE_ID` ✅ Optional (has default)
- `OPENAI_API_KEY` ✅ Already set

