# ECC

## Pick

| What you see | Go to |
| --- | --- |
| Curve order equals field size | [Smart attack](smart-attack.md) |
| Need recover `a` / `b` from points | [Recover parameter](recover-parameter.md) |
| Same `x,y` lies on two curve forms | [Curve intersection resultant](curve-intersection-resultant.md) |
| Discrete log split over factors | [ECDLP + CRT](ecdlp-+-crt.md) |
| ECDSA repeated nonce | [ECDSA nonce reuse](ecdsa/nonce-reuse.md) |
| ECDSA partial nonce bits | [ECDSA HNP](ecdsa/hnp-recover-d.md) |

## Sage Setup

```python
from sage.all import *

F = GF(p)
E = EllipticCurve(F, [a, b])
G = E(Gx, Gy)
P = E(Px, Py)
```

## Checks

```python
print(E.order())
print(factor(E.order()))
print(P in E)
print(G.discrete_log(P))
```
