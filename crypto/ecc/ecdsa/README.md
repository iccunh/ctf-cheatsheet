# ECDSA

## Pick

| What you see | Go to |
| --- | --- |
| Same `r` in two signatures | [Nonce reuse](nonce-reuse.md) |
| Partial nonce bits / biased nonce | [HNP recover d](hnp-recover-d.md) |

## Formula

```text
s = k^-1 * (h + r*d) mod n
d = (s*k - h) * r^-1 mod n
```
