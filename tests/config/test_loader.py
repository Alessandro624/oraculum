"""
Tests for the YAML config loader.
"""

import textwrap
from pathlib import Path

import pytest  # type: ignore

from oraculum.config.loader import load_config, _expand_env_vars


@pytest.fixture
def tmp_yaml(tmp_path):
    """Write a YAML string to a temp file and return the path."""

    def _write(content: str) -> Path:
        p = tmp_path / "cfg.yaml"
        p.write_text(textwrap.dedent(content))
        return p

    return _write


class TestLoadConfig:
    def test_basic_anthropic(self, tmp_yaml):
        path = tmp_yaml("""
            provider: anthropic
            model: claude-opus-4-5
            api_key: sk-test-key
            oracle:
              reverence: 7
              max_tokens: 256
        """)
        provider_cfg, oracle_cfg = load_config(path)
        assert provider_cfg.provider == "anthropic"
        assert provider_cfg.model == "claude-opus-4-5"
        assert provider_cfg.api_key == "sk-test-key"
        assert provider_cfg.max_tokens == 256
        assert oracle_cfg.reverence == 7

    def test_ollama_no_api_key(self, tmp_yaml):
        path = tmp_yaml("""
            provider: ollama
            model: llama3.2
            base_url: http://localhost:11434
        """)
        provider_cfg, _ = load_config(path)
        assert provider_cfg.provider == "ollama"
        assert provider_cfg.api_key is None
        assert provider_cfg.base_url == "http://localhost:11434"

    def test_defaults_applied(self, tmp_yaml):
        path = tmp_yaml("""
            provider: openai
            model: gpt-4o
            api_key: sk-x
        """)
        provider_cfg, oracle_cfg = load_config(path)
        assert provider_cfg.max_tokens == 512
        assert oracle_cfg.reverence == 5

    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            load_config("/nonexistent/path/cfg.yaml")

    def test_env_var_expanded(self, tmp_yaml, monkeypatch):
        monkeypatch.setenv("TEST_API_KEY", "sk-from-env")
        path = tmp_yaml("""
            provider: anthropic
            model: claude-opus-4-5
            api_key: "${TEST_API_KEY}"
        """)
        provider_cfg, _ = load_config(path)
        assert provider_cfg.api_key == "sk-from-env"

    def test_missing_env_var_left_as_placeholder(self, tmp_yaml, monkeypatch):
        monkeypatch.delenv("MISSING_VAR", raising=False)
        path = tmp_yaml("""
            provider: anthropic
            model: claude-opus-4-5
            api_key: "${MISSING_VAR}"
        """)
        provider_cfg, _ = load_config(path)
        assert provider_cfg.api_key == "${MISSING_VAR}"


class TestExpandEnvVars:
    def test_string_expanded(self, monkeypatch):
        monkeypatch.setenv("FOO", "bar")
        assert _expand_env_vars("${FOO}") == "bar"

    def test_nested_dict_expanded(self, monkeypatch):
        monkeypatch.setenv("KEY", "value")
        result = _expand_env_vars({"a": "${KEY}", "b": {"c": "${KEY}"}})
        assert result == {"a": "value", "b": {"c": "value"}}

    def test_list_expanded(self, monkeypatch):
        monkeypatch.setenv("X", "hello")
        assert _expand_env_vars(["${X}", "${X}"]) == ["hello", "hello"]

    def test_non_string_untouched(self):
        assert _expand_env_vars(42) == 42
        assert _expand_env_vars(True) is True
        assert _expand_env_vars(None) is None
