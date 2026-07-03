# Affine Cipher

## Challenge Source

### CBC 2025 affine-cipher

```python
import random

chrMap  = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789{_}"

def affine_encrypt(text, key):
    cipher = ""
    for c in text:
        cipher += chrMap[(key[0] * (chrMap.index(c)) + key[1]) % len(chrMap)]
    return cipher

text = open("flag.txt", "r").read().strip()
key = [random.getrandbits(64), random.getrandbits(64)]
cipher = affine_encrypt(text, key)
print(f"cipher = '{cipher}'")
```

## How It Works

`c = (a·p + b) mod m`, decryption: `p = a⁻¹·(c − b) mod m`

- `m` = alphabet size (65 for alphanumeric + `{_}`)
- `a` must satisfy `gcd(a, m) = 1` (invertible)
- For shift-only variant: `a = 1`, brute `b` only

## Solution

Brute-force all valid `(a, b)` pairs and check for known prefix:

```python
import math

def brute_affine(ct, m=65, prefix="CBC{"):
    for a in range(m):
        if math.gcd(a, m) != 1:
            continue
        for b in range(m):
            pt = ''.join(chr((a⁻¹ * (ord(c) - 32 - b)) % m + 32) for c in ct)
            if pt.startswith(prefix):
                return a, b, pt
```
