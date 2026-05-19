"""
OpenAI provider.

Uses the official openai SDK, which follows the OpenAI Chat Completions API.
Install: pip install openai
"""

import openai

from ..config.schema import ProviderConfig
from ..exceptions import OracleUnavailableError


class OpenAIProvider:
    """LLMProvider implementation backed by the OpenAI Chat Completions API."""

    def __init__(self, cfg: ProviderConfig) -> None:
        if not cfg.api_key:
            raise OracleUnavailableError("OpenAI provider requires an api_key in the config.")
        kwargs = {"api_key": cfg.api_key}
        if cfg.base_url:
            kwargs["base_url"] = cfg.base_url
        self._client = openai.OpenAI(**kwargs)
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
            raise OracleUnavailableError("OpenAI authentication failed.") from exc
        except openai.APIConnectionError as exc:
            raise OracleUnavailableError("Cannot reach OpenAI API.") from exc
        except openai.APIError as exc:
            raise OracleUnavailableError(f"OpenAI API error: {exc}") from exc
