"""
McpProvider — reads real data through MCP servers.

Milestone: M3 (Real Input Through MCP)

Implements the DataProvider protocol using MCP servers:
    - calendar_read  — Google Calendar (read-only)
    - gmail_read     — Gmail (read-only, Academic label)
    - docs_reader    — inbox/ folder (PDFs, text files)

Uses langchain-mcp-adapters MultiServerMCPClient.
Nodes that touch MCP are async, and the graph runs with await graph.ainvoke(...).

Stub until M3 — returns empty lists with a warning.
"""
