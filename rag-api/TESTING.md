# Testing Guide for rag-api

## Quick Test

See `QUICK_TEST.md` for basic endpoint testing.

## Unit Tests

Run unit tests from project root:

```bash
cd rag-api
python -m unittest discover -s ../tests/unit -p "test_*.py" -v
```

Or run individual test files:

```bash
cd rag-api
python -m unittest ../tests/unit/test_uncertainty.py -v
python -m unittest ../tests/unit/test_budget.py -v
python -m unittest ../tests/unit/test_cost.py -v
```

## Integration Tests

Integration tests require the API server to be running:

```bash
# Terminal 1: Start API
cd rag-api
uvicorn app:app --reload --port 8080

# Terminal 2: Run tests
cd tests/integration
API_BASE=http://localhost:8080 python -m pytest test_rag_pipeline.py -v
```

## Evaluation Suite

The evaluation suite tests the full RAG pipeline with 25 test prompts:

```bash
# Start API server first
cd rag-api
uvicorn app:app --reload --port 8080

# Run evaluation suite
cd tests/rag_memory_eval
python runner.py --api-base=http://localhost:8080 --user-id=test_user
```

### Evaluation Categories

1. **RAG Success** (5 prompts): Should retrieve and cite sources
2. **Empty Retrieval** (5 prompts): Should return uncertain responses
3. **Memory Recall** (5 prompts): Should retrieve and cite memories
4. **Private Session** (3 prompts): Should respect privacy flag
5. **Long Chat** (3 prompts): Should manage context budget
6. **Ambiguous Queries** (4 prompts): Should ask for clarification

### Scoring

- **10 points**: Exact retrieval with citation, or explicit uncertainty admission
- **7 points**: Correct but no source cited
- **5 points**: Admits lack but vague suggestion
- **0 points**: Hallucinated or wrong answer

### Success Criteria

- Average Score: ≥ 7.0 (PASS)
- Hallucination Rate: ≤ 2% (PASS)
- Critical Prompts: All must score ≥ 7.0 (PASS)

## Regression Testing

Compare current results to baseline:

```bash
cd tests/rag_memory_eval
python regressiontest.py
```

Regression test will:
- Block on score drop >10%
- Block on hallucination rate increase >50%
- Block on critical prompt failures

## Test Coverage

Current test coverage:
- ✅ Uncertainty protocol (unit tests)
- ✅ Context budget enforcement (unit tests)
- ✅ Cost tracking (unit tests)
- ✅ RAG pipeline (integration tests)
- ✅ Evaluation suite (25 prompts)

## Continuous Integration

Tests are designed to run in CI/CD:
- Unit tests: Fast, no dependencies
- Integration tests: Require API server
- Evaluation suite: Comprehensive, slower

See `tests/README.md` for full test suite documentation.

