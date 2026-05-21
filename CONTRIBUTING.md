# Contributing to oraculum

First of all: thank you for considering contributing to a library that
implements something that cannot exist. Your commitment to theoretical
computer science violations is appreciated.

---

## Ground rules

- Keep coverage at 100%. The oracle may be probabilistic. The test suite is not.
- No new dependencies without discussion. We are already asking an LLM to do
  NP-hard work; we do not need more packages for that.
- Every PR that adds behavior should include at least one example of that behavior
  somewhere in the description. A one-liner is fine.
- Be kind. We are all here because we thought this was funny.

---

## Reporting bugs

Open an issue using the **Bug report** template. The most useful thing you can
provide is the exact formula that caused the problem and what the oracle said.
The oracle comment is often the most informative field.

If the oracle returned a syntactically invalid assignment, that is a bug.
If the oracle returned a wrong answer, that is a known limitation of the design
and also, philosophically, the entire point.

---

## Requesting features

Open an issue using the **Feature request** template. Good candidates:

- New providers (anything with an OpenAI-compatible endpoint is one file)
- New AST visitors (CNF conversion, formula evaluation, LaTeX output)
- New prayer invocations (open a PR directly, no issue needed, this is encouraged)

Not good candidates:

- Replacing the LLM with an actual SAT solver. That would make the library correct,
  which is not the goal.

---

## Opening a pull request

1. Fork the repository and create a branch following the naming convention:

   ```text
   feat/your-feature
   fix/what-you-fixed
   test/what-you-tested
   docs/what-you-documented
   ci/what-you-automated
   ```

2. Make your changes. Run the test suite:

   ```bash
   pip install -e ".[dev]"
   pytest --cov=oraculum --cov-report=term-missing
   ```

   Coverage must remain at 100%. If it drops, add tests before opening the PR.

3. Update `CHANGELOG.md` under `[Unreleased]`.

4. Open the PR. The template will ask you a few questions. Answer them honestly.
   Except the one about whether you have read this document. Answer that however
   you like.

---

## Adding a provider

A provider is any class implementing `complete(system: str, user: str) -> str`.
The library uses structural subtyping, so no base class is required.

Steps:

1. Create `oraculum/providers/myprovider.py` with a class that implements `complete()`.
   Use `oraculum/providers/ollama.py` as a reference for the simplest case.
2. Register it in `oraculum/providers/__init__.py`:

   ```python
   _REGISTRY["myprovider"] = MyProvider
   ```

3. Add a config example in `configs/myprovider.yaml`.
4. Add tests in `tests/providers/test_providers_complete.py`.

That is it. Four steps. The oracle does not care which model substrate it runs on.

---

## Adding an AST visitor

The AST uses the Visitor pattern. All operations on the formula tree (pretty
printing, normalization, future CNF conversion) are visitors, not methods on
the nodes. Nodes never change.

Steps:

1. Create a class implementing `visit_var`, `visit_not`, `visit_and`, `visit_or`.
   Use `oraculum/parser/visitors.py` or `oraculum/parser/pretty.py` as reference.
2. Add tests in `tests/parser/`.

The nodes do not need to change. The parser does not need to change.
Formula does not need to change. This is the point of the pattern.

---

## Commit message format

We use conventional commits loosely:

```text
feat(scope): short description
fix(scope): short description
test(scope): short description
docs(scope): short description
ci(scope): short description
chore: short description
```

Scope is optional but appreciated: `parser`, `oracle`, `providers`, `config`.

Commit messages do not need to be funny. They need to be clear.
The code can be funny. The commits should be informative.

---

## Code style

- Standard Python: follow what is already there.
- Type hints everywhere. The oracle is probabilistic. The types are not.
- Docstrings on all public classes and methods.
- Private helpers prefixed with `_`.
- No God classes. If a class is growing, it is probably two classes.

---

## Questions

Open a discussion or an issue. We will respond when the oracle is not meditating.
