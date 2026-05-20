"""
Example: build an oracle from a YAML config file.

    ANTHROPIC_API_KEY=sk-ant-... python examples/from_config.py configs/anthropic.yaml
    OPENAI_API_KEY=sk-...       python examples/from_config.py configs/openai.yaml
    python examples/from_config.py configs/ollama.yaml
"""

import sys
from oraculum import Formula, from_config

if len(sys.argv) < 2:
    print("Usage: python examples/from_config.py <config_path>")
    sys.exit(1)

oracle = from_config(sys.argv[1])

cases = [
    ("osat",   "(x1 OR x2) AND (NOT x1 OR x3)"),
    ("osat",   "x1 AND (NOT x1)"),
    ("ounsat", "x1 AND (NOT x1)"),
    ("ounsat", "x1 OR x2"),
]

for mode, source in cases:
    print("-" * 60)
    formula = Formula.parse(source)
    result = oracle.osat(formula) if mode == "osat" else oracle.ounsat(formula)
    print(result)

print()
s = oracle.stats()
print(f"Total prophecies : {s.total_prophecies}")
print(f"SAT calls        : {s.sat_calls}")
print(f"UNSAT calls      : {s.unsat_calls}")
print(f"P vs NP          : {s.p_vs_np_status}")
