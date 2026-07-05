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

## Python `random.getrandbits(k)` Partial MT Output

For `k <= 32`, Python returns the high `k` bits of one MT19937 32-bit output:

```python
import random

r = random.Random(123)
a = r.getrandbits(11)

r = random.Random(123)
b = r.getrandbits(32)

assert a == (b >> 21)   # high bits, not low bits
```

If a challenge leaks only `getrandbits(11)`, submit known bits as:

```text
known_11_bits + "?" * 21
```

not:

```text
"?" * 21 + known_11_bits
```

Common indirect leak:

```python
k = random.getrandbits(11)
x = random.getrandbits(k) | (1 << k)
leaked_k = x.bit_length() - 1
```

After 624 partial outputs, use a symbolic MT untwister/Z3 model to recover state, then predict later `getrandbits()` values.

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
