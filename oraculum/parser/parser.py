"""
LL(1) recursive descent parser: list[Token] -> AST root Node.

Grammar (in order of increasing precedence):

    formula     ::= disjunction EOF
    disjunction ::= conjunction  ( OR  conjunction  )*
    conjunction ::= negation     ( AND negation     )*
    negation    ::= NOT negation | atom
    atom        ::= LPAREN formula_inner RPAREN | VAR
    formula_inner ::= disjunction

Precedence (lowest to highest): OR < AND < NOT < atom.
This matches standard Boolean algebra convention.

The parser never backtracks. Each grammar rule peeks at the current
token and immediately knows which production to apply.
"""

from ..exceptions import FormulaError
from .nodes import AndNode, NotNode, OrNode, VarNode
from .tokens import Token, TokenType


class _Parser:
    """
    Stateful parser. Instantiate once per formula string; do not reuse.
    """

    def __init__(self, tokens: list[Token]) -> None:
        self._tokens = tokens
        self._pos = 0

    # Public entry point

    def parse(self) -> AndNode | OrNode | NotNode | VarNode:
        root = self._disjunction()
        self._expect(TokenType.EOF)
        return root

    # Grammar rules (one method per rule)

    def _disjunction(self) -> AndNode | OrNode | NotNode | VarNode:
        left = self._conjunction()
        while self._current().type == TokenType.OR:
            self._advance()
            right = self._conjunction()
            left = OrNode(left, right)
        return left

    def _conjunction(self) -> AndNode | OrNode | NotNode | VarNode:
        left = self._negation()
        while self._current().type == TokenType.AND:
            self._advance()
            right = self._negation()
            left = AndNode(left, right)
        return left

    def _negation(self) -> AndNode | OrNode | NotNode | VarNode:
        if self._current().type == TokenType.NOT:
            self._advance()
            operand = self._negation()
            return NotNode(operand)
        return self._atom()

    def _atom(self) -> AndNode | OrNode | NotNode | VarNode:
        token = self._current()

        if token.type == TokenType.LPAREN:
            self._advance()
            inner = self._disjunction()
            self._expect(TokenType.RPAREN)
            return inner

        if token.type == TokenType.VAR:
            self._advance()
            return VarNode(token.value)

        raise FormulaError(f"Expected a variable or '(' but got {token.value!r} " f"at position {token.position}.")

    # Token stream helpers

    def _current(self) -> Token:
        return self._tokens[self._pos]

    def _advance(self) -> Token:
        token = self._tokens[self._pos]
        if token.type != TokenType.EOF:
            self._pos += 1
        return token

    def _expect(self, ttype: TokenType) -> Token:
        token = self._current()
        if token.type != ttype:
            raise FormulaError(f"Expected {ttype.name} but got {token.value!r} " f"at position {token.position}.")
        return self._advance()


def parse_tokens(tokens: list[Token]) -> AndNode | OrNode | NotNode | VarNode:
    """
    Parse a token list into an AST.

    Args:
        tokens: Output of tokenize(). Must end with an EOF token.

    Returns:
        The root node of the AST.

    Raises:
        FormulaError: On any syntactic error.
    """
    return _Parser(tokens).parse()
