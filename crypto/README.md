# Crypto

## Start

1. Identify the primitive: RSA, AES, ECC, PRNG, lattice, hash/MAC, classical.
2. Write down exactly what is given: public params, ciphertexts, oracle, leaks.
3. Check for reuse: nonce, IV, key, seed, `r`, keystream, modulus.
4. Check size: tiny exponent, small unknowns, short seed, small keyspace.
5. If equations appear, move to Sage/LLL early.

## Pick

| What you see | Go to |
| --- | --- |
| `n, e, c`, weird RSA parameters | [RSA](rsa/README.md) |
| AES mode, IV/nonce/oracle/block behavior | [AES](aes/README.md) |
| Elliptic curve points, ECDSA, curve params | [ECC](ecc/README.md) |
| Small unknowns in modular equations | [LLL](lll/README.md) |
| Polynomial/resultant/finite field math | [Sage](sage.md) |
| `random`, seed, MT19937, byte seed | [PRNG](prng/README.md) |
| Linear congruential generator outputs | [LCG](lcg/README.md) |
| Subset sum / weighted byte sum | [Knapsack](knapsack.md) |
| CRC / custom checksum | [CRC](crc.md) |
| Hash length extension / MAC weirdness | [Hash](hash/README.md) |
| Paillier encrypted arithmetic | [Paillier](paillier/README.md) |
| ZKP transcript leak | [ZKP](zkp/README.md) |
| Caesar/Affine/Hill/Polybius | [Classical](classical/README.md) |

## Common Checks

```text
RSA: gcd(n1,n2), small e, many primes, leaked d mod p-1, p+-1 smooth
AES-CBC: padding oracle, bit flip, fixed IV, CBC-MAC misuse
AES-CTR/OFB/stream: nonce reuse, known plaintext, keystream recovery
AES-ECB: repeated blocks, byte oracle, tiny key search
ECC: singular/anomalous curve, bad params, reused ECDSA nonce
LLL: hidden small value, approximate equation, partial nonce/key bits
PRNG: seed time, small seed, cloned state, truncated outputs
Hash/MAC: length extension, raw hash as MAC, CRC linearity
Classical/custom: flag prefix crib, frequency, invert byte transforms
```

## Attack Matrix

| What you see | First attack |
| --- | --- |
| Many RSA moduli | Pairwise `gcd(n_i, n_j)`. |
| Small RSA `e`, same message | CRT broadcast, integer e-th root. |
| Small RSA `e`, no padding, `m^e < n` | Integer e-th root of `c`. |
| Close RSA primes | Fermat factorization. |
| Smooth `p-1` or `p+1` hint | Pollard p-1 / Williams p+1. |
| Leaked `dp`, `dq`, `d mod p-1` | Recover prime from exponent relation. |
| Partial bits of prime/message/nonce | Coppersmith / LLL. |
| AES-ECB repeated blocks | ECB detection, byte oracle, block cut-paste. |
| CBC decrypt/encrypt oracle | Padding oracle or bit flip. |
| CTR/OFB reused nonce | XOR ciphertexts, recover keystream from known plaintext. |
| GCM nonce reuse | Recover auth key/tag relation. |
| ECDSA same `r` | Recover nonce and private key. |
| ECDSA biased/partial nonce | HNP lattice. |
| Python `random` | Time seed, small seed, MT state recovery. |
| LCG outputs | Recover `a`, `b`, maybe modulus `m`. |
| Hash prefix MAC | Length extension. |
| CRC/checksum | Linear algebra or brute force suffix. |

## Snippets

```python
from functools import reduce
from math import gcd
from Crypto.Util.number import long_to_bytes, inverse

def xor(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))

def chunks(data: bytes, size: int = 16):
    return [data[i:i + size] for i in range(0, len(data), size)]

def ecb_score(ct: bytes, size: int = 16) -> int:
    bs = chunks(ct, size)
    return len(bs) - len(set(bs))

def iroot(n: int, e: int):
    lo, hi = 0, 1 << ((n.bit_length() + e - 1) // e)
    while lo <= hi:
        mid = (lo + hi) // 2
        p = mid ** e
        if p == n:
            return mid, True
        if p < n:
            lo = mid + 1
        else:
            hi = mid - 1
    return hi, False

def crt(residues, moduli):
    n = reduce(lambda a, b: a * b, moduli, 1)
    out = 0
    for ai, ni in zip(residues, moduli):
        mi = n // ni
        out += ai * mi * inverse(mi, ni)
    return out % n

def shared_factors(ns):
    for i, ni in enumerate(ns):
        for j, nj in enumerate(ns[:i]):
            g = gcd(ni, nj)
            if 1 < g < ni:
                print("shared", i, j, g)

def ecdsa_repeated_nonce(q, r, s1, h1, s2, h2):
    k = ((h1 - h2) * inverse((s1 - s2) % q, q)) % q
    d = ((s1 * k - h1) * inverse(r, q)) % q
    return k, d

def recover_lcg_ab(x0, x1, x2, m):
    a = ((x2 - x1) * inverse((x1 - x0) % m, m)) % m
    b = (x1 - a * x0) % m
    return a, b
```

## Tools

```bash
sage solve.sage
sage -python solve.py
python -m pip install pycryptodome gmpy2 sympy z3-solver ortools
```
