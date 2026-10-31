"""
Unit tests for the Router node (Milestone M2).
Can be executed with: python -m unittest tests/test_router.py
"""

import unittest
from unittest.mock import patch, MagicMock
from agent.models import RouterDecision
from agent.nodes.router import router


class TestRouterNode(unittest.TestCase):
    def test_empty_input(self):
        state = {"user_input": "  "}
        result = router(state)
        self.assertEqual(result["route"], "unclear")
        self.assertEqual(result["route_confidence"], 0.0)

    @patch("agent.nodes.router._get_router_llm")
    def test_plan_request_classification(self, mock_get_llm):
        mock_llm = MagicMock()
        mock_structured = MagicMock()
        mock_structured.invoke.return_value = RouterDecision(
            route="plan",
            confidence=0.92,
            reason="User wants to see schedule and what is due",
        )
        mock_llm.with_structured_output.return_value = mock_structured
        mock_get_llm.return_value = mock_llm

        state = {"user_input": "What is due this week? Make me a study plan"}
        with patch("config.GROQ_API_KEY", "dummy_key"):
            result = router(state)

        self.assertEqual(result["route"], "plan")
        self.assertAlmostEqual(result["route_confidence"], 0.92)

    @patch("agent.nodes.router._get_router_llm")
    def test_command_request_classification(self, mock_get_llm):
        mock_llm = MagicMock()
        mock_structured = MagicMock()
        mock_structured.invoke.return_value = RouterDecision(
            route="command",
            confidence=0.88,
            reason="User wants to cancel OS class tomorrow",
        )
        mock_llm.with_structured_output.return_value = mock_structured
        mock_get_llm.return_value = mock_llm

        state = {"user_input": "Cancel my OS class tomorrow"}
        with patch("config.GROQ_API_KEY", "dummy_key"):
            result = router(state)

        self.assertEqual(result["route"], "command")
        self.assertAlmostEqual(result["route_confidence"], 0.88)

    @patch("agent.nodes.router._get_router_llm")
    def test_low_confidence_routes_to_unclear(self, mock_get_llm):
        mock_llm = MagicMock()
        mock_structured = MagicMock()
        mock_structured.invoke.return_value = RouterDecision(
            route="plan",
            confidence=0.55,  # below 0.7 threshold
            reason="Not sure what user wants",
        )
        mock_llm.with_structured_output.return_value = mock_structured
        mock_get_llm.return_value = mock_llm

        state = {"user_input": "maybe something tomorrow"}
        with patch("config.GROQ_API_KEY", "dummy_key"):
            result = router(state)

        self.assertEqual(result["route"], "unclear")
        self.assertAlmostEqual(result["route_confidence"], 0.55)


if __name__ == "__main__":
    unittest.main()
