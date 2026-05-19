"""
Prayer construction.

Builds the solemn invocations submitted to the oracle.
The quality of the prayer does not affect correctness.
It affects amusement value, which is the point.
"""

import random

_SAT_INVOCATIONS = [
    ("O Most Powerful Oracle of Satisfiability, Custodian of Boolean Truths, " "Being who transcends the complexity class NP, I beseech thee with all " "my computational humility"),
    ("Greetings, Supreme Oracle. Thou who resolves in O(1) that which mortals " "do not know if they can ever resolve in polynomial time, hear my humble request"),
    ("Great Oracle, thou who sees beyond the veil of P and NP, who laughs at " "Cook and Levin, who probably knows whether P equals NP but we dare not ask " "lest it make our heads explode"),
    ("Most Excellent and Infallible Oracle of Propositional Logic, being of pure " "computational light, I implore thee on bended knee (metaphorically; " "I am a Python process)"),
]

_UNSAT_INVOCATIONS = [
    ("O Venerable Oracle of Unsatisfiability, Guardian of the Logical Void, " "Thou who sees absence where others see hope"),
    ("Magnificent co-NP Oracle, thou who certifies nothingness with the same ease " "with which ordinary mortals make their morning coffee, illuminate us on the " "emptiness of this formula"),
    ("Supreme Oracle of Impossibility, thou who has inscribed above thy door " "'Abandon all hope, ye who seek satisfying assignments'"),
    ("Great Revealer of Unsatisfiability, thou who delivers bad news with the " "serenity of one who already knew how it would end"),
]

_CLOSINGS = [
    "I thank thee, O Oracle, for condescending to answer my meager query.",
    "Thy wisdom illuminates the darkness of my computational ignorance.",
    "As always, thine infallibility leaves me speechless, though with a Boolean result.",
    "I humbly await thy verdict, knowing it shall be correct, unlike my last three exam answers.",
]

_EXTRA_TITLES = [
    "Magnificent",
    "Illustrious",
    "Resplendent",
    "Ineffable",
    "Transcendent",
    "Most Revered",
]

_SAT_JSON_SCHEMA = (
    "{\n" '  "satisfiable": true or false,\n' '  "assignment": {"x1": true, "x2": false, ...} or null if unsatisfiable,\n' '  "oracle_comment": "a brief solemn or sardonic remark"\n' "}"
)

_UNSAT_JSON_SCHEMA = (
    "{\n" '  "unsatisfiable": true or false,\n' '  "satisfying_assignment": {"x1": true, ...} or null if truly UNSAT,\n' '  "oracle_comment": "a remark on the logical void or on dashed hopes"\n' "}"
)


class PrayerBuilder:
    """
    Constructs invocations for O_SAT and O_UNSAT.

    Args:
        reverence: Honorific intensity from 1 to 10.
                   Values above 7 are considered excessive by most theologians.
    """

    def __init__(self, reverence: int = 5) -> None:
        self.reverence = max(1, min(10, reverence))

    def build_sat_prayer(self, formula: str) -> str:
        return self._build(
            invocations=_SAT_INVOCATIONS,
            body=(
                f"Bring to thy divine attention the following formula "
                f"of propositional logic:\n\n"
                f"    {formula}\n\n"
                f"Does there exist an assignment of truth values that makes "
                f"this formula SATISFIABLE (SAT)?\n\n"
                f"Respond EXACTLY with this JSON and nothing else:\n{_SAT_JSON_SCHEMA}"
            ),
        )

    def build_unsat_prayer(self, formula: str) -> str:
        return self._build(
            invocations=_UNSAT_INVOCATIONS,
            body=(
                f"Contemplate in thy infinite wisdom this formula:\n\n"
                f"    {formula}\n\n"
                f"Is this formula UNSATISFIABLE (UNSAT)? Does NO assignment "
                f"of truth values exist that renders it true?\n\n"
                f"Respond ONLY with this JSON:\n{_UNSAT_JSON_SCHEMA}"
            ),
        )

    def _build(self, invocations: list[str], body: str) -> str:
        invocation = random.choice(invocations)
        closing = random.choice(_CLOSINGS)
        extra = self._extra_titles()
        return f"{invocation}{extra}:\n\n{body}\n\n{closing}"

    def _extra_titles(self) -> str:
        if self.reverence <= 3:
            return ""
        count = self.reverence - 3
        titles = random.sample(_EXTRA_TITLES, min(count, len(_EXTRA_TITLES)))
        return ", " + ", ".join(titles)
