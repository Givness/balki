from structures import *
from sympy import *
from numpy import float64

FList: list[Force] = [Force(1, 135, 1, 1, False), Force(2, 135, 1, 1, False), Force(0, 0, 0, 1, True)]

spec: dict[str: str | float64] = {f'Force_{force.id}': '?' if force.unknown else force.part_x for force in FList}

str_eq: str = ' + '.join(spec.keys())

eqs: list[Eq] = [
    Eq(simplify(str_eq), 0)
]

eqs_substituted: list[Eq] = [eq.subs({name: val for name, val in spec.items() if val != '?'}) for eq in eqs]

print(linsolve(eqs_substituted, (Symbol('Force_2'))))