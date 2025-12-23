# Test V3 Endpoints
# Make sure the server is running: cd rag-api && uvicorn app:app --reload

$baseUrl = "http://localhost:8080"

Write-Host "Testing V3 Endpoints..." -ForegroundColor Cyan
Write-Host ""

# Test 1: List Integrations
Write-Host "1. Testing /integrations endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/integrations" -Method GET
    $data = $response.Content | ConvertFrom-Json
    Write-Host "   ✅ Success! Found $($data.count) integrations" -ForegroundColor Green
    $data.integrations | ForEach-Object { Write-Host "      - $($_.name): $($_.status)" }
} catch {
    Write-Host "   ❌ Failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 2: List Memory Templates
Write-Host "2. Testing /memory/templates endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/memory/templates" -Method GET
    $data = $response.Content | ConvertFrom-Json
    Write-Host "   ✅ Success! Found $($data.count) templates" -ForegroundColor Green
    $data.templates | ForEach-Object { Write-Host "      - $($_.name): $($_.description)" }
} catch {
    Write-Host "   ❌ Failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 3: Agent Marketplace
Write-Host "3. Testing /agents/marketplace endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/agents/marketplace" -Method GET
    $data = $response.Content | ConvertFrom-Json
    Write-Host "   ✅ Success!" -ForegroundColor Green
    Write-Host "      Custom agents: $($data.custom_agents.Count)" -ForegroundColor White
    Write-Host "      Marketplace agents: $($data.marketplace_agents.Count)" -ForegroundColor White
} catch {
    Write-Host "   ❌ Failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 4: Analytics Usage
Write-Host "4. Testing /analytics/usage endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/analytics/usage?user_id=test_user&days=30" -Method GET
    $data = $response.Content | ConvertFrom-Json
    Write-Host "   ✅ Success! User: $($data.user_id)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 5: Create Collaboration Session
Write-Host "5. Testing /collaboration/sessions endpoint..." -ForegroundColor Yellow
try {
    $body = @{
        owner_id = "test_user"
        session_type = "browser"
        target_id = "test_session"
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri "$baseUrl/collaboration/sessions" -Method POST -Body $body -ContentType "application/json"
    $data = $response.Content | ConvertFrom-Json
    Write-Host "   ✅ Success! Session ID: $($data.session_id)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Testing complete!" -ForegroundColor Cyan

