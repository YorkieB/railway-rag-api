# RAG API Unit Tests

Unit tests for RAG API components (Sprint 1.1 & 1.2).

## Running Tests

```bash
# Install pytest if not already installed
pip install pytest pytest-asyncio

# Run all tests
pytest rag-api/tests/

# Run specific test file
pytest rag-api/tests/test_budget.py

# Run with coverage
pytest rag-api/tests/ --cov=rag_api --cov-report=html
```

## Test Coverage

### Current Tests
- ✅ `test_budget.py` - ContextBudgetEnforcer tests
- ✅ `test_uncertainty.py` - UncertaintyChecker tests
- ✅ `test_cost.py` - CostTracker tests
- ✅ `test_memory_storage.py` - MemoryStorage tests

### Test Categories
- Token tracking and estimation
- Budget enforcement and truncation
- Uncertainty protocol
- Cost estimation and tracking
- Memory CRUD operations
- Memory search

## Adding New Tests

When adding new components:
1. Create test file: `test_<component>.py`
2. Follow existing test patterns
3. Use fixtures for setup/teardown
4. Test both success and error cases
5. Test edge cases and boundaries

