"""
YAML configuration loader.
"""

import os
import re
from pathlib import Path

import yaml

from .schema import OracleConfig, ProviderConfig

_ENV_PATTERN = re.compile(r"\$\{([^}]+)\}")


def load_config(path: str | Path) -> tuple[ProviderConfig, OracleConfig]:
    """
    Load and parse a YAML config file.

    Environment variables referenced as ${VAR_NAME} in string values
    are expanded at load time. If a referenced variable is not set, the
    placeholder is left as-is so the error surfaces clearly later.

    Args:
        path: Path to a YAML config file.

    Returns:
        A (ProviderConfig, OracleConfig) tuple.

    Raises:
        FileNotFoundError: If the path does not exist.
        KeyError: If required fields are missing.
        yaml.YAMLError: If the file is not valid YAML.

    Example:
        provider_cfg, oracle_cfg = load_config("configs/anthropic.yaml")
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with path.open() as fh:
        raw = yaml.safe_load(fh)

    raw = _expand_env_vars(raw)

    provider_cfg = ProviderConfig(
        provider=raw["provider"],
        model=raw["model"],
        api_key=raw.get("api_key"),
        base_url=raw.get("base_url"),
        max_tokens=raw.get("oracle", {}).get("max_tokens", 512),
    )

    oracle_section = raw.get("oracle", {})
    oracle_cfg = OracleConfig(
        reverence=oracle_section.get("reverence", 5),
    )

    return provider_cfg, oracle_cfg


def _expand_env_vars(obj: object) -> object:
    """Recursively expand ${VAR} placeholders in all string values."""
    if isinstance(obj, str):
        return _ENV_PATTERN.sub(lambda m: os.environ.get(m.group(1), m.group(0)), obj)
    if isinstance(obj, dict):
        return {k: _expand_env_vars(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_expand_env_vars(item) for item in obj]
    return obj
