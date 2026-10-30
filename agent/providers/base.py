"""
DataProvider protocol — the interface that FileProvider and McpProvider implement.

Milestone: M0 (Foundation)

Defines:
    class DataProvider(Protocol):
        async def get_emails(self, days: int) -> list[RawEmail]
        async def get_lms_items(self) -> list[RawLMSItem]
        async def get_documents(self) -> list[RawDoc]
        async def get_busy_events(self, start: date, end: date) -> list[CalendarEvent]

Why a protocol:
    The same graph runs on dummy files (development/tests) or real MCP data
    (production) without changing any node code. Only the provider changes.
"""
