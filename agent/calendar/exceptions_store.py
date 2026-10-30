"""
Exceptions store — manages calendar exceptions (cancelled/moved classes).

Milestone: M1 (Calendar-Aware Planning)

A cancellation does NOT edit the real calendar event. Instead, it stores
an exception in state/exceptions.json. The free_slots calculator reads
this file and treats the cancelled class as free time.

This is a deliberate safety choice: the agent never modifies real calendar events.

File format (state/exceptions.json):
    [
        {"event_key": "...", "date": "2026-10-12", "status": "cancelled"},
        {"event_key": "...", "date": "2026-10-14", "status": "moved", "new_start": "14:00", "new_end": "16:00"}
    ]

Functions:
    load_exceptions() -> list[dict]
    save_exception(exception: dict) -> None
    is_cancelled(event_key: str, date: str) -> bool
"""
