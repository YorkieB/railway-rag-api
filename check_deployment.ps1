# Deployment Status Checker
# This script verifies that both frontend and backend are deploying correctly

Write-Host "=== Deployment Status Checker ===" -ForegroundColor Cyan
Write-Host ""

# Check if code is pushed
Write-Host "1. Checking Git Status..." -ForegroundColor Yellow
$gitStatus = git status --short
if ($gitStatus) {
    Write-Host "   ⚠️  WARNING: You have uncommitted changes!" -ForegroundColor Red
    Write-Host "   Run: git add . && git commit -m 'message' && git push" -ForegroundColor Yellow
} else {
    Write-Host "   ✅ All changes committed" -ForegroundColor Green
}

$branch = git branch --show-current
Write-Host "   Current branch: $branch" -ForegroundColor Gray

# Check if connected to remote
Write-Host ""
Write-Host "2. Checking Git Remote..." -ForegroundColor Yellow
$remote = git remote get-url origin
if ($remote) {
    Write-Host "   ✅ Remote configured: $remote" -ForegroundColor Green
} else {
    Write-Host "   ❌ No remote configured!" -ForegroundColor Red
    Write-Host "   Run: git remote add origin <your-repo-url>" -ForegroundColor Yellow
}

# Test Railway backend
Write-Host ""
Write-Host "3. Testing Railway Backend..." -ForegroundColor Yellow
$railwayUrl = "https://railway-rag-api-production.up.railway.app"
try {
    $response = Invoke-WebRequest -Uri "$railwayUrl/health" -Method GET -TimeoutSec 10 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✅ Backend is LIVE at: $railwayUrl" -ForegroundColor Green
        $healthData = $response.Content | ConvertFrom-Json
        Write-Host "   Status: $($healthData.status)" -ForegroundColor Gray
    }
} catch {
    Write-Host "   ❌ Backend is NOT responding!" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   Check Railway dashboard: https://railway.app" -ForegroundColor Yellow
}

# Instructions
Write-Host ""
Write-Host "=== Next Steps ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "If changes aren't appearing:" -ForegroundColor Yellow
Write-Host "1. Verify code is pushed: git push origin main" -ForegroundColor White
Write-Host "2. Check Railway dashboard: https://railway.app" -ForegroundColor White
Write-Host "   - Go to your project → rag-api service" -ForegroundColor Gray
Write-Host "   - Check Deployments tab for latest build" -ForegroundColor Gray
Write-Host "   - Verify Root Directory is set to 'rag-api'" -ForegroundColor Gray
Write-Host "3. Check Vercel dashboard: https://vercel.com" -ForegroundColor White
Write-Host "   - Go to your project → next-holo-ui" -ForegroundColor Gray
Write-Host "   - Check Deployments tab for latest build" -ForegroundColor Gray
Write-Host "   - Verify Root Directory is set to 'next-holo-ui'" -ForegroundColor Gray
Write-Host ""
Write-Host "For detailed instructions, see: DEPLOYMENT_VERIFICATION.md" -ForegroundColor Cyan

