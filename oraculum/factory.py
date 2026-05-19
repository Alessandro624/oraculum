"""
Convenience factory: build an Oraculum from a YAML config file.
"""

from pathlib import Path

from .config import load_config
from .oracle import Oraculum
from .providers import build_provider


def from_config(path: str | Path) -> Oraculum:
    """
    Build an Oraculum instance from a YAML config file.

    This is the recommended entry point for most users.

    Args:
        path: Path to a YAML config file. See configs/ for examples.

    Returns:
        A ready-to-use Oraculum instance.

    Raises:
        FileNotFoundError: If the config file does not exist.
        UnknownProviderError: If the provider name is not registered.
        OracleUnavailableError: If provider credentials are missing or invalid.

    Example:
        from oraculum import from_config

        oracle = from_config("configs/anthropic.yaml")
        result = oracle.osat("(x1 OR x2) AND (NOT x1)")
        print(result)
    """
    provider_cfg, oracle_cfg = load_config(path)
    provider = build_provider(provider_cfg)
    return Oraculum(provider, reverence=oracle_cfg.reverence)
