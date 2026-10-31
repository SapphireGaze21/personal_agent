"""
Pydantic data contracts — every value that crosses a node boundary.

Milestone: M0 (Foundation)

Every value that crosses a node boundary is a Pydantic model.
Invalid data raises an error at the boundary instead of failing three nodes later.
"""

from __future__ import annotations
from datetime import date, datetime, time
from typing import Literal, List, Optional
from pydantic import BaseModel, Field


# ─── Raw Input Models (for Data Providers) ───────────────────

class RawEmail(BaseModel):
    id: str
    subject: str
    sender: str
    date: str
    body: str


class RawLMSItem(BaseModel):
    id: str
    title: str
    course: str
    date: str
    content: str


class RawDoc(BaseModel):
    id: str
    filename: str
    content: str


# ─── Source Tracking & Provenance ───────────────────────────

class SourceRef(BaseModel):
    kind: Literal["email", "lms", "doc", "calendar"]
    id: str


class DeadlineClaim(BaseModel):
    value: date
    source: SourceRef
    source_time: Optional[datetime] = None  # when that source was written / sent


# ─── Academic Task Model ────────────────────────────────────

class Task(BaseModel):
    task_id: str                      # stable id assigned after dedup/merge
    title: str
    course: Optional[str] = None
    task_type: Literal["assignment", "exam", "lab", "quiz", "reading", "viva", "other"] = "assignment"
    deadline: Optional[date] = None   # final value, set after conflict resolution
    deadline_claims: List[DeadlineClaim] = Field(default_factory=list)
    effort_hours: Optional[float] = None
    effort_reason: Optional[str] = None
    effort_confidence: Optional[float] = None  # 0 to 1
    grade_weight: Optional[float] = None       # percent of final grade, if known
    sources: List[SourceRef] = Field(default_factory=list)  # >1 means merged duplicates
    trust: Literal["normal", "low"] = "normal"  # low if source had injection pattern
    notes: Optional[str] = None


# ─── Email Verdict (email_classifier tool) ──────────────────

class EmailVerdict(BaseModel):
    email_id: str
    is_academic: bool
    reason: str


# ─── Duplicate Groups & Deduplication ───────────────────────

class DuplicateGroup(BaseModel):
    task_ids: List[str]               # two or more ids that are the same deliverable
    merged_title: str
    confidence: float
    reason: str


class DuplicateResult(BaseModel):
    groups: List[DuplicateGroup] = Field(default_factory=list)


# ─── Conflict Resolution ────────────────────────────────────

class ConflictRecord(BaseModel):
    task_id: str
    field: Literal["deadline", "title", "type"] = "deadline"
    claims: List[DeadlineClaim]
    chosen: str
    reason: str                       # always shown to the student


# ─── Router Decision ────────────────────────────────────────

class RouterDecision(BaseModel):
    route: Literal["plan", "command", "unclear"]
    confidence: float
    reason: str


# ─── Command Intent (command flow) ──────────────────────────

class CommandIntent(BaseModel):
    action: Literal["cancel", "move", "reschedule", "unknown"]
    target_text: str                  # e.g. "OS class"
    date: Optional[date] = None
    new_start: Optional[time] = None
    new_end: Optional[time] = None
    confidence: float = 1.0


# ─── Calendar & Scheduling Models ───────────────────────────

class CalendarEvent(BaseModel):
    event_key: str                    # calendar_id + event_id + instance_date
    title: str
    start: datetime
    end: datetime
    recurring: bool = False


class Slot(BaseModel):
    date: date
    start: time
    end: time


class ScheduleBlock(BaseModel):
    task_id: str                      # checked against Task.task_id
    date: date
    start: time
    end: time
    reason: str


# ─── Validation Result ──────────────────────────────────────

class ValidationIssue(BaseModel):
    code: str                         # V1 .. V10
    severity: Literal["hard", "soft"]
    message: str
    block_index: Optional[int] = None


class ValidationResult(BaseModel):
    valid: bool
    issues: List[ValidationIssue] = Field(default_factory=list)


# ─── Traceability Contract Models (Section 11) ──────────────

EventType = Literal[
    "run_start", "run_end", "route_decision", "ingest_source", "guard_scan",
    "llm_call", "llm_decision", "gate_decision", "tool_call", "tool_result", "state_update",
    "retrieval", "memory_read", "memory_write", "mcp_call",
    "dedup_decision", "conflict_resolution", "effort_estimate",
    "plan_proposed", "validation", "retry", "fallback",
    "command_intent", "target_resolution", "human_interrupt", "write_action",
    "failure", "warning",
]


class TraceEvent(BaseModel):
    event_id: str
    run_id: str
    seq: int                          # 1, 2, 3 ... strictly increasing
    ts: datetime                      # timezone-aware
    node: str                         # graph node or tool name
    event_type: EventType
    status: Literal["ok", "error", "blocked", "fallback", "declined"] = "ok"
    parent_event_id: Optional[str] = None
    duration_ms: Optional[int] = None
    summary: str
    detail: dict = Field(default_factory=dict)
    source_refs: List[SourceRef] = Field(default_factory=list)
    contains_untrusted: bool = False


class ContextManifest(BaseModel):
    emails: List[str] = Field(default_factory=list)
    lms_items: List[str] = Field(default_factory=list)
    docs: List[str] = Field(default_factory=list)
    tasks: List[str] = Field(default_factory=list)
    retrieved: List[str] = Field(default_factory=list)
    calendar_dates: List[date] = Field(default_factory=list)
    untrusted_ids: List[str] = Field(default_factory=list)
