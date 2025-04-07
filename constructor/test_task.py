#https://isopromat.ru/tehmeh/reshenie-zadach/opredelenie-reakcij-opor-balki-sila-pod-uglom

from sympy import *
import mpmath
import numpy as np

class SymbolEnv:
    def __init__(self, spec):
        self.symbols = {}
        self.variables = []
        self.parameters = {}

        for name, val in spec.items():
            sym = symbols(name)
            self.symbols[name] = sym
            if val == '?':
                self.variables.append(sym)
            else:
                self.parameters[sym] = val

    def inject(self, scope=None):
        if scope is None:
            scope = globals()
        for name, sym in self.symbols.items():
            scope[name] = sym

spec: dict[str: np.float64| str] = {
    'Fx': np.cos(np.deg2rad(35)) * 10,
    'Fy': np.sin(np.deg2rad(35)) * 10,
    'M': 8,
    'q': 4,
    'BC': 5,
    'AE': 17,
    'KE': 8.5,
    'BE': 11,
    'DE': 1,
    'RBx': '?',
    'RBy': '?',
    'RDy': '?'
}

env = SymbolEnv(spec)
env.inject()

eqs = [
    Eq(-Fy - q * BC + RBy + RDy, 0),
    Eq(-Fx + RBx, 0),
    Eq(Fy * AE + M + q * BC * KE - RBy * BE - RDy * DE, 0)
]

eqs_substituted = [eq.subs(env.parameters) for eq in eqs]

print(linsolve(eqs_substituted, (RBx, RBy, RDy)))
