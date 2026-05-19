"""
Provider registry.

Adding a new provider means:
  1. Create oraculum/providers/myprovider.py implementing LLMProvider.
  2. Register it in _REGISTRY below.
  That is all.
"""

from .protocol import LLMProvider
from .anthropic import AnthropicProvider
from .openai import OpenAIProvider
from .ollama import OllamaProvider
from .openrouter import OpenRouterProvider
from ..config.schema import ProviderConfig
from ..exceptions import UnknownProviderError

_REGISTRY: dict[str, type[LLMProvider]] = {
    "anthropic": AnthropicProvider,
    "openai": OpenAIProvider,
    "ollama": OllamaProvider,
    "openrouter": OpenRouterProvider,
}


def build_provider(cfg: ProviderConfig) -> LLMProvider:
    """
    Instantiate the correct provider from a ProviderConfig.

    Args:
        cfg: A ProviderConfig produced by the config loader.

    Returns:
        An LLMProvider ready to call.

    Raises:
        UnknownProviderError: If cfg.provider is not registered.
    """
    cls = _REGISTRY.get(cfg.provider)
    if cls is None:
        known = ", ".join(sorted(_REGISTRY))
        raise UnknownProviderError(f"Unknown provider '{cfg.provider}'. Known providers: {known}.")
    return cls(cfg)


__all__ = ["LLMProvider", "build_provider"]
