# Academic Workflow Agent — Requirement Analysis Document

## 1. Project Overview

An agentic system that ingests a student's academic information — LMS content, email, calendar, and user-uploaded documents — reconciles it, and produces an explainable, deadline-aware study plan. The user can also interact with the system conversationally, including issuing updates in plain language (e.g. "class got cancelled today") that the system translates into real calendar changes.

Beyond the working system, the project investigates **how different agent architectures, retrieval strategies, tool interfaces (MCP), memory mechanisms, and guardrails affect the reliability and usefulness of an academic planning agent.**

Built entirely on free-tier LLM APIs and open-source tooling — no paid subscriptions anywhere in the stack.

## 2. Objectives

- **Applied objective** — a working system that reduces the manual effort of tracking deadlines, reconciling conflicting academic information, and planning study time.
- **Research objective** — measurable comparison of design choices (architecture, retrieval on/off, memory on/off, guardrail design) against reliability metrics on a benchmark of academic scenarios.

## 3. Functional Requirements

### 3.1 User Interaction

| ID | Requirement |
| --- | --- |
| FR1 | User can issue natural-language prompts at any time (e.g. "what's due this week", "move DBMS prep to the weekend") |
| FR2 | *(Later-stage)* User can upload documents (syllabi, assignment PDFs, notes); the system extracts tasks/deadlines/topics from them to build or update the study plan |

### 3.2 Information Ingestion

| ID | Requirement |
| --- | --- |
| FR3 | Read relevant emails (announcements, deadline changes), filtered for academic relevance — not every email is processed blindly |
| FR4 | Read LMS content (method depends on feasibility: RSS feed / calendar export / manual, per earlier findings — admin-gated full API is not assumed available) |
| FR5 | Read existing calendar events, to know what time is already occupied |
| FR6 | Create, update, and delete calendar events based on agent decisions or explicit user commands |
| FR7 | *(Later-stage, pairs with FR2)* Parse uploaded PDFs/documents into usable text |

### 3.3 Context & Memory

| ID | Requirement |
| --- | --- |
| FR8 | Recognize recurring patterns — e.g. a class that occupies 10:00–12:00 every Monday should be understood as a standing weekly constraint, not re-derived from a single calendar entry each time |
| FR9 | Persist user preferences (study habits, preferred free days/times) across sessions |
| FR10 | Learn from historical effort estimates vs. actual time taken, to improve future estimates (calibration) |

### 3.4 Planning & Scheduling

| ID | Requirement |
| --- | --- |
| FR11 | Convert raw text (LMS/email/documents) into structured tasks: title, deadline, type, source, estimated effort |
| FR12 | Decompose multi-part assignments into sub-tasks (e.g. code / report / analysis) with individually appropriate timing |
| FR13 | Detect contradictions between sources (e.g. LMS vs. email on a deadline) and resolve with an explicit, visible rule — never silently pick one |
| FR14 | Deduplicate the same task appearing across multiple sources |
| FR15 | Prioritize tasks by deadline, effort, and (if known) grade weight |
| FR16 | Generate a day-by-day schedule that fits within actual free calendar time |
| FR17 | Detect and flag overload — when required effort exceeds available free time — rather than silently cramming everything in |

### 3.5 Dynamic Updates

| ID | Requirement |
| --- | --- |
| FR18 | Interpret a natural-language instruction (e.g. "class got cancelled today") by determining: (a) which calendar event it refers to, (b) what calendar action is required (delete/modify), and (c) whether downstream plan items need to shift |
| FR19 | Re-plan only the affected portion of the schedule after such an update — not a full regeneration |

### 3.6 Validation & Explainability

| ID | Requirement |
| --- | --- |
| FR20 | Every item in the final plan is traceable to a specific source (prevents hallucinated tasks/deadlines) |
| FR21 | Deterministic feasibility check — does the proposed schedule actually fit available free time |
| FR22 | Per-decision explanation — the plan states *why* each item is prioritized/scheduled as it is |
| FR23 | Low-confidence extractions (e.g., a messily parsed PDF date) are flagged, not presented with false certainty |

## 4. Non-Functional Requirements

| ID | Requirement |
| --- | --- |
| NFR1 | Entire stack runs on free tiers / open-source tools — zero paid subscriptions |
| NFR2 | Data-source backends (calendar, email, LMS) are swappable without changing agent logic |
| NFR3 | Personal academic data (email content, grade-adjacent info) is handled with care; prefer synthetic data for broad experimentation |
| NFR4 | System behavior is evaluable against a benchmark, not just demoed once |
| NFR5 | Architecture grows in phases, each phase independently demoable |

## 5. Tools & Technology Mapping

| Requirement area | Tool | Why / what it's for |
| --- | --- | --- |
| Orchestration (all FRs) | **LangGraph** | Multi-agent graph, conditional routing, shared state, retry loops |
| Reasoning, extraction, explanation | **Groq free tier** (primary), **Gemini free tier** (backup) | Free LLM inference, no card required |
| Retrieval (RAG) | **Chroma or FAISS** + **sentence-transformers** embeddings | (a) historical calibration data (FR10); (b) semantic search over uploaded documents/syllabi (FR2, FR7); (c) retrieving related past context when planning |
| Calendar read/write | **Calendar MCP server** wrapping Google Calendar API (free tier) | Exposes `get_events()`, `create_event()`, `update_event()`, `delete_event()` as MCP tools — serves FR5, FR6, FR18 |
| Email read/filter | **Email MCP server** wrapping Gmail/Outlook API where available, manual-paste fallback otherwise | Exposes `get_recent_emails()`; feeds a relevance-filtering node — FR3 |
| LMS | **LMS MCP server**, backend depends on feasibility (RSS/calendar export/manual file) | FR4 |
| Document parsing | `pdfplumber` / `PyPDF2` wrapped as a **Document MCP server** tool `extract_text()` | FR2, FR7 |
| Deterministic scheduling/conflict logic | Plain Python, optionally **Google OR-Tools** | FR13, FR16, FR17, FR21 — kept out of the LLM deliberately, same principle as using flake8 instead of an LLM for style checks |
| Natural-language command interpretation | LLM node that maps an instruction to a structured intent (e.g. `{"action": "delete_event", "event_ref": "..."}`) | The LLM only identifies *intent*; the actual calendar change is executed deterministically via the Calendar MCP tool — keeps the risky, data-changing step auditable (FR18) |

## 6. Updated System Architecture

```
          USER
            │
   ┌────────┴─────────┐
   │  Prompt / Upload  │
   └────────┬─────────┘
            ↓
   ┌─────────────────┐
   │  Supervisor /    │
   │  Orchestrator    │
   └────────┬─────────┘
            │
 ┌──────────┼──────────────────┬─────────────────┐
 ↓          ↓                  ↓                  ↓
Information  Task Analysis   Planning          Command
  Agent        Agent          Agent          Interpreter
 │            │                │                  │
 ↓            ↓                ↓                  ↓
MCP tools:   RAG / Memory   Calendar /        Calendar MCP
Calendar,    (Chroma/FAISS) Task state        (write actions:
Email, LMS,                                   create/update/
Documents                                     delete event)
 │            │                │                  │
 └────────────┼────────────────┴──────────────────┘
              ↓
       Plan Validator
      (deterministic:
   feasibility + grounding)
              │
        ┌─────┴─────┐
        ↓           ↓
      Valid       Invalid
        │           │
        ↓           ↓
      Output      Re-plan
```

## 7. Phased Scope

**MVP (near-term):** FR3–FR6, FR8, FR11, FR13–FR17, FR20–FR23 — core ingestion (email/calendar/LMS via feasible method), planning, and validation, on synthetic + whatever live data proves accessible.

**Later-stage (explicitly deferred, as you flagged):** FR1 (full conversational interface), FR2 and FR7 (document upload and parsing), FR9–FR10 (persistent preferences and calibration memory), FR18–FR19 (natural-language-driven calendar updates).

## 8. Research Questions / Evaluation Plan

- Does adding RAG/memory measurably reduce effort-estimate error or improve plan quality, compared to a cold-start version?
- Does the explicit conflict-resolution step reduce missed/incorrect deadlines compared to a naive "just take the latest mentioned" rule?
- How does a deterministic validator vs. no validator affect hallucination rate (plan items not traceable to a source)?
- Benchmark: 5–10 synthetic scenarios (contradictory sources, overload weeks, missing data, a cancelled-class update) with metrics — deadline-miss rate, conflict-detection recall, hallucination rate, effort-estimate error — measured with each feature on/off.