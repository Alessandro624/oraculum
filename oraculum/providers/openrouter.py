"""
OpenRouter provider.

OpenRouter exposes an OpenAI-compatible API that routes requests to
hundreds of models from different vendors. Handy if you want the oracle
to channel a different deity depending on the day.

Install: pip install openai
Docs: https://openrouter.ai/docs
"""

import openai

from ..config.schema import ProviderConfig
from ..exceptions import OracleUnavailableError

_BASE_URL = "https://openrouter.ai/api/v1"


class OpenRouterProvider:
    """LLMProvider implementation backed by OpenRouter."""

    def __init__(self, cfg: ProviderConfig) -> None:
        if not cfg.api_key:
            raise OracleUnavailableError("OpenRouter provider requires an api_key in the config.")
        self._client = openai.OpenAI(
            api_key=cfg.api_key,
            base_url=cfg.base_url or _BASE_URL,
        )
        self._model = cfg.model
        self._max_tokens = cfg.max_tokens

    def complete(self, system: str, user: str) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                max_tokens=self._max_tokens,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
            return (response.choices[0].message.content or "").strip()
        except openai.AuthenticationError as exc:
            raise OracleUnavailableError("OpenRouter authentication failed.") from exc
        except openai.APIConnectionError as exc:
            raise OracleUnavailableError("Cannot reach OpenRouter API.") from exc
        except openai.APIError as exc:
            raise OracleUnavailableError(f"OpenRouter API error: {exc}") from exc
