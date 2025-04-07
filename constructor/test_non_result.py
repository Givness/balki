from sympy import *

#A, B = symbols('A B')

eqs = [
    Eq(simplify('A'), 0),
    Eq(simplify('B'), 0)
]

print(solve(eqs, symbols(['B'])))