# Jarvis Implementation TODO List

**Last Updated:** 2025-01-XX  
**Current Sprint:** 1.1 - Context Budget & Memory Foundation

---

## 🎯 Sprint 1.1: Context Budget & Memory Foundation (Week 1)

### Context Budget Enforcement

- [ ] **Create ContextBudgetEnforcer class** (`rag-api/budget.py`)
  - Track tokens per component (system, history, RAG docs)
  - Implement truncation/summarization when over budget
  - Warn at 80% utilization
  - Configuration: `MAX_CONTEXT_TOKENS=100000`, `WARN_THRESHOLD=0.8`

- [ ] **Integrate ContextBudgetEnforcer into /query endpoint**
  - Add budget checking before LLM call
  - Truncate history if needed
  - Return warning in response if at 80%

### Memory System

- [ ] **Create MemoryItem Pydantic model** (`rag-api/models.py`)
  ```python
  - id: str
  - user_id: str
  - project_id: Optional[str]
  - content: str
  - memory_type: str  # "fact", "preference", "decision"
  - created_at: datetime
  - updated_at: datetime
  ```

- [ ] **Create MemoryStorage interface** (abstract base class)
  - Define CRUD methods
  - Define search method

- [ ] **Implement BigQuery memory storage**
  - Create `memories` table in BigQuery
  - Implement all MemoryStorage methods
  - Or use Firestore if preferred

- [ ] **Implement POST /memory endpoint**
  - Create memory with validation
  - Respect `private_session` flag (no writes)

- [ ] **Implement GET /memory endpoint**
  - List memories (global + project-scoped)
  - Support `?project_id={id}` filter

- [ ] **Implement PUT /memory/{id} endpoint**
  - Update existing memory
  - Validate ownership

- [ ] **Implement DELETE /memory/{id} endpoint**
  - Delete memory
  - Validate ownership

- [ ] **Implement GET /memory/search endpoint**
  - Semantic search using embeddings
  - Return top-k relevant memories

- [ ] **Integrate memory retrieval into RAG pipeline**
  - Retrieve relevant memories before RAG query
  - Inject memories into LLM context
  - Show memory citations in response

---

## 🎯 Sprint 1.2: Uncertainty Protocol & Cost Tracking (Week 2)

### Uncertainty Protocol

- [ ] **Create UncertaintyChecker class** (`rag-api/uncertainty.py`)
  - Check RAG retrieval confidence
  - Generate structured uncertain responses:
    ```python
    {
        "answer": "I don't have information about X...",
        "uncertain": True,
        "suggestions": ["search the web", "ask you", "check documents"]
    }
    ```
  - Threshold: `RAG_CONFIDENCE_THRESHOLD=0.6`

- [ ] **Integrate UncertaintyChecker into /query endpoint**
  - Check retrieval results
  - Return uncertain response if needed
  - Never guess or fabricate

### Cost Tracking

- [ ] **Create CostTracker class** (`rag-api/cost.py`)
  - Track per-user daily budgets:
    - Text tokens: 500K/day
    - Vision tokens: 50K/day
    - Audio minutes: 60/day
    - Dollars: $10/day (configurable)

- [ ] **Set up user_daily_budgets table**
  - BigQuery or Firestore
  - Schema: user_id, date, tokens_used, vision_tokens_used, audio_minutes_used, dollars_used

- [ ] **Implement pre-query cost estimation**
  - Estimate tokens before API call
  - Check if within budget

- [ ] **Add cost tracking middleware**
  - Track token usage from API responses
  - Update daily budget after each request
  - Return cost info in headers: `X-Cost-Tokens`, `X-Cost-Dollars`

- [ ] **Implement cost warnings and halts**
  - Warning at 80%: return `{"warning": "Approaching daily limit"}`
  - Hard halt at 100%: return `{"error": "Daily limit reached"}`

---

## 🎯 Sprint 1.3: Frontend Integration (Week 3)

### Budget Status UI

- [ ] **Create BudgetStatus component** (`next-holo-ui/components/BudgetStatus.tsx`)
  - Display progress bars for:
    - Context usage (tokens)
    - Daily budget (tokens, cost, reset time)
  - Show warnings at 80%
  - Show error state at 100%
  - Add to StatusBar or new section

### RAG/Memory Transparency

- [ ] **Enhance SourcesPanel component**
  - Show which documents/memories were used
  - Display "No relevant context found" when uncertain
  - Add memory citations

### Memory Controls

- [ ] **Create MemoryPanel component** (`next-holo-ui/components/MemoryPanel.tsx`)
  - Toggle global/project memory on/off
  - Enter private-session mode (checkbox)
  - List/search/edit/delete memories
  - Add to SettingsDrawer or new tab

### API Client Updates

- [ ] **Update API client** (`next-holo-ui/lib/api.ts`)
  - Add memory CRUD functions:
    - `createMemory()`
    - `listMemories()`
    - `updateMemory()`
    - `deleteMemory()`
    - `searchMemories()`
  - Add `getBudgetStatus()` function
  - Handle uncertainty responses
  - Pass `private_session` flag in requests

---

## 🎯 Sprint 1.4: Testing & Documentation (Week 4)

### Evaluation Suite

- [ ] **Create tests/rag_memory_eval/ directory**
  - `__init__.py`
  - `prompts.json`
  - `runner.py`
  - `regressiontest.py`
  - `baseline.json`

- [ ] **Create prompts.json with 25 test cases**
  - RAG success (5 prompts)
  - Empty retrieval (5 prompts)
  - Memory recall (5 prompts)
  - Private session (3 prompts)
  - Long chat (3 prompts)
  - Ambiguous queries (4 prompts)

- [ ] **Implement runner.py**
  - Call `/query` endpoint
  - Parse answer + citations
  - Score 0-10 per rubric
  - Generate report.json

- [ ] **Implement regressiontest.py**
  - Compare to baseline.json
  - Block on score drop or hallucination increase
  - Update baseline on success

- [ ] **Create initial baseline.json**
  - Run eval suite once
  - Save results as baseline

### Unit Tests

- [ ] **Test ContextBudgetEnforcer**
  - Test truncation logic
  - Test warning at 80%
  - Test hard limit at 100%

- [ ] **Test UncertaintyChecker**
  - Test threshold logic
  - Test uncertain response format
  - Test suggestions generation

- [ ] **Test CostTracker**
  - Test budget tracking
  - Test warnings at 80%
  - Test halts at 100%

- [ ] **Test memory CRUD operations**
  - Test create/read/update/delete
  - Test search functionality
  - Test private session flag

### Integration Tests

- [ ] **Test full RAG pipeline with budget enforcement**
- [ ] **Test memory injection in RAG queries**
- [ ] **Test uncertainty protocol end-to-end**
- [ ] **Test cost tracking across multiple requests**

### Documentation

- [ ] **Update API documentation**
  - OpenAPI/Swagger docs
  - Document new endpoints (`/memory/*`)
  - Document cost headers
  - Document uncertainty responses

- [ ] **Update user documentation**
  - README with MVP features
  - Memory system usage guide
  - Budget/cost controls guide

---

## 🎯 Sprint 2.1: Enhanced Live Sessions (Week 5)

### LiveSession Model

- [ ] **Create LiveSession Pydantic model** (`rag-api/models.py`)
  - id, user_id, state, mode, timestamps
  - transcript fields, budget fields, recording consent

- [ ] **Set up LiveSession storage**
  - Firestore or BigQuery
  - Index by user_id and state

### LiveSession APIs

- [ ] **POST /live-sessions** - Create session
- [ ] **GET /live-sessions/{id}** - Get session status
- [ ] **PUT /live-sessions/{id}/pause** - Pause session
- [ ] **PUT /live-sessions/{id}/resume** - Resume session
- [ ] **DELETE /live-sessions/{id}** - End session
- [ ] **GET /live-sessions** - List user sessions

### LS1A Audio Pipeline

- [ ] **Integrate Deepgram WebSocket** (reuse companion-api pattern)
- [ ] **Integrate OpenAI streaming LLM**
- [ ] **Integrate ElevenLabs streaming TTS**
- [ ] **Implement barge-in detection** (VAD events)
- [ ] **Track audio minutes** in session state
- [ ] **Enforce daily audio budget** (60 min default)

### WebSocket Enhancement

- [ ] **Update /gemini-live/ws/{session_id}** to use LiveSession model
- [ ] **Handle session state transitions**
- [ ] **Send budget warnings at 80%**
- [ ] **Auto-pause at 100% budget**

---

## 🎯 Sprint 2.2: Browser Automation Foundation (Week 6)

- [ ] **Set up Playwright** (`rag-api/browser/`)
- [ ] **Create BrowserSession class**
- [ ] **Implement AX Tree extraction**
- [ ] **Create basic browser APIs** (sessions, navigate, ax-tree)
- [ ] **Implement safety guardrails** (blocklist, domain checks)

---

## 🎯 Sprint 2.3: Browser Automation Actions (Week 7)

- [ ] **Implement action executor** (click, type, extract)
- [ ] **Implement Plan-Act-Verify-Recover pattern**
- [ ] **Add uncertainty protocol for browser**
- [ ] **Create browser action APIs**

---

## 🎯 Sprint 2.4: Frontend Browser Integration (Week 8)

- [ ] **Create BrowserPanel component**
- [ ] **Implement browser session management**
- [ ] **Add browser controls to UI**
- [ ] **Display action history and safety warnings**

---

## 📋 Quick Reference

### Priority Order
1. **Sprint 1.1** - Foundation (budget, memory)
2. **Sprint 1.2** - Safety (uncertainty, cost)
3. **Sprint 1.3** - UX (frontend integration)
4. **Sprint 1.4** - Quality (testing, docs)

### Key Files to Create
- `rag-api/budget.py` - ContextBudgetEnforcer
- `rag-api/uncertainty.py` - UncertaintyChecker
- `rag-api/cost.py` - CostTracker
- `rag-api/models.py` - MemoryItem, LiveSession models
- `next-holo-ui/components/BudgetStatus.tsx`
- `next-holo-ui/components/MemoryPanel.tsx`
- `tests/rag_memory_eval/` - Eval suite

### Success Criteria
- ✅ Context budget enforced
- ✅ Memory system functional
- ✅ Uncertainty protocol active
- ✅ Cost tracking accurate
- ✅ Frontend shows all features
- ✅ Eval suite passing

---

**Next Action:** Start with Sprint 1.1, Task 1: Create ContextBudgetEnforcer class

