# Jarvis Implementation Plan

**Status:** Active Development  
**Last Updated:** 2025-01-XX  
**Phase:** MVP → V1 Transition

---

## Executive Summary

This plan outlines the implementation roadmap for Jarvis, building from the current MVP foundation toward V1 capabilities. The plan is organized into **sprints** with clear priorities, dependencies, and success criteria.

### Current State Assessment

**✅ What Exists:**
- **rag-api**: Basic RAG with BigQuery, document upload, Gemini Live WebSocket (simplified)
- **companion-api**: Real-time audio pipeline (Deepgram + OpenAI + ElevenLabs), ChromaDB memory
- **next-holo-ui**: Chat, document upload, Gemini Live UI, companion voice interface
- **Foundation**: BigQuery vector search, basic embeddings, document chunking

**❌ What's Missing (MVP Gaps):**
- Context budget enforcement
- Memory APIs (global/project-scoped)
- Uncertainty protocol enforcement
- Cost tracking & budgets
- Evaluation suite
- Proper session management

**🚧 V1 Requirements (Next Phase):**
- Browser automation (Playwright)
- Enhanced live sessions (screen share, video)
- Windows Companion
- Advanced safety guardrails

---

## Phase 1: Complete MVP (Weeks 1-4)

### Sprint 1.1: Context Budget & Memory Foundation (Week 1)

**Goal:** Implement context budget enforcement and basic memory system

#### Backend Tasks

1. **ContextBudgetEnforcer** (`rag-api/budget.py`)
   - [ ] Create `ContextBudgetEnforcer` class
   - [ ] Track tokens per component (system, history, RAG docs)
   - [ ] Implement truncation/summarization when over budget
   - [ ] Warn at 80% utilization
   - [ ] Integrate into `/query` endpoint
   - [ ] Add configuration: `MAX_CONTEXT_TOKENS=100000`, `WARN_THRESHOLD=0.8`

2. **Memory Data Models** (`rag-api/models.py`)
   - [ ] Create `MemoryItem` Pydantic model:
     ```python
     class MemoryItem(BaseModel):
         id: str
         user_id: str
         project_id: Optional[str]
         content: str
         memory_type: str  # "fact", "preference", "decision"
         created_at: datetime
         updated_at: datetime
     ```
   - [ ] Create `MemoryStorage` interface (abstract base class)
   - [ ] Implement BigQuery memory storage (or Firestore if preferred)

3. **Memory APIs** (`rag-api/app_bigquery.py`)
   - [ ] `POST /memory` - Create memory
   - [ ] `GET /memory?project_id={id}` - List memories (global + project)
   - [ ] `PUT /memory/{id}` - Update memory
   - [ ] `DELETE /memory/{id}` - Delete memory
   - [ ] `GET /memory/search?query={text}` - Search memories
   - [ ] Respect `private_session` flag (no writes)

4. **Memory Integration in RAG**
   - [ ] Retrieve relevant memories before RAG query
   - [ ] Inject memories into LLM context
   - [ ] Update memory from conversation (optional, user-controlled)

**Success Criteria:**
- Context budget enforced on all queries
- Memory CRUD APIs functional
- Memory retrieval integrated into RAG pipeline
- Tests pass for budget limits and memory operations

---

### Sprint 1.2: Uncertainty Protocol & Cost Tracking (Week 2)

**Goal:** Enforce uncertainty protocol and implement cost tracking

#### Backend Tasks

1. **Uncertainty Protocol Enforcement** (`rag-api/uncertainty.py`)
   - [ ] Create `UncertaintyChecker` class
   - [ ] Check RAG retrieval confidence (empty or low score → uncertain)
   - [ ] Generate structured "uncertain" responses:
     ```python
     {
         "answer": "I don't have information about X in your knowledge base.",
         "uncertain": True,
         "suggestions": ["search the web", "ask you", "check documents again"]
     }
     ```
   - [ ] Integrate into `/query` endpoint
   - [ ] Add threshold: `RAG_CONFIDENCE_THRESHOLD=0.6`

2. **Cost Tracking Middleware** (`rag-api/cost.py`)
   - [ ] Create `CostTracker` class
   - [ ] Track per-user daily budgets:
     - Text tokens: 500K/day
     - Vision tokens: 50K/day
     - Audio minutes: 60/day
     - Dollars: $10/day (configurable)
   - [ ] Store in BigQuery/Firestore: `user_daily_budgets` table
   - [ ] Pre-query cost estimation
   - [ ] Warning at 80%: return `{"warning": "Approaching daily limit"}`
   - [ ] Hard halt at 100%: return `{"error": "Daily limit reached"}`

3. **Cost Middleware Integration**
   - [ ] Add middleware to all endpoints
   - [ ] Track token usage from Gemini API responses
   - [ ] Update daily budget after each request
   - [ ] Return cost info in response headers: `X-Cost-Tokens`, `X-Cost-Dollars`

**Success Criteria:**
- Uncertainty protocol triggers on low-confidence RAG
- Cost tracking accurate (within 5% of actual API costs)
- Warnings/halts work at 80%/100% thresholds
- Tests verify uncertainty and cost enforcement

---

### Sprint 1.3: Frontend Integration (Week 3)

**Goal:** Expose context/budget status and memory controls in UI

#### Frontend Tasks

1. **Context & Budget Status UI** (`next-holo-ui/components/BudgetStatus.tsx`)
   - [ ] Create `BudgetStatus` component
   - [ ] Display progress bars for:
     - Context usage (tokens)
     - Daily budget (tokens, cost, reset time)
   - [ ] Show warnings at 80%
   - [ ] Show error state at 100%
   - [ ] Add to `StatusBar` or new section

2. **RAG/Memory Transparency** (`next-holo-ui/components/SourcesPanel.tsx`)
   - [ ] Enhance existing sources display
   - [ ] Show which documents/memories were used
   - [ ] Display "No relevant context found" message when uncertain
   - [ ] Add memory citations (if memory was used)

3. **Memory Controls** (`next-holo-ui/components/MemoryPanel.tsx`)
   - [ ] Create memory management panel
   - [ ] Toggle global/project memory on/off
   - [ ] Enter private-session mode (checkbox)
   - [ ] List/search/edit/delete memories
   - [ ] Add to `SettingsDrawer` or new tab

4. **API Client Updates** (`next-holo-ui/lib/api.ts`)
   - [ ] Add memory CRUD functions
   - [ ] Add cost/budget status endpoint
   - [ ] Handle uncertainty responses
   - [ ] Pass `private_session` flag in requests

**Success Criteria:**
- Budget status visible and accurate
- Sources/memories displayed correctly
- Memory controls functional
- Private session mode works

---

### Sprint 1.4: Testing & Documentation (Week 4)

**Goal:** Create evaluation suite foundation and document MVP

#### Testing Tasks

1. **RAG & Memory Eval Harness** (`tests/rag_memory_eval/`)
   - [ ] Create directory structure
   - [ ] Implement `prompts.json` with 25 test cases:
     - RAG success (5 prompts)
     - Empty retrieval (5 prompts)
     - Memory recall (5 prompts)
     - Private session (3 prompts)
     - Long chat (3 prompts)
     - Ambiguous queries (4 prompts)
   - [ ] Implement `runner.py`:
     - Call `/query` endpoint
     - Parse answer + citations
     - Score 0-10 per rubric
   - [ ] Implement `regressiontest.py`:
     - Compare to baseline
     - Block on score drop or hallucination increase
   - [ ] Create `baseline.json` (initial baseline)

2. **Unit Tests**
   - [ ] Test `ContextBudgetEnforcer` (truncation, warnings)
   - [ ] Test `UncertaintyChecker` (thresholds, responses)
   - [ ] Test `CostTracker` (budget tracking, warnings)
   - [ ] Test memory CRUD operations

3. **Integration Tests**
   - [ ] Test full RAG pipeline with budget enforcement
   - [ ] Test memory injection in RAG queries
   - [ ] Test uncertainty protocol end-to-end
   - [ ] Test cost tracking across multiple requests

**Documentation Tasks**

1. **API Documentation**
   - [ ] Update OpenAPI/Swagger docs
   - [ ] Document new endpoints (`/memory/*`, cost headers)
   - [ ] Document uncertainty protocol responses

2. **User Documentation**
   - [ ] Update README with MVP features
   - [ ] Document memory system usage
   - [ ] Document budget/cost controls

**Success Criteria:**
- Eval harness runs and produces reports
- Unit tests pass (>80% coverage)
- Integration tests pass
- Documentation complete

---

## Phase 2: V1 Foundation (Weeks 5-8)

### Sprint 2.1: Enhanced Live Sessions (Week 5)

**Goal:** Implement proper LiveSession model and LS1A audio pipeline

#### Backend Tasks

1. **LiveSession Model** (`rag-api/models.py`)
   - [ ] Create `LiveSession` Pydantic model:
     ```python
     class LiveSession(BaseModel):
         id: str
         user_id: str
         state: Literal["IDLE", "CONNECTING", "LIVE", "PAUSED", "ENDED"]
         mode: Literal["LS1A", "LS1B", "LS1C", "LS2", "LS3"]
         started_at: datetime
         paused_at: Optional[datetime]
         ended_at: Optional[datetime]
         transcript_partial: str
         transcript_final: Optional[str]
         audio_minutes_used: float
         frames_processed: int
         daily_budget_remaining: Dict[str, float]
         recording_consent: bool
     ```
   - [ ] Store in Firestore or BigQuery

2. **LiveSession APIs** (`rag-api/app_bigquery.py`)
   - [ ] `POST /live-sessions` - Create session
   - [ ] `GET /live-sessions/{id}` - Get session status
   - [ ] `PUT /live-sessions/{id}/pause` - Pause session
   - [ ] `PUT /live-sessions/{id}/resume` - Resume session
   - [ ] `DELETE /live-sessions/{id}` - End session
   - [ ] `GET /live-sessions` - List user sessions

3. **LS1A Audio Pipeline** (`rag-api/live_sessions.py`)
   - [ ] Integrate Deepgram WebSocket (reuse companion-api pattern)
   - [ ] Integrate OpenAI streaming LLM
   - [ ] Integrate ElevenLabs streaming TTS
   - [ ] Implement barge-in detection (VAD events)
   - [ ] Track audio minutes in session state
   - [ ] Enforce daily audio budget (60 min default)

4. **WebSocket Enhancement** (`rag-api/app_bigquery.py`)
   - [ ] Update `/gemini-live/ws/{session_id}` to use LiveSession model
   - [ ] Handle session state transitions
   - [ ] Send budget warnings at 80%
   - [ ] Auto-pause at 100% budget

**Success Criteria:**
- LiveSession model functional
- LS1A pipeline works with sub-1000ms latency
- Barge-in works (<50ms response)
- Budget enforcement active

---

### Sprint 2.2: Browser Automation Foundation (Week 6)

**Goal:** Set up Playwright and basic browser automation infrastructure

#### Backend Tasks

1. **Playwright Setup** (`rag-api/browser/`)
   - [ ] Create `browser/` directory
   - [ ] Install Playwright: `pip install playwright`
   - [ ] Create `BrowserSession` class:
     - Manage browser instance
     - Handle navigation
     - Extract AX Tree
   - [ ] Create `BrowserAutomation` orchestrator

2. **AX Tree Extraction** (`rag-api/browser/ax_tree.py`)
   - [ ] Extract accessibility tree from Playwright
   - [ ] Parse into structured format
   - [ ] Filter by role, name, state
   - [ ] Return as JSON

3. **Basic Browser APIs** (`rag-api/app_bigquery.py`)
   - [ ] `POST /browser/sessions` - Create browser session
   - [ ] `GET /browser/sessions/{id}/ax-tree` - Get AX Tree
   - [ ] `POST /browser/sessions/{id}/navigate` - Navigate to URL
   - [ ] `DELETE /browser/sessions/{id}` - Close session

4. **Safety Guardrails** (`rag-api/browser/safety.py`)
   - [ ] Implement blocklist (banking, password managers)
   - [ ] Check domain allow/deny lists
   - [ ] Enforce "no payments" rule
   - [ ] Log all actions

**Success Criteria:**
- Playwright integrated
- AX Tree extraction works
- Basic navigation functional
- Safety checks active

---

### Sprint 2.3: Browser Automation Actions (Week 7)

**Goal:** Implement Plan-Act-Verify-Recover pattern for browser actions

#### Backend Tasks

1. **Action Executor** (`rag-api/browser/actions.py`)
   - [ ] `click_element(selector)` - Click by AX Tree selector
   - [ ] `type_text(selector, text)` - Type into input
   - [ ] `navigate(url)` - Navigate to URL
   - [ ] `extract_text(selector)` - Extract text content
   - [ ] All actions verify state after execution

2. **Plan-Act-Verify-Recover** (`rag-api/browser/agent_loop.py`)
   - [ ] `plan()` - Generate action sequence
   - [ ] `act()` - Execute single action
   - [ ] `verify()` - Screenshot + vision check state
   - [ ] `recover()` - Retry or escalate on failure

3. **Uncertainty Protocol for Browser** (`rag-api/browser/uncertainty.py`)
   - [ ] Check if element exists in AX Tree
   - [ ] If not found, return uncertainty response
   - [ ] Never invent selectors
   - [ ] Use vision fallback if AX Tree insufficient

4. **Browser APIs** (`rag-api/app_bigquery.py`)
   - [ ] `POST /browser/sessions/{id}/actions/click` - Click element
   - [ ] `POST /browser/sessions/{id}/actions/type` - Type text
   - [ ] `POST /browser/sessions/{id}/actions/extract` - Extract text
   - [ ] All return verification results

**Success Criteria:**
- Browser actions work reliably
- Plan-Act-Verify-Recover pattern functional
- Uncertainty protocol triggers correctly
- Tests pass for all action types

---

### Sprint 2.4: Frontend Browser Integration (Week 8)

**Goal:** Add browser automation UI to frontend

#### Frontend Tasks

1. **Browser Panel** (`next-holo-ui/components/BrowserPanel.tsx`)
   - [ ] Create browser control panel
   - [ ] Display browser viewport (screenshot or iframe)
   - [ ] Show AX Tree (collapsible)
   - [ ] Action buttons (navigate, click, type)

2. **Browser Session Management** (`next-holo-ui/lib/browser.ts`)
   - [ ] Create browser session
   - [ ] Manage session lifecycle
   - [ ] Handle action requests/responses
   - [ ] Display uncertainty messages

3. **Integration**
   - [ ] Add BrowserPanel to main page
   - [ ] Connect to backend APIs
   - [ ] Show action history
   - [ ] Display safety warnings

**Success Criteria:**
- Browser panel functional
- Actions work from UI
- Uncertainty messages displayed
- Safety warnings visible

---

## Phase 3: Evaluation & Polish (Weeks 9-12)

### Sprint 3.1: Complete Evaluation Suite (Week 9)

**Goal:** Implement all three eval harnesses (RAG, Browser, Live)

#### Testing Tasks

1. **Browser Eval Harness** (`tests/browser_eval/`)
   - [ ] Create `scenarios.py` with 15 test scenarios
   - [ ] Implement `runner.py` using Playwright
   - [ ] Create `baseline.json`
   - [ ] Implement `regressiontest.py`

2. **Live Sessions Eval** (`tests/live_eval/`)
   - [ ] Create test scenarios (10 OS, 5 audio, 5 screen-share)
   - [ ] Implement runner
   - [ ] Create baseline
   - [ ] Regression tests

3. **CI/CD Integration** (`.github/workflows/eval-suite.yml`)
   - [ ] Run RAG eval on PR
   - [ ] Run browser eval on PR
   - [ ] Run live eval on PR
   - [ ] Block merge on regression failures
   - [ ] Upload reports to artifacts

**Success Criteria:**
- All three eval harnesses run
- CI/CD blocks on regressions
- Reports generated and stored

---

### Sprint 3.2: Windows Companion Planning (Week 10)

**Goal:** Design Windows Companion architecture (Lab 4 spec)

#### Design Tasks

1. **Architecture Document**
   - [ ] Device pairing model (Ed25519 keys)
   - [ ] Permission tiers (SUGGEST/ASSIST/AGENT)
   - [ ] OS action set (launch, focus, file ops)
   - [ ] Guardrails (blocklist, confirmations, Panic Stop)

2. **Implementation Plan**
   - [ ] Break down into tasks
   - [ ] Estimate effort
   - [ ] Identify dependencies

**Note:** Full Windows Companion implementation deferred to V2, but architecture should be ready.

---

### Sprint 3.3: Documentation & Deployment (Week 11-12)

**Goal:** Complete documentation and prepare for V1 release

#### Documentation Tasks

1. **API Documentation**
   - [ ] Complete OpenAPI spec
   - [ ] Add examples for all endpoints
   - [ ] Document error codes

2. **User Guide**
   - [ ] How to use RAG
   - [ ] How to manage memory
   - [ ] How to use browser automation
   - [ ] How to use live sessions

3. **Developer Guide**
   - [ ] Architecture overview
   - [ ] How to add new features
   - [ ] Testing guide
   - [ ] Deployment guide

4. **Deployment**
   - [ ] Update Cloud Run configs
   - [ ] Set up monitoring
   - [ ] Configure budgets
   - [ ] Test production deployment

**Success Criteria:**
- Documentation complete
- Production deployment tested
- Monitoring active
- Ready for V1 release

---

## Success Metrics

### MVP Completion Criteria

- [ ] Context budget enforced on all queries
- [ ] Memory system functional (CRUD + RAG integration)
- [ ] Uncertainty protocol triggers correctly
- [ ] Cost tracking accurate and enforced
- [ ] Frontend shows budget/memory/uncertainty
- [ ] Eval suite runs and passes baseline
- [ ] Documentation complete

### V1 Completion Criteria

- [ ] LiveSession model and LS1A pipeline functional
- [ ] Browser automation works (Plan-Act-Verify-Recover)
- [ ] Safety guardrails active
- [ ] All three eval harnesses passing
- [ ] CI/CD integrated
- [ ] Production deployment stable

---

## Risk Mitigation

### Technical Risks

1. **BigQuery Vector Search Limitations**
   - **Risk:** Performance or cost issues
   - **Mitigation:** Monitor costs, consider Qdrant migration if needed

2. **Latency Targets**
   - **Risk:** Sub-1000ms TTFT not achievable
   - **Mitigation:** Optimize streaming, use faster models, cache responses

3. **Browser Automation Reliability**
   - **Risk:** Playwright fails on complex sites
   - **Mitigation:** Robust error handling, vision fallback, uncertainty protocol

### Process Risks

1. **Scope Creep**
   - **Risk:** Adding V2 features too early
   - **Mitigation:** Strict phase boundaries, prioritize MVP completion

2. **Testing Gaps**
   - **Risk:** Insufficient test coverage
   - **Mitigation:** Eval suite mandatory, >80% unit test coverage

---

## Dependencies & Prerequisites

### External Dependencies

- Google Cloud Platform (BigQuery, Cloud Run, Firestore)
- Gemini API (embeddings, generation)
- OpenAI API (GPT-4o for live sessions)
- Deepgram API (STT)
- ElevenLabs API (TTS)
- Playwright (browser automation)

### Internal Dependencies

- Environment variables configured
- API keys available
- GCP project set up
- CI/CD pipeline configured

---

## Next Steps (Immediate)

1. **Review this plan** with team
2. **Prioritize Sprint 1.1** tasks
3. **Set up project board** (GitHub Projects or similar)
4. **Create initial tasks** for Sprint 1.1
5. **Begin implementation** of ContextBudgetEnforcer

---

## References

- `Jarvis Master Specs & Governance.md` - Global constitution
- `Implementation_Checklist.md` - RAG/memory/cost checklist
- `Lab4_Windows_Companion_Live_Sessions.md` - Windows & Live spec
- `Jarvis-Eval-Suite-Specification.md` - Evaluation framework
- `AGENTS.MD` - Current architecture

---

**Plan Status:** ✅ Ready for Implementation  
**Next Review:** After Sprint 1.1 completion

