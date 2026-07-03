# PRNG

## Pick

| What you see | Go to |
| --- | --- |
| Python `random`, same seed/state needed | [Make same state PRNG](make-same-state-prng.md) |
| Byte-sized or short seed | [Recover seed byte](recover-seed-byte.md) |
| Truncated MT19937 outputs | [Recover MT19937 12-bit](recover-mt19937-12-bit.md) |

## Checks

```text
seed = time?
seed = bytes / username / pid?
output is random.randint or getrandbits?
can we ask many outputs?
is output truncated or modulo reduced?
```

## Brute Seed Shape

```python
import random

target = ...

for seed in range(1 << 24):
    r = random.Random(seed)
    if r.getrandbits(32) == target:
        print(seed)
        break
```
