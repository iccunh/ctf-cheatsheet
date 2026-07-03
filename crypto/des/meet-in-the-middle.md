# Double DES - Meet in the Middle

## Challenge Source

### CBC 2025 desdes

```python
from Crypto.Cipher import DES
import binascii
import random
import string

def pad(msg):
    block_len = 8
    over = len(msg) % block_len
    pad = block_len - over
    return (msg + " " * pad).encode()

def encrypt(m, key):
    des1 = DES.new(pad(key[:6]), DES.MODE_ECB)
    des2 = DES.new(pad(key[-6:]), DES.MODE_ECB)
    cipher = des2.encrypt(des1.encrypt(pad(m)))
    return binascii.hexlify(cipher).decode()

key = "".join(random.choice(string.digits) for _ in range(16))
flag = "Here's your flag: CBC{14300a868d7805ae1b6e9b16c953d931}"
cipher = encrypt(flag, key)
print(f"cipher = '{cipher}'")
```

## How It Works

`C = DES_{k2}(DES_{k1}(P))` with two independent keys k1, k2. Meet-in-the-middle reduces complexity from `2^(2n)` to `2^n + 2^n`.

1. Build a lookup table of intermediate values after first encryption for all possible k1
2. For each k2, decrypt the ciphertext and check if the result is in the table
3. A match reveals both keys

## Solution

```python
from Crypto.Cipher import DES

# 6-digit decimal DES keys
def encrypt(k1, pt):
    return DES.new(str(k1).zfill(6).encode(), DES.MODE_ECB).encrypt(pt)

def decrypt(k2, ct):
    return DES.new(str(k2).zfill(6).encode(), DES.MODE_ECB).decrypt(ct)

table = {}
for k1 in range(10**6):
    table[encrypt(k1, P)] = k1

for k2 in range(10**6):
    mid = decrypt(k2, C)
    if mid in table:
        print(f"k1={table[mid]}, k2={k2}")
        break
```
