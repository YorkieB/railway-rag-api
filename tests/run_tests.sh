#!/bin/bash
# Test runner script for Jarvis evaluation suite

set -e

echo "=========================================="
echo "Jarvis Test Suite Runner"
echo "=========================================="

API_BASE="${API_BASE:-http://localhost:8080}"
USER_ID="${USER_ID:-test_user}"

# Check if API is available
echo "Checking API availability..."
if ! curl -s "${API_BASE}/health" > /dev/null; then
    echo "❌ API not available at ${API_BASE}"
    echo "Please start the API server first:"
    echo "  cd rag-api && uvicorn app:app --reload"
    exit 1
fi
echo "✅ API is available"

# Run unit tests
echo ""
echo "=========================================="
echo "Running Unit Tests"
echo "=========================================="
cd unit
python -m pytest test_*.py -v || echo "⚠️  Some unit tests failed"
cd ..

# Run integration tests
echo ""
echo "=========================================="
echo "Running Integration Tests"
echo "=========================================="
cd integration
python -m pytest test_*.py -v --api-base="${API_BASE}" || echo "⚠️  Some integration tests failed"
cd ..

# Run evaluation suite
echo ""
echo "=========================================="
echo "Running RAG & Memory Evaluation Suite"
echo "=========================================="
cd rag_memory_eval
python runner.py --api-base="${API_BASE}" --user-id="${USER_ID}" || echo "⚠️  Evaluation suite failed"
cd ..

# Run regression test
echo ""
echo "=========================================="
echo "Running Regression Test"
echo "=========================================="
cd rag_memory_eval
if [ -f "baseline.json" ] && [ -f "results.json" ]; then
    python regressiontest.py || echo "⚠️  Regression test failed"
else
    echo "⚠️  Baseline or results file not found. Skipping regression test."
    echo "   First run will create baseline."
fi
cd ..

echo ""
echo "=========================================="
echo "Test Suite Complete"
echo "=========================================="

