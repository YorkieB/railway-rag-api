# Comprehensive Test Suite for Jarvis RAG API
# Tests all endpoints including V3 features

$baseUrl = "http://localhost:8080"
$testResults = @()
$passed = 0
$failed = 0

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Method,
        [string]$Path,
        [hashtable]$Body = $null,
        [hashtable]$Params = $null,
        [int]$ExpectedStatus = 200
    )
    
    Write-Host "Testing: $Name" -ForegroundColor Cyan -NoNewline
    Write-Host " [$Method $Path]" -ForegroundColor Gray
    
    try {
        $uri = "$baseUrl$Path"
        if ($Params) {
            $queryString = ($Params.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join "&"
            $uri += "?$queryString"
        }
        
        $headers = @{"Content-Type" = "application/json"}
        
        if ($Method -eq "GET") {
            $response = Invoke-WebRequest -Uri $uri -Method GET -Headers $headers -ErrorAction Stop
        } elseif ($Method -eq "POST") {
            $jsonBody = if ($Body) { $Body | ConvertTo-Json -Depth 10 } else { "{}" }
            $response = Invoke-WebRequest -Uri $uri -Method POST -Body $jsonBody -Headers $headers -ErrorAction Stop
        } elseif ($Method -eq "PUT") {
            $jsonBody = if ($Body) { $Body | ConvertTo-Json -Depth 10 } else { "{}" }
            $response = Invoke-WebRequest -Uri $uri -Method PUT -Body $jsonBody -Headers $headers -ErrorAction Stop
        } elseif ($Method -eq "DELETE") {
            $response = Invoke-WebRequest -Uri $uri -Method DELETE -Headers $headers -ErrorAction Stop
        }
        
        if ($response.StatusCode -eq $ExpectedStatus) {
            Write-Host "  ✅ PASSED" -ForegroundColor Green
            $script:passed++
            $script:testResults += @{
                Name = $Name
                Status = "PASSED"
                StatusCode = $response.StatusCode
            }
            return $true
        } else {
            Write-Host "  ❌ FAILED (Expected $ExpectedStatus, got $($response.StatusCode))" -ForegroundColor Red
            $script:failed++
            $script:testResults += @{
                Name = $Name
                Status = "FAILED"
                StatusCode = $response.StatusCode
                Expected = $ExpectedStatus
            }
            return $false
        }
    } catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        if ($statusCode -eq $ExpectedStatus -or ($ExpectedStatus -eq 200 -and $statusCode -ge 200 -and $statusCode -lt 300)) {
            Write-Host "  ✅ PASSED (Status: $statusCode)" -ForegroundColor Green
            $script:passed++
            $script:testResults += @{
                Name = $Name
                Status = "PASSED"
                StatusCode = $statusCode
            }
            return $true
        } else {
            Write-Host "  ❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
            $script:failed++
            $script:testResults += @{
                Name = $Name
                Status = "FAILED"
                Error = $_.Exception.Message
                StatusCode = $statusCode
            }
            return $false
        }
    }
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  JARVIS RAG API - FULL TEST SUITE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if server is running
Write-Host "Checking server status..." -ForegroundColor Yellow
try {
    $healthCheck = Invoke-WebRequest -Uri "$baseUrl/health" -Method GET -TimeoutSec 5
    Write-Host "✅ Server is running" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "❌ Server is not running!" -ForegroundColor Red
    Write-Host "Please start the server first:" -ForegroundColor Yellow
    Write-Host "  cd rag-api" -ForegroundColor White
    Write-Host "  uvicorn app:app --reload --port 8080" -ForegroundColor White
    exit 1
}

Write-Host "Starting comprehensive tests..." -ForegroundColor Yellow
Write-Host ""

# ============================================
# CORE API TESTS
# ============================================
Write-Host "=== CORE API ===" -ForegroundColor Magenta
Test-Endpoint -Name "Health Check" -Method "GET" -Path "/health"
Test-Endpoint -Name "Root Endpoint" -Method "GET" -Path "/"
Test-Endpoint -Name "List Documents" -Method "GET" -Path "/documents"

Write-Host ""

# ============================================
# V3 FEATURES - INTEGRATIONS
# ============================================
Write-Host "=== V3: INTEGRATIONS ===" -ForegroundColor Magenta
Test-Endpoint -Name "List Integrations" -Method "GET" -Path "/integrations"
Test-Endpoint -Name "Zapier Status" -Method "GET" -Path "/integrations/zapier/status"
Test-Endpoint -Name "Slack Status" -Method "GET" -Path "/integrations/slack/status"
Test-Endpoint -Name "Email Status" -Method "GET" -Path "/integrations/email/status"
Test-Endpoint -Name "Spotify Status" -Method "GET" -Path "/integrations/spotify/status"

Write-Host ""

# ============================================
# V3 FEATURES - MEMORY
# ============================================
Write-Host "=== V3: MEMORY FEATURES ===" -ForegroundColor Magenta
Test-Endpoint -Name "List Memory Templates" -Method "GET" -Path "/memory/templates"
Test-Endpoint -Name "List Memories" -Method "GET" -Path "/memory" -Params @{user_id="test_user"}
Test-Endpoint -Name "Memory Clustering" -Method "POST" -Path "/memory/cluster" -Params @{user_id="test_user"} -ExpectedStatus 200
Test-Endpoint -Name "Memory Conflicts" -Method "GET" -Path "/memory/conflicts" -Params @{user_id="test_user"} -ExpectedStatus 200

Write-Host ""

# ============================================
# V3 FEATURES - COLLABORATION
# ============================================
Write-Host "=== V3: COLLABORATION ===" -ForegroundColor Magenta
$collabSession = Test-Endpoint -Name "Create Collaboration Session" -Method "POST" -Path "/collaboration/sessions" -Body @{
    owner_id = "test_user"
    session_type = "browser"
    target_id = "test_session"
}
if ($collabSession) {
    $sessionData = ($response.Content | ConvertFrom-Json)
    $sessionId = $sessionData.session_id
    Test-Endpoint -Name "Get Collaboration Session" -Method "GET" -Path "/collaboration/sessions/$sessionId"
    Test-Endpoint -Name "List Collaboration Sessions" -Method "GET" -Path "/collaboration/sessions" -Params @{user_id="test_user"}
}

Write-Host ""

# ============================================
# V3 FEATURES - AGENTS
# ============================================
Write-Host "=== V3: AGENTS ===" -ForegroundColor Magenta
Test-Endpoint -Name "Agent Marketplace" -Method "GET" -Path "/agents/marketplace"
Test-Endpoint -Name "Agent Status" -Method "GET" -Path "/agents/status"
Test-Endpoint -Name "Agent Learning" -Method "POST" -Path "/agents/test_agent/learn" -Body @{
    feedback = "Good job"
    pattern = @{
        agent_type = "browser"
        success = $true
    }
} -ExpectedStatus 200
Test-Endpoint -Name "Agent Improvement" -Method "POST" -Path "/agents/test_agent/improve" -ExpectedStatus 200

Write-Host ""

# ============================================
# V3 FEATURES - ANALYTICS
# ============================================
Write-Host "=== V3: ANALYTICS ===" -ForegroundColor Magenta
Test-Endpoint -Name "Usage Statistics" -Method "GET" -Path "/analytics/usage" -Params @{user_id="test_user"; days=30}
Test-Endpoint -Name "Cost Analysis" -Method "GET" -Path "/analytics/cost" -Params @{user_id="test_user"; days=30}
Test-Endpoint -Name "Performance Metrics" -Method "GET" -Path "/analytics/performance" -Params @{user_id="test_user"; days=30}

Write-Host ""

# ============================================
# V3 FEATURES - DOCUMENT PROCESSING
# ============================================
Write-Host "=== V3: DOCUMENT PROCESSING ===" -ForegroundColor Magenta
Test-Endpoint -Name "Document Categorization" -Method "POST" -Path "/documents/categorize" -Params @{
    text = "This is a meeting note about project planning and deadlines."
    user_id = "test_user"
} -ExpectedStatus 200
Test-Endpoint -Name "Document Summarization" -Method "POST" -Path "/documents/summarize" -Params @{
    text = "This is a long document about various topics that need to be summarized into a shorter version."
    max_length = 100
    user_id = "test_user"
} -ExpectedStatus 200

Write-Host ""

# ============================================
# EXISTING FEATURES - MEMORY API
# ============================================
Write-Host "=== EXISTING: MEMORY API ===" -ForegroundColor Magenta
Test-Endpoint -Name "Search Memories" -Method "POST" -Path "/memory/search" -Body @{
    user_id = "test_user"
    query = "test query"
    top_k = 5
} -ExpectedStatus 200

Write-Host ""

# ============================================
# EXISTING FEATURES - BROWSER AUTOMATION
# ============================================
Write-Host "=== EXISTING: BROWSER AUTOMATION ===" -ForegroundColor Magenta
$browserSession = Test-Endpoint -Name "Create Browser Session" -Method "POST" -Path "/browser/sessions" -Params @{user_id="test_user"}
if ($browserSession) {
    $browserData = ($response.Content | ConvertFrom-Json)
    $browserSessionId = $browserData.session_id
    Test-Endpoint -Name "Get AX Tree" -Method "GET" -Path "/browser/sessions/$browserSessionId/ax-tree" -ExpectedStatus 200
}

Write-Host ""

# ============================================
# SUMMARY
# ============================================
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TEST SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Total Tests: $($passed + $failed)" -ForegroundColor White
Write-Host "✅ Passed: $passed" -ForegroundColor Green
Write-Host "❌ Failed: $failed" -ForegroundColor Red
Write-Host ""

if ($failed -eq 0) {
    Write-Host "🎉 ALL TESTS PASSED!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Some tests failed. Check the output above for details." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Failed tests:" -ForegroundColor Red
    $testResults | Where-Object { $_.Status -eq "FAILED" } | ForEach-Object {
        Write-Host "  - $($_.Name)" -ForegroundColor Yellow
        if ($_.Error) {
            Write-Host "    Error: $($_.Error)" -ForegroundColor Gray
        }
    }
}

Write-Host ""

