# Chacha 20

Referensi: Crypto ByuCTF 2025 [https://github.com/BYU-CSA/BYUCTF-2025/tree/main/crypto](https://github.com/BYU-CSA/BYUCTF-2025/tree/main/crypto)

```python
#!/usr/local/bin/python

from Crypto.Cipher import ChaCha20
from Crypto.Random import get_random_bytes
from secrets import FLAG

key = get_random_bytes(32)
nonce = get_random_bytes(8)

cipher = ChaCha20.new(key=key, nonce=nonce)
print(bytes.hex(cipher.encrypt(b'Slide to the left')))
print(bytes.hex(cipher.encrypt(b'Slide to the right')))

try:
    user_in = input().rstrip('\n')
    cipher = ChaCha20.new(key=key, nonce=nonce)
    decrypted = cipher.decrypt(bytes.fromhex(user_in))
    if decrypted == b'Criss cross, criss cross':
        print("Cha cha real smooth")
        print(FLAG)
    else:
        print("Those aren't the words!")
except Exception as e:
    print("Those aren't the words!")
```

```python
from pwn import remote

# 1) connect
host, port = "smooth.chal.cyberjousting.com", 1350
conn = remote(host, port)

# 2) read the two ciphertext lines
ct1_hex = conn.recvline().strip().decode()
ct2_hex = conn.recvline().strip().decode()

ct1 = bytes.fromhex(ct1_hex)
ct2 = bytes.fromhex(ct2_hex)

# 3) known plaintexts
pt1 = b"Slide to the left"
pt2 = b"Slide to the right"

# sanity check lengths
assert len(ct1) == len(pt1)
assert len(ct2) == len(pt2)

'''
pt1 -> 16 bytes
jadi keynya 0-16

pt2 -> 17 bytes
jadi key 17-35

bgt seterusnya yang bisa digabung membentuk keseluruhan key
'''
# 4) recover keystream bytes
ks1 = bytes(c ^ p for c, p in zip(ct1, pt1))
ks2 = bytes(c ^ p for c, p in zip(ct2, pt2))
keystream = ks1 + ks2

# 5) craft our target plaintext
target = b"Criss cross, criss cross"
assert len(target) <= len(keystream)

# 6) XOR against keystream to get our ciphertext
payload = bytes(t ^ k for t, k in zip(target, keystream))

# 7) send and get the flag
conn.sendline(payload.hex())
print(conn.recvall().decode())

```
