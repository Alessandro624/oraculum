"""
Token types and the Token dataclass.
"""

from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    AND = auto()
    OR = auto()
    NOT = auto()
    LPAREN = auto()
    RPAREN = auto()
    VAR = auto()
    EOF = auto()


@dataclass(frozen=True)
class Token:
    """
    A single lexical token.

    Attributes:
        type:     The category of this token.
        value:    The literal string from the source (e.g. "AND", "x1", "(").
        position: Zero-based character offset in the original source string.
                  Used to produce precise error messages.
    """

    type: TokenType
    value: str
    position: int

    def __str__(self) -> str:
        return f"{self.type.name}({self.value!r}) at position {self.position}"
