"""
Planning Agent — generates a day-by-day study schedule.

Implements:
  FR15 — Prioritize tasks by deadline, effort, and type
  FR16 — Generate a day-by-day schedule fitting available free time
  FR17 — Detect and flag overload
"""

from datetime import datetime, timedelta
from agent.state import AgentState, ScheduleEntry


# Study window: 8:00 AM to 8:00 PM (12 hours max per day)
DAY_START_HOUR = 8
DAY_END_HOUR = 20

# Fixed reference date for Phase 0 reproducibility
REFERENCE_DATE = datetime(2026, 10, 6)

# Planning horizon
PLANNING_DAYS = 14


def _get_free_slots(occupied: set[int]) -> list[tuple[int, int]]:
    """Get available 1-hour slots between DAY_START and DAY_END."""
    return [
        (h, h + 1)
        for h in range(DAY_START_HOUR, DAY_END_HOUR)
        if h not in occupied
    ]


def _task_priority_key(task: dict) -> tuple:
    """
    Sort key for task prioritization (FR15).

    Priority order:
    1. Earliest deadline first
    2. Exams > assignments > labs > quizzes > readings
    3. Higher effort first (bigger tasks need more lead time)
    """
    deadline = task.get("deadline", "9999-99-99") or "9999-99-99"

    type_priority = {
        "exam": 0,
        "assignment": 1,
        "lab": 2,
        "quiz": 3,
        "reading": 4,
        "unknown": 5,
    }
    task_type_rank = type_priority.get(task.get("task_type", "unknown"), 5)

    # Negate effort so higher effort comes first
    effort = -(task.get("effort_hours", 0) or 0)

    return (deadline, task_type_rank, effort)


def planner(state: AgentState) -> dict:
    """
    Create a day-by-day schedule by:
    1. Sorting tasks by priority (deadline → type → effort)
    2. Greedily assigning tasks to free calendar slots
    3. Flagging overload when tasks can't fit
    """
    tasks = state.get("extracted_tasks", [])
    messages = []

    # Sort by priority
    sorted_tasks = sorted(tasks, key=_task_priority_key)
    messages.append(
        f"[Planner] Planning {len(sorted_tasks)} tasks over {PLANNING_DAYS} days"
    )

    schedule: list[ScheduleEntry] = []
    overload_tasks: list[tuple[str, float]] = []

    for task in sorted_tasks:
        effort = task.get("effort_hours", 2.0) or 2.0
        remaining_effort = effort

        for day_offset in range(PLANNING_DAYS):
            if remaining_effort <= 0:
                break

            date = REFERENCE_DATE + timedelta(days=day_offset)
            date_str = date.strftime("%Y-%m-%d")

            # Don't schedule on or after the deadline day
            deadline = task.get("deadline", "")
            if deadline and date_str >= deadline:
                break

            # Get occupied hours: already-scheduled blocks
            occupied = set()
            for existing in schedule:
                if existing["date"] == date_str:
                    existing_h = int(existing["start_time"].split(":")[0])
                    occupied.add(existing_h)

            free_slots = _get_free_slots(occupied)

            for start_h, end_h in free_slots:
                if remaining_effort <= 0:
                    break

                entry: ScheduleEntry = {
                    "task_title": task["title"],
                    "date": date_str,
                    "start_time": f"{start_h:02d}:00",
                    "end_time": f"{end_h:02d}:00",
                    "source": task.get("source", "unknown"),
                }
                schedule.append(entry)
                remaining_effort -= 1

        if remaining_effort > 0:
            overload_tasks.append((task["title"], remaining_effort))

    messages.append(
        f"[Planner] Scheduled {len(schedule)} time blocks "
        f"for {len(sorted_tasks)} tasks"
    )

    if overload_tasks:
        for name, remaining in overload_tasks:
            messages.append(
                f"[Planner] OVERLOAD: '{name}' needs {remaining:.0f}h more "
                f"but no free slots available before deadline"
            )

    return {
        "schedule": schedule,
        "messages": messages,
    }
