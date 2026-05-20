"""
Tests for the LL(1) parser: list[Token] -> AST.
"""

import pytest  # type: ignore
from oraculum.parser.tokenizer import tokenize
from oraculum.parser.parser import parse_tokens
from oraculum.parser.nodes import AndNode, OrNode, NotNode, VarNode
from oraculum.exceptions import FormulaError


def parse(source: str):
    return parse_tokens(tokenize(source))


class TestVariables:
    def test_single_var(self):
        node = parse("x1")
        assert isinstance(node, VarNode)
        assert node.name == "x1"


class TestNot:
    def test_not_var(self):
        node = parse("NOT x1")
        assert isinstance(node, NotNode)
        assert isinstance(node.operand, VarNode)

    def test_double_not(self):
        node = parse("NOT NOT x1")
        assert isinstance(node, NotNode)
        assert isinstance(node.operand, NotNode)


class TestAnd:
    def test_simple_and(self):
        node = parse("x1 AND x2")
        assert isinstance(node, AndNode)
        assert isinstance(node.left, VarNode)
        assert isinstance(node.right, VarNode)

    def test_and_is_left_associative(self):
        # x1 AND x2 AND x3 -> (x1 AND x2) AND x3
        node = parse("x1 AND x2 AND x3")
        assert isinstance(node, AndNode)
        assert isinstance(node.left, AndNode)
        assert isinstance(node.right, VarNode)


class TestOr:
    def test_simple_or(self):
        node = parse("x1 OR x2")
        assert isinstance(node, OrNode)

    def test_or_is_left_associative(self):
        node = parse("x1 OR x2 OR x3")
        assert isinstance(node, OrNode)
        assert isinstance(node.left, OrNode)


class TestPrecedence:
    def test_and_binds_tighter_than_or(self):
        # x1 OR x2 AND x3  ->  x1 OR (x2 AND x3)
        node = parse("x1 OR x2 AND x3")
        assert isinstance(node, OrNode)
        assert isinstance(node.right, AndNode)

    def test_not_binds_tighter_than_and(self):
        # NOT x1 AND x2  ->  (NOT x1) AND x2
        node = parse("NOT x1 AND x2")
        assert isinstance(node, AndNode)
        assert isinstance(node.left, NotNode)

    def test_parentheses_override_precedence(self):
        # (x1 OR x2) AND x3
        node = parse("(x1 OR x2) AND x3")
        assert isinstance(node, AndNode)
        assert isinstance(node.left, OrNode)


class TestParentheses:
    def test_nested(self):
        node = parse("((x1))")
        assert isinstance(node, VarNode)

    def test_complex_nesting(self):
        node = parse("(x1 OR x2) AND (NOT x1 OR x3)")
        assert isinstance(node, AndNode)
        assert isinstance(node.left, OrNode)
        assert isinstance(node.right, OrNode)


class TestErrors:
    def test_empty_tokens_raises(self):
        with pytest.raises(FormulaError):
            parse("")

    def test_unmatched_lparen(self):
        with pytest.raises(FormulaError):
            parse("(x1 AND x2")

    def test_double_operator(self):
        with pytest.raises(FormulaError):
            parse("x1 AND OR x2")

    def test_operator_at_start(self):
        with pytest.raises(FormulaError):
            parse("AND x1")

    def test_missing_operand_after_not(self):
        with pytest.raises(FormulaError):
            parse("NOT")

    def test_error_includes_position(self):
        with pytest.raises(FormulaError, match="position"):
            parse("x1 AND OR x2")
