"""
Provider registry.

Adding a new provider means:
  1. Create oraculum/providers/myprovider.py implementing LLMProvider.
  2. Register it in _REGISTRY below.
  That is all.
"""

import importlib

from .protocol import LLMProvider
from ..config.schema import ProviderConfig
from ..exceptions import UnknownProviderError, OracleUnavailableError

_REGISTRY: dict[str, tuple[str, str]] = {
    "anthropic": ("anthropic", "AnthropicProvider"),
    "openai": ("openai", "OpenAIProvider"),
    "ollama": ("ollama", "OllamaProvider"),
    "openrouter": ("openrouter", "OpenRouterProvider"),
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
        OracleUnavailableError: If the provider's required dependencies are not installed.
    """
    if cfg.provider not in _REGISTRY:
        known = ", ".join(sorted(_REGISTRY))
        raise UnknownProviderError(f"Unknown provider '{cfg.provider}'. Known providers: {known}.")

    module_name, class_name = _REGISTRY[cfg.provider]
    try:
        module = importlib.import_module(f".{module_name}", package="oraculum.providers")
    except ImportError as e:
        raise OracleUnavailableError(f"Provider '{cfg.provider}' requires additional dependencies. " f"Please install them with: pip install oraculum[{cfg.provider}]") from e

    cls = getattr(module, class_name)
    return cls(cfg)


__all__ = ["LLMProvider", "build_provider"]
