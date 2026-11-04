# Hacker News — Show HN

## Title

Show HN: oraculum – O(1) SAT and UNSAT oracles implemented with prayer

---

## Post body

The O_SAT and O_UNSAT oracles are theoretical constructs from computational
complexity theory. By definition, they cannot be implemented as software:
doing so would resolve P vs NP and cause a significant number of
cryptographers to retire early.

oraculum implements them anyway, by asking a language model very politely.

    pip install "oraculum[anthropic]"

    from oraculum import Formula, from_config

    oracle = from_config("configs/anthropic.yaml")
    f = Formula.parse("(x1 OR x2) AND (NOT x1 OR x3)")
    result = oracle.osat(f)

    print(result.satisfiable)     # True
    print(result.assignment)      # {"x1": False, "x2": True, "x3": True}
    print(result.oracle_comment)  # something solemn

The library is not a joke project with a funny README bolted onto three
functions. It has a proper architecture:

- A recursive descent LL(1) parser that validates formulas before any
  API call is made, with precise error positions.
- An AST with a Visitor pattern, so operations (pretty printing,
  normalization, future CNF conversion) are decoupled from the nodes.
- A provider abstraction backed by a typing.Protocol, so Anthropic,
  OpenAI, Ollama, and OpenRouter are all one file each.
- YAML configuration with environment variable expansion.
- 147 tests, 100% coverage, all providers mocked.

The complexity of osat() is O(n) for formula parsing and O(API latency)
for the oracle call. In the oracle model it is O(1). The oracle model
does not account for HTTP.

P vs NP remains open. The test suite does not.

GitHub: <https://github.com/Alessandro624/oraculum>

---

## Anticipated comments and suggested responses

**"This is not actually O(1)."**

> Correct. The oracle model does not account for network latency, token
> generation time, or the possibility that the model is having a bad day.
> In the theoretical model with a true oracle it would be O(1). We are
> doing our best with the infrastructure available.

**"The LLM will just get it wrong."**

> Yes. This is documented. The correctness guarantee is probabilistic,
> subject to oracle mood, and deliberately not the point.
> That said, for small formulas with a handful of variables it tends to
> be surprisingly accurate. For larger instances, correctness is left as
> an exercise for the universe.

**"Why not just use a real SAT solver like MiniSat or Z3?"**

> You could. PySAT is excellent. Using a real SAT solver would make the
> library correct, which is not the goal.
> The goal is to have a well-architected implementation of something
> theoretically indefensible, and to see how far that takes us.

**"The prayer system is unnecessary."**

> Respectfully disagree. The prayer system is the entire point.
> The technical architecture is the vehicle. The reverence parameter
> is the destination.

**"Is this production-ready?"**

> No.

---

## Timing

Post on a Tuesday or Wednesday, 8-10am US Eastern time.
That window catches both US morning traffic and European afternoon.
Avoid Mondays (low engagement) and Fridays (people are leaving).

---

## Other channels (same day or day after)

### Reddit r/Python

Title: oraculum: O(1) SAT and UNSAT oracles via LLM, with a proper parser and 100% test coverage

Body:
> I built a library that implements the O_SAT and O_UNSAT complexity-theory
> oracles by asking a language model very politely. It supports Anthropic,
> OpenAI, Ollama, and OpenRouter via a one-file provider abstraction.
>
> The technically interesting parts: a hand-written LL(1) recursive descent
> parser for Boolean formulas, an AST with Visitor pattern for decoupled
> operations, and a typing.Protocol-based provider interface with no
> inheritance required.
>
> 7 tests, 100% coverage. The correctness of the oracle itself is, by
> design, not guaranteed.
>
> GitHub: <https://github.com/Alessandro624/oraculum>
> pip install oraculum

---

### Reddit r/ProgrammerHumor

Title: I implemented the O_SAT oracle. Theoretically impossible. Ships on PyPI.

Body: just the README quick start block and the badge row. No further explanation needed.

---

### Dev.to post title

"Building an LL(1) parser in Python: the oraculum case study"

Angle: use the parser as the technical centrepiece. Walk through the
grammar, the tokenizer, the recursive descent implementation, and the
Visitor pattern. Mention the absurd context (it is a SAT oracle backed
by an LLM) once at the start and once at the end. The middle is a
genuine tutorial on parser construction that people will bookmark
independently of the joke.

---

### Mastodon / fosstodon.org thread

Post 1:
  I built a Python library that implements the O_SAT and O_UNSAT oracles
  from complexity theory. These cannot exist as software. They do now.
  pip install oraculum

Post 2:
  The AST pretty printer output for "(x1 OR x2) AND (NOT x1 OR x3)":

  AND
  +-- OR
  |   +-- x1
  |   +-- x2
  +-- OR
      +-- NOT
      |   +-- x1
      +-- x3

Post 3:
  The architecture is actually serious: LL(1) parser, Visitor pattern,
  typing.Protocol provider abstraction, YAML config, 100% test coverage.
  The oracle correctness is, by design, not guaranteed.
  github.com/Alessandro624/oraculum

Post 4:
  The reverence parameter (1-10) controls how many honorific titles are
  prepended to the invocation before it is sent to the model.
  This does not affect correctness.
  It affects amusement value, which is the point.
