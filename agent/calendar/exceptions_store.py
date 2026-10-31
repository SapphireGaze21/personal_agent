"""
Exceptions store — manages calendar exceptions (cancelled/moved classes).

Milestone: M1 (Calendar-Aware Planning)

A cancellation does NOT edit the real calendar event. Instead, it stores
an exception in state/exceptions.json. The free_slots calculator reads
this file and treats the cancelled class as free time.

This is a deliberate safety choice: the agent never modifies real calendar events.
"""

from __future__ import annotations
import os
import json
from pathlib import Path
from typing import List, Dict, Optional

# Default path to state/exceptions.json
DEFAULT_EXCEPTIONS_PATH = (
    Path(__file__).resolve().parent.parent.parent / "state" / "exceptions.json"
)


def get_exceptions_path(override_path: Optional[str | Path] = None) -> Path:
    if override_path is not None:
        return Path(override_path)
    return DEFAULT_EXCEPTIONS_PATH


def load_exceptions(file_path: Optional[str | Path] = None) -> List[Dict]:
    """Return the list of exception dicts, or an empty list if file is missing/empty."""
    path = get_exceptions_path(file_path)
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except (json.JSONDecodeError, OSError):
        return []


def save_exceptions(exceptions: List[Dict], file_path: Optional[str | Path] = None) -> None:
    """Save the full list of exception dicts to state/exceptions.json."""
    path = get_exceptions_path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(exceptions, f, indent=2, ensure_ascii=False)


def add_exception(
    event_key: str,
    date_str: str,
    status: str = "cancelled",
    note: str = "",
    file_path: Optional[str | Path] = None,
) -> None:
    """Add a new exception or update an existing one matching event_key and date."""
    exceptions = load_exceptions(file_path)
    # Remove any existing exception with the same key and date
    filtered = [
        e for e in exceptions
        if not (e.get("event_key") == event_key and e.get("date") == date_str)
    ]
    filtered.append({
        "event_key": event_key,
        "date": date_str,
        "status": status,
        "note": note,
    })
    save_exceptions(filtered, file_path)


def is_cancelled(event_key: str, date_str: str, file_path: Optional[str | Path] = None) -> bool:
    """Check if a specific event on a specific date is marked as cancelled."""
    exceptions = load_exceptions(file_path)
    for e in exceptions:
        if (
            e.get("event_key") == event_key
            and e.get("date") == date_str
            and e.get("status") == "cancelled"
        ):
            return True
    return False


def get_exception(event_key: str, date_str: str, file_path: Optional[str | Path] = None) -> Optional[Dict]:
    """Retrieve exception detail for an event on a date if it exists."""
    exceptions = load_exceptions(file_path)
    for e in exceptions:
        if e.get("event_key") == event_key and e.get("date") == date_str:
            return e
    return None
