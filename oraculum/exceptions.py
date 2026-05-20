"""
Custom exceptions for oraculum.

These exceptions are thrown when the oracle is displeased,
confused, offline or simply unwilling to violate the
Church-Turing thesis today.
"""


class OraculumError(Exception):
    """
    Base exception for all Oraculum errors.

    If you are catching this, something went wrong with
    your invocation of the oracle.
    Consider increasing the reverance level and trying again.
    """


class OracleUnavailableError(OraculumError):
    """
    Raised when the oracle CANNOT be reached.

    Possible causes:
    - Invalid API key
    - Network issues
    - The oracle is mediating and CANNOT be disturbed
    - The oracle has achieved enlightenment and no longer responds to SAT queries
    """


class MalformedResponseError(OraculumError):
    """
    Raised when the oracle responds in a form that cannot be parsed.

    This happens when the oracle, despite being instructed to
    return a valid JSON object, decides to express itself in free verse
    or ancient Sumerian cuneiform.
    The oracle's communication style is notoriously unpredictable, and
    it may choose to convey its wisdom in a manner that defies
    conventional parsing techniques.
    """


class UnknownProviderError(OraculumError):
    """
    The provider specified in the configuration is not recognized.

    Check your configuration file for typos or unsupported providers.
    """


class FormulaError(OraculumError):
    """
    The formula string is lexically or syntactically malformed.

    Raised by Formula.parse() with a message that includes the exact
    position and the unexpected token or character, so the caller can
    provide precise feedback without inspecting the exception type.
    """
