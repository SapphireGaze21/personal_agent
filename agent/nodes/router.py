"""
Router node — decides whether the user wants a plan or a command.

Milestone: M2 (Router + Orchestrator Skeleton)

Uses a small LLM with structured output (RouterDecision) to classify:
    - "plan": user wants to see what's due or get a study plan
    - "command": user wants to change something (cancel, move, reschedule)
    - "unclear": can't tell — asks a clarifying question

The router only chooses a route. It never changes anything itself.

If confidence is below ROUTER_MIN_CONFIDENCE, it routes to "unclear"
and the graph goes to ask_clarification → END.

Input:  state["user_input"]
Output: state["route"], state["route_confidence"]
"""

from typing import TypedDict, Any
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field, ValidationError
import os
# Import the schema we already have in models.py
from ..models import RouterDecision
# Helper to load the LLM – respects .env variables
def _get_router_llm() -> ChatGroq:
    model_name = os.getenv("ROUTER_MODEL", "llama-3.1-8b-instant")
    # The Groq wrapper falls back to a mock key if GROQ_API_KEY is missing.
    return ChatGroq(model=model_name, temperature=0.0, max_tokens=512)
def router(state: dict) -> dict:
    """LangGraph node function.
    Input:  state dict (must contain key `user_input`).
    Output: state dict with added keys `route` and `route_confidence`.
    """
    user_input = state.get("user_input", "").strip()
    if not user_input:
        # No input – treat as unclear
        state.update({"route": "unclear", "route_confidence": 0.0})
        return state
    llm = _get_router_llm()
    # Very small prompt – the heavy lifting is in the structured output schema
    prompt = PromptTemplate.from_template(
        "Classify the student's message.\n"
        "- plan: wants a study plan or due‑dates.\n"
        "- command: wants to change something (cancel, move, reschedule).\n"
        "- unclear: cannot tell.\n"
        "Return a JSON with fields `route`, `confidence` (0‑1) and `reason`."
    )
    # Bind the structured output schema
    structured_llm = llm.with_structured_output(RouterDecision)
    try:
        decision: RouterDecision = structured_llm.invoke(
            [HumanMessage(content=user_input)],  # single turn
            # The prompt template is already baked into the LLM call
        )
    except ValidationError as e:
        # If the LLM returns malformed JSON, fallback to unclear
        state.update({"route": "unclear", "route_confidence": 0.0, "router_error": str(e)})
        return state
    except Exception as exc:
        # Any other failure – also fallback
        state.update({"route": "unclear", "route_confidence": 0.0, "router_error": str(exc)})
        return state
    # Confidence threshold is defined in .env (default 0.7)
    min_conf = float(os.getenv("ROUTER_MIN_CONFIDENCE", "0.7"))
    route = decision.route if decision.confidence >= min_conf else "unclear"
    # Update the state
    state.update(
        {
            "route": route,
            "route_confidence": decision.confidence,
            "router_reason": decision.reason,
        }
    )
    return state