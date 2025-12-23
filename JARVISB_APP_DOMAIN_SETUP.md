# Custom Domain Setup for jarvisb.app

## ✅ Step 1: Vercel Frontend Domain (COMPLETED)

**Status**: ✅ Domain `jarvisb.app` added to Vercel project

The domain is configured and will automatically get SSL certificate. Vercel is managing the nameservers.

---

## 🔧 Step 2: Railway Backend Domain Setup

### Add `api.jarvisb.app` to Railway

**You need to do this in Railway Dashboard:**

1. **Go to Railway Dashboard**
   - Visit: https://railway.app
   - Select project: `wonderful-energy`
   - Select service: `railway-rag-api`
   - Click **"Settings"** tab
   - Scroll to **"Domains"** section

2. **Add Custom Domain**
   - Click **"Custom Domain"** button
   - Enter: `api.jarvisb.app`
   - Click **"Add Domain"**

3. **Railway will show you DNS records**
   - You'll see something like:
     ```
     Type: CNAME
     Name: api
     Value: [Railway-provided value, e.g., cname.railway.app or similar]
     ```

4. **Copy the DNS record values** Railway provides

---

## 📝 Step 3: Add DNS Records for Railway

Since Vercel is managing your nameservers, you have two options:

### Option A: Add DNS Record via Vercel Dashboard (Recommended)

1. **Go to Vercel Dashboard**
   - Visit: https://vercel.com
   - Select project: `next-holo-ui`
   - Click **"Settings"** → **"Domains"**
   - Click on `jarvisb.app`
   - Look for **"DNS Records"** or **"DNS Configuration"** section

2. **Add CNAME Record**
   - **Type**: CNAME
   - **Name**: `api`
   - **Value**: [The Railway-provided value from Step 2]
   - **TTL**: 3600 (or Auto)
   - Click **"Add Record"**

### Option B: Add DNS Record via Domain Registrar

If your domain registrar allows DNS management even with Vercel nameservers:

1. **Log in to your domain registrar**
2. **Find DNS Management** section
3. **Add CNAME Record**:
   - **Type**: CNAME
   - **Name**: `api`
   - **Value**: [Railway-provided value]
   - **TTL**: 3600

---

## ⏱️ Step 4: Wait for DNS Propagation

- **DNS Propagation**: 5 minutes to 1 hour (usually ~15 minutes)
- **Railway SSL**: Automatically provisions after DNS propagates (~5-10 minutes)

**Check DNS Propagation:**
- Visit: https://dnschecker.org
- Enter: `api.jarvisb.app`
- Check if CNAME record is visible globally

**Test Railway Domain:**
- Visit: `https://api.jarvisb.app/health`
- Should return: `{"status":"healthy"}`

---

## 🔄 Step 5: Update Vercel Environment Variable

After Railway domain is active and SSL is provisioned:

1. **Update Environment Variable via CLI:**
   ```bash
   cd next-holo-ui
   vercel env rm NEXT_PUBLIC_API_BASE production
   vercel env add NEXT_PUBLIC_API_BASE production
   # Enter: https://api.jarvisb.app
   ```

2. **Or via Vercel Dashboard:**
   - Go to: https://vercel.com → Project → Settings → Environment Variables
   - Edit `NEXT_PUBLIC_API_BASE`
   - Change from: `https://railway-rag-api-production.up.railway.app`
   - Change to: `https://api.jarvisb.app`
   - Save

3. **Redeploy Frontend:**
   ```bash
   cd next-holo-ui
   vercel --prod
   ```

---

## ✅ Step 6: Verify Everything Works

1. **Test Backend:**
   - Visit: `https://api.jarvisb.app/health`
   - Should return: `{"status":"healthy"}`

2. **Test Frontend:**
   - Visit: `https://jarvisb.app`
   - Frontend should load
   - Check browser console (F12) → Network tab
   - Verify API calls go to `api.jarvisb.app`

3. **Test Full Stack:**
   - Try a query/feature in the frontend
   - Should work with custom domain

---

## 📋 Summary

**Your domains will be:**
- **Frontend**: `https://jarvisb.app` (Vercel) ✅ Configured
- **Backend API**: `https://api.jarvisb.app` (Railway) ⏳ Needs setup

**Next Actions:**
1. ✅ Vercel domain added
2. ⏳ Add `api.jarvisb.app` in Railway dashboard
3. ⏳ Add CNAME record for `api` subdomain
4. ⏳ Wait for DNS/SSL propagation
5. ⏳ Update `NEXT_PUBLIC_API_BASE` environment variable
6. ⏳ Redeploy frontend

---

## 🆘 Troubleshooting

### Railway domain not working?
- Check DNS propagation: https://dnschecker.org
- Verify CNAME record is correct
- Wait up to 1 hour for full propagation

### SSL certificate not issued?
- Wait 5-10 minutes after DNS propagates
- Check Railway dashboard for domain status
- Railway auto-provisions SSL (Let's Encrypt)

### Frontend can't connect to API?
- Verify `NEXT_PUBLIC_API_BASE` is updated
- Redeploy frontend after updating env var
- Check browser console for errors

---

**Ready to proceed?** 
1. Go to Railway dashboard and add `api.jarvisb.app`
2. Share the DNS record Railway provides
3. I'll help you add it to Vercel DNS

