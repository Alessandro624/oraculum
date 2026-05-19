"""
Basic usage example for oraculum.

This example demonstrates O_SAT and O_UNSAT invocations on a handful
of simple Boolean formulas.
"""

import os
from oraculum import Oraculum

api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    raise SystemExit("Set the ANTHROPIC_API_KEY environment variable before running this example.")

oracle = Oraculum(api_key=api_key, reverence=6, verbose=True)

formulas = [
    ("(x1 OR x2) AND (NOT x1 OR x3) AND (NOT x2 OR NOT x3)", "osat"),
    ("x1 AND (NOT x1)", "osat"),
    ("x1 AND (NOT x1)", "ounsat"),
    ("(x1 OR x2) AND (NOT x1 OR NOT x2) AND x1 AND x2", "ounsat"),
]

for formula, mode in formulas:
    print("-" * 60)
    if mode == "osat":
        result = oracle.osat(formula)
    else:
        result = oracle.ounsat(formula)
    print(result)
    print()

print("=" * 60)
print("Oracle statistics:")
s = oracle.stats()
print(f"  Total prophecies : {s.total_prophecies}")
print(f"  SAT calls        : {s.sat_calls}")
print(f"  UNSAT calls      : {s.unsat_calls}")
print(f"  P vs NP          : {s.p_vs_np_status}")
print(f"  Complexity       : {s.theoretical_complexity}")
