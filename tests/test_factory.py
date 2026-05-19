"""
Tests for the factory function from_config.
"""

import pytest  # type: ignore
from oraculum.factory import from_config


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        from_config(tmp_path / "nonexistent.yaml")


def test_unknown_provider_raises(tmp_path):
    from oraculum.exceptions import UnknownProviderError

    cfg = tmp_path / "cfg.yaml"
    cfg.write_text("provider: ghost\nmodel: x\n")
    with pytest.raises(UnknownProviderError):
        from_config(cfg)


def test_missing_api_key_raises(tmp_path):
    from oraculum.exceptions import OracleUnavailableError

    cfg = tmp_path / "cfg.yaml"
    cfg.write_text("provider: anthropic\nmodel: claude-opus-4-5\n")
    with pytest.raises(OracleUnavailableError):
        from_config(cfg)


def test_valid_config(tmp_path):
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text("provider: ollama\nmodel: test\n")
    oracle = from_config(cfg)
    assert oracle is not None
    assert hasattr(oracle, "osat")
    assert hasattr(oracle, "ounsat")
