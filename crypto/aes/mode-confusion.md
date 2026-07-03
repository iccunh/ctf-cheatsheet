# Mode Confusion

## OFB Known Plaintext

OFB encryption is `ct = pt ^ stream`. If a service encrypts known plaintext with OFB, recover stream bytes.

```python
def xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

known_pt = hashlib.sha256(b"\xff").digest()
known_ct = bytes.fromhex("...")

stream = xor(known_ct, known_pt)
```

## OFB + CBC + ECB Confusion

Pattern:

```python
IV = os.urandom(16)
KEY = os.urandom(16)

AES.new(IV, AES.MODE_ECB).encrypt(flag)
AES.new(KEY, AES.MODE_OFB, IV).encrypt(known)
AES.new(KEY, AES.MODE_CBC, user_iv).decrypt(user_ct)
```

OFB known plaintext gives first stream block:

```python
stream0 = xor(ofb_ct[:16], known_pt[:16])  # AES_KEY(IV)
```

If CBC decrypt accepts chosen ciphertext/IV, use it to turn `AES_KEY(IV)` into `IV`, then decrypt the flag encrypted under `AES-ECB(key=IV)`.

```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import hashlib

known_pt = hashlib.sha256(b"\xff").digest()
stream0 = xor(ofb_ct[:16], known_pt[:16])

# challenge-specific oracle shape
iv = cbc_decrypt_oracle(stream0, b"\x00" * 16)[:16]

flag = unpad(AES.new(iv, AES.MODE_ECB).decrypt(enc_flag), 16)
print(flag)
```

