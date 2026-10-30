"""
Gmail Read MCP Server — read-only access to labelled emails.

Milestone: M3 (Real Input Through MCP)

A FastMCP server run over stdio.
OAuth scope: gmail.readonly

Tools exposed:
    list_emails(label="Academic", days=14, max_results=30) -> list of email summaries
    get_email(id) -> full email body

Hard limits:
    - Read only. No send/delete/modify.
    - Only reads the "Academic" label (configurable).
    - Body text stripped of HTML and cut to 4000 characters.
    - Token stored in secrets/gmail_read.token.json.

Privacy note:
    Real email text is sent to the LLM provider (Groq).
    Only read the Academic label, truncate bodies, avoid personal content.
"""
