"""
Document Reader MCP Server — reads files from the inbox/ drop folder.

Milestone: M3 (Real Input Through MCP)

A FastMCP server run over stdio.
No OAuth needed — reads local files only.

Tools exposed:
    list_documents() -> list of filenames in inbox/
    read_document(name) -> text content of the file

Supported formats:
    - .txt: plain text
    - .pdf: extracted via pdfplumber
    - .md: plain text

Hard limits:
    - Reads ONLY inside inbox/. Path traversal is blocked.
    - No write/delete/rename capability.
"""
