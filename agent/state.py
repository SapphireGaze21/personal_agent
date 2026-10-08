"""
Shared state schema for the Academic Workflow Agent graph.

Every node reads from and writes to this TypedDict.
LangGraph manages the state — each node returns a partial dict
that gets merged into the running state.
"""

from __future__ import annotations
from typing import TypedDict, Annotated


# ---------------------------------------------------------------------------
# Domain types
# ---------------------------------------------------------------------------

class Task(TypedDict, total=False):
    """A single academic task extracted from any source."""
    title: str
    deadline: str          # YYYY-MM-DD
    source: str            # "email" | "lms" | "calendar" | "email+lms" (merged)
    task_type: str         # "assignment" | "exam" | "lab" | "reading" | "quiz"
    effort_hours: float
    course: str
    details: str


class ScheduleEntry(TypedDict):
    """A scheduled block of study/work time in the plan."""
    task_title: str
    date: str              # YYYY-MM-DD
    start_time: str        # HH:MM
    end_time: str          # HH:MM
    source: str            # traceability — which source this task came from


# ---------------------------------------------------------------------------
# State reducer — messages accumulate across nodes
# ---------------------------------------------------------------------------

def _merge_lists(left: list, right: list) -> list:
    """Reducer: append new items to existing list."""
    return left + right


# ---------------------------------------------------------------------------
# Agent state — the single shared TypedDict for the entire graph
# ---------------------------------------------------------------------------

class AgentState(TypedDict, total=False):
    """
    Shared state flowing through the LangGraph.

    Fields without an Annotated reducer use 'last writer wins' semantics.
    The `messages` field accumulates across all nodes via _merge_lists.
    """
    # --- Input ---
    user_input: str

    # --- Raw data from sources ---
    raw_emails: list[dict]
    raw_lms: list[dict]

    # --- Processed data ---
    extracted_tasks: list[Task]

    # --- Schedule ---
    schedule: list[ScheduleEntry]
    validation_result: dict                             # {valid: bool, issues: [...]}
    plan_output: str

    # --- Meta ---
    messages: Annotated[list[str], _merge_lists]        # accumulated execution trace
