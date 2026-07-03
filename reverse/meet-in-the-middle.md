# Meet In The Middle

Use when brute force is split into two independent halves and the transform is reversible.

## Shape

```text
state0 --left choices--> middle == middle <--reverse right choices-- target
```

Good signs:

* Final state is known.
* Each step can be inverted.
* Keyspace is too big as `2^n`, but `2^(n/2)` is fine.
* State can be stored as an int/tuple/bytes key.

## Generic Template

```python
from itertools import product

INIT = ...
TARGET = ...
N = 32
SPLIT = N // 2
ALPHABET = [0, 1]


def step(state, pos, choice):
    # forward transform for one choice
    return state


def unstep(state, pos, choice):
    # inverse of step()
    return state


def encode(choices):
    return "".join(map(str, choices))


mid = {}

for left in product(ALPHABET, repeat=SPLIT):
    s = INIT
    for pos, choice in enumerate(left):
        s = step(s, pos, choice)
    mid[s] = left

for right in product(ALPHABET, repeat=N - SPLIT):
    s = TARGET
    for pos in range(N - 1, SPLIT - 1, -1):
        choice = right[pos - SPLIT]
        s = unstep(s, pos, choice)

    if s in mid:
        ans = mid[s] + right
        print(encode(ans))
        break
```

## 64-Bit Helpers

```python
MASK = (1 << 64) - 1

def rol64(x, r):
    return ((x << r) | (x >> (64 - r))) & MASK

def ror64(x, r):
    return ((x >> r) | (x << (64 - r))) & MASK
```

## Notes

* If multiple paths reach the same middle state, store a list: `mid.setdefault(s, []).append(left)`.
* If state is bytes/list, convert it to immutable `bytes` or `tuple` before using as a dict key.
* Verify `unstep(step(s, i, c), i, c) == s` before running the full search.
