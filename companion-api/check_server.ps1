# Quick server status checker
Write-Host "`n🔍 Checking server status...`n" -ForegroundColor Cyan

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080/health" -UseBasicParsing -TimeoutSec 2
    Write-Host "✅ Server is RUNNING!" -ForegroundColor Green
    Write-Host "`nResponse:" -ForegroundColor White
    $response.Content | ConvertFrom-Json | ConvertTo-Json
    Write-Host "`n🌐 Server URL: http://localhost:8080" -ForegroundColor Cyan
    Write-Host "📋 Health Check: http://localhost:8080/health" -ForegroundColor Cyan
    Write-Host "📚 API Docs: http://localhost:8080/docs`n" -ForegroundColor Cyan
} catch {
    Write-Host "⏳ Server is not ready yet..." -ForegroundColor Yellow
    Write-Host "`nThe server may still be:" -ForegroundColor Gray
    Write-Host "  • Installing dependencies" -ForegroundColor Gray
    Write-Host "  • Creating virtual environment" -ForegroundColor Gray
    Write-Host "  • Starting up`n" -ForegroundColor Gray
    Write-Host "💡 Wait 1-2 minutes and run this script again, or check the terminal window.`n" -ForegroundColor Yellow
}

