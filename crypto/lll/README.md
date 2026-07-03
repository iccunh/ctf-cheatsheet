# LLL

## Pick

| What you see | Go to |
| --- | --- |
| Small unknown hidden in linear/modular equation | [Basic small](basic-small.md) |
| ML-KEM / Kyber error equations leak | [ML-KEM error leak](ml-kem-error-leak.md) |
| Older lattice note / generic basis | [Page 1](page-1.md) |

## When

```text
x is small
a*x + b == 0 mod n
known high bits / low bits
many approximate equations
nonce has partial known bits
```

## Sage Skeleton

```python
from sage.all import *

M = Matrix(ZZ, [
    [1, 0, 123],
    [0, 1, 456],
    [0, 0, 789],
])

for row in M.LLL():
    print(row)
```
