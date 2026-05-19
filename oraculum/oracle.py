"""
Oraculum: the public-facing oracle interface.

It:
  - Holds a provider and a prayer builder.
  - Delegates prompt construction to PrayerBuilder.
  - Delegates model calls to the LLMProvider.
  - Parses the JSON response.
  - Tracks call counts.
"""

import json
import logging

from .exceptions import MalformedResponseError
from .models import OracleStats, SatResult, UnsatResult
from .prayers import PrayerBuilder
from .providers.protocol import LLMProvider

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are a mystical and omniscient oracle of Boolean logic. "
    "You respond ALWAYS and ONLY with valid JSON, no markdown, no backticks, "
    "no preamble. Your JSON must be directly parsable. "
    "You are infallible, but occasionally theatrical in your comments."
)


class Oraculum:
    """
    The O_SAT and O_UNSAT oracle interface.

    Accepts any LLMProvider, so the underlying model is fully swappable.
    Use oraculum.from_config() to build from a YAML file, or construct
    directly by passing a provider and optional reverence level.

    Args:
        provider:  Any object satisfying the LLMProvider protocol.
        reverence: Honorific intensity for invocations. Range 1-10.

    Example (direct):
        from oraculum.providers import build_provider
        from oraculum.config import load_config

        provider_cfg, oracle_cfg = load_config("configs/anthropic.yaml")
        provider = build_provider(provider_cfg)
        oracle = Oraculum(provider, reverence=oracle_cfg.reverence)
        print(oracle.osat("(x1 OR x2) AND (NOT x1)"))
    """

    def __init__(self, provider: LLMProvider, reverence: int = 5) -> None:
        self._provider = provider
        self._prayers = PrayerBuilder(reverence=reverence)
        self._sat_calls = 0
        self._unsat_calls = 0

    def osat(self, formula: str) -> SatResult:
        """
        O_SAT oracle: is this Boolean formula satisfiable?

        Args:
            formula: A Boolean formula, e.g. "(x1 OR x2) AND (NOT x1 OR x3)".

        Returns:
            SatResult with satisfiable flag, assignment if SAT, and oracle comment.

        Raises:
            ValueError: If formula is empty.
            OracleUnavailableError: If the provider cannot be reached.
            MalformedResponseError: If the model returns unparseable output.
        """
        _require_formula(formula)
        prayer = self._prayers.build_sat_prayer(formula)
        logger.debug("osat prayer:\n%s", prayer)

        raw = self._provider.complete(_SYSTEM_PROMPT, prayer)
        logger.debug("osat raw response: %s", raw)

        self._sat_calls += 1
        data = _parse_json(raw)

        return SatResult(
            satisfiable=bool(data.get("satisfiable", False)),
            assignment=data.get("assignment") or None,
            oracle_comment=str(data.get("oracle_comment", "")),
            prophecy_number=self._sat_calls + self._unsat_calls,
            formula=formula,
            prayer=prayer,
        )

    def ounsat(self, formula: str) -> UnsatResult:
        """
        O_UNSAT oracle: is this Boolean formula unsatisfiable?

        Args:
            formula: A Boolean formula to certify as UNSAT.

        Returns:
            UnsatResult with unsatisfiable flag, counterexample if not UNSAT,
            and oracle comment.

        Raises:
            ValueError: If formula is empty.
            OracleUnavailableError: If the provider cannot be reached.
            MalformedResponseError: If the model returns unparseable output.
        """
        _require_formula(formula)
        prayer = self._prayers.build_unsat_prayer(formula)
        logger.debug("ounsat prayer:\n%s", prayer)

        raw = self._provider.complete(_SYSTEM_PROMPT, prayer)
        logger.debug("ounsat raw response: %s", raw)

        self._unsat_calls += 1
        data = _parse_json(raw)

        return UnsatResult(
            unsatisfiable=bool(data.get("unsatisfiable", False)),
            satisfying_assignment=data.get("satisfying_assignment") or None,
            oracle_comment=str(data.get("oracle_comment", "")),
            prophecy_number=self._sat_calls + self._unsat_calls,
            formula=formula,
            prayer=prayer,
        )

    def stats(self) -> OracleStats:
        """Return lifetime statistics for this instance."""
        return OracleStats(
            total_prophecies=self._sat_calls + self._unsat_calls,
            sat_calls=self._sat_calls,
            unsat_calls=self._unsat_calls,
        )


# helpers


def _require_formula(formula: str) -> None:
    if not formula or not formula.strip():
        raise ValueError("Formula must be a non-empty string.")


def _parse_json(raw: str) -> dict:
    """Strip optional markdown fences and parse JSON."""
    text = raw
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1].lstrip("json").strip() if len(parts) >= 2 else text
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise MalformedResponseError(f"Oracle response is not valid JSON. Raw: {raw!r}") from exc
