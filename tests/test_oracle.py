"""
Tests for Oraculum using a stub LLMProvider.

No real API is called. The stub returns pre-configured JSON responses,
allowing us to test parsing, counting, and error handling in isolation.
"""

import json
from typing import Optional

import pytest

from oraculum.exceptions import MalformedResponseError
from oraculum.models import SatResult, UnsatResult
from oraculum.oracle import Oraculum


class StubProvider:
    """
    A minimal LLMProvider stub that returns a fixed JSON string.

    Accepts an optional override to simulate malformed responses.
    """

    def __init__(self, response: str) -> None:
        self._response = response
        self.calls: list[tuple[str, str]] = []

    def complete(self, system: str, user: str) -> str:
        self.calls.append((system, user))
        return self._response


def _sat_response(satisfiable: bool, assignment: Optional[dict] = None, comment: str = "test") -> str:
    return json.dumps(
        {
            "satisfiable": satisfiable,
            "assignment": assignment,
            "oracle_comment": comment,
        }
    )


def _unsat_response(unsatisfiable: bool, assignment: Optional[dict] = None, comment: str = "test") -> str:
    return json.dumps(
        {
            "unsatisfiable": unsatisfiable,
            "satisfying_assignment": assignment,
            "oracle_comment": comment,
        }
    )


class TestOsat:
    def test_returns_sat_result(self):
        provider = StubProvider(_sat_response(True, {"x1": True}))
        oracle = Oraculum(provider)
        result = oracle.osat("x1")
        assert isinstance(result, SatResult)
        assert result.satisfiable is True
        assert result.assignment == {"x1": True}

    def test_returns_unsat_result(self):
        provider = StubProvider(_sat_response(False))
        oracle = Oraculum(provider)
        result = oracle.osat("x1 AND (NOT x1)")
        assert result.satisfiable is False
        assert result.assignment is None

    def test_oracle_comment_stored(self):
        provider = StubProvider(_sat_response(True, comment="Behold."))
        oracle = Oraculum(provider)
        result = oracle.osat("x1")
        assert result.oracle_comment == "Behold."

    def test_formula_stored_in_result(self):
        provider = StubProvider(_sat_response(True))
        oracle = Oraculum(provider)
        formula = "(x1 OR x2)"
        result = oracle.osat(formula)
        assert result.formula == formula

    def test_prayer_sent_to_provider(self):
        provider = StubProvider(_sat_response(True))
        oracle = Oraculum(provider)
        oracle.osat("x1")
        assert len(provider.calls) == 1
        _, user_msg = provider.calls[0]
        assert "x1" in user_msg

    def test_empty_formula_raises(self):
        provider = StubProvider(_sat_response(True))
        oracle = Oraculum(provider)
        with pytest.raises(ValueError):
            oracle.osat("   ")

    def test_malformed_json_raises(self):
        provider = StubProvider("not json at all")
        oracle = Oraculum(provider)
        with pytest.raises(MalformedResponseError):
            oracle.osat("x1")

    def test_markdown_fences_stripped(self):
        raw = "```json\n" + _sat_response(True, {"x1": True}) + "\n```"
        provider = StubProvider(raw)
        oracle = Oraculum(provider)
        result = oracle.osat("x1")
        assert result.satisfiable is True

    def test_prophecy_number_increments(self):
        provider = StubProvider(_sat_response(True))
        oracle = Oraculum(provider)
        r1 = oracle.osat("x1")
        r2 = oracle.osat("x2")
        assert r1.prophecy_number == 1
        assert r2.prophecy_number == 2


class TestOunsat:
    def test_returns_unsat_result(self):
        provider = StubProvider(_unsat_response(True))
        oracle = Oraculum(provider)
        result = oracle.ounsat("x1 AND (NOT x1)")
        assert isinstance(result, UnsatResult)
        assert result.unsatisfiable is True

    def test_counterexample_returned_when_not_unsat(self):
        provider = StubProvider(_unsat_response(False, {"x1": True}))
        oracle = Oraculum(provider)
        result = oracle.ounsat("x1 OR x2")
        assert result.unsatisfiable is False
        assert result.satisfying_assignment == {"x1": True}

    def test_empty_formula_raises(self):
        provider = StubProvider(_unsat_response(True))
        oracle = Oraculum(provider)
        with pytest.raises(ValueError):
            oracle.ounsat("")


class TestStats:
    def test_initial_state(self):
        oracle = Oraculum(StubProvider("{}"))
        s = oracle.stats()
        assert s.total_prophecies == 0
        assert s.sat_calls == 0
        assert s.unsat_calls == 0

    def test_counts_tracked_separately(self):
        sat_stub = StubProvider(_sat_response(True))
        unsat_stub = StubProvider(_unsat_response(True))

        oracle = Oraculum(sat_stub)
        oracle.osat("x1")
        oracle.osat("x2")

        oracle._provider = unsat_stub
        oracle.ounsat("x1 AND (NOT x1)")

        s = oracle.stats()
        assert s.sat_calls == 2
        assert s.unsat_calls == 1
        assert s.total_prophecies == 3

    def test_editorial_fields_present(self):
        oracle = Oraculum(StubProvider("{}"))
        s = oracle.stats()
        assert "open" in s.p_vs_np_status
        assert "O(1)" in s.theoretical_complexity
