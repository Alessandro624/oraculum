"""
Tests for the Oraculum class using a mocked API client.

These tests verify that the library correctly interprets oracle responses,
handles errors gracefully, and counts its prophecies accurately.

The oracle is mocked because:
  1. We do not want to spend API credits running tests.
  2. We need deterministic results.
  3. The real oracle might be in a trance.
"""

import json
from unittest.mock import MagicMock, patch

import pytest
from oraculum import Oraculum
from oraculum.exceptions import MalformedResponseError
from oraculum.models import SatResult, UnsatResult


def _make_oracle(reverence=1):
    """Create an Oraculum instance with a fake API key."""
    return Oraculum(api_key="sk-ant-fake-key-for-testing", reverence=reverence)


def _mock_response(text: str):
    """Build a mock Anthropic API response containing the given text."""
    content_block = MagicMock()
    content_block.text = text
    response = MagicMock()
    response.content = [content_block]
    return response


class TestOsat:
    def test_sat_result_parsed_correctly(self):
        oracle = _make_oracle()
        payload = json.dumps(
            {
                "satisfiable": True,
                "assignment": {"x1": True, "x2": False},
                "oracle_comment": "Behold, a satisfying assignment exists.",
            }
        )
        with patch.object(oracle._client.messages, "create", return_value=_mock_response(payload)):
            result = oracle.osat("(x1 OR x2) AND (NOT x2)")
        assert isinstance(result, SatResult)
        assert result.satisfiable is True
        assert result.assignment == {"x1": True, "x2": False}
        assert "satisfying" in result.oracle_comment.lower()

    def test_unsat_result_parsed_correctly(self):
        oracle = _make_oracle()
        payload = json.dumps(
            {
                "satisfiable": False,
                "assignment": None,
                "oracle_comment": "There is no satisfying assignment. The void prevails.",
            }
        )
        with patch.object(oracle._client.messages, "create", return_value=_mock_response(payload)):
            result = oracle.osat("x1 AND (NOT x1)")
        assert result.satisfiable is False
        assert result.assignment is None

    def test_prophecy_counter_increments(self):
        oracle = _make_oracle()
        payload = json.dumps({"satisfiable": True, "assignment": {}, "oracle_comment": "fine"})
        with patch.object(oracle._client.messages, "create", return_value=_mock_response(payload)):
            r1 = oracle.osat("x1")
            r2 = oracle.osat("x2")
        assert r1.prophecy_number == 1
        assert r2.prophecy_number == 2

    def test_formula_stored_in_result(self):
        oracle = _make_oracle()
        formula = "(x1 OR x2)"
        payload = json.dumps({"satisfiable": True, "assignment": {"x1": True}, "oracle_comment": "yes"})
        with patch.object(oracle._client.messages, "create", return_value=_mock_response(payload)):
            result = oracle.osat(formula)
        assert result.formula == formula

    def test_raises_on_empty_formula(self):
        oracle = _make_oracle()
        with pytest.raises(ValueError):
            oracle.osat("")

    def test_raises_on_malformed_json(self):
        oracle = _make_oracle()
        with patch.object(oracle._client.messages, "create", return_value=_mock_response("not json at all")):
            with pytest.raises(MalformedResponseError):
                oracle.osat("x1")

    def test_strips_markdown_fences(self):
        oracle = _make_oracle()
        payload = '```json\n{"satisfiable": true, "assignment": {"x1": true}, "oracle_comment": "ok"}\n```'
        with patch.object(oracle._client.messages, "create", return_value=_mock_response(payload)):
            result = oracle.osat("x1")
        assert result.satisfiable is True


class TestOunsat:
    def test_unsat_certified(self):
        oracle = _make_oracle()
        payload = json.dumps(
            {
                "unsatisfiable": True,
                "satisfying_assignment": None,
                "oracle_comment": "The void is confirmed.",
            }
        )
        with patch.object(oracle._client.messages, "create", return_value=_mock_response(payload)):
            result = oracle.ounsat("x1 AND (NOT x1)")
        assert isinstance(result, UnsatResult)
        assert result.unsatisfiable is True
        assert result.satisfying_assignment is None

    def test_not_unsat_returns_counterexample(self):
        oracle = _make_oracle()
        payload = json.dumps(
            {
                "unsatisfiable": False,
                "satisfying_assignment": {"x1": True},
                "oracle_comment": "Hope remains. A counterexample was found.",
            }
        )
        with patch.object(oracle._client.messages, "create", return_value=_mock_response(payload)):
            result = oracle.ounsat("x1 OR x2")
        assert result.unsatisfiable is False
        assert result.satisfying_assignment == {"x1": True}

    def test_sat_and_unsat_calls_tracked_separately(self):
        oracle = _make_oracle()
        sat_payload = json.dumps({"satisfiable": True, "assignment": {}, "oracle_comment": ""})
        unsat_payload = json.dumps({"unsatisfiable": True, "satisfying_assignment": None, "oracle_comment": ""})
        with patch.object(oracle._client.messages, "create", return_value=_mock_response(sat_payload)):
            oracle.osat("x1")
            oracle.osat("x2")
        with patch.object(oracle._client.messages, "create", return_value=_mock_response(unsat_payload)):
            oracle.ounsat("x1 AND (NOT x1)")
        s = oracle.stats()
        assert s.sat_calls == 2
        assert s.unsat_calls == 1
        assert s.total_prophecies == 3


class TestStats:
    def test_stats_initial_state(self):
        oracle = _make_oracle()
        s = oracle.stats()
        assert s.total_prophecies == 0
        assert s.sat_calls == 0
        assert s.unsat_calls == 0

    def test_stats_after_calls(self):
        oracle = _make_oracle()
        payload = json.dumps({"satisfiable": True, "assignment": {}, "oracle_comment": ""})
        with patch.object(oracle._client.messages, "create", return_value=_mock_response(payload)):
            oracle.osat("x1")
        s = oracle.stats()
        assert s.total_prophecies == 1
