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
