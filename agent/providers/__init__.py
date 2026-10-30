"""
DataProvider protocol — abstract interface for data sources.

Milestone: M0 (Foundation)

The graph never calls Google or the filesystem directly. It calls a provider.
This file defines the protocol that both FileProvider and McpProvider implement.

Methods:
    get_emails(days) -> list[RawEmail]
    get_lms_items() -> list[RawLMSItem]
    get_documents() -> list[RawDoc]
    get_busy_events(start, end) -> list[CalendarEvent]

Selected with DATA_MODE=files|mcp in .env.
Every test runs on FileProvider so evaluation does not depend on live accounts.
"""
