# RSA Broadcast Attack

## Challenge Sources

### CBC 2025 broadcast-message

```python
from Crypto.Util.number import bytes_to_long, long_to_bytes, getPrime

def genKey():
    p = getPrime(512)
    q = getPrime(512)
    return p * q

flag = open("flag.txt", "rb").read().strip()

N = genKey()
e1 = 65537
e2 = 61543
e3 = 56383

c1 = pow(bytes_to_long(flag), e1, N)
c2 = pow(bytes_to_long(flag), e2, N)
c3 = pow(bytes_to_long(flag), e3, N)

print(f"c1 = {c1}\nc2 = {c2}\nc3 = {c3}")
print(f"e1 = {e1}\ne2 = {e2}\ne3 = {e3}")
print(f"N = {N}")
```

### CBC 2025 i-wanna-cry

```python
from Crypto.PublicKey import RSA
from secret import FLAG, E

bits = 1024
count = 3
m = int.from_bytes(FLAG, "big")

while True:
    keys = [RSA.generate(bits, e=E) for _ in range(count)]
    if m**E < math.prod([k.n for k in keys]):
        break

ns = [k.n for k in keys]
cs = [pow(m, E, n) for n in ns]
```

## Solution

### Variant 1: Same N, multiple e (gcd(e1,e2)=1)

Extended GCD gives `a*e1 + b*e2 = 1`, then `m = c1^a * c2^b mod N`.

```python
def egcd(a, b):
    if b == 0: return a, 1, 0
    g, x1, y1 = egcd(b, a % b)
    return g, y1, x1 - (a // b) * y1

_, a, b = egcd(e1, e2)
m = (pow(c1, a, n) * pow(c2, b, n)) % n
```

### Variant 2: Hastad - same e (small), different N, same m

Use CRT to combine, then e-th root.

```python
import gmpy2
from functools import reduce

def crt(residues, moduli):
    M = reduce(lambda x, y: x * y, moduli)
    x = 0
    for r, m in zip(residues, moduli):
        Mi = M // m
        x = (x + r * Mi * gmpy2.invert(Mi, m)) % M
    return x

m_e = crt([c1, c2, c3], [n1, n2, n3])
m = int(gmpy2.iroot(m_e, e)[0])
```
