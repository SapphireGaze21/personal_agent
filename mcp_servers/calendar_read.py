"""
Google Calendar Read MCP Server — read-only access to calendar events.

Milestone: M3 (Real Input Through MCP)

A FastMCP server run over stdio.
OAuth scope: calendar.readonly

Tools exposed:
    list_calendars() -> list of calendar names and IDs
    list_events(start, end, calendar_ids?) -> list of events between two ISO datetimes

Hard limits:
    - Read only. No create/update/delete.
    - Recurring events expanded with singleEvents=True.
    - Token stored in secrets/calendar_read.token.json (separate from write token).

Usage:
    python mcp_servers/calendar_read.py  (starts the stdio server)
"""
