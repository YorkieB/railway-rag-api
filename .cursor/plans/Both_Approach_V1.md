# Both_Approach_V1

*Extracted from PDF*

---

## Page 1

You now have four major specs and Lab 4ʼs Windows/live spec; the next moves are (a) a
Windows/live checklist and (b) a consolidated PRD. [file:82eb882a-50d04ad7-b6ec-
b19d2d0d1972file:eaeb91548f4d-4ad7-b6ec-b19d2d0d1972file:eb48a5e095bd-4953
80a8-bfc8e7973831both
1
Windows & live implementation checklist
Windows companion OS agent)
Implement secure pairing
Device keypair on Windows, cloud-signed device certificate, revocation check on
startup.1
Store secrets locally via DPAPI/Credential Manager; never send credentials to cloud.1
Build OS action layer
APIs for: launch/close apps, focus/switch windows, keyboard shortcuts, safe file
operations, clipboard.21
Enforce region-of-control: act only within the user-selected window/area.21
Enforce permission tiers
Map Suggest/Assist/Agent →  Read ‑ only / Limited / Full sets of OS actions and
approvals.21
Blocklisted apps (password managers, banking, system utilities) at the OS layer.12
Add guardrails & UX
Always-visible “Automation Active” indicator and Panic Stop that kills all automation.2
1
Confirmation flows for destructive actions showing path, action, and diff preview.12
Logging & evaluation
Log OS actions with redaction; wire the OS eval scenarios (open app, blocked
password manager, mis ‑ target detection) into CI.21

## Page 2

Live sessions (audio/video/screen)
Implement LiveSession model & lifecycle
States: IDLE →  CONNECTING →  LIVE →  PAUSED →  ENDED with timestamps and
budget fields.1
Store transcripts, frame counts, consent flags, and links to stored artifacts.1
Build audio call pipeline LS1A
WebRTC audio to streaming STT (e.g., Deepgram), streaming LLM, streaming TTS
(e.g., ElevenLabs/Piper) with sub ‑ second latency.321
Implement barge ‑ in: cancel TTS and clear queues when user starts speaking.31
Build video & avatar modes LS1B/LS1C
Camera capture, lightweight preview, basic network adaptation; waveform/“presence”
UI and states (listening/thinking/speaking).21
Build screen share assist LS3
getDisplayMedia capture, configurable frame sampling 0.52 fps), ROI selection,
secret blurring on frames before vision call.421
Vision analysis to “describe what you see” and step ‑ by ‑ step guidance; pinning
snapshots.41
Uncertainty, privacy, cost
Apply uncertainty protocol on low ‑ confidence STT, unclear OS/UI states, or ambiguous
screen content.321
Default: transcripts only; optional AV recording with explicit consent and retention
policy.521
Integrate audio/vision budgets from the cost spec (minutes, frames, token limits,
degradation at 80%, halt at 100%. [file:eaeb91548f4d-4ad7-b6ec-b19d2d0d19721
Dev rules
.cursorrules for OS and live: no actions outside allowed window, confirmation for
destructive ops, silence or explicit “uncertain” on low ‑ confidence STT.41
Consolidated Jarvis PRD (high ‑ level outline)
Product definition
Jarvis is a sovereign, multi ‑ modal AI assistant with: chat, RAG, memory, browser control,
OS control, and live sessions, governed by strict uncertainty, privacy, and safety rules.
[file:eb48a5e095bd-495380a8-bfc8e79738312

## Page 3

If youʼd like, the next step can be turning this PRD outline into a formatted document you can
drop straight into your repo, or creating a unified “master implementation checklist” that merges
all four subsystem checklists by phase.
⁂Core capabilities
Conversation & knowledge: chat, long ‑ context reasoning, RAG over user docs,
global/project memory. [file:eaeb91548f4d-4ad7-b6ec-b19d2d0d19722
Action in the world: browser automation Playwright + hybrid observation), Windows
companion OS control, and live audio/video/screen assistance. [file:82eb882a-50d04ad7
b6ec-b19d2d0d197212
Governance: mission, out ‑ of ‑ scope, uncertainty protocol, privacy/retention, permission tiers,
budgets. [file:eb48a5e095bd-495380a8-bfc8e79738312
Architecture & data flows
Backend on Cloud Run with auth, projects, conversations, files, memories, LiveSessions,
BrowserSessions, DeviceAgents, and cost tracking.52
RAG & memory layer with vector DB, chunking, embeddings, retrieval thresholds, and a
context budget enforcer. [file:eaeb91548f4d-4ad7-b6ec-b19d2d0d19725
Agent layer implementing Plan–Act–Verify–Recover for browser, OS, and live actions, all
sharing the same safety and uncertainty rules. [file:82eb882a-50d04ad7-b6ec-
b19d2d0d1972412
Safety, privacy, and cost
Uncertainty protocol across chat, RAG, browser, OS, and live: Jarvis must admit when it
does not know or cannot see an element/state. [file:eb48a5e095bd-495380a8
bfc8e79738314
Privacy: local secrets, no default AV storage, redacted logs, configurable retention, device
pairing and revocation for Windows.512
Cost: per ‑session and daily budgets for tokens, audio minutes, vision frames; pre ‑ query cost
estimates and graceful degradation. [file:eaeb91548f4d-4ad7-b6ec-b19d2d0d1972
Roadmap anchors
MVP: chat + RAG + basic governance. [file:eb48a5e095bd-495380a8-bfc8e79738312
V1: add browser automation and audio live sessions. [file:82eb882a-50d04ad7-b6ec-
b19d2d0d197212
V2: full Windows companion, advanced memory, avatar presence, and complete eval packs
for RAG, browser, OS, and live.512
Lab-4-should-design-Windows-companion-live-sessi-1.pdf
Research.pdf

## Page 4

Building-a-Real-Time-AICompanion.pdf
Research-Assistant-AIHallucination-Mitigation.pdf
Building-a-Jarvis-AISystem.pdf
