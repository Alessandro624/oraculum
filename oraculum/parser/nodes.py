"""
AST node types and the Visitor protocol.

Adding a new operation means adding a new Visitor. Nodes never change.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, TypeVar

T = TypeVar("T")


class Visitor(Protocol[T]):
    """
    Visitor protocol for AST traversal.

    Implement this protocol to add a new operation over the AST without
    modifying any node class.
    """

    def visit_var(self, node: VarNode) -> T: ...
    def visit_not(self, node: NotNode) -> T: ...
    def visit_and(self, node: AndNode) -> T: ...
    def visit_or(self, node: OrNode) -> T: ...


class Node(Protocol):
    """Structural protocol satisfied by all AST node types."""

    def accept(self, visitor: Visitor[T]) -> T: ...


@dataclass(frozen=True)
class VarNode:
    """A propositional variable, e.g. x1, A, p."""

    name: str

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_var(self)


@dataclass(frozen=True)
class NotNode:
    """Logical negation: NOT operand."""

    operand: VarNode | NotNode | AndNode | OrNode

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_not(self)


@dataclass(frozen=True)
class AndNode:
    """Logical conjunction: left AND right."""

    left: VarNode | NotNode | AndNode | OrNode
    right: VarNode | NotNode | AndNode | OrNode

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_and(self)


@dataclass(frozen=True)
class OrNode:
    """Logical disjunction: left OR right."""

    left: VarNode | NotNode | AndNode | OrNode
    right: VarNode | NotNode | AndNode | OrNode

    def accept(self, visitor: Visitor[T]) -> T:
        return visitor.visit_or(self)
