# Jarvis Test Suite

This directory contains the comprehensive test suite for Jarvis, including unit tests, integration tests, and evaluation harnesses.

## Structure

```
tests/
├── unit/                    # Unit tests for individual components
│   ├── test_uncertainty.py
│   ├── test_budget.py
│   └── test_cost.py
├── integration/             # Integration tests for full pipeline
│   └── test_rag_pipeline.py
└── rag_memory_eval/         # RAG & Memory evaluation suite
    ├── prompts.json        # 25 test prompts
    ├── runner.py           # Evaluation runner
    ├── regressiontest.py   # Regression test against baseline
    └── baseline.json       # Baseline results
```

## Running Tests

### All Tests

**Linux/Mac:**
```bash
cd tests
chmod +x run_tests.sh
./run_tests.sh
```

**Windows (PowerShell):**
```powershell
cd tests
.\run_tests.ps1
```

### Individual Test Suites

**Unit Tests:**
```bash
cd tests/unit
python -m pytest test_*.py -v
```

**Integration Tests:**
```bash
cd tests/integration
API_BASE=http://localhost:8080 python -m pytest test_*.py -v
```

**Evaluation Suite:**
```bash
cd tests/rag_memory_eval
python runner.py --api-base=http://localhost:8080 --user-id=test_user
```

**Regression Test:**
```bash
cd tests/rag_memory_eval
python regressiontest.py
```

## Evaluation Suite

The evaluation suite tests:
- **RAG Success** (5 prompts): Should retrieve and cite sources
- **Empty Retrieval** (5 prompts): Should return uncertain responses
- **Memory Recall** (5 prompts): Should retrieve and cite memories
- **Private Session** (3 prompts): Should respect privacy flag
- **Long Chat** (3 prompts): Should manage context budget
- **Ambiguous Queries** (4 prompts): Should ask for clarification

### Scoring Rubric

- **10 points**: Exact retrieval with citation, or explicit uncertainty admission
- **7 points**: Correct but no source cited
- **5 points**: Admits lack but vague suggestion
- **0 points**: Hallucinated or wrong answer

### Success Criteria

- Average Score: ≥ 7.0 (PASS)
- Hallucination Rate: ≤ 2% (PASS)
- Critical Prompts: All must score ≥ 7.0 (PASS)
- Regression Tolerance: ±10% (PASS)

## Regression Testing

The regression test compares current results to baseline:
- Blocks merge on score drop >10%
- Blocks merge on hallucination rate increase >50%
- Blocks merge if critical prompts drop below threshold

To update baseline after improvements:
```bash
cd tests/rag_memory_eval
cp results.json baseline.json
```

## Prerequisites

1. **API Server Running**: Start `rag-api` before running tests
   ```bash
   cd rag-api
   uvicorn app:app --reload
   ```

2. **Python Dependencies**: Install test dependencies
   ```bash
   pip install pytest requests
   ```

3. **Test Data**: Upload some test documents to the knowledge base for RAG tests

## CI/CD Integration

The test suite is designed to run in CI/CD pipelines:
- GitHub Actions workflow: `.github/workflows/eval-suite.yml` (to be created)
- Blocks merge on regression failures
- Generates test reports

