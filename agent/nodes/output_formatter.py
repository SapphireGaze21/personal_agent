"""
Output Formatter node — renders the final plan for display.

Formats the schedule, conflicts, and validation results
into a human-readable output string.
"""

from datetime import datetime
from agent.state import AgentState


def output_formatter(state: AgentState) -> dict:
    """
    Format the final plan output with:
    - Scheduled time blocks grouped by day
    - Conflict warnings with resolution details
    - Validation summary
    - Command intent (if applicable)
    """
    schedule = state.get("schedule", [])
    validation = state.get("validation_result", {})
    tasks = state.get("extracted_tasks", [])
    messages = []

    lines = []
    lines.append("")
    lines.append("=" * 62)
    lines.append("   ACADEMIC WORKFLOW AGENT — GENERATED PLAN")
    lines.append("=" * 62)


    # ── Task summary ───────────────────────────────────────────
    if tasks:
        lines.append("")
        lines.append(f"TASKS IDENTIFIED ({len(tasks)}):")
        lines.append("─" * 42)
        for t in sorted(tasks, key=lambda x: x.get("deadline", "9999")):
            deadline = t.get("deadline", "none")
            effort = t.get("effort_hours", 0)
            source = t.get("source", "?")
            ttype = t.get("task_type", "?")
            lines.append(
                f"  • [{t.get('course', '?'):>4}] {t['title']}"
            )
            lines.append(
                f"         deadline={deadline}  effort={effort}h  "
                f"type={ttype}  source={source}"
            )

    # ── Schedule ───────────────────────────────────────────────
    if schedule:
        lines.append("")
        lines.append(f"SCHEDULE ({len(schedule)} blocks):")
        lines.append("─" * 42)

        # Group by date
        sorted_schedule = sorted(schedule, key=lambda e: (e["date"], e["start_time"]))
        current_date = ""

        for entry in sorted_schedule:
            if entry["date"] != current_date:
                current_date = entry["date"]
                try:
                    day_name = datetime.strptime(current_date, "%Y-%m-%d").strftime("%A")
                except ValueError:
                    day_name = "?"
                lines.append(f"")
                lines.append(f"{current_date} ({day_name})")

            lines.append(
                f"     {entry['start_time']}–{entry['end_time']}  │  "
                f"{entry['task_title']:40s}  [{entry['source']}]"
            )

    # ── Validation ─────────────────────────────────────────────
    if validation:
        valid = validation.get("valid", False)
        status = "VALID" if valid else "HAS ISSUES"
        lines.append("")
        lines.append(f"VALIDATION: {status}")
        lines.append(
            f"{validation.get('total_scheduled_blocks', 0)} blocks scheduled "
            f"for {validation.get('total_tasks', 0)} tasks"
        )
        for issue in validation.get("issues", []):
            lines.append(f"{issue}")

    lines.append("")
    lines.append("=" * 62)
    lines.append("")

    plan_output = "\n".join(lines)

    return {
        "plan_output": plan_output
    }
