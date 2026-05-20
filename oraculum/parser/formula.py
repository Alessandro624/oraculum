"""
Formula: the validated, immutable representation of a Boolean formula.

This is the only type accepted by Oraculum.osat() and Oraculum.ounsat().
Construction is only possible via Formula.parse(), which guarantees that
any Formula instance is syntactically well-formed.

This module coordinates the tokenizer, the parser, and the internal
visitors.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .nodes import AndNode, NotNode, OrNode, VarNode
from .parser import parse_tokens
from .tokenizer import tokenize
from .visitors import DepthVisitor, NormalizeVisitor, VariableVisitor

_AnyNode = AndNode | OrNode | NotNode | VarNode


@dataclass(frozen=True)
class Formula:
    """
    A syntactically validated Boolean formula.

    Attributes:
        normalized: Canonical string form, ready to be sent to the LLM.
                    Keywords are uppercase; parentheses are minimal but unambiguous.
        variables:  Frozenset of all variable names found in the formula.
                    Used to validate the LLM's returned assignment.
        depth:      Maximum nesting depth of the AST.
                    Depth 1 means a single variable or literal.
        ast:        The root node of the AST. Use this for further operations
                    (pretty printing, future CNF conversion, etc.).
                    Excluded from repr to keep output readable.

    Do not construct directly. Use Formula.parse().
    """

    normalized: str
    variables: frozenset[str]
    depth: int
    ast: _AnyNode = field(repr=False)

    @staticmethod
    def parse(source: str) -> Formula:
        """
        Parse and validate a Boolean formula string.

        Args:
            source: A formula string, e.g. "(x1 OR x2) AND (NOT x1 OR x3)".
                    Supported syntax:
                        Variables : any identifier starting with a letter, e.g. x1, A, p
                        Operators : AND, OR, NOT (case-insensitive)
                        Grouping  : parentheses

        Returns:
            A Formula instance.

        Raises:
            FormulaError: If the source is empty, contains unrecognized
                          characters, or is syntactically malformed.

        Examples:
            Formula.parse("(x1 OR x2) AND (NOT x1 OR x3)")
            Formula.parse("x1 AND NOT x1")
            Formula.parse("(A and b) or not C")   # keywords are case-insensitive
        """
        if not source or not source.strip():
            from ..exceptions import FormulaError

            raise FormulaError("Formula source must be a non-empty string.")

        tokens = tokenize(source)
        ast = parse_tokens(tokens)

        normalized = ast.accept(NormalizeVisitor())
        variables = ast.accept(VariableVisitor())
        depth = ast.accept(DepthVisitor())

        return Formula(
            normalized=normalized,
            variables=variables,
            depth=depth,
            ast=ast,
        )

    def __str__(self) -> str:
        return self.normalized
