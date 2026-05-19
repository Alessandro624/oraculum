"""
Tests for PrayerBuilder. No API key required.
"""

from oraculum.prayers import PrayerBuilder


class TestSatPrayer:
    def test_contains_formula(self):
        formula = "(x1 OR x2) AND (NOT x1)"
        prayer = PrayerBuilder().build_sat_prayer(formula)
        assert formula in prayer

    def test_requests_json_keys(self):
        prayer = PrayerBuilder().build_sat_prayer("x1")
        assert "satisfiable" in prayer
        assert "assignment" in prayer
        assert "oracle_comment" in prayer

    def test_returns_string(self):
        assert isinstance(PrayerBuilder().build_sat_prayer("x1"), str)


class TestUnsatPrayer:
    def test_contains_formula(self):
        formula = "x1 AND (NOT x1)"
        prayer = PrayerBuilder().build_unsat_prayer(formula)
        assert formula in prayer

    def test_requests_json_keys(self):
        prayer = PrayerBuilder().build_unsat_prayer("x1")
        assert "unsatisfiable" in prayer
        assert "satisfying_assignment" in prayer
        assert "oracle_comment" in prayer


class TestReverence:
    def test_clamped_at_minimum(self):
        assert PrayerBuilder(reverence=0).reverence == 1

    def test_clamped_at_maximum(self):
        assert PrayerBuilder(reverence=99).reverence == 10

    def test_high_reverence_longer_than_low(self):
        low = PrayerBuilder(reverence=1)
        high = PrayerBuilder(reverence=10)
        formula = "x1 OR x2"
        low_avg = sum(len(low.build_sat_prayer(formula)) for _ in range(20)) / 20
        high_avg = sum(len(high.build_sat_prayer(formula)) for _ in range(20)) / 20
        assert high_avg >= low_avg
