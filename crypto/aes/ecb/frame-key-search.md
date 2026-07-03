# Frame Key Search

Use when each encrypted frame has a tiny keyspace and adjacent plaintext frames are correlated.

```python
import numpy as np
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2

HEX = "0123456789abcdef"
KEYS = {ch: PBKDF2(ch, b"salt", dkLen=16, count=1000) for ch in HEX}

def dec_frame(hexdata, key, h, w):
    pt = AES.new(key, AES.MODE_ECB).decrypt(bytes.fromhex(hexdata))
    return np.frombuffer(pt, dtype=np.uint8).reshape(h, w)

def score(prev, cur):
    same = (cur == prev).sum()
    shifted = (cur == np.roll(prev, shift=(-1, -1), axis=(0, 1))).sum()
    return max(same, shifted)

cands = [[dec_frame(enc[i], KEYS[ch], height, width) for ch in HEX] for i in range(len(enc))]

best = np.zeros((len(enc), 16), dtype=np.int64)
bt = -np.ones((len(enc), 16), dtype=np.int16)

for i in range(1, len(enc)):
    for k in range(16):
        vals = [best[i - 1, j] + score(cands[i - 1][j], cands[i][k]) for j in range(16)]
        bt[i, k] = int(np.argmax(vals))
        best[i, k] = vals[bt[i, k]]

k = int(np.argmax(best[-1]))
path = [k]
for i in range(len(enc) - 1, 0, -1):
    k = int(bt[i, k])
    path.append(k)
path = path[::-1]
print("".join(HEX[i] for i in path))
```

