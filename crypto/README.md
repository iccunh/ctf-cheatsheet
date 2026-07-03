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
```

## Tools

```bash
sage solve.sage
sage -python solve.py
python -m pip install pycryptodome gmpy2 sympy z3-solver ortools
```
