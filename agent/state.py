"""
Shared state schema for the Academic Workflow Agent graph.

Milestone: M0 (Foundation)

Every node reads from and writes to this TypedDict.
LangGraph manages the state — each node returns a partial dict
that gets merged into the running state.
"""

from __future__ import annotations
import operator
from datetime import date
from typing import TypedDict, Annotated, Literal, List, Dict, Optional
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

from .models import (
    RawEmail,
    RawLMSItem,
    RawDoc,
    CalendarEvent,
    Task,
    EmailVerdict,
    DuplicateGroup,
    ConflictRecord,
    Slot,
    ScheduleBlock,
    ValidationResult,
    CommandIntent,
    TraceEvent,
)


def _merge_lists(left: list, right: list) -> list:
    """Reducer: append new items to existing list."""
    if left is None:
        left = []
    if right is None:
        right = []
    return left + right


class AgentState(TypedDict, total=False):
    run_id: str
    user_input: str

    # ─── Routing ────────────────────────────────────────────────
    route: Literal["plan", "command", "unclear"]
    route_confidence: float
    router_reason: str

    # ─── Ingest ─────────────────────────────────────────────────
    raw_emails: List[RawEmail]
    raw_lms: List[RawLMSItem]
    raw_docs: List[RawDoc]
    busy_events: List[CalendarEvent]
    source_status: Dict[str, str]

    # ─── Orchestrator Workspace ─────────────────────────────────
    messages: Annotated[List[AnyMessage], add_messages]
    email_verdicts: Dict[str, EmailVerdict]
    tasks: List[Task]
    duplicate_groups: List[DuplicateGroup]
    conflicts: List[ConflictRecord]
    tool_calls_made: int
    last_tool_signature: str

    # ─── Planning ───────────────────────────────────────────────
    planner_mode: Literal["full", "replan"]
    affected_dates: List[date]
    free_slots: List[Slot]
    schedule: List[ScheduleBlock]
    validation: ValidationResult
    retry_count: int

    # ─── Command Flow ───────────────────────────────────────────
    command_intent: Optional[CommandIntent]
    resolved_event: Optional[CalendarEvent]
    confirmed: Optional[bool]

    # ─── Output & Observability ─────────────────────────────────
    plan_output: str
    warnings: Annotated[List[str], _merge_lists]
    trace: Annotated[List[TraceEvent], _merge_lists]
