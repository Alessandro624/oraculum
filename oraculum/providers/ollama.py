"""
Ollama provider.

Ollama exposes a local OpenAI-compatible endpoint, so this provider
uses the openai SDK pointed at localhost. No API key is required.

Install: pip install openai
Run locally: https://ollama.com
"""

import openai

from ..config.schema import ProviderConfig
from ..exceptions import OracleUnavailableError

_DEFAULT_BASE_URL = "http://localhost:11434/v1"


class OllamaProvider:
    """LLMProvider implementation backed by a local Ollama instance."""

    def __init__(self, cfg: ProviderConfig) -> None:
        base_url = cfg.base_url or _DEFAULT_BASE_URL
        self._client = openai.OpenAI(api_key="ollama", base_url=base_url)
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
        except openai.APIConnectionError as exc:
            raise OracleUnavailableError(f"Cannot reach Ollama. Is it running at {self._client.base_url}?") from exc
        except openai.APIError as exc:
            raise OracleUnavailableError(f"Ollama error: {exc}") from exc
