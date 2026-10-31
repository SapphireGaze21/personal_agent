"""
Policy Gate — allowlist, budgets, and loop detection.

Milestone: M2 (Router + Orchestrator Skeleton)

Enforces safety rules on tool calls made by the orchestrator:
1. Allowlist check (tool must be registered)
2. Budget check (tool_calls_made < MAX_TOOL_CALLS)
3. Loop detection (same tool + same arguments hash as last call)
4. Prerequisite checks (e.g. tasks must exist to estimate effort)
"""

from __future__ import annotations
import hashlib
import json
from typing import Literal, Tuple, Any, Dict
import config

ALLOWED_TOOLS = {
    "classify_emails",
    "extract_tasks",
    "check_duplicates",
    "resolve_conflicts",
    "estimate_effort",
    "read_document",
    "finish",
}


def hash_tool_call(tool_name: str, tool_args: Dict[str, Any]) -> str:
    """Create a deterministic hash signature of a tool call."""
    canonical = json.dumps({"tool": tool_name, "args": tool_args}, sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def check_tool_policy(
    tool_name: str,
    tool_args: Dict[str, Any],
    tool_calls_made: int,
    last_tool_signature: str,
    tasks_count: int,
    unclassified_emails_count: int = 0,
) -> Tuple[Literal["allowed", "blocked", "budget_exceeded"], str]:
    """Evaluate whether the orchestrator is allowed to invoke the requested tool.

    Returns:
        (decision, reason_message)
    """
    if not config.POLICY_GATE_ENABLED:
        return "allowed", "Policy gate is disabled by configuration"

    # Rule 1: Allowlist check
    if tool_name not in ALLOWED_TOOLS:
        return "blocked", f"Tool '{tool_name}' is not in the allowed tool registry: {sorted(list(ALLOWED_TOOLS))}"

    # Rule 2: Budget check
    if tool_calls_made >= config.MAX_TOOL_CALLS:
        return "budget_exceeded", f"Maximum tool call budget ({config.MAX_TOOL_CALLS}) reached"

    # Rule 3: Loop detection (identical repeated call)
    current_sig = hash_tool_call(tool_name, tool_args)
    if current_sig == last_tool_signature and tool_name != "finish":
        return "blocked", f"Loop detected: identical tool call to '{tool_name}' with the same arguments was just executed"

    # Rule 4: Prerequisites check
    if tool_name in ("check_duplicates", "resolve_conflicts", "estimate_effort") and tasks_count == 0:
        return "blocked", f"Prerequisite failed: cannot run '{tool_name}' when 0 tasks have been extracted"

    return "allowed", "Tool call conforms to safety policy"
