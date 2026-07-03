# Padding Oracle

referensi: midnight ctf

```python
from Crypto.Cipher import AES
from Crypto.Util import Counter
from Crypto.Util.Padding import pad, unpad
from Crypto.Util.number import bytes_to_long
import os

class CTR:
    def __init__(self):
        self.key = os.urandom(16)

    def encrypt(self, pt):
        iv = os.urandom(16)
        ctr = Counter.new(128, initial_value=bytes_to_long(iv))
        cipher = AES.new(self.key, AES.MODE_CTR, counter=ctr)
        enc = iv + cipher.encrypt(pad(pt, 16))
        return enc

    def decrypt(self, ct):
        try:
            ctr = Counter.new(128, initial_value=bytes_to_long(ct[:16]))
            cipher = AES.new(self.key, AES.MODE_CTR, counter=ctr)
            dec = unpad(cipher.decrypt(ct[16:]), 16)
            return dec
        except Exception:
            # print("tes")
            return False

if __name__ == "__main__":
    cipher = CTR()
    flag = os.getenv('FLAG', 'MCTF{ThisIsAFakeFlag}').encode()
    ct = cipher.encrypt(flag)

    print(f"CTR(flag)={ct.hex()}")
    while 1:
        enc = bytes.fromhex(input("enc="))
        dec = cipher.decrypt(enc)

        if bool(dec) or dec == flag:
            print('Look\'s good')
        else:
            print('Hum,this is a weird input')


```

```python
from pwn import *
from tqdm import *
from Crypto.Util.Padding import *
from Crypto.Util.number import *

# r = remote('chall2.midnightflag.fr', 14524)

script_path = os.path.join(os.path.dirname(__file__), 'SOAL - 2.py')
r = process(['python', script_path])

shit = bytes.fromhex(r.recvline().decode().strip().split('=')[1])
iv = shit[:16]

def oracle(ct):
    r.sendline(iv.hex() + ct.hex())
    resp = r.recvline().decode().strip()
    if 'good' in resp:
        return True
    else:
        return False

flag = b''
nblocks = len(shit) // 16  - 1
for n in range(nblocks):
    keystream = bytearray(bytes(16))
    block = bytearray(bytes(16))
    for i in range(15, -1, -1):
        for x in tqdm(range(257)):
            if x == 256:
                print('ohno')
                break
            keystream[i] = x
            if oracle(b'\x00'*16*n + keystream):
                block[i] = x ^ (16-i)
                for j in range(i, 16):
                    keystream[j] = block[j] ^ (16 - i + 1)
                break
    flag += xor(shit, block)[16*(n+1):16*(n+2)]

print(flag)
```
