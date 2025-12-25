# Frontend Testing Script for Jarvis UI (PowerShell)
# Tests all components and API connectivity

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Frontend Testing Script" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$API_BASE_URL = if ($env:API_BASE_URL) { $env:API_BASE_URL } else { "http://localhost:8000" }
$FRONTEND_URL = if ($env:FRONTEND_URL) { $env:FRONTEND_URL } else { "http://localhost:3000" }

Write-Host "API Base URL: $API_BASE_URL"
Write-Host "Frontend URL: $FRONTEND_URL"
Write-Host ""

# Check if API is running
Write-Host "Checking API connectivity..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$API_BASE_URL/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "✓ API is running" -ForegroundColor Green
} catch {
    Write-Host "✗ API is not running at $API_BASE_URL" -ForegroundColor Red
    Write-Host "Please start the API first: cd rag-api && uvicorn app:app --reload" -ForegroundColor Yellow
    exit 1
}

# Check if frontend is running
Write-Host "Checking frontend connectivity..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$FRONTEND_URL" -UseBasicParsing -TimeoutSec 5
    Write-Host "✓ Frontend is running" -ForegroundColor Green
} catch {
    Write-Host "⚠ Frontend is not running at $FRONTEND_URL" -ForegroundColor Yellow
    Write-Host "Please start the frontend first: cd next-holo-ui && npm run dev" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Testing API Endpoints" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Test endpoints
$endpoints = @(
    "/",
    "/health",
    "/metrics",
    "/memory?user_id=test",
    "/live-sessions?user_id=test"
)

foreach ($endpoint in $endpoints) {
    Write-Host -NoNewline "Testing $endpoint... "
    try {
        $response = Invoke-WebRequest -Uri "$API_BASE_URL$endpoint" -UseBasicParsing -TimeoutSec 5
        Write-Host "✓" -ForegroundColor Green
    } catch {
        Write-Host "✗" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Component Checklist" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Please manually verify the following components:"
Write-Host ""
Write-Host "Core Components:"
Write-Host "  [ ] BudgetStatus component renders"
Write-Host "  [ ] MemoryPanel component renders"
Write-Host "  [ ] BrowserPanel component renders"
Write-Host "  [ ] UncertaintyBanner component renders"
Write-Host ""
Write-Host "Feature Components:"
Write-Host "  [ ] ImageGenerator component renders"
Write-Host "  [ ] SpotifyPlayer component renders"
Write-Host "  [ ] MusicCreator component renders"
Write-Host "  [ ] SocialMediaPoster component renders"
Write-Host "  [ ] WordProcessor component renders"
Write-Host ""
Write-Host "UI Components:"
Write-Host "  [ ] ThemeToggle works"
Write-Host "  [ ] Dark mode switches correctly"
Write-Host "  [ ] Buttons are clickable"
Write-Host "  [ ] Cards display correctly"
Write-Host ""
Write-Host "API Integration:"
Write-Host "  [ ] Components can fetch data from API"
Write-Host "  [ ] Error states display correctly"
Write-Host "  [ ] Loading states display correctly"
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Testing Complete" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

