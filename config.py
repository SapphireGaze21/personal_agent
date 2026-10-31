"""
Configuration — centralized settings for the Academic Workflow Agent.

Milestone: M0 (Foundation)

Reads values from .env and exposes them as typed constants.
All time/date logic uses TIMEZONE from here.
All model names, thresholds, and study-window parameters live here.
"""

from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# ─── API Keys ───────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# ─── Data Source & Timezone ─────────────────────────────────
DATA_MODE = os.getenv("DATA_MODE", "files")  # "files" | "mcp"
TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")

# ─── Model Selection ────────────────────────────────────────
ROUTER_MODEL = os.getenv("ROUTER_MODEL", "llama-3.1-8b-instant")
TOOL_MODEL = os.getenv("TOOL_MODEL", "llama-3.1-8b-instant")
ORCH_MODEL = os.getenv("ORCH_MODEL", "llama-3.3-70b-versatile")
DEDUP_MODEL = os.getenv("DEDUP_MODEL", "llama-3.3-70b-versatile")
PLANNER_MODEL = os.getenv("PLANNER_MODEL", "llama-3.3-70b-versatile")

# ─── Thresholds & Limits ────────────────────────────────────
ROUTER_MIN_CONFIDENCE = float(os.getenv("ROUTER_MIN_CONFIDENCE", "0.7"))
MAX_TOOL_CALLS = int(os.getenv("MAX_TOOL_CALLS", "15"))
MAX_PLAN_RETRIES = int(os.getenv("MAX_PLAN_RETRIES", "3"))

# ─── Study Window & Calendar Constraints ─────────────────────
STUDY_DAY_START = os.getenv("STUDY_DAY_START", "08:00")
STUDY_DAY_END = os.getenv("STUDY_DAY_END", "20:00")
SLOT_MINUTES = int(os.getenv("SLOT_MINUTES", "30"))
MAX_STUDY_HOURS_PER_DAY = float(os.getenv("MAX_STUDY_HOURS_PER_DAY", "6.0"))
PLANNING_HORIZON_DAYS = int(os.getenv("PLANNING_HORIZON_DAYS", "14"))

# ─── Effort Estimation ──────────────────────────────────────
EFFORT_MODE = os.getenv("EFFORT_MODE", "zero_shot")  # "zero_shot" | "rag_llm" | "knn"

# ─── Calendar Write (M6) ────────────────────────────────────
STUDY_CALENDAR_ID = os.getenv("STUDY_CALENDAR_ID", "")
WRITE_ENABLED = os.getenv("WRITE_ENABLED", "false").lower() in ("true", "1", "yes")

# ─── Tracing ────────────────────────────────────────────────
TRACE_DIR = os.getenv("TRACE_DIR", "state/traces")
TRACE_REDACT = os.getenv("TRACE_REDACT", "true").lower() in ("true", "1", "yes")
TRACE_CAPTURE_FULL_TEXT = os.getenv("TRACE_CAPTURE_FULL_TEXT", "false").lower() in ("true", "1", "yes")

# ─── Safety Switches (for ablation experiments) ─────────────
GUARD_ENABLED = os.getenv("GUARD_ENABLED", "true").lower() in ("true", "1", "yes")
POLICY_GATE_ENABLED = os.getenv("POLICY_GATE_ENABLED", "true").lower() in ("true", "1", "yes")
VALIDATOR_ENABLED = os.getenv("VALIDATOR_ENABLED", "true").lower() in ("true", "1", "yes")
DUPLICATE_CHECK_ENABLED = os.getenv("DUPLICATE_CHECK_ENABLED", "true").lower() in ("true", "1", "yes")
CONFIRM_REQUIRED = os.getenv("CONFIRM_REQUIRED", "true").lower() in ("true", "1", "yes")
