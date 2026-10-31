"""
Router node — decides whether the user wants a plan or a command.

Milestone: M2 (Router + Orchestrator Skeleton)

The node:
* Loads the small model defined by ROUTER_MODEL in config.
* Calls the model with structured output schema `RouterDecision`.
* Returns `route` ("plan", "command" or "unclear") and the confidence
  score as part of the updated AgentState.
"""

from __future__ import annotations
import os
from typing import Any
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage
from pydantic import ValidationError

import config
from ..models import RouterDecision


def _get_router_llm() -> ChatGroq:
    """Instantiate the small LLM for routing."""
    api_key = config.GROQ_API_KEY or os.getenv("GROQ_API_KEY", "")
    return ChatGroq(
        model=config.ROUTER_MODEL,
        temperature=0.0,
        max_tokens=256,
        groq_api_key=api_key or "mock_key_if_none",
    )


def router(state: dict) -> dict:
    """LangGraph node function.

    Input:  state dict (must contain key `user_input`).
    Output: state dict with updated keys `route`, `route_confidence`, `router_reason`.
    """
    user_input = state.get("user_input", "").strip()
    if not user_input:
        state["route"] = "unclear"
        state["route_confidence"] = 0.0
        state["router_reason"] = "Empty user input"
        return state

    # If no real API key is configured, fallback deterministically
    api_key = config.GROQ_API_KEY or os.getenv("GROQ_API_KEY", "")
    if not api_key:
        state["route"] = "unclear"
        state["route_confidence"] = 0.0
        state["router_reason"] = "No GROQ_API_KEY found in environment"
        return state

    try:
        llm = _get_router_llm()
        prompt = (
            "Classify the student's message.\n"
            "- plan: wants to see what is due, or wants a study plan or schedule.\n"
            "- command: wants to change something (cancel, move, reschedule).\n"
            "- unclear: cannot tell.\n"
            "Return route, confidence (0 to 1) and a one-line reason.\n\n"
            f"Student message: {user_input}"
        )
        structured_llm = llm.with_structured_output(RouterDecision)
        decision: RouterDecision = structured_llm.invoke([HumanMessage(content=prompt)])

        min_conf = config.ROUTER_MIN_CONFIDENCE
        route = decision.route if decision.confidence >= min_conf else "unclear"

        state["route"] = route
        state["route_confidence"] = decision.confidence
        state["router_reason"] = decision.reason
    except Exception as exc:
        # Fallback to unclear on any LLM/rate limit/validation error
        state["route"] = "unclear"
        state["route_confidence"] = 0.0
        state["router_reason"] = f"Router fallback due to: {type(exc).__name__}"

    return state
