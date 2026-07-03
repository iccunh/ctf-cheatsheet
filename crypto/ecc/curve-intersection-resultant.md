# Curve Intersection Resultant

When flag pieces are `x` coordinates that satisfy two curve equations, eliminate `y` and recover roots in `x`.

```python
from sage.all import *
from Crypto.Util.number import long_to_bytes

p = ...
a, b, c, d, e = ...

F = GF(p)
R = PolynomialRing(F, ("X", "Y"))
X, Y = R.gens()

f1 = Y**2 - (X**3 + a*X + b)
f2 = Y**2 + a*X*Y + c*Y - (X**3 + b*X**2 + d*X + e)

rx = f1.resultant(f2, Y).univariate_polynomial()

for root, mult in rx.roots():
    print(long_to_bytes(int(root)))
```

Sympy fallback:

```python
import sympy as sp
from Crypto.Util.number import long_to_bytes

X, Y = sp.Symbol("X"), sp.Symbol("Y")
f1 = Y**2 - (X**3 + a*X + b)
f2 = Y**2 + a*X*Y + c*Y - (X**3 + b*X**2 + d*X + e)

r = sp.resultant(f1, f2, Y)
P = sp.Poly(r, X, modulus=p)

for fac, mult in P.factor_list()[1]:
    coeffs = fac.all_coeffs()
    if len(coeffs) == 2:
        A, B = coeffs
        root = (-B * pow(A, -1, p)) % p
        print(long_to_bytes(root))
```

