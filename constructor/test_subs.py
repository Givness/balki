from structures import *
from sympy import *
from numpy import float64

spec = {
    'A': '?',
    'B': '10 * A',
    'C': 1
}

str_eq = 'A + B + C'

eqs = [
    Eq(simplify(str_eq), 12),
]

secondary_eqs = [
    Eq(simplify('10 * A'), Symbol('B')),
    Eq(Symbol('C'), 1)
]

print(linsolve(eqs + secondary_eqs, symbols(['A', 'B', 'C'])))