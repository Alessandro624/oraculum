"""
Tests for provider complete() error handling.
Uses unittest.mock to simulate API exceptions without network calls.
"""

from unittest.mock import MagicMock, patch
import pytest  # type: ignore
from oraculum.config.schema import ProviderConfig
from oraculum.exceptions import OracleUnavailableError


def _anthropic():
    from oraculum.providers.anthropic import AnthropicProvider

    cfg = ProviderConfig(provider="anthropic", model="m", api_key="sk-fake")
    return AnthropicProvider(cfg)


def _openai():
    from oraculum.providers.openai import OpenAIProvider

    cfg = ProviderConfig(provider="openai", model="m", api_key="sk-fake")
    return OpenAIProvider(cfg)


def _ollama():
    from oraculum.providers.ollama import OllamaProvider

    cfg = ProviderConfig(provider="ollama", model="m")
    return OllamaProvider(cfg)


def _openrouter():
    from oraculum.providers.openrouter import OpenRouterProvider

    cfg = ProviderConfig(provider="openrouter", model="m", api_key="sk-fake")
    return OpenRouterProvider(cfg)


class TestAnthropicComplete:
    def test_auth_error_raises(self):
        import anthropic

        p = _anthropic()
        with patch.object(p._client.messages, "create", side_effect=anthropic.AuthenticationError.__new__(anthropic.AuthenticationError)):
            with pytest.raises(OracleUnavailableError, match="authentication"):
                p.complete("sys", "user")

    def test_connection_error_raises(self):
        import anthropic

        p = _anthropic()
        with patch.object(p._client.messages, "create", side_effect=anthropic.APIConnectionError.__new__(anthropic.APIConnectionError)):
            with pytest.raises(OracleUnavailableError, match="reach"):
                p.complete("sys", "user")

    def test_api_error_raises(self):
        import anthropic

        p = _anthropic()
        with patch.object(p._client.messages, "create", side_effect=anthropic.APIError.__new__(anthropic.APIError)):
            with pytest.raises(OracleUnavailableError):
                p.complete("sys", "user")

    def test_success_returns_text(self):
        p = _anthropic()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="  hello  ")]
        with patch.object(p._client.messages, "create", return_value=mock_response):
            assert p.complete("sys", "user") == "hello"


class TestOpenAIComplete:
    def test_auth_error_raises(self):
        import openai

        p = _openai()
        with patch.object(p._client.chat.completions, "create", side_effect=openai.AuthenticationError.__new__(openai.AuthenticationError)):
            with pytest.raises(OracleUnavailableError, match="authentication"):
                p.complete("sys", "user")

    def test_connection_error_raises(self):
        import openai

        p = _openai()
        with patch.object(p._client.chat.completions, "create", side_effect=openai.APIConnectionError.__new__(openai.APIConnectionError)):
            with pytest.raises(OracleUnavailableError, match="reach"):
                p.complete("sys", "user")

    def test_api_error_raises(self):
        import openai

        p = _openai()
        with patch.object(p._client.chat.completions, "create", side_effect=openai.APIError.__new__(openai.APIError)):
            with pytest.raises(OracleUnavailableError):
                p.complete("sys", "user")

    def test_success_returns_text(self):
        p = _openai()
        mock_choice = MagicMock()
        mock_choice.message.content = "  result  "
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        with patch.object(p._client.chat.completions, "create", return_value=mock_response):
            assert p.complete("sys", "user") == "result"


class TestOllamaComplete:
    def test_connection_error_raises(self):
        import openai

        p = _ollama()
        with patch.object(p._client.chat.completions, "create", side_effect=openai.APIConnectionError.__new__(openai.APIConnectionError)):
            with pytest.raises(OracleUnavailableError, match="Ollama"):
                p.complete("sys", "user")

    def test_api_error_raises(self):
        import openai

        p = _ollama()
        with patch.object(p._client.chat.completions, "create", side_effect=openai.APIError.__new__(openai.APIError)):
            with pytest.raises(OracleUnavailableError):
                p.complete("sys", "user")

    def test_success_returns_text(self):
        p = _ollama()
        mock_choice = MagicMock()
        mock_choice.message.content = "  ok  "
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        with patch.object(p._client.chat.completions, "create", return_value=mock_response):
            assert p.complete("sys", "user") == "ok"


class TestOpenRouterComplete:
    def test_auth_error_raises(self):
        import openai

        p = _openrouter()
        with patch.object(p._client.chat.completions, "create", side_effect=openai.AuthenticationError.__new__(openai.AuthenticationError)):
            with pytest.raises(OracleUnavailableError, match="authentication"):
                p.complete("sys", "user")

    def test_connection_error_raises(self):
        import openai

        p = _openrouter()
        with patch.object(p._client.chat.completions, "create", side_effect=openai.APIConnectionError.__new__(openai.APIConnectionError)):
            with pytest.raises(OracleUnavailableError, match="reach"):
                p.complete("sys", "user")

    def test_api_error_raises(self):
        import openai

        p = _openrouter()
        with patch.object(p._client.chat.completions, "create", side_effect=openai.APIError.__new__(openai.APIError)):
            with pytest.raises(OracleUnavailableError):
                p.complete("sys", "user")

    def test_success_returns_text(self):
        p = _openrouter()
        mock_choice = MagicMock()
        mock_choice.message.content = "  done  "
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        with patch.object(p._client.chat.completions, "create", return_value=mock_response):
            assert p.complete("sys", "user") == "done"
