"""JSON-lines transport for the Unity Editor. Stdout is reserved for replies."""

import hashlib
import json
import os
import random
import re
import sys

from oraculum import Formula, Oraculum
from oraculum.config.schema import ProviderConfig
from oraculum.providers import build_provider


def generate_formula(question):
    seed = " ".join(question.casefold().split()).encode("utf-8")

    if not seed:
        raise ValueError("Enter a question.")

    rng = random.Random(hashlib.sha256(seed).digest())

    def literal():
        return rng.choice(("", "NOT ")) + rng.choice(("x1", "x2", "x3", "x4"))

    return " AND ".join(f"({literal()} OR {literal()})" for _ in range(3))


def configure(settings):
    name = settings["provider"]
    key = None

    if name != "ollama":
        variable = settings["variable"].strip()

        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", variable):
            raise ValueError("Enter the name of the environment variable containing your API key.")

        key = os.getenv(variable)

        if not key:
            raise ValueError(f"Missing environment variable: {variable}")

    model = settings["model"].strip()

    if not model:
        raise ValueError("Enter a model name in Local Settings.")

    return build_provider(ProviderConfig(provider=name, model=model, api_key=key, base_url=settings.get("url") or None))


def serve(lines, output):
    provider = None

    for line in lines:
        try:
            request = json.loads(line)
            if provider is None:
                provider = configure(request)
                reply = {"ready": True}
            else:
                level = request["reverence"]

                if type(level) is not int or not 1 <= level <= 10:
                    raise ValueError("Reverence must be an integer from 1 to 10.")

                expression = request.get("formula") or generate_formula(request["question"])

                result = Oraculum(provider, level).osat(Formula.parse(expression))

                if not result.oracle_comment.strip():
                    raise ValueError("The model returned an empty comment.")

                reply = {"comment": result.oracle_comment}
        except Exception as exc:
            reply = {"error": str(exc)}

        print(json.dumps(reply), file=output, flush=True)


if __name__ == "__main__":
    sys.stdin.reconfigure(encoding="utf-8-sig")

    serve(sys.stdin, sys.stdout)
