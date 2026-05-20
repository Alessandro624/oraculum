"""
oraculum.parser - Boolean formula parsing and AST.

Public surface:
    Formula       - validated formula type; entry point is Formula.parse()
    FormulaError  - raised on lexical or syntactic errors

Everything else (tokenizer, parser, nodes, visitors) is an internal
implementation detail and may change without notice.

The pretty printer is exposed separately because it is useful interactively:
    from oraculum.parser.pretty import pretty
    print(pretty(formula.ast))
"""

from .formula import Formula
from ..exceptions import FormulaError

__all__ = ["Formula", "FormulaError"]
