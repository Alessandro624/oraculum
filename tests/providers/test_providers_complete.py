"""
Tests for provider complete() error handling.
Uses unittest.mock to simulate API exceptions without network calls.
"""

from unittest.mock import MagicMock, patch
import pytest  # type: ignore
import httpx  # type: ignore

from oraculum.config.schema import ProviderConfig
from oraculum.exceptions import OracleUnavailableError

# Shared stubs for SDK exception construction

_REQUEST = httpx.Request("GET", "https://example.com")
_RESPONSE = httpx.Response(401, request=_REQUEST)


def _anthropic_exc(cls, message="error"):
    import anthropic

    if cls is anthropic.APIConnectionError:
        return cls(message=message, request=_REQUEST)
    if cls is anthropic.APIError:
        return cls(message, _REQUEST, body=None)
    return cls(message, response=_RESPONSE, body=None)


def _openai_exc(cls, message="error"):
    import openai

    if cls is openai.APIConnectionError:
        return cls(request=_REQUEST)
    if cls is openai.APIError:
        return cls(message, _REQUEST, body=None)
    return cls(message, response=_RESPONSE, body=None)


# Provider factories (no real credentials needed for complete() tests)


def _anthropic():
    from oraculum.providers.anthropic import AnthropicProvider

    return AnthropicProvider(ProviderConfig(provider="anthropic", model="m", api_key="sk-fake"))


def _openai():
    from oraculum.providers.openai import OpenAIProvider

    return OpenAIProvider(ProviderConfig(provider="openai", model="m", api_key="sk-fake"))


def _ollama():
    from oraculum.providers.ollama import OllamaProvider

    return OllamaProvider(ProviderConfig(provider="ollama", model="m"))


def _openrouter():
    from oraculum.providers.openrouter import OpenRouterProvider

    return OpenRouterProvider(ProviderConfig(provider="openrouter", model="m", api_key="sk-fake"))


def _ok_response(text: str) -> MagicMock:
    """Build a mock Chat Completions response with a single choice."""
    choice = MagicMock()
    choice.message.content = text
    resp = MagicMock()
    resp.choices = [choice]
    return resp


# Anthropic


class TestAnthropicComplete:
    def test_success(self):
        p = _anthropic()
        mock_resp = MagicMock()
        mock_resp.content = [MagicMock(text="  hello  ")]
        with patch.object(p._client.messages, "create", return_value=mock_resp):
            assert p.complete("sys", "user") == "hello"

    def test_authentication_error(self):
        import anthropic

        p = _anthropic()
        with patch.object(p._client.messages, "create", side_effect=_anthropic_exc(anthropic.AuthenticationError)):
            with pytest.raises(OracleUnavailableError, match="authentication"):
                p.complete("sys", "user")

    def test_connection_error(self):
        import anthropic

        p = _anthropic()
        with patch.object(p._client.messages, "create", side_effect=_anthropic_exc(anthropic.APIConnectionError)):
            with pytest.raises(OracleUnavailableError, match="reach"):
                p.complete("sys", "user")

    def test_api_error(self):
        import anthropic

        p = _anthropic()
        with patch.object(p._client.messages, "create", side_effect=_anthropic_exc(anthropic.APIError)):
            with pytest.raises(OracleUnavailableError, match="API error"):
                p.complete("sys", "user")


# OpenAI


class TestOpenAIComplete:
    def test_success(self):
        p = _openai()
        with patch.object(p._client.chat.completions, "create", return_value=_ok_response("  result  ")):
            assert p.complete("sys", "user") == "result"

    def test_base_url_passed_to_client(self):
        from oraculum.providers.openai import OpenAIProvider

        cfg = ProviderConfig(provider="openai", model="m", api_key="sk-fake", base_url="https://custom.endpoint/v1")
        p = OpenAIProvider(cfg)
        assert "custom.endpoint" in str(p._client.base_url)

    def test_none_content_returns_empty(self):
        p = _openai()
        choice = MagicMock()
        choice.message.content = None
        mock_resp = MagicMock()
        mock_resp.choices = [choice]
        with patch.object(p._client.chat.completions, "create", return_value=mock_resp):
            assert p.complete("sys", "user") == ""

    def test_authentication_error(self):
        import openai

        p = _openai()
        with patch.object(p._client.chat.completions, "create", side_effect=_openai_exc(openai.AuthenticationError)):
            with pytest.raises(OracleUnavailableError, match="authentication"):
                p.complete("sys", "user")

    def test_connection_error(self):
        import openai

        p = _openai()
        with patch.object(p._client.chat.completions, "create", side_effect=_openai_exc(openai.APIConnectionError)):
            with pytest.raises(OracleUnavailableError, match="reach"):
                p.complete("sys", "user")

    def test_api_error(self):
        import openai

        p = _openai()
        with patch.object(p._client.chat.completions, "create", side_effect=_openai_exc(openai.APIError)):
            with pytest.raises(OracleUnavailableError, match="API error"):
                p.complete("sys", "user")


# Ollama


class TestOllamaComplete:
    def test_success(self):
        p = _ollama()
        with patch.object(p._client.chat.completions, "create", return_value=_ok_response("  ok  ")):
            assert p.complete("sys", "user") == "ok"

    def test_connection_error(self):
        import openai

        p = _ollama()
        with patch.object(p._client.chat.completions, "create", side_effect=_openai_exc(openai.APIConnectionError)):
            with pytest.raises(OracleUnavailableError, match="Ollama"):
                p.complete("sys", "user")

    def test_api_error(self):
        import openai

        p = _ollama()
        with patch.object(p._client.chat.completions, "create", side_effect=_openai_exc(openai.APIError)):
            with pytest.raises(OracleUnavailableError, match="Ollama error"):
                p.complete("sys", "user")


# OpenRouter


class TestOpenRouterComplete:
    def test_success(self):
        p = _openrouter()
        with patch.object(p._client.chat.completions, "create", return_value=_ok_response("  done  ")):
            assert p.complete("sys", "user") == "done"

    def test_authentication_error(self):
        import openai

        p = _openrouter()
        with patch.object(p._client.chat.completions, "create", side_effect=_openai_exc(openai.AuthenticationError)):
            with pytest.raises(OracleUnavailableError, match="authentication"):
                p.complete("sys", "user")

    def test_connection_error(self):
        import openai

        p = _openrouter()
        with patch.object(p._client.chat.completions, "create", side_effect=_openai_exc(openai.APIConnectionError)):
            with pytest.raises(OracleUnavailableError, match="reach"):
                p.complete("sys", "user")

    def test_api_error(self):
        import openai

        p = _openrouter()
        with patch.object(p._client.chat.completions, "create", side_effect=_openai_exc(openai.APIError)):
            with pytest.raises(OracleUnavailableError, match="API error"):
                p.complete("sys", "user")
