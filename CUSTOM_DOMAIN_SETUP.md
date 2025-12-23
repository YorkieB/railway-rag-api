# Custom Domain Setup Guide

## Prerequisites
- ✅ Domain purchased and registered
- ✅ Access to domain registrar DNS settings
- ✅ Railway account (https://railway.app)
- ✅ Vercel account (https://vercel.com)

---

## Step 1: Configure Backend Domain (Railway)

### Recommended: `api.yourdomain.com`

1. **Go to Railway Dashboard**
   - Visit: https://railway.app
   - Select project: `wonderful-energy`
   - Select service: `railway-rag-api`
   - Click **"Settings"** tab
   - Scroll to **"Domains"** section

2. **Add Custom Domain**
   - Click **"Custom Domain"** button
   - Enter your subdomain: `api.yourdomain.com` (replace with your actual domain)
   - Click **"Add Domain"**

3. **Get DNS Records**
   - Railway will show you DNS records to add
   - **Type**: CNAME
   - **Name**: `api` (or the subdomain you chose)
   - **Value**: Railway will provide (e.g., `cname.railway.app` or similar)
   - **Copy these values** - you'll need them in Step 3

4. **Wait for SSL**
   - Railway automatically provisions SSL certificate
   - Takes ~5-10 minutes after DNS propagates

---

## Step 2: Configure Frontend Domain (Vercel)

### Recommended: `yourdomain.com` (root) or `www.yourdomain.com`

1. **Go to Vercel Dashboard**
   - Visit: https://vercel.com
   - Select project: `next-holo-ui`
   - Click **"Settings"** tab
   - Click **"Domains"** in sidebar

2. **Add Custom Domain**
   - Enter your domain: `yourdomain.com` (or `www.yourdomain.com`)
   - Click **"Add"**

3. **Get DNS Records**
   - Vercel will show you DNS records to add
   - **Type**: A or CNAME (Vercel will specify)
   - **Name**: `@` (for root) or `www` (for www subdomain)
   - **Value**: Vercel will provide (e.g., `76.76.21.21` for A record or CNAME value)
   - **Copy these values** - you'll need them in Step 3

4. **Wait for SSL**
   - Vercel automatically provisions SSL certificate
   - Takes ~5-10 minutes after DNS propagates

---

## Step 3: Configure DNS at Your Registrar

### Common Registrars:
- **Namecheap**: https://www.namecheap.com/myaccount/login/
- **GoDaddy**: https://www.godaddy.com/
- **Google Domains**: https://domains.google.com/
- **Cloudflare**: https://dash.cloudflare.com/

### Steps:

1. **Log in to your domain registrar**
2. **Navigate to DNS Management**
   - Usually under "DNS Settings", "DNS Management", or "Advanced DNS"
3. **Add DNS Records**

   **For Railway (Backend API):**
   ```
   Type: CNAME
   Name: api
   Value: [Railway-provided value]
   TTL: 3600 (or Auto)
   ```

   **For Vercel (Frontend):**
   ```
   Type: A (or CNAME as Vercel specifies)
   Name: @ (for root domain) or www
   Value: [Vercel-provided value]
   TTL: 3600 (or Auto)
   ```

4. **Save Changes**
   - DNS propagation can take 5 minutes to 48 hours
   - Usually completes within 1 hour

---

## Step 4: Update Environment Variables

### Update Vercel Environment Variable

After Railway domain is active:

1. **Vercel Dashboard** → Project → Settings → Environment Variables
2. **Update** `NEXT_PUBLIC_API_BASE`:
   - Old: `https://railway-rag-api-production.up.railway.app`
   - New: `https://api.yourdomain.com`
3. **Redeploy**:
   ```bash
   cd next-holo-ui
   vercel --prod
   ```

---

## Step 5: Verify Everything Works

1. **Check Railway Domain**:
   - Visit: `https://api.yourdomain.com/health`
   - Should return: `{"status":"healthy"}`

2. **Check Vercel Domain**:
   - Visit: `https://yourdomain.com`
   - Frontend should load and connect to API

3. **Test Full Stack**:
   - Open frontend at your custom domain
   - Test a query/feature
   - Check browser console for API calls to `api.yourdomain.com`

---

## Troubleshooting

### DNS Not Propagating?
- Use https://dnschecker.org to check DNS propagation globally
- Wait up to 48 hours (usually much faster)
- Clear browser cache and DNS cache: `ipconfig /flushdns` (Windows)

### SSL Certificate Not Issued?
- Wait 5-10 minutes after DNS propagates
- Railway/Vercel auto-provisions SSL (Let's Encrypt)
- Check domain status in dashboard

### Frontend Can't Connect to API?
- Verify `NEXT_PUBLIC_API_BASE` is updated in Vercel
- Redeploy frontend after updating env var
- Check browser console for CORS errors

---

## Example Configuration

If your domain is `jarvis.ai`:

**Backend (Railway):**
- Domain: `api.jarvis.ai`
- DNS: CNAME `api` → Railway value

**Frontend (Vercel):**
- Domain: `jarvis.ai` (root) or `www.jarvis.ai`
- DNS: A record `@` → Vercel IP or CNAME `www` → Vercel value

**Environment Variable:**
- `NEXT_PUBLIC_API_BASE=https://api.jarvis.ai`

---

**Need Help?** Share your domain name and I'll provide specific DNS records!

