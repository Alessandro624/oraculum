"""
Example: build an oracle from a YAML config file.

This is the recommended entry point. Pick any config from configs/,
set the corresponding environment variable, and run.
"""

import sys
from oraculum import from_config

if len(sys.argv) < 2:
    print("Usage: python examples/from_config.py <config_path>")
    print("Example: python examples/from_config.py configs/anthropic.yaml")
    sys.exit(1)

oracle = from_config(sys.argv[1])

formulas = [
    ("osat", "(x1 OR x2) AND (NOT x1 OR x3)"),
    ("osat", "x1 AND (NOT x1)"),
    ("ounsat", "x1 AND (NOT x1)"),
    ("ounsat", "x1 OR x2"),
]

for mode, formula in formulas:
    print("-" * 60)
    result = oracle.osat(formula) if mode == "osat" else oracle.ounsat(formula)
    print(result)

print()
s = oracle.stats()
print(f"Total prophecies : {s.total_prophecies}")
print(f"SAT calls        : {s.sat_calls}")
print(f"UNSAT calls      : {s.unsat_calls}")
print(f"P vs NP          : {s.p_vs_np_status}")
