"""
Tests for the pretty printer.
"""

from oraculum.parser.formula import Formula
from oraculum.parser.pretty import pretty
from oraculum.parser.nodes import VarNode, NotNode, AndNode, OrNode


def tree(source: str) -> str:
    return pretty(Formula.parse(source).ast)


class TestStructure:
    def test_single_var(self):
        assert tree("x1") == "x1"

    def test_not_has_child(self):
        output = tree("NOT x1")
        lines = output.splitlines()
        assert lines[0] == "NOT"
        assert "x1" in lines[1]

    def test_and_has_two_children(self):
        output = tree("x1 AND x2")
        lines = output.splitlines()
        assert lines[0] == "AND"
        assert len(lines) == 3

    def test_or_has_two_children(self):
        output = tree("x1 OR x2")
        lines = output.splitlines()
        assert lines[0] == "OR"

    def test_last_child_uses_corner(self):
        output = tree("x1 AND x2")
        assert any(line.startswith("\u2514") for line in output.splitlines())

    def test_first_child_uses_branch(self):
        output = tree("x1 AND x2")
        assert any(line.startswith("\u251c") for line in output.splitlines())


class TestNestedOutput:
    def test_complex_formula_multiline(self):
        output = tree("(x1 OR x2) AND (NOT x1 OR x3)")
        lines = output.splitlines()
        assert lines[0] == "AND"
        assert len(lines) > 4

    def test_deep_not_indents_correctly(self):
        output = tree("NOT NOT x1")
        lines = output.splitlines()
        assert lines[0] == "NOT"
        assert "NOT" in lines[1]
        assert "x1" in lines[2]

    def test_returns_string(self):
        assert isinstance(tree("x1 AND x2"), str)


class TestDirectNodeUsage:
    def test_works_on_raw_nodes(self):
        node = AndNode(VarNode("a"), OrNode(VarNode("b"), NotNode(VarNode("c"))))
        output = pretty(node)
        assert "AND" in output
        assert "OR" in output
        assert "NOT" in output
        assert "a" in output
