# RSA

## Pick

| What you see | Go to |
| --- | --- |
| Same message, low `e`, multiple moduli | [Broadcast](broadcast.md) |
| `e = 16` or non-coprime exponent | [e-16](e-16.md) |
| `d mod (p-1)` leaked | [d mod p-1](d-mod-p-1.md) |
| Many small-ish primes | [Many primes](many-primes.md) |
| `p-1` smooth | [Pollard p-1](pollards-p-1.md) |
| `p+1` smooth | [Williams p+1](williams-p+1.md) |
| Two ciphertexts, exponents related | [2 ct 2 e 1 n](2-ct-2-e-1-n.md) |
| PKCS#1 v1.5 / partial padding / nonce bits | [PKCS#1 v1.5 HNP](pkcs-1-v1.5-padding-hnp.md) |

## Start

```python
from Crypto.Util.number import long_to_bytes, inverse
from math import gcd

print(gcd(n1, n2))
phi = (p - 1) * (q - 1)
d = inverse(e, phi)
print(long_to_bytes(pow(c, d, n)))
```

## Factor Checks

```python
from math import gcd

for m in moduli:
    g = gcd(n, m)
    if 1 < g < n:
        print(g, n // g)
```

## Recover Modulus From Known Plaintext Encryptions

If the service hides `n` but gives raw RSA ciphertexts for known small messages with the same exponent:

```python
c = pow(m, e, n)
```

then each value `pow(m, e) - c` is a multiple of `n`.

```python
from math import gcd

pairs = [(m1, c1), (m2, c2), (m3, c3)]
g = 0
for m, c in pairs:
    g = gcd(g, pow(m, e) - c)

# Strip accidental small factors if needed.
for p in range(2, 100000):
    while g % p == 0:
        g //= p

n = g
```

## Related Message Same `n`, Same `e`

If two plaintexts differ by a known constant under the same modulus/exponent:

```text
c1 = x^e mod n
c2 = (x + delta)^e mod n
```

use Franklin-Reiter: compute the gcd of both polynomials over `Zmod(n)`.

```python
# Sage
R.<x> = PolynomialRing(Zmod(n))
f1 = x^e - c1
f2 = (x + delta)^e - c2

def monic_gcd(a, b):
    while b:
        a, b = b, a % b
    return a.monic()

g = monic_gcd(f1, f2)
m = int(-g[0])       # if g == x - m
```

Shape from padded oracle:

```text
m1 = secret || known_suffix_1
m2 = secret || known_suffix_2
delta = bytes_to_long(known_suffix_2) - bytes_to_long(known_suffix_1)
```
