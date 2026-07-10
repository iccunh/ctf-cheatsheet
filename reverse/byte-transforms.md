# Byte Transforms

Use this after the decompiler shows a target array and a byte transform. Rebuild the forward check first, then invert.

## Helpers

```python
def u8(x):
    return x & 0xff

def rol8(x, r):
    r &= 7
    return u8((x << r) | (x >> (8 - r)))

def ror8(x, r):
    r &= 7
    return u8((x >> r) | (x << (8 - r)))

def rol32(x, r):
    r &= 31
    return ((x << r) | (x >> (32 - r))) & 0xffffffff

def ror32(x, r):
    r &= 31
    return ((x >> r) | (x << (32 - r))) & 0xffffffff
```

## Parse C Arrays

```python
import re

s = """
0x66, 0x6c, 0x61, 0x67, 123, 0x7d
"""

arr = [int(x, 0) for x in re.findall(r"0x[0-9a-fA-F]+|\d+", s)]
print(bytes(arr))
```

## Repeating XOR / ADD

```python
target = bytes.fromhex("12 34 56")
key = b"key"

plain = bytes(c ^ key[i % len(key)] for i, c in enumerate(target))
plain = bytes((c - key[i % len(key)]) & 0xff for i, c in enumerate(target))
plain = bytes((c + key[i % len(key)]) & 0xff for i, c in enumerate(target))
```

## Rotate / XOR / ADD Chain

Forward:

```python
y = rol8((x ^ key[i % len(key)]) + 7, 3)
```

Inverse:

```python
x = (ror8(y, 3) - 7) & 0xff
x ^= key[i % len(key)]
```

Invert operations in reverse order.

## Prefix XOR / Sum

Forward:

```python
y[i] = x[0] ^ x[1] ^ ... ^ x[i]
```

Inverse:

```python
x = [y[0]]
for i in range(1, len(y)):
    x.append(y[i] ^ y[i - 1])
```

Forward:

```python
y[i] = sum(x[:i+1]) & 0xff
```

Inverse:

```python
x = [y[0]]
for i in range(1, len(y)):
    x.append((y[i] - y[i - 1]) & 0xff)
```

## Permutation

If:

```python
y[i] = x[perm[i]]
```

Then:

```python
x = [0] * len(y)
for i, p in enumerate(perm):
    x[p] = y[i]
```

If:

```python
y[perm[i]] = x[i]
```

Then:

```python
x = [0] * len(y)
for i, p in enumerate(perm):
    x[i] = y[p]
```

## S-Box

```python
sbox = [...]
inv = {v: i for i, v in enumerate(sbox)}
plain = bytes(inv[c] for c in target)
```

If duplicate values exist, it is not a true inverse. Use brute force per byte:

```python
plain = []
for c in target:
    plain.append(next(i for i in range(256) if sbox[i] == c))
```

## Pairwise Chain

Forward:

```python
y[0] = x[0] ^ 0x42
for i in range(1, n):
    y[i] = x[i] ^ y[i - 1]
```

Inverse:

```python
x = [y[0] ^ 0x42]
for i in range(1, len(y)):
    x.append(y[i] ^ y[i - 1])
```

## Modular Multiply

Only odd constants have an inverse modulo 256.

```python
plain = bytes((c * pow(k, -1, 256)) & 0xff for c in target)
```

For 32-bit:

```python
plain = [(c * pow(k, -1, 2**32)) & 0xffffffff for c in target]
```

## Verify

Always keep a forward checker:

```python
def check(inp):
    out = []
    for i, x in enumerate(inp):
        out.append(rol8((x ^ key[i % len(key)]) + 7, 3))
    return bytes(out)

assert check(plain) == target
print(plain)
```
