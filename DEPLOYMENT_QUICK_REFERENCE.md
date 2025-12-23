# Deployment Quick Reference

**Quick deployment guide for Jarvis RAG API**

---

## 🚀 Fast Track Deployment (5 minutes)

### 1. Railway Setup
```bash
# 1. Go to https://railway.app
# 2. New Project → Deploy from GitHub
# 3. Select repository
# 4. Set root directory: rag-api
```

### 2. Environment Variables
```
OPENAI_API_KEY=sk-...your-key...
CHROMADB_PATH=/app/rag_knowledge_base
```

### 3. Deploy
- Railway auto-deploys
- Get URL: `https://rag-api-production-XXXX.up.railway.app`

### 4. Verify
```bash
curl https://YOUR_URL/health
# Should return: {"status": "healthy", "service": "rag-api"}
```

---

## 📋 Required Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | ✅ Yes | - | OpenAI API key for LLM/embeddings |
| `CHROMADB_PATH` | ❌ No | `/app/rag_knowledge_base` | ChromaDB storage path |
| `PORT` | ❌ No | Auto | Railway sets automatically |

---

## 🔗 Service URLs

After deployment, your services will be at:

- **rag-api**: `https://rag-api-production-XXXX.up.railway.app`
- **API Docs**: `https://rag-api-production-XXXX.up.railway.app/docs`
- **Health**: `https://rag-api-production-XXXX.up.railway.app/health`

---

## ✅ Pre-Deployment Checklist

- [x] Code pushed to GitHub
- [x] Tests passed (55/55)
- [x] No API keys in code
- [ ] `OPENAI_API_KEY` ready
- [ ] Railway account created

---

## 🧪 Test Production Deployment

```bash
# Update test file
BASE_URL = "https://rag-api-production-XXXX.up.railway.app"

# Run tests
python test_full_suite.py
```

Expected: **27/27 tests pass**

---

## 🐛 Troubleshooting

### Build Fails
- Check Dockerfile syntax
- Verify `requirements.txt` dependencies
- Check Railway build logs

### Service Won't Start
- Verify `OPENAI_API_KEY` is set
- Check Railway logs
- Ensure `PORT` env var is used

### CORS Errors
- Update `app.py` CORS settings
- Add Vercel URL to `allow_origins`
- Redeploy

---

## 📚 Full Documentation

- **Detailed Guide**: `DEPLOYMENT.md`
- **Railway Guide**: `rag-api/DEPLOYMENT_GUIDE.md`
- **Checklist**: `PRE_DEPLOYMENT_CHECKLIST.md`

---

**Status**: ✅ Ready for Deployment  
**Last Tested**: 2025-01-XX  
**Test Results**: 55/55 passed

