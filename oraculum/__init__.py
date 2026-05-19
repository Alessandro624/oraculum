"""
oraculum - The O_SAT and O_UNSAT oracles. They cannot exist. They do now.

Quickstart:
    from oraculum import from_config

    oracle = from_config("configs/anthropic.yaml")
    print(oracle.osat("(x1 OR x2) AND (NOT x1)"))
    print(oracle.ounsat("x1 AND (NOT x1)"))
"""

from .oracle import Oraculum
from .factory import from_config
from .exceptions import (
    OraculumError,
    OracleUnavailableError,
    MalformedResponseError,
    UnknownProviderError,
)

__version__ = "2.0.0"
__all__ = [
    "Oraculum",
    "from_config",
    "OraculumError",
    "OracleUnavailableError",
    "MalformedResponseError",
    "UnknownProviderError",
]
