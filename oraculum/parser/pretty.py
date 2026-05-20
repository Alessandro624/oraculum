"""
Pretty printer: AST -> human-readable indented tree string.

Completely separate from Formula and from normalization.
Operates directly on AST nodes via the Visitor protocol.

Example output for "(x1 OR x2) AND (NOT x1 OR x3)":

    AND
    ├── OR
    │   ├── x1
    │   └── x2
    └── OR
        ├── NOT
        │   └── x1
        └── x3
"""

from .nodes import AndNode, NotNode, OrNode, VarNode

_BRANCH = "├── "
_LAST = "└── "
_PIPE = "│   "
_BLANK = "    "


class PrettyPrintVisitor:
    """
    Renders an AST as an indented Unicode tree.

    Usage:
        visitor = PrettyPrintVisitor()
        print(formula.ast.accept(visitor))
    """

    def visit_var(self, node: VarNode) -> str:
        return node.name

    def visit_not(self, node: NotNode) -> str:
        return self._render_unary("NOT", node.operand)

    def visit_and(self, node: AndNode) -> str:
        return self._render_binary("AND", node.left, node.right)

    def visit_or(self, node: OrNode) -> str:
        return self._render_binary("OR", node.left, node.right)

    # Internal rendering helpers

    def _render_unary(self, label: str, child) -> str:
        child_lines = child.accept(self).splitlines()
        return self._join(label, [child_lines])

    def _render_binary(self, label: str, left, right) -> str:
        left_lines = left.accept(self).splitlines()
        right_lines = right.accept(self).splitlines()
        return self._join(label, [left_lines, right_lines])

    def _join(self, label: str, children_lines: list[list[str]]) -> str:
        lines = [label]
        for i, child in enumerate(children_lines):
            is_last = i == len(children_lines) - 1
            prefix_first = _LAST if is_last else _BRANCH
            prefix_continue = _BLANK if is_last else _PIPE
            lines.append(prefix_first + child[0])
            for continuation in child[1:]:
                lines.append(prefix_continue + continuation)
        return "\n".join(lines)


def pretty(node: AndNode | OrNode | NotNode | VarNode) -> str:
    """
    Render an AST node as an indented tree string.

    Args:
        node: Any AST node (typically the root stored in Formula.ast).

    Returns:
        A multi-line string suitable for printing.

    Example:
        from oraculum.parser import Formula
        from oraculum.parser.pretty import pretty

        f = Formula.parse("(x1 OR x2) AND NOT x1")
        print(pretty(f.ast))
    """
    return node.accept(PrettyPrintVisitor())
