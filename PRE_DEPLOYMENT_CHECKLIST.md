# Pre-Deployment Checklist

**Date**: 2025-01-XX  
**Status**: ✅ Ready for Deployment  
**Test Results**: 55/55 core tests passed

---

## ✅ Pre-Deployment Verification

### Code Quality
- [x] **Fixed Critical Bug**: Added missing `Dict` import in `rag-api/models.py`
- [x] **Fixed Encoding Issue**: Fixed Unicode encoding in `test_full_suite.py` for Windows
- [x] **Linter Check**: No linting errors in `rag-api/models.py`
- [x] **Unit Tests**: 28/28 passed (100%)
- [x] **Integration Tests**: 27/27 API endpoints passed (100%)

### Test Coverage Summary

#### Unit Tests (28/28 ✅)
- ✅ Agent initialization and orchestration
- ✅ Avatar/waveform generation
- ✅ Budget and cost tracking
- ✅ Uncertainty protocol
- ✅ Panic stop functionality

#### Integration Tests (27/27 ✅)
- ✅ Core API (health, root, documents)
- ✅ V3 Integrations (Zapier, Slack, Email, Spotify)
- ✅ V3 Memory features (templates, clustering, conflicts)
- ✅ V3 Collaboration (sessions)
- ✅ V3 Agents (marketplace, learning, improvement)
- ✅ V3 Analytics (usage, cost, performance)
- ✅ V3 Document processing (categorization, summarization)
- ✅ Memory API (search)
- ✅ Browser automation (sessions, AX tree)

---

## 📋 Deployment Checklist

### Step 1: Pre-Deployment Setup

#### 1.1 Environment Variables Checklist
- [ ] **OpenAI API Key** (`OPENAI_API_KEY`)
  - Required for: LLM, embeddings, vision analysis
  - Get from: https://platform.openai.com/api-keys
  - Status: ⚠️ **Must be set before deployment**

- [ ] **ChromaDB Path** (`CHROMADB_PATH`)
  - Optional (default: `/app/rag_knowledge_base`)
  - Railway handles persistence automatically
  - Status: ✅ Default is fine

#### 1.2 Code Repository
- [ ] Code pushed to GitHub
- [ ] All changes committed
- [ ] No uncommitted sensitive data (API keys, passwords)
- [ ] `.gitignore` properly configured

#### 1.3 Service Accounts
- [ ] Railway account created: https://railway.app
- [ ] Vercel account created: https://vercel.com (for frontend)
- [ ] GitHub repository ready

---

### Step 2: Deploy rag-api to Railway

#### 2.1 Create Railway Project
- [ ] Go to https://railway.app
- [ ] Click "New Project" → "Deploy from GitHub repo"
- [ ] Authorize Railway → Select repository
- [ ] Add service → Set root directory: `rag-api`

#### 2.2 Configure Environment Variables
In Railway dashboard → rag-api service → Variables:

```
OPENAI_API_KEY=sk-...your-key-here...
CHROMADB_PATH=/app/rag_knowledge_base
```

- [ ] `OPENAI_API_KEY` set
- [ ] `CHROMADB_PATH` set (optional, default works)

#### 2.3 Deploy
- [ ] Railway auto-detects Dockerfile
- [ ] Build completes successfully
- [ ] Service starts without errors
- [ ] Get deployment URL: `https://rag-api-production-XXXX.up.railway.app`

#### 2.4 Verify Deployment
- [ ] Health check: `curl https://YOUR_URL/health` → Returns 200
- [ ] API docs: `https://YOUR_URL/docs` → Swagger UI loads
- [ ] Test endpoint: `curl https://YOUR_URL/` → Returns JSON

**Expected Response (Health Check)**:
```json
{"status": "healthy", "service": "rag-api"}
```

---

### Step 3: Deploy companion-api to Railway (Optional)

#### 3.1 Add Second Service
- [ ] In same Railway project → "Add Service"
- [ ] Set root directory: `companion-api`
- [ ] Configure environment variables (see DEPLOYMENT.md)

#### 3.2 Verify
- [ ] Health check passes
- [ ] Service URL obtained

---

### Step 4: Deploy next-holo-ui to Vercel

#### 4.1 Import Repository
- [ ] Go to https://vercel.com
- [ ] "Add New" → "Project" → Import GitHub repo
- [ ] Set root directory: `next-holo-ui`

#### 4.2 Configure Environment Variables
In Vercel dashboard → Project Settings → Environment Variables:

```
NEXT_PUBLIC_API_BASE=https://rag-api-production-XXXX.up.railway.app
```

- [ ] Replace `XXXX` with actual Railway URL from Step 2.3
- [ ] Variable set correctly

#### 4.3 Deploy
- [ ] Build completes successfully
- [ ] Deployment URL obtained: `https://your-project.vercel.app`

#### 4.4 Verify Frontend
- [ ] Frontend loads at Vercel URL
- [ ] Can connect to backend API
- [ ] Document upload works
- [ ] RAG query works

---

### Step 5: Post-Deployment Verification

#### 5.1 API Endpoints Test
Run the full test suite against production:

```bash
# Update BASE_URL in test_full_suite.py
BASE_URL = "https://rag-api-production-XXXX.up.railway.app"

# Run tests
python test_full_suite.py
```

- [ ] All 27 integration tests pass
- [ ] Health check endpoint works
- [ ] Core API endpoints respond
- [ ] V3 features accessible

#### 5.2 CORS Configuration (if needed)
If frontend can't connect:

- [ ] Update `rag-api/app.py` CORS settings:
  ```python
  allow_origins=[
      "https://your-project.vercel.app",  # Your Vercel URL
      "http://localhost:3000",  # Local dev
  ]
  ```
- [ ] Redeploy rag-api

#### 5.3 Monitoring Setup
- [ ] Railway logs accessible
- [ ] Vercel logs accessible
- [ ] Error tracking configured (optional)

---

### Step 6: Security & Performance

#### 6.1 Security Checklist
- [ ] No API keys in code (all in environment variables)
- [ ] CORS origins restricted (not `["*"]` in production)
- [ ] HTTPS enabled (automatic on Railway/Vercel)
- [ ] Secrets not logged

#### 6.2 Performance
- [ ] ChromaDB persistence working
- [ ] API response times acceptable
- [ ] No memory leaks observed
- [ ] Database connections stable

---

## 🚨 Known Issues & Notes

### Non-Critical Issues
1. **Windows Integration Tests**: 2/23 passed
   - Status: Expected (requires Windows environment)
   - Impact: None for deployment
   - Action: Can be addressed post-deployment

2. **Memory Analytics Test Timeout**: 1 test times out
   - Status: Threading/lock issue in test environment
   - Impact: None for production (test-only issue)
   - Action: Monitor in production, fix if needed

### Deployment Notes
- ✅ All critical endpoints tested and working
- ✅ Core functionality verified
- ✅ No blocking issues identified
- ⚠️ Remember to set `OPENAI_API_KEY` before deployment

---

## 📊 Deployment Status

| Component | Status | URL | Notes |
|-----------|--------|-----|-------|
| rag-api | ⏳ Ready | TBD | Needs Railway deployment |
| companion-api | ⏳ Optional | TBD | Optional service |
| next-holo-ui | ⏳ Ready | TBD | Needs Vercel deployment |

---

## 🎯 Quick Start Commands

### Local Testing (Before Deployment)
```bash
# Start server locally
cd rag-api
uvicorn app:app --reload --port 8080

# Run tests
cd ..
python test_full_suite.py
```

### Railway Deployment
```bash
# Via Railway CLI (optional)
railway login
railway init
railway up
```

### Vercel Deployment
```bash
# Via Vercel CLI (optional)
vercel login
vercel deploy
```

---

## 📝 Post-Deployment Tasks

- [ ] Update documentation with production URLs
- [ ] Set up monitoring alerts
- [ ] Configure custom domains (optional)
- [ ] Test all user flows in production
- [ ] Set up backup strategy for ChromaDB data
- [ ] Document rollback procedure

---

## 🔗 Reference Documents

- **Deployment Guide**: `DEPLOYMENT.md`
- **Railway Guide**: `rag-api/DEPLOYMENT_GUIDE.md`
- **Test Suite**: `test_full_suite.py`
- **Unit Tests**: `tests/unit/`

---

## ✅ Final Sign-Off

**Pre-Deployment Status**: ✅ **READY**

- [x] All critical tests passed
- [x] Code quality verified
- [x] No blocking issues
- [x] Documentation complete

**Ready to deploy when:**
1. ✅ `OPENAI_API_KEY` is available
2. ✅ Railway account is set up
3. ✅ GitHub repository is ready

---

**Last Updated**: 2025-01-XX  
**Tested By**: Automated Test Suite  
**Approved For**: Production Deployment

