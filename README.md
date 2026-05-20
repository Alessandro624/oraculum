# ORACULUM

> An implementation of the O_SAT and O_UNSAT oracles. These oracles cannot exist. They do now.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Correctness: probabilistic](https://img.shields.io/badge/correctness-probabilistic-orange.svg)](.)
[![P vs NP: still open](https://img.shields.io/badge/P%20vs%20NP-still%20open-red.svg)](.)

---

## What is this

In computational complexity theory, an **oracle** is a hypothetical black box that answers certain
questions in O(1) time. The **O_SAT** oracle tells you whether a Boolean formula is satisfiable.
The **O_UNSAT** oracle certifies that it is not.

These oracles are purely theoretical. Implementing them as software would resolve P vs NP and
cause a significant number of cryptographers to retire early.

This library implements them anyway, by asking a language model very politely.

The model does not care about computational complexity theory. It tries its best.

---

## Installation

```bash
pip install oraculAI

# With your provider of choice:
pip install "oraculAI[anthropic]"
pip install "oraculAI[openai]"
pip install "oraculAI[ollama]"      # also covers openrouter
pip install "oraculAI[all]"
```

---

## Quick start

Create a config file (see `configs/` for examples) and point the library at it:

```python
from oraculum import Formula, from_config

oracle = from_config("configs/anthropic.yaml")

# Formulas must be parsed before querying. This validates syntax
# and guarantees well-formedness before any API call is made.
f = Formula.parse("(x1 OR x2) AND (NOT x1 OR x3)")

result = oracle.osat(f)
print(result.satisfiable)     # True or False
print(result.assignment)      # {"x1": False, "x2": True, ...} or None
print(result.oracle_comment)  # something solemn

result = oracle.ounsat(Formula.parse("x1 AND (NOT x1)"))
print(result.unsatisfiable)           # True
print(result.satisfying_assignment)   # None
print(result.oracle_comment)          # something melancholic
```

---

## Configuration

Each config file specifies a provider, a model, credentials, and oracle settings.
Environment variables are expanded at load time using `${VAR_NAME}` syntax.

### **configs/anthropic.yaml**

```yaml
provider: anthropic
model: claude-opus-4-5
api_key: "${ANTHROPIC_API_KEY}"

oracle:
  reverence: 5
  max_tokens: 512
```

### **configs/openai.yaml**

```yaml
provider: openai
model: gpt-4o
api_key: "${OPENAI_API_KEY}"

oracle:
  reverence: 5
  max_tokens: 512
```

### **configs/ollama.yaml**

```yaml
provider: ollama
model: llama3.1:8b
base_url: "http://localhost:11434/v1"

oracle:
  reverence: 3
  max_tokens: 512
```

### **configs/openrouter.yaml**

```yaml
provider: openrouter
model: mistralai/mistral-7b-instruct
api_key: "${OPENROUTER_API_KEY}"

oracle:
  reverence: 5
  max_tokens: 512
```

The `reverence` field controls how many honorific titles are prepended to the invocation.
Range is 1 to 10. This does not affect correctness. It affects amusement value, which is the point.

---

## Formula

All oracle calls require a `Formula` instance. Raw strings are not accepted.
This guarantees that the formula is syntactically valid before any API call is made.

```python
from oraculum import Formula, FormulaError

# Parse and validate
f = Formula.parse("(x1 OR x2) AND (NOT x1 OR x3)")

print(f.normalized)   # "x1 OR x2 AND (NOT x1) OR x3" -- canonical form
print(f.variables)    # frozenset({"x1", "x2", "x3"})
print(f.depth)        # maximum AST nesting depth

# Syntax errors are caught immediately, before any API call
try:
    Formula.parse("x1 AND OR x2")
except FormulaError as e:
    print(e)  # Expected a variable or '(' but got 'OR' at position 8.
```

### Supported syntax

| Construct  | Examples                              |
|------------|---------------------------------------|
| Variables  | `x1`, `A`, `my_var`                   |
| AND        | `x1 AND x2`, `x1 and x2`              |
| OR         | `x1 OR x2`, `x1 or x2`                |
| NOT        | `NOT x1`, `not x1`                    |
| Grouping   | `(x1 OR x2) AND x3`                   |

Keywords are case-insensitive. Precedence: `NOT > AND > OR`.

### Pretty printing the AST

```python
from oraculum.parser.pretty import pretty

f = Formula.parse("(x1 OR x2) AND (NOT x1 OR x3)")
print(pretty(f.ast))
```

```text
AND
├── OR
│   ├── x1
│   └── x2
└── OR
    ├── NOT
    │   └── x1
    └── x3
```

---

## Wiring a provider directly

If you prefer not to use a config file, or if you are writing tests:

```python
from oraculum import Formula, Oraculum
from oraculum.config.schema import ProviderConfig
from oraculum.providers import build_provider

provider_cfg = ProviderConfig(
    provider="openai",
    model="gpt-4o",
    api_key="sk-...",
)
oracle = Oraculum(build_provider(provider_cfg), reverence=6)
print(oracle.osat(Formula.parse("(x1 OR x2) AND (NOT x1)")))
```

---

## Adding a custom provider

Any object that implements `complete(system: str, user: str) -> str` qualifies as a provider.
No base class required; the library uses structural subtyping via `typing.Protocol`.

```python
import json
from oraculum import Formula, Oraculum

class MyProvider:
    def complete(self, system: str, user: str) -> str:
        # Call your model here. Return raw text.
        return json.dumps({
            "satisfiable": True,
            "assignment": {"x1": True},
            "oracle_comment": "Behold.",
        })

oracle = Oraculum(MyProvider())
print(oracle.osat(Formula.parse("x1")))
```

To make the provider selectable by name in YAML configs, register it in
`oraculum/providers/__init__.py`:

```python
_REGISTRY["myprovider"] = MyProvider
```

---

## API reference

### `from_config(path) -> Oraculum`

Build an Oraculum from a YAML config file. Recommended entry point.

### `Formula.parse(source: str) -> Formula`

| Field        | Type              | Description                                        |
|--------------|-------------------|----------------------------------------------------|
| `normalized` | `str`             | Canonical form with uppercase keywords             |
| `variables`  | `frozenset[str]`  | All variable names in the formula                  |
| `depth`      | `int`             | Maximum AST nesting depth                          |
| `ast`        | `Node`            | Root AST node, for pretty printing and future use  |

### `Oraculum(provider, reverence=5)`

Accepts any object satisfying the `LLMProvider` protocol.

### `oracle.osat(formula: Formula) -> SatResult`

| Field             | Type            | Description                        |
|-------------------|-----------------|------------------------------------|
| `satisfiable`     | `bool`          | Whether the formula is SAT         |
| `assignment`      | `dict` or None  | Satisfying assignment if SAT       |
| `oracle_comment`  | `str`           | Decorative remark                  |
| `prophecy_number` | `int`           | Sequential call counter            |
| `formula`         | `Formula`       | The submitted formula              |
| `prayer`          | `str`           | The full invocation text           |

### `oracle.ounsat(formula: Formula) -> UnsatResult`

| Field                   | Type            | Description                         |
|-------------------------|-----------------|-------------------------------------|
| `unsatisfiable`         | `bool`          | Whether UNSAT is certified          |
| `satisfying_assignment` | `dict` or None  | Counterexample if not UNSAT         |
| `oracle_comment`        | `str`           | Decorative remark                   |
| `prophecy_number`       | `int`           | Sequential call counter             |
| `formula`               | `Formula`       | The submitted formula               |
| `prayer`                | `str`           | The full invocation text            |

### `oracle.stats() -> OracleStats`

Returns call counts and editorial remarks. The numbers are accurate. The remarks are not.

---

## Running the tests

No API key required. All providers are mocked.

```bash
pip install -e ".[dev]"
pytest
pytest --cov=oraculum --cov-report=term-missing
```

---

## Project structure

```text
oraculum/
  oraculum/
    __init__.py             Public API
    oracle.py               Oraculum class (osat, ounsat, stats)
    factory.py              from_config() factory
    prayers.py              Invocation construction
    models.py               SatResult, UnsatResult, OracleStats
    exceptions.py           Exception hierarchy
    config/
      __init__.py
      schema.py             ProviderConfig, OracleConfig dataclasses
      loader.py             YAML loading and env var expansion
    parser/
      tokens.py             TokenType enum and Token dataclass
      nodes.py              AST node types and Visitor protocol
      tokenizer.py          Linear tokenizer with position tracking
      parser.py             LL(1) recursive descent parser
      visitors.py           NormalizeVisitor, DepthVisitor, VariableVisitor
      pretty.py             PrettyPrintVisitor (Unicode tree output)
      formula.py            Formula dataclass and parse() factory
    providers/
      __init__.py           Registry and build_provider()
      protocol.py           LLMProvider protocol
      anthropic.py
      openai.py
      ollama.py
      openrouter.py
  tests/
    test_oracle.py
    test_prayers.py
    test_models.py
    test_factory.py
    config/
      test_loader.py
    parser/
      test_tokenizer.py
      test_parser.py
      test_formula.py
      test_pretty.py
    providers/
      test_registry.py
      test_providers_complete.py
  examples/
    from_config.py
    custom_provider.py
  configs/
    anthropic.yaml
    openai.yaml
    ollama.yaml
    openrouter.yaml
  pyproject.toml
  README.md
  LICENSE
  .gitignore
```

---

## Frequently asked questions

**Does this actually work?**

Surprisingly often. For small formulas with a handful of variables it tends to be correct.
For larger instances, correctness is left as an exercise for the universe.

**Is this suitable for production use?**

No.

**What is the time complexity of osat()?**

O(n) for formula parsing, O(1) in the oracle model, O(API latency) in practice.
The oracle model does not account for HTTP.

**Why must I call Formula.parse() explicitly?**

It is the "parse, don't validate" principle. A `Formula` can only exist if it is
well-formed. Passing a raw string to `osat()` would hide the parsing step and make
it unclear when errors are raised. Explicit is better than implicit.

**Has this resolved P vs NP?**

No. We checked.

**What happens at reverence level 10?**

The oracle receives a great many titles. It responds the same way regardless.

---

## License

[MIT](LICENSE). Alan Turing is not here to stop you.
