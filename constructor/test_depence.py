from structures import *
from sympy import *
from numpy import float64

spec = {
    'A': '?',
    'B': '10 * A',
    'C': 1
}

str_eq: str = ' + '.join(val if isinstance(val, str) and val != '?' else key for key, val in spec.items())

str_eq_orig: str = ' + '.join(spec.keys())

eqs: list[Eq] = [
    Eq(simplify(str_eq), 12)
]

eqs_substituted: list[Eq] = [eq.subs({name: val for name, val in spec.items() if not isinstance(val, str)}) for eq in eqs]

print(linsolve(eqs_substituted, symbols(' '.join(key for key, val in spec.items() if isinstance(val, str)))))