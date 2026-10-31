"""
DataProvider protocol — abstract interface for data sources.

Milestone: M0 (Foundation)

The graph never calls Google or the filesystem directly. It calls a provider.
This file defines the protocol that both FileProvider and McpProvider implement.
"""

from __future__ import annotations
from datetime import date
from typing import Protocol, List
from ..models import RawEmail, RawLMSItem, RawDoc, CalendarEvent


class DataProvider(Protocol):
    async def get_emails(self, days: int = 14) -> List[RawEmail]:
        """Fetch emails within the given day horizon."""
        ...

    async def get_lms_items(self) -> List[RawLMSItem]:
        """Fetch announcements and task items from LMS."""
        ...

    async def get_documents(self) -> List[RawDoc]:
        """Fetch documents from drop folder or storage."""
        ...

    async def get_busy_events(self, start: date, end: date) -> List[CalendarEvent]:
        """Fetch busy calendar events between start and end date (inclusive)."""
        ...
