# Testing Scripts

This directory contains comprehensive testing scripts for the Jarvis RAG API.

## Scripts

### `test_api.py`
Comprehensive API endpoint testing script.

**Usage:**
```bash
python scripts/test_api.py [--base-url BASE_URL]
```

**Features:**
- Tests all API endpoints
- Validates response status codes
- Tests authentication flow
- Tests rate limiting
- Generates test report

**Example:**
```bash
# Test local API
python scripts/test_api.py

# Test remote API
python scripts/test_api.py --base-url https://api.example.com
```

### `test_integration.py`
Integration testing script for complete user flows.

**Usage:**
```bash
python scripts/test_integration.py [--base-url BASE_URL]
```

**Features:**
- Tests complete query flow with memory
- Tests live session lifecycle
- Tests browser automation flow
- Tests reasoning workflows
- Tests media generation flows

**Example:**
```bash
# Test local integration
python scripts/test_integration.py

# Test remote integration
python scripts/test_integration.py --base-url https://api.example.com
```

## Installation

Install required dependencies:

```bash
pip install httpx colorama pytest pytest-asyncio
```

Or install from requirements:

```bash
pip install -r requirements.txt
```

## Running Tests

### Quick Test
```bash
# Start API first
cd rag-api
uvicorn app:app --reload

# In another terminal, run tests
python scripts/test_api.py
```

### Full Integration Test
```bash
# Start API first
cd rag-api
uvicorn app:app --reload

# In another terminal, run integration tests
python scripts/test_integration.py
```

## Test Results

Test results are saved as JSON files:
- `test_results_YYYYMMDD_HHMMSS.json` - API test results
- Integration test results are printed to console

## Environment Variables

Set these environment variables for testing:

```bash
export OPENAI_API_KEY=your-key
export REDIS_URL=redis://localhost:6379
export USE_FIRESTORE_SESSIONS=false
export USE_BIGQUERY_MEMORY=false
```

## Troubleshooting

### API not running
Make sure the API is running on the specified base URL:
```bash
curl http://localhost:8000/health
```

### Authentication failures
Some tests require authentication. Make sure JWT is configured:
```bash
export JWT_SECRET=your-secret
```

### Rate limiting
If rate limiting is too aggressive, adjust in environment:
```bash
export RATE_LIMIT_ENABLED=false
```

