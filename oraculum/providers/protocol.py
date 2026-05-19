"""
LLMProvider protocol.

Every provider must satisfy this interface. Nothing more is required.
The protocol uses structural subtyping (typing.Protocol) so providers
do not need to inherit from a base class.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class LLMProvider(Protocol):
    """
    A callable that sends a prompt to a language model and returns text.

    Implementors receive a ProviderConfig at construction and expose
    a single method: complete().
    """

    def complete(self, system: str, user: str) -> str:
        """
        Send a system prompt and a user message; return the model's text reply.

        Args:
            system: The system-level instruction (oracle persona).
            user:   The user message (the prayer).

        Returns:
            The raw text response from the model.

        Raises:
            OracleUnavailableError: On any connectivity or auth failure.
        """
        ...
