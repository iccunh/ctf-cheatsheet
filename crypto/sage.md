# Sage

## Run

```bash
sage solve.sage
sage -python solve.py
```

```python
from sage.all import *
```

## GF / Polynomial Ring

```python
p = 34552766466194213521879675822306514044891870393271
F = GF(p)
R = PolynomialRing(F, "x")
x = R.gen()

f = x**3 + 1337*x + 42
print(f.factor())
print(f.roots())
```

Sage syntax:

```python
F = GF(p)
R.<x> = PolynomialRing(F)
f = x^3 + 1337*x + 42
```

## Resultant

Eliminate one variable from two equations.

```python
F = GF(p)
R = PolynomialRing(F, ("X", "Y"))
X, Y = R.gens()

f1 = Y**2 - (X**3 + a*X + b)
f2 = Y**2 + a*X*Y + c*Y - (X**3 + b*X**2 + d*X + e)

rx = f1.resultant(f2, Y)
print(rx.factor())

for root, mult in rx.univariate_polynomial().roots():
    print(int(root), mult)
```

## Linear Factor Root

For `A*x + B = 0 mod p`:

```python
root = (-B * inverse_mod(A, p)) % p
```

## Matrix / LLL

```python
M = Matrix(ZZ, [
    [1, 0, 123],
    [0, 1, 456],
    [0, 0, 789],
])

L = M.LLL()
print(L)
```

## CRT

```python
x = crt([a1, a2, a3], [m1, m2, m3])
print(x)
```

## Bytes

```python
from Crypto.Util.number import long_to_bytes, bytes_to_long

print(long_to_bytes(int(root)))
```

