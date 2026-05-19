"""
Result models.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class SatResult:
    """
    Result of an O_SAT invocation.

    Attributes:
        satisfiable:      Whether the formula is satisfiable.
        assignment:       A satisfying variable assignment, or None if UNSAT.
        oracle_comment:   A decorative remark from the oracle.
        prophecy_number:  Sequential call counter for this Oraculum instance.
        formula:          The original formula string.
        prayer:           The full invocation text. Exposed for logging and parties.
    """

    satisfiable: bool
    assignment: Optional[Dict[str, bool]]
    oracle_comment: str
    prophecy_number: int
    formula: str
    prayer: str = field(repr=False)

    def __str__(self) -> str:
        status = "SAT" if self.satisfiable else "UNSAT"
        lines = [f"[#{self.prophecy_number}] {status}  formula={self.formula!r}"]
        if self.assignment:
            pairs = ", ".join(f"{k}={v}" for k, v in self.assignment.items())
            lines.append(f"  assignment : {pairs}")
        lines.append(f'  oracle says: "{self.oracle_comment}"')
        return "\n".join(lines)


@dataclass
class UnsatResult:
    """
    Result of an O_UNSAT invocation.

    Attributes:
        unsatisfiable:          Whether the formula is certified UNSAT.
        satisfying_assignment:  A counterexample assignment if not UNSAT, else None.
        oracle_comment:         A decorative remark, usually melancholic.
        prophecy_number:        Sequential call counter for this Oraculum instance.
        formula:                The original formula string.
        prayer:                 The full invocation text.
    """

    unsatisfiable: bool
    satisfying_assignment: Optional[Dict[str, bool]]
    oracle_comment: str
    prophecy_number: int
    formula: str
    prayer: str = field(repr=False)

    def __str__(self) -> str:
        if self.unsatisfiable:
            status = "UNSAT certified"
        else:
            status = "NOT UNSAT (counterexample found)"
        lines = [f"[#{self.prophecy_number}] {status}  formula={self.formula!r}"]
        if self.satisfying_assignment:
            pairs = ", ".join(f"{k}={v}" for k, v in self.satisfying_assignment.items())
            lines.append(f"  counterexample: {pairs}")
        lines.append(f'  oracle says: "{self.oracle_comment}"')
        return "\n".join(lines)


@dataclass
class OracleStats:
    """
    Lifetime statistics for an Oraculum instance.

    The numbers are accurate. The editorial remarks are not.
    """

    total_prophecies: int
    sat_calls: int
    unsat_calls: int
    p_vs_np_status: str = "still open, but we are working on it"
    theoretical_complexity: str = "O(1) with oracle (obviously)"
    turing_award_eta: str = "not before 2087"
