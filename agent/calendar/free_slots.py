"""
Free-slot calculation — determines available study time per day.

Milestone: M1 (Calendar-Aware Planning)

Algorithm:
    for each date from start_date to end_date:
        window = [STUDY_DAY_START, STUDY_DAY_END]
        busy   = busy_events on that date (from calendar)
        busy   = busy minus events marked cancelled in exceptions_store
        free   = window minus busy
        split into SLOT_MINUTES slots, drop anything shorter than 30 minutes

Output:
    - List[Slot]: available time blocks for scheduling
"""

from __future__ import annotations
from datetime import date, datetime, time, timedelta
from typing import List, Union, Optional
from pathlib import Path

import config
from ..models import Slot, CalendarEvent
from .exceptions_store import load_exceptions, is_cancelled, get_exception


def parse_time_str(time_val: Union[str, time]) -> time:
    """Parse HH:MM string into time object if needed."""
    if isinstance(time_val, time):
        return time_val
    parts = time_val.strip().split(":")
    return time(hour=int(parts[0]), minute=int(parts[1]))


def compute_free_slots(
    busy_events: List[Union[CalendarEvent, dict]],
    start_date: date,
    end_date: date,
    exceptions_path: Optional[Union[str, Path]] = None,
    day_start_str: Optional[str] = None,
    day_end_str: Optional[str] = None,
    slot_minutes: Optional[int] = None,
) -> List[Slot]:
    """Compute available study slots between start_date and end_date (inclusive).

    Args:
        busy_events: List of CalendarEvent models or equivalent dicts.
        start_date: Starting date.
        end_date: Ending date (inclusive).
        exceptions_path: Optional path to exceptions.json.
        day_start_str: e.g. "08:00" (defaults to config.STUDY_DAY_START).
        day_end_str: e.g. "20:00" (defaults to config.STUDY_DAY_END).
        slot_minutes: Slot granularity in minutes (defaults to config.SLOT_MINUTES).

    Returns:
        List of Slot objects.
    """
    day_start = parse_time_str(day_start_str or config.STUDY_DAY_START)
    day_end = parse_time_str(day_end_str or config.STUDY_DAY_END)
    slot_step = slot_minutes if slot_minutes is not None else config.SLOT_MINUTES

    # Normalize busy events to CalendarEvent objects
    normalized_events: List[CalendarEvent] = []
    for ev in busy_events:
        if isinstance(ev, CalendarEvent):
            normalized_events.append(ev)
        elif isinstance(ev, dict):
            normalized_events.append(CalendarEvent(**ev))

    free_slots_list: List[Slot] = []
    curr_date = start_date

    while curr_date <= end_date:
        date_iso = curr_date.isoformat()
        window_start = datetime.combine(curr_date, day_start)
        window_end = datetime.combine(curr_date, day_end)

        # Collect busy intervals for this date
        busy_intervals: List[tuple[datetime, datetime]] = []

        for ev in normalized_events:
            # Check if this event is cancelled for this specific date
            if is_cancelled(ev.event_key, date_iso, exceptions_path):
                continue

            # Check if event has a modified/moved time exception
            exc = get_exception(ev.event_key, date_iso, exceptions_path)
            ev_start = ev.start
            ev_end = ev.end

            if exc and exc.get("status") == "moved":
                if exc.get("new_start") and exc.get("new_end"):
                    n_start = parse_time_str(exc["new_start"])
                    n_end = parse_time_str(exc["new_end"])
                    ev_start = datetime.combine(curr_date, n_start)
                    ev_end = datetime.combine(curr_date, n_end)

            # Strip tzinfo for pure calendar math comparison with naive window_start/end
            if ev_start.tzinfo is not None:
                ev_start = ev_start.replace(tzinfo=None)
            if ev_end.tzinfo is not None:
                ev_end = ev_end.replace(tzinfo=None)

            # Overlap check with this day's study window
            if ev_start < window_end and ev_end > window_start:
                clipped_start = max(window_start, ev_start)
                clipped_end = min(window_end, ev_end)
                if clipped_start < clipped_end:
                    busy_intervals.append((clipped_start, clipped_end))

        # Sort and merge overlapping busy intervals
        busy_intervals.sort(key=lambda x: x[0])
        merged_busy: List[list[datetime]] = []
        for b_start, b_end in busy_intervals:
            if not merged_busy:
                merged_busy.append([b_start, b_end])
            else:
                last = merged_busy[-1]
                if b_start <= last[1]:
                    last[1] = max(last[1], b_end)
                else:
                    merged_busy.append([b_start, b_end])

        # Compute free intervals by subtracting busy from [window_start, window_end]
        free_intervals: List[tuple[datetime, datetime]] = []
        pointer = window_start

        for b_start, b_end in merged_busy:
            if pointer < b_start:
                free_intervals.append((pointer, b_start))
            pointer = max(pointer, b_end)

        if pointer < window_end:
            free_intervals.append((pointer, window_end))

        # Split free intervals into slot_step (30 min) slots
        # Any remainder shorter than slot_step (30 min) is dropped
        for f_start, f_end in free_intervals:
            slot_cursor = f_start
            while slot_cursor + timedelta(minutes=slot_step) <= f_end:
                slot_next = slot_cursor + timedelta(minutes=slot_step)
                free_slots_list.append(
                    Slot(
                        date=curr_date,
                        start=slot_cursor.time(),
                        end=slot_next.time(),
                    )
                )
                slot_cursor = slot_next

        curr_date += timedelta(days=1)

    return free_slots_list


# Convenient alias matching LangGraph node convention
def free_slots(state: dict, start_date: date, end_date: date) -> List[Slot]:
    """Extract busy_events from state dict and compute free slots."""
    busy_events = state.get("busy_events", [])
    return compute_free_slots(busy_events, start_date, end_date)
