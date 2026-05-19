"""
Tests for the provider registry and factory.
"""

from unittest.mock import patch
import pytest  # type: ignore

from oraculum.config.schema import ProviderConfig
from oraculum.exceptions import UnknownProviderError
from oraculum.providers import build_provider, LLMProvider


def _cfg(provider: str, **kwargs) -> ProviderConfig:
    return ProviderConfig(provider=provider, model="test-model", **kwargs)


class TestBuildProvider:
    def test_unknown_provider_raises(self):
        with pytest.raises(UnknownProviderError, match="unknown_provider"):
            build_provider(_cfg("unknown_provider", api_key="x"))

    def test_error_message_lists_known_providers(self):
        with pytest.raises(UnknownProviderError, match="anthropic"):
            build_provider(_cfg("typo_provider", api_key="x"))

    def test_anthropic_missing_key_raises(self):
        from oraculum.exceptions import OracleUnavailableError

        with pytest.raises(OracleUnavailableError):
            build_provider(_cfg("anthropic"))

    def test_openai_missing_key_raises(self):
        from oraculum.exceptions import OracleUnavailableError

        with pytest.raises(OracleUnavailableError):
            build_provider(_cfg("openai"))

    def test_openrouter_missing_key_raises(self):
        from oraculum.exceptions import OracleUnavailableError

        with pytest.raises(OracleUnavailableError):
            build_provider(_cfg("openrouter"))

    def test_ollama_builds_without_key(self):
        # Ollama does not require an API key; construction should succeed
        provider = build_provider(_cfg("ollama"))
        assert isinstance(provider, LLMProvider)

    def test_returned_object_satisfies_protocol(self):
        provider = build_provider(_cfg("ollama"))
        assert isinstance(provider, LLMProvider)

    @patch("oraculum.providers.importlib.import_module")
    def test_import_error_raises_oracle_unavailable(self, mock_import):
        from oraculum.exceptions import OracleUnavailableError

        mock_import.side_effect = ImportError("No module named 'ollama'")
        with pytest.raises(OracleUnavailableError, match="ollama"):
            build_provider(_cfg("ollama", api_key="x"))
