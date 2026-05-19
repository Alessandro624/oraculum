"""
Tests for Oraculum using a stub LLMProvider.

No real API is called. All provider interactions go through StubProvider.
Formula instances are constructed with Formula.parse() as in real usage.
"""

import json
from typing import Optional

import pytest  # type: ignore

from oraculum.exceptions import MalformedResponseError
from oraculum.models import SatResult, UnsatResult
from oraculum.oracle import Oraculum
from oraculum.parser.formula import Formula


class StubProvider:
    def __init__(self, response: str) -> None:
        self._response = response
        self.calls: list[tuple[str, str]] = []

    def complete(self, system: str, user: str) -> str:
        self.calls.append((system, user))
        return self._response


def _sat_json(satisfiable: bool, assignment: Optional[dict] = None, comment: str = "test") -> str:
    return json.dumps({"satisfiable": satisfiable, "assignment": assignment, "oracle_comment": comment})


def _unsat_json(unsatisfiable: bool, assignment: Optional[dict] = None, comment: str = "test") -> str:
    return json.dumps({"unsatisfiable": unsatisfiable, "satisfying_assignment": assignment, "oracle_comment": comment})


def _oracle(response: str) -> tuple[Oraculum, StubProvider]:
    provider = StubProvider(response)
    return Oraculum(provider), provider


class TestOsat:
    def test_returns_sat_result(self):
        oracle, _ = _oracle(_sat_json(True, {"x1": True}))
        result = oracle.osat(Formula.parse("x1"))
        assert isinstance(result, SatResult)
        assert result.satisfiable is True

    def test_assignment_filtered_to_known_variables(self):
        # Oracle returns y99 which is not in the formula; should be dropped
        oracle, _ = _oracle(_sat_json(True, {"x1": True, "y99": False}))
        result = oracle.osat(Formula.parse("x1"))
        assert "y99" not in (result.assignment or {})
        assert result.assignment == {"x1": True}

    def test_unsat_result(self):
        oracle, _ = _oracle(_sat_json(False))
        result = oracle.osat(Formula.parse("x1 AND (NOT x1)"))
        assert result.satisfiable is False
        assert result.assignment is None

    def test_oracle_comment_stored(self):
        oracle, _ = _oracle(_sat_json(True, comment="Behold."))
        result = oracle.osat(Formula.parse("x1"))
        assert result.satisfiable is True
        assert result.oracle_comment == "Behold."

    def test_formula_stored_in_result(self):
        f = Formula.parse("x1 OR x2")
        oracle, _ = _oracle(_sat_json(True))
        result = oracle.osat(f)
        assert result.formula is f

    def test_prayer_contains_normalized_formula(self):
        oracle, provider = _oracle(_sat_json(True))
        oracle.osat(Formula.parse("x1 or x2"))
        _, user_msg = provider.calls[0]
        assert "x1 OR x2" in user_msg

    def test_wrong_type_raises_typeerror(self):
        oracle, _ = _oracle(_sat_json(True))
        with pytest.raises(TypeError, match="Formula"):
            oracle.osat("x1 OR x2")  # type: ignore

    def test_malformed_json_raises(self):
        oracle, _ = _oracle("not json")
        with pytest.raises(MalformedResponseError):
            oracle.osat(Formula.parse("x1"))

    def test_markdown_fences_stripped(self):
        raw = "```json\n" + _sat_json(True, {"x1": True}) + "\n```"
        oracle, _ = _oracle(raw)
        result = oracle.osat(Formula.parse("x1"))
        assert result.satisfiable is True

    def test_prophecy_number_increments(self):
        oracle, _ = _oracle(_sat_json(True))
        r1 = oracle.osat(Formula.parse("x1"))
        r2 = oracle.osat(Formula.parse("x2"))
        assert r1.prophecy_number == 1
        assert r2.prophecy_number == 2


class TestOunsat:
    def test_returns_unsat_result(self):
        oracle, _ = _oracle(_unsat_json(True))
        result = oracle.ounsat(Formula.parse("x1 AND (NOT x1)"))
        assert isinstance(result, UnsatResult)
        assert result.unsatisfiable is True

    def test_counterexample_filtered(self):
        oracle, _ = _oracle(_unsat_json(False, {"x1": True, "ghost": True}))
        result = oracle.ounsat(Formula.parse("x1 OR x2"))
        assert "ghost" not in (result.satisfying_assignment or {})

    def test_wrong_type_raises_typeerror(self):
        oracle, _ = _oracle(_unsat_json(True))
        with pytest.raises(TypeError, match="Formula"):
            oracle.ounsat("x1")  # type: ignore


class TestStats:
    def test_initial_zeroes(self):
        oracle, _ = _oracle("{}")
        s = oracle.stats()
        assert s.total_prophecies == 0
        assert s.sat_calls == 0
        assert s.unsat_calls == 0

    def test_counts_tracked_separately(self):
        oracle, _ = _oracle(_sat_json(True))
        oracle.osat(Formula.parse("x1"))
        oracle.osat(Formula.parse("x2"))

        oracle._provider = StubProvider(_unsat_json(True))
        oracle.ounsat(Formula.parse("x1 AND (NOT x1)"))

        s = oracle.stats()
        assert s.sat_calls == 2
        assert s.unsat_calls == 1
        assert s.total_prophecies == 3

    def test_editorial_fields_present(self):
        oracle, _ = _oracle(_sat_json(True))
        s = oracle.stats()
        assert "open" in s.p_vs_np_status
        assert "O(1)" in s.theoretical_complexity
