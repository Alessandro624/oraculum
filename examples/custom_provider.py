"""
Example: wire a provider directly without a config file.

Use this pattern when you need programmatic control over provider
construction, or when writing tests with a stub provider.
"""

import json
import os

from oraculum import Formula, Oraculum
from oraculum.config.schema import ProviderConfig
from oraculum.providers import build_provider

# Option A: build from a ProviderConfig programmatically
provider_cfg = ProviderConfig(
    provider="anthropic",
    model="claude-opus-4-5",
    api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
    max_tokens=512,
)
provider = build_provider(provider_cfg)
oracle = Oraculum(provider, reverence=4)

f = Formula.parse("(x1 OR x2) AND (NOT x1 OR x3)")
result = oracle.osat(f)
print(result)


# Option B: stub provider for local development or testing
class EchoProvider:
    """
    A stub that always returns SAT with a fixed assignment.
    Useful for testing without spending API credits.
    """

    def complete(self, system: str, user: str) -> str:
        return json.dumps(
            {
                "satisfiable": True,
                "assignment": {"x1": True, "x2": False},
                "oracle_comment": "This is a stub. The oracle is on holiday.",
            }
        )


stub_oracle = Oraculum(EchoProvider(), reverence=1)
result = stub_oracle.osat(Formula.parse("x1 OR x2"))
print(result)


# Option C: pretty-print the AST before querying
from oraculum.parser.pretty import pretty

formula = Formula.parse("(x1 OR x2) AND (NOT x1 OR x3)")
print(pretty(formula.ast))
