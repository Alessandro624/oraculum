"""
Tests for result model dataclasses.
"""

from oraculum.models import OracleStats, SatResult, UnsatResult


def _sat(satisfiable=True, assignment=None, comment="test comment"):
    return SatResult(
        satisfiable=satisfiable,
        assignment=assignment,
        oracle_comment=comment,
        prophecy_number=1,
        formula="x1 OR x2",
        prayer="O Great Oracle...",
    )


def _unsat(unsatisfiable=True, assignment=None):
    return UnsatResult(
        unsatisfiable=unsatisfiable,
        satisfying_assignment=assignment,
        oracle_comment="the void",
        prophecy_number=2,
        formula="x1 AND (NOT x1)",
        prayer="O Venerable Oracle...",
    )


class TestSatResult:
    def test_str_contains_sat(self):
        assert "SAT" in str(_sat(True))

    def test_str_contains_unsat(self):
        assert "UNSAT" in str(_sat(False))

    def test_str_shows_assignment(self):
        result = _sat(True, assignment={"x1": True, "x2": False})
        assert "x1" in str(result)
        assert "x2" in str(result)

    def test_prayer_excluded_from_repr(self):
        assert "O Great Oracle" not in repr(_sat())

    def test_prophecy_number_in_str(self):
        assert "#1" in str(_sat())


class TestUnsatResult:
    def test_certified_in_str(self):
        assert "certified" in str(_unsat(True)).lower()

    def test_counterexample_in_str_when_not_unsat(self):
        result = _unsat(False, assignment={"x1": True})
        assert "counterexample" in str(result).lower()

    def test_prayer_excluded_from_repr(self):
        assert "O Venerable Oracle" not in repr(_unsat())


class TestOracleStats:
    def test_fields(self):
        s = OracleStats(total_prophecies=10, sat_calls=6, unsat_calls=4)
        assert s.total_prophecies == 10
        assert s.sat_calls == 6
        assert s.unsat_calls == 4

    def test_editorial_defaults(self):
        s = OracleStats(total_prophecies=0, sat_calls=0, unsat_calls=0)
        assert "open" in s.p_vs_np_status
        assert "O(1)" in s.theoretical_complexity
        assert "2087" in s.turing_award_eta
