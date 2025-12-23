# Script to stop hanging test processes and restart tests with fixes
# This script stops the hanging pytest processes and runs tests again with timeout protection

Write-Host "=========================================="
Write-Host "Stopping Hanging Test Processes"
Write-Host "=========================================="

# List of hanging process IDs
$hangingPids = @(1048, 7588, 9584, 10068, 13140, 13800)

$stoppedCount = 0
foreach ($processId in $hangingPids) {
    try {
        $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
        if ($process) {
            Write-Host "Stopping process $processId ($($process.ProcessName))..."
            Stop-Process -Id $processId -Force -ErrorAction Stop
            $stoppedCount++
            Write-Host "  [OK] Stopped process $processId"
        } else {
            Write-Host "  - Process $processId not found (already stopped)"
        }
    } catch {
        Write-Host "  [WARNING] Error stopping process $processId : $_"
    }
}

Write-Host ""
Write-Host "Stopped $stoppedCount processes"
Write-Host ""

# Wait a moment for processes to fully terminate
Start-Sleep -Seconds 2

Write-Host "=========================================="
Write-Host "Installing pytest-timeout"
Write-Host "=========================================="

# Check if pytest-timeout is installed
try {
    $pytestTimeoutInstalled = pip show pytest-timeout 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Installing pytest-timeout..."
        pip install pytest-timeout>=2.0.0
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] pytest-timeout installed successfully"
        } else {
            Write-Host "[WARNING] Failed to install pytest-timeout. Tests may still hang."
        }
    } else {
        Write-Host "[OK] pytest-timeout already installed"
    }
} catch {
    Write-Host "[WARNING] Could not check pytest-timeout installation: $_"
    Write-Host "Attempting to install pytest-timeout..."
    pip install pytest-timeout>=2.0.0
}

Write-Host ""
Write-Host "=========================================="
Write-Host "Running Tests with Timeout Protection"
Write-Host "=========================================="

# Change to tests/unit directory
Push-Location "tests/unit"

try {
    Write-Host "Running CrewAI tests with timeout protection..."
    Write-Host ""
    
    # Run CrewAI tests specifically
    pytest test_agents.py -v --tb=short --timeout=10
    
    Write-Host ""
    Write-Host "Running Windows Apps tests with timeout protection..."
    Write-Host ""
    
    # Run Windows Apps tests
    pytest test_windows_apps.py -v --tb=short --timeout=10
    
    Write-Host ""
    Write-Host "=========================================="
    Write-Host "Test Run Complete"
    Write-Host "=========================================="
    
} catch {
    Write-Host "Error running tests: $_"
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "Note: Tests should complete within 10 seconds each."
Write-Host "If a test hangs, it will timeout and fail after 10 seconds."

