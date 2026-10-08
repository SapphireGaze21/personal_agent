"""
Information Agent — reads dummy .txt data sources.

Phase 0: Reads from local data/*.txt files.
Phase 2+: Calls MCP servers for Calendar API, Gmail API, LMS.
"""

from pathlib import Path
from agent.state import AgentState


# Resolve data directory relative to this file's location
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def _parse_block_file(filepath: Path, delimiter: str) -> list[dict]:
    """
    Parse a block-delimited text file into a list of dicts.

    Each block is separated by `delimiter` (e.g., '---EMAIL---')
    and contains key: value pairs, one per line.
    Blocks end with '---END---'.
    """
    if not filepath.exists():
        return []

    text = filepath.read_text(encoding="utf-8")
    blocks = text.split(delimiter)
    results = []

    for block in blocks:
        block = block.strip()
        if not block or block == "---END---":
            continue

        # Remove trailing ---END---
        block = block.replace("---END---", "").strip()

        entry: dict[str, str] = {}
        for line in block.split("\n"):
            line = line.strip()
            if not line:
                continue
            # Split on first colon only — values may contain colons (e.g., times)
            key, _, value = line.partition(":")
            key = key.strip().lower().replace(" ", "_")
            value = value.strip()
            if key and value:
                entry[key] = value

        if entry:
            results.append(entry)

    return results


def ingest(state: AgentState) -> dict:
    """
    Read all three dummy data sources and return parsed dicts.

    Populates: raw_emails, raw_calendar, raw_lms
    """
    messages = []

    # Read emails
    raw_emails = _parse_block_file(DATA_DIR / "emails.txt", "---EMAIL---")
    messages.append(f"[Ingest] Read {len(raw_emails)} emails from emails.txt")

    # Read LMS announcements
    raw_lms = _parse_block_file(DATA_DIR / "lms.txt", "---ANNOUNCEMENT---")
    messages.append(f"[Ingest] Read {len(raw_lms)} LMS announcements from lms.txt")

    return {
        "raw_emails": raw_emails,
        "raw_lms": raw_lms,
        "messages": messages,
    }
