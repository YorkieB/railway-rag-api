# PowerShell Test Runner for Jarvis API
# This script helps run tests with proper path handling

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Jarvis API Test Runner" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ragApiDir = if ($scriptDir -like "*rag-api*") { $scriptDir } else { Join-Path $scriptDir "rag-api" }

Write-Host "Working directory: $ragApiDir" -ForegroundColor Yellow
Write-Host ""

# Check if API is running
Write-Host "Checking if API is running..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
    Write-Host "[PASS] API is running!" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "[FAIL] API is not running" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please start the API first in another terminal:" -ForegroundColor Yellow
    Write-Host "  cd $ragApiDir" -ForegroundColor White
    Write-Host "  python -m uvicorn app:app --reload" -ForegroundColor White
    Write-Host ""
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

# Change to rag-api directory
Set-Location $ragApiDir

# Menu
Write-Host "Select test to run:" -ForegroundColor Cyan
Write-Host "  1. Quick Test (5 core endpoints)" -ForegroundColor White
Write-Host "  2. Full API Tests (all endpoints)" -ForegroundColor White
Write-Host "  3. Integration Tests (user flows)" -ForegroundColor White
Write-Host "  4. Run All Tests" -ForegroundColor White
Write-Host ""
$choice = Read-Host "Enter choice (1-4)"

Write-Host ""

switch ($choice) {
    "1" {
        Write-Host "Running Quick Test..." -ForegroundColor Yellow
        python quick_test.py
    }
    "2" {
        Write-Host "Running Full API Tests..." -ForegroundColor Yellow
        python scripts\test_api.py
    }
    "3" {
        Write-Host "Running Integration Tests..." -ForegroundColor Yellow
        python scripts\test_integration.py
    }
    "4" {
        Write-Host "Running All Tests..." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "--- Quick Test ---" -ForegroundColor Cyan
        python quick_test.py
        Write-Host ""
        Write-Host "--- Full API Tests ---" -ForegroundColor Cyan
        python scripts\test_api.py
        Write-Host ""
        Write-Host "--- Integration Tests ---" -ForegroundColor Cyan
        python scripts\test_integration.py
    }
    default {
        Write-Host "Invalid choice" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Tests complete!" -ForegroundColor Green
Write-Host ""

