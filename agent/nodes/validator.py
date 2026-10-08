"""
Plan Validator node — deterministic feasibility checks.

Implements:
  FR20 - Every plan item traceable to a source (no hallucinated tasks)
  FR21 - Deterministic feasibility check (schedule fits available time)
  FR22 - Validation issues are surfaced, not suppressed
"""

from collections import defaultdict
from agent.state import AgentState


def validator(state: AgentState) -> dict:
    """
    Validate the generated schedule with deterministic checks:
    1. No overlapping time blocks on the same day
    2. Every scheduled item traces back to a known extracted task
    3. All conflicts are surfaced (not silently resolved)
    """
    schedule = state.get("schedule", [])
    tasks = state.get("extracted_tasks", [])
    messages = []
    issues = []

    # ── Check 1: No time overlaps ──────────────────────────────
    by_date: dict[str, list[dict]] = defaultdict(list)
    for entry in schedule:
        by_date[entry["date"]].append(entry)

    for date, entries in by_date.items():
        sorted_entries = sorted(entries, key=lambda e: e["start_time"])
        for i in range(len(sorted_entries) - 1):
            if sorted_entries[i]["end_time"] > sorted_entries[i + 1]["start_time"]:
                issues.append(
                    f"TIME OVERLAP on {date}: "
                    f"'{sorted_entries[i]['task_title']}' "
                    f"({sorted_entries[i]['start_time']}–{sorted_entries[i]['end_time']}) "
                    f"overlaps with '{sorted_entries[i+1]['task_title']}' "
                    f"({sorted_entries[i+1]['start_time']}–{sorted_entries[i+1]['end_time']})"
                )

    # ── Check 2: Source traceability (FR20) ────────────────────
    task_titles = {t["title"] for t in tasks}
    for entry in schedule:
        if entry["task_title"] not in task_titles:
            issues.append(
                f"UNGROUNDED TASK: '{entry['task_title']}' appears in schedule "
                f"but has no matching extracted task — possible hallucination"
            )

    # ── Determine validity ─────────────────────────────────────
    # Only overlaps and ungrounded tasks are "hard" failures
    hard_failures = [
        i for i in issues
        if i.startswith("TIME OVERLAP") or i.startswith("UNGROUNDED")
    ]
    valid = len(hard_failures) == 0

    result = {
        "valid": valid,
        "issues": issues,
        "total_scheduled_blocks": len(schedule),
        "total_tasks": len(tasks),
        "hard_failures": len(hard_failures),
    }

    status = "VALID" if valid else "INVALID"
    messages.append(
        f"[Validator] {status} — "
        f"{len(hard_failures)} hard failure(s), "
        f"{len(issues)} total issue(s)"
    )
    for issue in issues:
        messages.append(f"[Validator]   • {issue}")

    return {
        "validation_result": result,
        "messages": messages,
    }
