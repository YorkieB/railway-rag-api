# Test runner script for Jarvis evaluation suite (PowerShell)

$ErrorActionPreference = "Stop"

$API_BASE = if ($env:API_BASE) { $env:API_BASE } else { "http://localhost:8080" }
$USER_ID = if ($env:USER_ID) { $env:USER_ID } else { "test_user" }

Write-Host "=========================================="
Write-Host "Jarvis Test Suite Runner"
Write-Host "=========================================="

# Check if API is available
Write-Host "Checking API availability..."
try {
    $response = Invoke-WebRequest -Uri "$API_BASE/health" -Method GET -TimeoutSec 2 -UseBasicParsing
    Write-Host "✅ API is available"
} catch {
    Write-Host "❌ API not available at $API_BASE"
    Write-Host "Please start the API server first:"
    Write-Host "  cd rag-api && uvicorn app:app --reload"
    exit 1
}

# Run unit tests
Write-Host ""
Write-Host "=========================================="
Write-Host "Running Unit Tests"
Write-Host "=========================================="
Push-Location unit
try {
    python -m pytest test_*.py -v
} catch {
    Write-Host "⚠️  Some unit tests failed"
}
Pop-Location

# Run integration tests
Write-Host ""
Write-Host "=========================================="
Write-Host "Running Integration Tests"
Write-Host "=========================================="
Push-Location integration
$env:API_BASE = $API_BASE
try {
    python -m pytest test_*.py -v
} catch {
    Write-Host "⚠️  Some integration tests failed"
}
Pop-Location

# Run evaluation suite
Write-Host ""
Write-Host "=========================================="
Write-Host "Running RAG & Memory Evaluation Suite"
Write-Host "=========================================="
Push-Location rag_memory_eval
try {
    python runner.py --api-base="$API_BASE" --user-id="$USER_ID"
} catch {
    Write-Host "⚠️  Evaluation suite failed"
}
Pop-Location

# Run regression test
Write-Host ""
Write-Host "=========================================="
Write-Host "Running Regression Test"
Write-Host "=========================================="
Push-Location rag_memory_eval
if ((Test-Path "baseline.json") -and (Test-Path "results.json")) {
    try {
        python regressiontest.py
    } catch {
        Write-Host "⚠️  Regression test failed"
    }
} else {
    Write-Host "⚠️  Baseline or results file not found. Skipping regression test."
    Write-Host "   First run will create baseline."
}
Pop-Location

Write-Host ""
Write-Host "=========================================="
Write-Host "Test Suite Complete"
Write-Host "=========================================="

