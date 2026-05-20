"""
Tokenizer: source string -> list[Token].

Single linear scan, O(n). Knows nothing about grammar or AST.
Raises FormulaError with exact character position on unrecognized input.
"""

from ..exceptions import FormulaError
from .tokens import Token, TokenType

_KEYWORDS: dict[str, TokenType] = {
    "AND": TokenType.AND,
    "OR": TokenType.OR,
    "NOT": TokenType.NOT,
}


def tokenize(source: str) -> list[Token]:
    """
    Scan source and return a flat list of tokens ending with EOF.

    Args:
        source: A raw formula string, e.g. "(x1 OR x2) AND (NOT x1)".

    Returns:
        List of Token objects. The last token is always EOF.

    Raises:
        FormulaError: On any unrecognized character.
    """
    tokens: list[Token] = []
    i = 0
    n = len(source)

    while i < n:
        ch = source[i]

        if ch.isspace():
            i += 1
            continue

        if ch == "(":
            tokens.append(Token(TokenType.LPAREN, ch, i))
            i += 1
            continue

        if ch == ")":
            tokens.append(Token(TokenType.RPAREN, ch, i))
            i += 1
            continue

        if ch.isalpha() or ch == "_":
            start = i
            while i < n and (source[i].isalnum() or source[i] == "_"):
                i += 1
            word = source[start:i]
            ttype = _KEYWORDS.get(word.upper())
            if ttype is not None:
                tokens.append(Token(ttype, word.upper(), start))
            else:
                tokens.append(Token(TokenType.VAR, word, start))
            continue

        raise FormulaError(f"Unrecognized character {ch!r} at position {i}.")

    tokens.append(Token(TokenType.EOF, "", n))
    return tokens
