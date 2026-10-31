"""
FileProvider — reads dummy data from local files.

Milestone: M0 (Foundation)

Implements the DataProvider protocol using local text files:
    data/emails.txt
    data/lms.txt
    data/calendar.txt
    inbox/ (drop folder for docs)
"""

from __future__ import annotations
import os
import re
from pathlib import Path
from datetime import date, datetime, time, timedelta
from typing import List, Optional

from .base import DataProvider
from ..models import RawEmail, RawLMSItem, RawDoc, CalendarEvent


DAY_MAP = {
    "mon": 0, "monday": 0,
    "tue": 1, "tuesday": 1,
    "wed": 2, "wednesday": 2,
    "thu": 3, "thursday": 3,
    "fri": 4, "friday": 4,
    "sat": 5, "saturday": 5,
    "sun": 6, "sunday": 6,
}


class FileProvider:
    """Reads data from local files in data/ and inbox/."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path(__file__).resolve().parent.parent.parent
        self.data_dir = self.base_dir / "data"
        self.inbox_dir = self.base_dir / "inbox"

    async def get_emails(self, days: int = 14) -> List[RawEmail]:
        """Parse emails from data/emails.txt."""
        path = self.data_dir / "emails.txt"
        if not path.exists():
            return []

        text = path.read_text(encoding="utf-8")
        blocks = re.split(r"---EMAIL---", text)
        emails: List[RawEmail] = []

        for idx, block in enumerate(blocks):
            clean = block.strip()
            if not clean:
                continue
            # Remove trailing delimiter if present
            clean = re.sub(r"---END---.*", "", clean, flags=re.DOTALL).strip()

            sender = ""
            subject = ""
            date_str = ""
            body = ""

            for line in clean.splitlines():
                if line.lower().startswith("from:"):
                    sender = line.split(":", 1)[1].strip()
                elif line.lower().startswith("subject:"):
                    subject = line.split(":", 1)[1].strip()
                elif line.lower().startswith("date:"):
                    date_str = line.split(":", 1)[1].strip()
                elif line.lower().startswith("body:"):
                    body = line.split(":", 1)[1].strip()
                elif body:
                    body += " " + line.strip()

            emails.append(
                RawEmail(
                    id=f"email_{idx+1}",
                    sender=sender,
                    subject=subject,
                    date=date_str,
                    body=body.strip(),
                )
            )

        return emails

    async def get_lms_items(self) -> List[RawLMSItem]:
        """Parse announcements from data/lms.txt."""
        path = self.data_dir / "lms.txt"
        if not path.exists():
            return []

        text = path.read_text(encoding="utf-8")
        blocks = re.split(r"---ANNOUNCEMENT---", text)
        items: List[RawLMSItem] = []

        for idx, block in enumerate(blocks):
            clean = block.strip()
            if not clean:
                continue
            clean = re.sub(r"---END---.*", "", clean, flags=re.DOTALL).strip()

            course = ""
            title = ""
            date_str = ""
            content_lines = []

            for line in clean.splitlines():
                if line.lower().startswith("course:"):
                    course = line.split(":", 1)[1].strip()
                elif line.lower().startswith("title:"):
                    title = line.split(":", 1)[1].strip()
                elif line.lower().startswith("date:"):
                    date_str = line.split(":", 1)[1].strip()
                else:
                    content_lines.append(line.strip())

            items.append(
                RawLMSItem(
                    id=f"lms_{idx+1}",
                    title=title,
                    course=course,
                    date=date_str,
                    content="\n".join([cl for cl in content_lines if cl]),
                )
            )

        return items

    async def get_documents(self) -> List[RawDoc]:
        """Read documents from inbox/ drop folder."""
        if not self.inbox_dir.exists():
            return []

        docs: List[RawDoc] = []
        for file in sorted(self.inbox_dir.glob("*")):
            if file.is_file() and not file.name.startswith("."):
                try:
                    content = file.read_text(encoding="utf-8", errors="replace")
                    docs.append(
                        RawDoc(
                            id=file.stem,
                            filename=file.name,
                            content=content,
                        )
                    )
                except Exception:
                    pass
        return docs

    async def get_busy_events(self, start: date, end: date) -> List[CalendarEvent]:
        """Parse calendar templates from data/calendar.txt and expand into CalendarEvents."""
        path = self.data_dir / "calendar.txt"
        if not path.exists():
            return []

        text = path.read_text(encoding="utf-8")
        blocks = re.split(r"---EVENT---", text)
        events: List[CalendarEvent] = []

        # Parsed templates
        templates = []
        for block in blocks:
            clean = block.strip()
            if not clean:
                continue
            clean = re.sub(r"---END---.*", "", clean, flags=re.DOTALL).strip()

            props = {}
            for line in clean.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    props[k.strip().lower()] = v.strip()
            if props:
                templates.append(props)

        # Expand across [start, end]
        curr = start
        while curr <= end:
            weekday_idx = curr.weekday()

            for tpl in templates:
                key_base = tpl.get("key", "cal_ev")
                title = tpl.get("title", "Class")
                is_recurring = tpl.get("recurring", "false").lower() in ("true", "1", "yes")

                start_str = tpl.get("start", "09:00")
                end_str = tpl.get("end", "10:00")
                s_h, s_m = map(int, start_str.split(":"))
                e_h, e_m = map(int, end_str.split(":"))

                event_start = datetime.combine(curr, time(s_h, s_m))
                event_end = datetime.combine(curr, time(e_h, e_m))

                if is_recurring:
                    day_name = tpl.get("day", "").lower()
                    if day_name in DAY_MAP and DAY_MAP[day_name] == weekday_idx:
                        events.append(
                            CalendarEvent(
                                event_key=f"{key_base}|{curr.isoformat()}",
                                title=title,
                                start=event_start,
                                end=event_end,
                                recurring=True,
                            )
                        )
                else:
                    specific_date = tpl.get("date", "")
                    if specific_date == curr.isoformat():
                        events.append(
                            CalendarEvent(
                                event_key=f"{key_base}|{curr.isoformat()}",
                                title=title,
                                start=event_start,
                                end=event_end,
                                recurring=False,
                            )
                        )

            curr += timedelta(days=1)

        return events
