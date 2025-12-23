# V2 Implementation Plan

**Status:** Planning  
**Target:** Weeks 21+  
**Foundation:** V1 Complete ✅

---

## Executive Summary

V2 builds on the V1 foundation to add advanced capabilities: Windows OS automation, multi-agent orchestration, enhanced memory, comprehensive evaluation, and avatar presence.

---

## V2 Features Overview

### 1. Windows Companion (CC0-CC3)
- **Device Pairing**: Ed25519 key exchange + revocation model
- **Credential Management**: Windows Credential Manager + DPAPI
- **OS Automation**: App launch, file operations, screen-based fallback
- **Region-of-Control (ROC)**: User-selected automation boundaries
- **Panic Stop**: Immediate automation cancellation

### 2. Multi-Agent CrewAI Pipelines
- **Task Orchestration**: Complex multi-step automation
- **Agent Specialization**: Browser agent, OS agent, RAG agent
- **Workflow Management**: Plan-Act-Verify-Recover at scale

### 3. Advanced Memory System
- **Project + Global Scoping**: Enhanced memory organization
- **Memory Relationships**: Link related memories
- **Memory Expiration**: Time-based memory management
- **Memory Analytics**: Usage patterns and insights

### 4. Complete Evaluation Suite
- **50-100 Test Cases**: Comprehensive test coverage
- **Automated Regression**: Continuous performance monitoring
- **Multi-Modal Testing**: Text, vision, audio, browser automation
- **Performance Benchmarks**: Latency, accuracy, cost metrics

### 5. Avatar Presence
- **Waveform Visualization**: Audio-driven visual feedback
- **Lip Sync**: Phoneme-level mouth animation
- **2D/3D Avatar**: Optional talking head
- **Presence States**: Listening, thinking, speaking

---

## Sprint Breakdown

### Sprint 3.1: Windows Companion Foundation (Week 21-22)

**Goal:** Implement device pairing and credential management

#### Backend Tasks

1. **Device Pairing System** (`rag-api/windows/device.py`)
   - [ ] Ed25519 keypair generation
   - [ ] Device certificate signing
   - [ ] DPAPI storage for device key
   - [ ] Revocation check endpoint
   - [ ] Device registration API

2. **Credential Management** (`rag-api/windows/credentials.py`)
   - [ ] Windows Credential Manager integration
   - [ ] DPAPI encryption for secrets
   - [ ] Credential storage/retrieval APIs
   - [ ] Never-send-to-cloud enforcement

3. **Trust Boundaries** (`rag-api/windows/security.py`)
   - [ ] Local-only secret storage
   - [ ] Session key management (in-memory only)
   - [ ] Automation log encryption
   - [ ] Screenshot auto-delete (24h)

#### Frontend Tasks

1. **Device Pairing UI** (`next-holo-ui/components/DevicePairing.tsx`)
   - [ ] Pair device button
   - [ ] QR code or pairing code display
   - [ ] Pairing status indicator
   - [ ] Revocation handling

**Success Criteria:**
- Device pairs successfully
- Credentials stored locally only
- Revocation works within 2 seconds

---

### Sprint 3.2: OS Automation (Week 23-24)

**Goal:** Implement Windows OS automation with safety guardrails

#### Backend Tasks

1. **App Launch/Switch** (`rag-api/windows/apps.py`)
   - [ ] App launch API
   - [ ] App blocklist check
   - [ ] System tool approval flow
   - [ ] App switching logic

2. **File Operations** (`rag-api/windows/files.py`)
   - [ ] File read (with folder allow-list)
   - [ ] File write/delete (with approval)
   - [ ] System directory protection
   - [ ] Batch operation handling

3. **Screen-Based Fallback** (`rag-api/windows/vision.py`)
   - [ ] Screenshot capture
   - [ ] Vision model integration
   - [ ] Bounding box detection
   - [ ] Coordinate-based clicking
   - [ ] Overlay for user adjustment

4. **Region-of-Control (ROC)** (`rag-api/windows/roc.py`)
   - [ ] Window selection API
   - [ ] ROC boundary enforcement
   - [ ] Element filtering (outside ROC ignored)

#### Frontend Tasks

1. **OS Automation Panel** (`next-holo-ui/components/OSAutomationPanel.tsx`)
   - [ ] App launch controls
   - [ ] File operation UI
   - [ ] ROC selection interface
   - [ ] Approval dialogs
   - [ ] Automation indicator

**Success Criteria:**
- Apps launch successfully
- File operations require approval
- ROC boundaries enforced
- Screen-based fallback works

---

### Sprint 3.3: Panic Stop & Safety Enhancements (Week 25)

**Goal:** Implement panic stop and always-visible automation indicators

#### Backend Tasks

1. **Panic Stop System** (`rag-api/windows/panic.py`)
   - [ ] Keyboard hook (Ctrl+Alt+J)
   - [ ] Immediate action cancellation
   - [ ] Rollback partial operations
   - [ ] Incident logging

2. **Automation Indicator** (`rag-api/windows/indicator.py`)
   - [ ] Taskbar badge API
   - [ ] On-screen banner (for long automations)
   - [ ] Automation console endpoint
   - [ ] Status updates

#### Frontend Tasks

1. **Panic Stop UI** (`next-holo-ui/components/PanicStop.tsx`)
   - [ ] Always-visible stop button
   - [ ] Keyboard shortcut handler
   - [ ] Automation status display
   - [ ] Console view

**Success Criteria:**
- Panic stop works within 500ms
- Automation indicator always visible
- Partial operations rolled back

---

### Sprint 3.4: Multi-Agent CrewAI Integration (Week 26-27)

**Goal:** Implement multi-agent orchestration for complex tasks

#### Backend Tasks

1. **CrewAI Setup** (`rag-api/agents/crew.py`)
   - [ ] CrewAI integration
   - [ ] Agent definitions (Browser, OS, RAG)
   - [ ] Task orchestration
   - [ ] Workflow management

2. **Agent Specialization** (`rag-api/agents/browser_agent.py`, `os_agent.py`, `rag_agent.py`)
   - [ ] Browser agent (Playwright automation)
   - [ ] OS agent (Windows automation)
   - [ ] RAG agent (Document search)

3. **Multi-Step Automation** (`rag-api/agents/orchestrator.py`)
   - [ ] Plan generation
   - [ ] Agent coordination
   - [ ] State management
   - [ ] Error recovery

#### Frontend Tasks

1. **Agent Orchestration UI** (`next-holo-ui/components/AgentOrchestration.tsx`)
   - [ ] Task input
   - [ ] Agent selection
   - [ ] Progress tracking
   - [ ] Agent status display

**Success Criteria:**
- Multi-agent tasks execute successfully
- Agents coordinate properly
- Error recovery works

---

### Sprint 3.5: Advanced Memory System (Week 28-29)

**Goal:** Enhance memory with relationships, expiration, and analytics

#### Backend Tasks

1. **Memory Relationships** (`rag-api/memory/relationships.py`)
   - [ ] Memory linking
   - [ ] Relationship types (related, contradicts, updates)
   - [ ] Graph traversal
   - [ ] Relationship APIs

2. **Memory Expiration** (`rag-api/memory/expiration.py`)
   - [ ] TTL support
   - [ ] Auto-cleanup
   - [ ] Expiration policies
   - [ ] Manual expiration override

3. **Memory Analytics** (`rag-api/memory/analytics.py`)
   - [ ] Usage patterns
   - [ ] Memory effectiveness metrics
   - [ ] Search frequency
   - [ ] Analytics API

#### Frontend Tasks

1. **Advanced Memory Panel** (`next-holo-ui/components/AdvancedMemoryPanel.tsx`)
   - [ ] Memory graph visualization
   - [ ] Relationship management
   - [ ] Expiration settings
   - [ ] Analytics dashboard

**Success Criteria:**
- Memory relationships work
- Expiration policies enforced
- Analytics provide insights

---

### Sprint 3.6: Complete Evaluation Suite (Week 30-31)

**Goal:** Expand evaluation suite to 50-100 test cases

#### Backend Tasks

1. **Test Case Expansion** (`tests/rag_memory_eval/prompts.json`)
   - [ ] Add 25-50 more test cases
   - [ ] Cover all V1 features
   - [ ] Add V2-specific tests
   - [ ] Multi-modal test cases

2. **Automated Regression** (`tests/regression/`)
   - [ ] Daily regression runs
   - [ ] Performance tracking
   - [ ] Baseline comparison
   - [ ] Alert system

3. **Multi-Modal Testing** (`tests/multimodal/`)
   - [ ] Vision tests
   - [ ] Audio tests
   - [ ] Browser automation tests
   - [ ] OS automation tests

#### Frontend Tasks

1. **Evaluation Dashboard** (`next-holo-ui/components/EvaluationDashboard.tsx`)
   - [ ] Test results display
   - [ ] Performance charts
   - [ ] Regression alerts
   - [ ] Manual test runner

**Success Criteria:**
- 50-100 test cases pass
- Regression detection works
- Multi-modal tests cover all features

---

### Sprint 3.7: Avatar Presence (Week 32-33)

**Goal:** Implement avatar with waveform sync and lip sync

#### Backend Tasks

1. **Waveform Generation** (`rag-api/avatar/waveform.py`)
   - [ ] Audio amplitude analysis
   - [ ] Confidence-based visualization
   - [ ] State machine (listening, thinking, speaking)
   - [ ] Waveform data API

2. **Lip Sync** (`rag-api/avatar/lipsync.py`)
   - [ ] ElevenLabs timing_info parsing
   - [ ] Phoneme mapping
   - [ ] Mouth animation data
   - [ ] Sync accuracy

#### Frontend Tasks

1. **Avatar Component** (`next-holo-ui/components/Avatar.tsx`)
   - [ ] Waveform visualization
   - [ ] 2D sprite or 3D model
   - [ ] Lip sync animation
   - [ ] State transitions
   - [ ] GPU rendering (client-side)

**Success Criteria:**
- Waveform syncs with audio
- Lip sync accurate
- Avatar states transition smoothly
- Zero server cost (client-side rendering)

---

## Dependencies

### External Services
- **Windows APIs**: Win32, DPAPI, Credential Manager
- **CrewAI**: Multi-agent orchestration framework
- **ElevenLabs**: Timing info for lip sync
- **OpenAI**: Vision for screen-based fallback

### Internal Dependencies
- V1 foundation complete ✅
- Browser automation working ✅
- Screen share working ✅
- Memory system functional ✅

---

## Success Metrics

### V2 Completion Criteria
- [ ] Windows Companion pairs and manages credentials
- [ ] OS automation works with safety guardrails
- [ ] Panic stop works within 500ms
- [ ] Multi-agent CrewAI orchestrates complex tasks
- [ ] Advanced memory with relationships and analytics
- [ ] 50-100 test cases in evaluation suite
- [ ] Avatar with waveform and lip sync

---

## Risk Mitigation

1. **Windows API Complexity**
   - Risk: Windows APIs may be complex or platform-specific
   - Mitigation: Use well-documented libraries, test on multiple Windows versions

2. **CrewAI Integration**
   - Risk: Multi-agent coordination may be complex
   - Mitigation: Start with simple workflows, iterate

3. **Avatar Performance**
   - Risk: Client-side rendering may impact performance
   - Mitigation: Optimize rendering, use WebGL, test on various devices

4. **Evaluation Suite Scale**
   - Risk: 50-100 tests may be time-consuming
   - Mitigation: Parallelize tests, use CI/CD, prioritize critical paths

---

## Next Steps

1. **Start Sprint 3.1**: Windows Companion Foundation
2. **Set up Windows development environment**: Install Windows SDK, test DPAPI
3. **Research CrewAI**: Understand framework, plan integration
4. **Begin implementation**: Follow sprint order

---

**Plan Status:** Ready for Implementation

