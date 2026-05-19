"""
Configuration dataclasses.

These are plain data containers.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ProviderConfig:
    """
    Settings that identify and authenticate a provider.

    Attributes:
        provider:   Provider name. One of: anthropic, openai, ollama, openrouter.
        model:      Model identifier as understood by the chosen provider.
        api_key:    API key, if the provider requires one. Not needed for Ollama.
        base_url:   Override the provider base URL. Required for Ollama.
                    Optional for OpenAI-compatible endpoints.
        max_tokens: Maximum tokens to request from the model.
    """

    provider: str
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    max_tokens: int = 512


@dataclass(frozen=True)
class OracleConfig:
    """
    Settings that control oracle behaviour (not provider-specific).

    Attributes:
        reverence: Honorific intensity appended to invocations. Range 1-10.
    """

    reverence: int = 5
