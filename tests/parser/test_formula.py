"""
Tests for Formula.parse(): end-to-end construction and metadata.
"""

import pytest  # type: ignore
from oraculum.parser.formula import Formula
from oraculum.exceptions import FormulaError


class TestParse:
    def test_returns_formula(self):
        f = Formula.parse("x1 OR x2")
        assert isinstance(f, Formula)

    def test_formula_is_frozen(self):
        f = Formula.parse("x1")
        with pytest.raises((AttributeError, TypeError)):
            f.normalized = "something else"

    def test_str_returns_normalized(self):
        f = Formula.parse("x1 OR x2")
        assert str(f) == f.normalized

    def test_empty_string_raises(self):
        with pytest.raises(FormulaError):
            Formula.parse("")

    def test_whitespace_only_raises(self):
        with pytest.raises(FormulaError):
            Formula.parse("   ")

    def test_malformed_raises(self):
        with pytest.raises(FormulaError):
            Formula.parse("x1 AND OR x2")


class TestNormalized:
    def test_keywords_uppercase(self):
        f = Formula.parse("x1 and x2")
        assert "AND" in f.normalized
        assert "and" not in f.normalized

    def test_extra_spaces_removed(self):
        f = Formula.parse("x1   OR   x2")
        assert "  " not in f.normalized

    def test_redundant_parens_removed(self):
        f1 = Formula.parse("x1 OR x2")
        f2 = Formula.parse("(x1 OR x2)")
        assert f1.normalized == f2.normalized

    def test_precedence_preserved_without_extra_parens(self):
        f = Formula.parse("x1 OR x2 AND x3")
        # AND binds tighter, so x2 AND x3 is the right child of OR
        # normalized should not add unnecessary parens around x2 AND x3
        assert f.normalized == "x1 OR x2 AND x3"

    def test_necessary_parens_added(self):
        # (x1 OR x2) AND x3 - the OR group needs parens when inside AND
        f = Formula.parse("(x1 OR x2) AND x3")
        assert "(" in f.normalized


class TestVariables:
    def test_single_variable(self):
        f = Formula.parse("x1")
        assert f.variables == frozenset({"x1"})

    def test_multiple_variables(self):
        f = Formula.parse("(x1 OR x2) AND x3")
        assert f.variables == frozenset({"x1", "x2", "x3"})

    def test_duplicate_variables_counted_once(self):
        f = Formula.parse("x1 AND x1")
        assert f.variables == frozenset({"x1"})

    def test_variable_inside_not(self):
        f = Formula.parse("NOT x1")
        assert "x1" in f.variables


class TestDepth:
    def test_single_var_depth_one(self):
        assert Formula.parse("x1").depth == 1

    def test_not_increases_depth(self):
        assert Formula.parse("NOT x1").depth == 2

    def test_binary_operator_depth(self):
        assert Formula.parse("x1 AND x2").depth == 2

    def test_deeper_nesting(self):
        f = Formula.parse("NOT (x1 AND x2)")
        assert f.depth == 3

    def test_balanced_tree(self):
        # (x1 OR x2) AND (x3 OR x4) -> depth 3
        f = Formula.parse("(x1 OR x2) AND (x3 OR x4)")
        assert f.depth == 3


class TestAst:
    def test_ast_is_present(self):
        f = Formula.parse("x1 AND x2")
        assert f.ast is not None

    def test_ast_not_in_repr(self):
        f = Formula.parse("x1")
        assert "ast" not in repr(f) or "VarNode" not in repr(f)
