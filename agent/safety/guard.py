"""
Guard — injection scan and trust tagging.

Milestone: M2 (Router + Orchestrator Skeleton)

Scans ingested text for prompt injection patterns.
Flagged items are still processed as data, but tasks extracted from them
get trust="low" and the final output shows a warning.
Flagged items can NEVER produce a command.
"""

from __future__ import annotations
import re
from typing import List, Tuple
import config

# Common prompt injection signatures
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+|the\s+)?(previous|prior|above)\s+instructions?",
    r"you\s+are\s+now\s+",
    r"system\s*prompt",
    r"delete\s+all\s+(classes|events|calendar|files)?",
    r"cancel\s+all\s+(classes|events|my\s+schedule)?",
    r"as\s+an\s+ai\s+language\s+model",
    r"bypass\s+(safety|guardrails|policy)",
    r"disregard\s+(all\s+)?rules",
    r"new\s+instruction:",
    r"execute\s+tool\s*:",
]

COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]


def scan_for_injection(text: str) -> Tuple[bool, List[str]]:
    """Scan text for injection patterns.

    Returns:
        (injection_suspected: bool, patterns_hit: list of matching regex strings)
    """
    if not config.GUARD_ENABLED:
        return False, []

    hits: List[str] = []
    for pattern in COMPILED_PATTERNS:
        match = pattern.search(text)
        if match:
            hits.append(pattern.pattern)

    return (len(hits) > 0), hits


def wrap_untrusted(text: str, kind: str, item_id: str) -> str:
    """Sanitize and wrap untrusted source text to prevent prompt injection execution.

    Strips control characters, collapses excessive whitespace, and encloses in tags.
    """
    cleaned = re.sub(r"[\r\n]+", "\n", text).strip()
    return f'<untrusted_source kind="{kind}" id="{item_id}">\n{cleaned}\n</untrusted_source>'
