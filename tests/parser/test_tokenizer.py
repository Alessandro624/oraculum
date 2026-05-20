"""
Tests for the tokenizer: source string -> list[Token].
"""

import pytest  # type: ignore
from oraculum.parser.tokenizer import tokenize
from oraculum.parser.tokens import TokenType, Token
from oraculum.exceptions import FormulaError


def types(source: str) -> list[TokenType]:
    return [t.type for t in tokenize(source)]


def values(source: str) -> list[str]:
    return [t.value for t in tokenize(source) if t.type != TokenType.EOF]


class TestKeywords:
    def test_and(self):
        assert TokenType.AND in types("AND")

    def test_or(self):
        assert TokenType.OR in types("OR")

    def test_not(self):
        assert TokenType.NOT in types("NOT")

    def test_keywords_case_insensitive(self):
        assert types("and") == types("AND")
        assert types("or") == types("OR")
        assert types("not") == types("NOT")

    def test_keywords_normalized_to_uppercase(self):
        assert values("and or not") == ["AND", "OR", "NOT"]


class TestVariables:
    def test_single_letter(self):
        assert values("x") == ["x"]

    def test_alphanumeric(self):
        assert values("x1") == ["x1"]

    def test_underscore_allowed(self):
        assert values("my_var") == ["my_var"]

    def test_multiple_variables(self):
        assert values("x1 x2 x3") == ["x1", "x2", "x3"]

    def test_variable_not_confused_with_keyword_prefix(self):
        assert values("ANDY") == ["ANDY"]
        assert values("ORwell") == ["ORwell"]


class TestPunctuation:
    def test_lparen(self):
        assert TokenType.LPAREN in types("(")

    def test_rparen(self):
        assert TokenType.RPAREN in types(")")

    def test_parentheses_no_spaces(self):
        toks = tokenize("(x1)")
        assert toks[0].type == TokenType.LPAREN
        assert toks[1].type == TokenType.VAR
        assert toks[2].type == TokenType.RPAREN


class TestPositions:
    def test_position_of_first_token(self):
        toks = tokenize("x1 AND x2")
        assert toks[0].position == 0

    def test_position_of_and(self):
        toks = tokenize("x1 AND x2")
        assert toks[1].position == 3

    def test_position_of_second_var(self):
        toks = tokenize("x1 AND x2")
        assert toks[2].position == 7


class TestEof:
    def test_always_ends_with_eof(self):
        assert types("x1")[-1] == TokenType.EOF

    def test_empty_string_is_just_eof(self):
        assert types("   ") == [TokenType.EOF]


class TestErrors:
    def test_unknown_character_raises(self):
        with pytest.raises(FormulaError, match="position"):
            tokenize("x1 & x2")

    def test_error_includes_character(self):
        with pytest.raises(FormulaError, match="&"):
            tokenize("x1 & x2")

    def test_hash_raises(self):
        with pytest.raises(FormulaError):
            tokenize("x1 # x2")


class TestTokenStr:
    def test_str_contains_value(self):
        t = Token(TokenType.VAR, "x1", 3)
        assert "x1" in str(t)

    def test_str_contains_position(self):
        t = Token(TokenType.VAR, "x1", 3)
        assert "3" in str(t)

    def test_str_contains_type_name(self):
        t = Token(TokenType.AND, "AND", 0)
        assert "AND" in str(t)
