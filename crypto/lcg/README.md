# LCG

## Pick

| What you see | Go to |
| --- | --- |
| Need recover `a`, `b` with known modulus | [Basic recover a and b](basic-recover-a-and-b.md) |
| Modulus unknown | [Recover n](recover-n.md) |
| Multiple small unknowns / Coppersmith shape | [Coppersmith multivariate](coppersmith-multivariate.md) |

## Formula

```text
x[i+1] = (a*x[i] + b) mod n
```

## Known Modulus

```python
a = ((x2 - x1) * pow(x1 - x0, -1, n)) % n
b = (x1 - a*x0) % n
```
