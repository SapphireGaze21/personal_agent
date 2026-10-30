# Academic Workflow Agent — Detailed Project Explanation

This document provides a comprehensive, deep-dive explanation of the **Phase 1** Academic Workflow Agent. It breaks down every file, every function, the role of LLMs, and how tools map to each node.

---

## 1. Project Overview & Current State (Phase 1)

Currently, the project has advanced to **Phase 1**. We have integrated **Large Language Models (LLMs)** into the system to handle complex reasoning, extraction, and routing. We are still using dummy text files for data ingestion, but the intelligence interpreting that data is now powered by an LLM (LangChain + Groq/Gemini).

### Where are LLMs and Tools used?

| Node | Current Phase 1 Logic | Future Phase 2+ Logic (Tools) |
|------|-----------------------|--------------------------------------|
| **Ingest** | Reads local `.txt` files | **Tool Use:** Uses Email MCP and LMS MCP to fetch real data. |
| **Task Extractor** | **LLM Decision:** Parses raw email/LMS text and outputs structured JSON (date, effort, course) using Pydantic. | *No change.* |
| **Planner** | Python greedy slot-filling algorithm | *Remains Deterministic Python or OR-Tools.* (Math/scheduling is bad for LLMs). |
| **Validator** | Python checks for overlapping times | *Remains Deterministic Python.* |

---

## 2. The LangGraph Architecture & State

LangGraph works by passing a single dictionary (the "State") through a series of "Nodes" (Python functions).

### `agent/state.py`
This file defines the `AgentState` schema. It is a `TypedDict` that defines exactly what variables are passed between nodes.

- **`_merge_lists(left: list, right: list)`**: A special "reducer" function. Ensures that any new messages a node returns are *appended* to the existing list, creating a full execution trace.

### `agent/graph.py`
This file wires all the nodes together into a graph.

- **`build_graph()`**: Initializes the `StateGraph`, adds all nodes, defines all edges, and compiles it.

### `agent/llm.py`
This is a centralized utility file introduced in Phase 1.
- **`get_llm()`**: Initializes and returns the LLM client (e.g., `ChatGroq`). It reads API keys from the environment or `.env` files.

---

## 3. Node Details: Functions and Logic

### A. `agent/nodes/ingest.py`
**Purpose:** Fetches raw data.
- **`_parse_block_file(filepath, delimiter)`**: Helper function that parses dummy text files into dictionaries.
- **`ingest(state)`**: The main node function that reads emails and LMS data into state.

### B. `agent/nodes/task_extractor.py`
**Purpose:** Converts messy raw data into neat, standardized `Task` dictionaries.
- **`ExtractedTask`, `EmailAnalysis`, `LMSAnalysis`**: Pydantic schemas that define the exact JSON format we want the LLM to return.
- **`_extract_from_emails_llm(raw_emails)`**: Iterates over emails and asks the LLM to read them. The LLM determines if it's an academic email (`is_academic`) and extracts tasks if it is.
- **`_extract_from_lms_llm(raw_lms)`**: Asks the LLM to read LMS announcements and extract exact dates, effort, and titles.
- **`task_extractor(state)`**: The main node function that calls the LLM extraction helpers and saves the combined list to state.

### C. `agent/nodes/planner.py`
**Purpose:** Schedules the tasks into available calendar time (Deterministic).
- **`_get_free_slots`, `_task_priority_key`**: Helpers to manage time blocks and sort tasks.
- **`planner(state)`**: Main node function. Greedily assigns hours to a task until the task's effort is fulfilled in free slots.

### D. `agent/nodes/validator.py`
**Purpose:** Ensures the planner didn't make a mistake (Deterministic).
- **`validator(state)`**: Loops through the schedule to ensure no two tasks overlap in time. Also checks for "hallucinated" tasks.

### E. `agent/nodes/output_formatter.py`
**Purpose:** Formats the raw JSON/Dict data into readable text.
- **`output_formatter(state)`**: Formats the schedule into a clean string.

---

## 4. Summary of Node Tools

Right now, **nodes have NO tools**. They use standard Python libraries and LLM API calls.

In **Phase 2+**, the **Tools** will belong to specific nodes:
1. **Ingest Node** will have access to:
   - `get_emails()` tool
   - `get_lms_announcements()` tool

By isolating tools to specific nodes, we ensure a clean, reliable workflow.
