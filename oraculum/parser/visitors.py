"""
Internal visitors used by Formula during construction.

NormalizeVisitor  -> canonical string sent to the LLM
DepthVisitor      -> maximum nesting depth of the AST
VariableVisitor   -> frozenset of variable names
"""

from .nodes import AndNode, NotNode, OrNode, VarNode


class NormalizeVisitor:
    """
    Produces a canonical string representation of the formula.

    Conventions:
    - Keywords are uppercase: AND, OR, NOT.
    - Binary operators are surrounded by single spaces.
    - Parentheses are added only where needed to reflect actual AST structure,
      respecting operator precedence (no redundant parentheses).
    """

    def visit_var(self, node: VarNode) -> str:
        return node.name

    def visit_not(self, node: NotNode) -> str:
        operand = node.operand.accept(self)
        if isinstance(node.operand, (AndNode, OrNode)):
            return f"NOT ({operand})"
        return f"NOT {operand}"

    def visit_and(self, node: AndNode) -> str:
        left = self._paren_if(node.left, (OrNode,))
        right = self._paren_if(node.right, (OrNode,))
        return f"{left} AND {right}"

    def visit_or(self, node: OrNode) -> str:
        left = node.left.accept(self)
        right = node.right.accept(self)
        return f"{left} OR {right}"

    def _paren_if(self, node: AndNode | OrNode | NotNode | VarNode, types: tuple) -> str:
        result = node.accept(self)
        if isinstance(node, types):
            return f"({result})"
        return result


class DepthVisitor:
    """Returns the maximum nesting depth of the AST (root = depth 1)."""

    def visit_var(self, node: VarNode) -> int:
        return 1

    def visit_not(self, node: NotNode) -> int:
        return 1 + node.operand.accept(self)

    def visit_and(self, node: AndNode) -> int:
        return 1 + max(node.left.accept(self), node.right.accept(self))

    def visit_or(self, node: OrNode) -> int:
        return 1 + max(node.left.accept(self), node.right.accept(self))


class VariableVisitor:
    """Collects all variable names in the AST."""

    def visit_var(self, node: VarNode) -> frozenset[str]:
        return frozenset({node.name})

    def visit_not(self, node: NotNode) -> frozenset[str]:
        return node.operand.accept(self)

    def visit_and(self, node: AndNode) -> frozenset[str]:
        return node.left.accept(self) | node.right.accept(self)

    def visit_or(self, node: OrNode) -> frozenset[str]:
        return node.left.accept(self) | node.right.accept(self)
