# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

P vs NP remains open. The changelog does not.

---

## [Unreleased]

---

## [2.1.1] - 2026-11-04

### Fixed

- Require actual JSON booleans for SAT and UNSAT verdicts. Missing fields and
  values such as `"false"`, `0`, or `null` now raise `MalformedResponseError`
  instead of being silently coerced.
- Require model responses to be JSON objects and assignments to be objects or
  `null`. Assignment values for formula variables must be actual JSON booleans;
  unknown variables continue to be filtered out.
- Trim surrounding whitespace before parsing model responses and omit raw model
  output from the invalid-JSON error message.
- Declare `httpx` explicitly in development dependencies for provider tests.

### Added

- Regression tests for malformed response objects, verdicts and assignments.
- Contribution, security and community guidelines, plus GitHub issue and pull
  request templates.

### Changed

- Enforce 100% statement coverage in CI and build and validate both source and
  wheel distributions with Twine before publishing.
- Use SPDX MIT license metadata with an explicit license file, require
  `setuptools>=77.0`, and remove the deprecated license classifier.

### Compatibility

- The documented public API is unchanged. Integrations relying on coercion of
  malformed model responses must handle `MalformedResponseError` instead.
- Validation checks response structure and types; it does not establish that an
  assignment satisfies a formula or provide a formal SAT/UNSAT certificate.

---

## [2.1.0] - 2024-01-01

### Added

- `oraculum/parser/` submodule: full Boolean formula parser with AST.
  - `tokens.py` — `TokenType` enum and `Token` dataclass with position tracking.
  - `nodes.py` — Frozen AST node types (`VarNode`, `NotNode`, `AndNode`, `OrNode`)
    and a `Visitor` protocol for extensible tree operations.
  - `tokenizer.py` — Linear O(n) tokenizer. Case-insensitive keywords.
    Raises `FormulaError` with exact character position on unrecognized input.
  - `parser.py` — LL(1) recursive descent parser. Correct operator precedence:
    `NOT > AND > OR`. No backtracking.
  - `visitors.py` — Internal visitors: `NormalizeVisitor`, `DepthVisitor`,
    `VariableVisitor`.
  - `pretty.py` — `PrettyPrintVisitor` rendering AST as a Unicode indented tree.
  - `formula.py` — `Formula` dataclass (frozen) with `parse()` factory.
    Fields: `normalized`, `variables`, `depth`, `ast`.
- `FormulaError` added to the exception hierarchy.
- `Formula` and `FormulaError` exposed in the top-level public API.
- `osat()` and `ounsat()` now accept `Formula` only. Passing a raw `str`
  raises `TypeError` with a message explaining what to do instead.
- Assignment validation: variables returned by the LLM that are not present
  in the formula are silently filtered and logged at WARNING level.
- `test_factory.py`, `tests/parser/` suite, `tests/providers/test_providers_complete.py`
  added. Total: 147 tests, 100% coverage.

### Changed

- `SatResult.formula` and `UnsatResult.formula` are now `Formula` instead of `str`.
- `oracle.py` uses `formula.normalized` for prayer construction and
  `formula.variables` for assignment validation.
- `__version__` bumped to `2.1.0`.

---

## [2.0.0] - 2024-01-01

### Added

- Multi-provider support: Anthropic, OpenAI, Ollama, OpenRouter.
- `LLMProvider` protocol (structural subtyping, no base class required).
- Provider registry in `oraculum/providers/__init__.py`. Adding a provider
  is two lines.
- YAML configuration system with `${ENV_VAR}` expansion.
- Example configs in `configs/` for all four providers.
- `from_config(path)` factory in `oraculum/factory.py`.
- `OracleStats` dataclass with call counters and editorial commentary.
- `UnknownProviderError` added to the exception hierarchy.
- `pyproject.toml` optional dependency groups: `[anthropic]`, `[openai]`,
  `[ollama]`, `[openrouter]`, `[all]`, `[dev]`.

### Changed

- `Oraculum` constructor now takes a `LLMProvider` instead of an API key.
  Provider construction is the caller's responsibility (or `from_config()`'s).
- Project restructured into `oraculum/config/` and `oraculum/providers/`
  submodules.
- `__version__` bumped to `2.0.0`.

### Removed

- Direct `api_key` parameter from `Oraculum.__init__`. Use a provider.

---

## [1.0.0] - 2024-01-01

### Added

- Initial release.
- `Oraculum` class with `osat()` and `ounsat()` methods backed by the
  Anthropic API.
- `PrayerBuilder` with configurable `reverence` level (1-10).
- `SatResult` and `UnsatResult` dataclasses.
- Custom exception hierarchy: `OracolumError`, `OracleUnavailableError`,
  `MalformedResponseError`.
- Theoretical complexity: O(1) in the oracle model.
- Turing Award ETA: not before 2087.

[Unreleased]: https://github.com/Alessandro624/oraculum/compare/v2.1.1...HEAD
[2.1.1]: https://github.com/Alessandro624/oraculum/compare/v2.1.0...v2.1.1
[2.1.0]: https://github.com/Alessandro624/oraculum/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/Alessandro624/oraculum/compare/v1.0.0...v2.0.0
[1.0.0]: Not available - sorry :)
