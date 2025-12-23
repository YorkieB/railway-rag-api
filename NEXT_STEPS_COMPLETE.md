# Next Steps Implementation Guide

This guide walks through completing all optional next steps for your deployed RAG API.

---

## ✅ Step 1: Frontend Deployment (Vercel)

### Prerequisites
- Vercel account (sign up at https://vercel.com)
- GitHub repository connected

### Quick Steps

1. **Go to Vercel Dashboard**
   - Visit: https://vercel.com
   - Sign in with GitHub

2. **Import Project**
   - Click "Add New" → "Project"
   - Select repository: `YorkieB/railway-rag-api`
   - Vercel auto-detects Next.js

3. **Configure Project**
   - **Root Directory**: `next-holo-ui` ⚠️ **CRITICAL**
   - **Framework**: Next.js (auto-detected)
   - **Build Command**: `npm run build` (auto)
   - **Output Directory**: `.next` (auto)

4. **Set Environment Variable**
   - Click "Environment Variables"
   - Add:
     ```
     Name: NEXT_PUBLIC_API_BASE
     Value: https://railway-rag-api-production.up.railway.app
     ```
   - Select: Production, Preview, Development

5. **Deploy**
   - Click "Deploy"
   - Wait ~2-3 minutes for build

6. **Verify**
   - Open the Vercel URL
   - Test API connection
   - Check browser console for errors

**Full Guide**: See `VERCEL_DEPLOYMENT_GUIDE.md`

---

## ✅ Step 2: Custom Domain (Railway)

### Prerequisites
- Domain name registered (e.g., from Namecheap, GoDaddy, etc.)
- Access to domain DNS settings

### Steps

1. **In Railway Dashboard**
   - Go to: https://railway.app
   - Select project: `wonderful-energy`
   - Select service: `railway-rag-api`
   - Click "Settings" tab
   - Scroll to "Domains" section

2. **Add Custom Domain**
   - Click "Generate Domain" (if you want Railway's free domain)
   - OR Click "Custom Domain"
   - Enter your domain: `api.yourdomain.com`

3. **Configure DNS**
   Railway will show you DNS records to add:
   ```
   Type: CNAME
   Name: api (or @ for root domain)
   Value: [Railway-provided value]
   ```

4. **Add DNS Records**
   - Go to your domain registrar's DNS settings
   - Add the CNAME record Railway provided
   - Wait for DNS propagation (5-60 minutes)

5. **SSL Certificate**
   - Railway automatically provisions SSL certificate
   - Wait for certificate to be issued (~5 minutes)
   - Your API will be accessible at: `https://api.yourdomain.com`

### Alternative: Railway Subdomain
If you don't have a custom domain, Railway provides:
- `railway-rag-api-production.up.railway.app` (already active)

---

## ✅ Step 3: Monitoring & Alerts (Railway)

### Set Up Monitoring

1. **View Metrics**
   - Railway Dashboard → Service → "Metrics" tab
   - View: CPU, Memory, Network, Request rates

2. **View Logs**
   - Railway Dashboard → Service → "Deployments" tab
   - Click any deployment → "View Logs"
   - Real-time logs available

3. **Set Up Alerts** (Railway Pro/Team)
   - Railway Dashboard → Service → "Settings" → "Alerts"
   - Configure:
     - **CPU Usage**: Alert if > 80% for 5 minutes
     - **Memory Usage**: Alert if > 80% for 5 minutes
     - **Error Rate**: Alert if > 5% errors
     - **Response Time**: Alert if > 2 seconds

4. **Health Check Monitoring** (External)
   - Use services like:
     - **UptimeRobot**: https://uptimerobot.com (free)
     - **Pingdom**: https://pingdom.com
     - **StatusCake**: https://statuscake.com
   - Monitor: `https://railway-rag-api-production.up.railway.app/health`
   - Set check interval: 5 minutes
   - Alert on: Status != 200

### Recommended Alerts

**UptimeRobot Setup**:
1. Sign up at https://uptimerobot.com
2. Add Monitor:
   - **Type**: HTTP(s)
   - **URL**: `https://railway-rag-api-production.up.railway.app/health`
   - **Interval**: 5 minutes
   - **Alert Contacts**: Your email
3. Save and activate

---

## ✅ Step 4: Production Testing

### Run Full Test Suite

1. **Update Test Configuration**
   ```bash
   # Test suite is already configured with production URL
   # BASE_URL = https://railway-rag-api-production.up.railway.app
   ```

2. **Run Tests**
   ```bash
   # From project root
   python test_full_suite.py
   ```

3. **Expected Results**
   - All 27 integration tests should pass
   - Health check: ✅
   - All API endpoints: ✅
   - V3 features: ✅

4. **Test Specific Endpoints**
   ```bash
   # Health check
   curl https://railway-rag-api-production.up.railway.app/health
   
   # Query test
   curl -X POST https://railway-rag-api-production.up.railway.app/query \
     -H "Content-Type: application/json" \
     -d '{"query": "Test query", "user_id": "test_user"}'
   ```

### Manual Testing Checklist

- [ ] Health endpoint returns 200
- [ ] API docs accessible at `/docs`
- [ ] Can upload a document
- [ ] Can query the knowledge base
- [ ] Memory endpoints work
- [ ] Browser automation endpoints respond
- [ ] Export functionality works

---

## Summary Checklist

### Frontend Deployment
- [ ] Vercel account created
- [ ] Project imported from GitHub
- [ ] Root directory set to `next-holo-ui`
- [ ] Environment variable `NEXT_PUBLIC_API_BASE` set
- [ ] Build successful
- [ ] Frontend accessible and working

### Custom Domain
- [ ] Domain registered (or using Railway subdomain)
- [ ] DNS records configured
- [ ] SSL certificate issued
- [ ] Domain accessible

### Monitoring
- [ ] Railway metrics dashboard accessible
- [ ] Logs accessible
- [ ] External monitoring set up (optional)
- [ ] Alerts configured (if Railway Pro)

### Testing
- [ ] Full test suite run against production
- [ ] All tests passing
- [ ] Manual testing completed
- [ ] No critical issues found

---

## Quick Reference

**Production URLs**:
- **API**: https://railway-rag-api-production.up.railway.app
- **API Docs**: https://railway-rag-api-production.up.railway.app/docs
- **Health**: https://railway-rag-api-production.up.railway.app/health
- **Frontend**: (After Vercel deployment)

**Railway Dashboard**: https://railway.app  
**Vercel Dashboard**: https://vercel.com

---

**Status**: Ready to implement all steps  
**Estimated Time**: 30-60 minutes total

