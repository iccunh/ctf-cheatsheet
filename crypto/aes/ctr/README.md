# CTR

## Pick

| What you see | Go to |
| --- | --- |
| Same nonce/key used twice | [Keystream reuse](keystream-reuse.md) |
| Oracle leaks validity/content | [Padding oracle](padding-oracle.md) |

## Keystream

```python
from pwn import xor

ks = xor(known_pt, known_ct)
pt = xor(ct, ks)
```
