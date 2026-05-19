"""
Anthropic provider.

Uses the official anthropic SDK.
Install: pip install anthropic
"""

import anthropic

from ..config.schema import ProviderConfig
from ..exceptions import OracleUnavailableError


class AnthropicProvider:
    """LLMProvider implementation backed by the Anthropic Messages API."""

    def __init__(self, cfg: ProviderConfig) -> None:
        if not cfg.api_key:
            raise OracleUnavailableError("Anthropic provider requires an api_key in the config.")
        self._client = anthropic.Anthropic(api_key=cfg.api_key)
        self._model = cfg.model
        self._max_tokens = cfg.max_tokens

    def complete(self, system: str, user: str) -> str:
        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=self._max_tokens,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            return response.content[0].text.strip()
        except anthropic.AuthenticationError as exc:
            raise OracleUnavailableError("Anthropic authentication failed.") from exc
        except anthropic.APIConnectionError as exc:
            raise OracleUnavailableError("Cannot reach Anthropic API.") from exc
        except anthropic.APIError as exc:
            raise OracleUnavailableError(f"Anthropic API error: {exc}") from exc
