# Basic Recover a And b

Referensi: LitCTF 2025 dan CSGS 2025

```python
from random import SystemRandom
random = SystemRandom()
from Crypto.Util.number import getPrime
p = getPrime(64)
class LCG:
    def __init__(self, a, b, x):
        self.a = a
        self.b = b
        self.x = x
        self.m = p
    def next(self):
        self.x = (self.a * self.x + self.b) % self.m
        ret = self.x
        return ret

class LCG2:
    def __init__(self, baselcg, n=100):
        self.lcg = baselcg
        for i in range(n):
            a = self.lcg.next()
            b = self.lcg.next()
            x = self.lcg.next()
            self.lcg = LCG(a,b,x)
    def next(self):
        return self.lcg.next()

a = random.randint(1, 2**64)
b = random.randint(1, 2**64)
x = random.randint(1, 2**64)
lcg = LCG(a, b, x)
lcg2 = LCG2(lcg)
print(p)
for x in range(3):
    print(lcg2.next())

from Crypto.Cipher import AES
from Crypto.Util.number import long_to_bytes as l2b
from Crypto.Util.Padding import pad
from os import urandom
r = lcg.next()
k = pad(l2b(r**2), 16)
iv = urandom(16)
cipher = AES.new(k, AES.MODE_CBC, iv=iv)
print(iv.hex())
f = b"testing{135}" #flag redacted
enc = cipher.encrypt(pad(f,16))
print(enc.hex())
```

```python
'''
dari s2 = a*s1 + b, s3 = a*s2 + b →
s3 - s2 = a*(s2 - s1) (mod p)
⇒ a = (s3 - s2) * (s2 - s1)^{-1} (mod p)
(kita cukup kalikan selisih kedua dengan invers modular dari selisih pertama).

lalu b = (s2 - a*s1) (mod p).

seed awal saat LCG dibuat (state sebelum mengeluarkan s1):
x0 = (s1 - b) * a^{-1} (mod p).
'''
def params_from_three(s1, s2, s3, p):
    # Pulihkan a, b, seed_awal dari 3 keluaran berurutan
    denom = (s2 - s1) % p
    if denom == 0:
        raise ValueError("Degenerate triple; cannot invert.")
    a = ((s3 - s2) * pow(denom, -1, p)) % p
    b = (s2 - a * s1) % p
    x0 = ((s1 - b) * pow(a, -1, p)) % p  # seed saat LCG dibuat
    return a, b, x0

def get_3_output_from_start(p, s1, s2, s3, layers=100):
    for _ in range(layers):
        A, B, X = params_from_three(s1,s2,s3,p)

        # (A, B, X) = tiga output berurutan lapis k-1
        s1, s2, s3 = A, B, X

    # Sekarang s1,s2,s3 = (X1, X2, X3) dari LCG awal
    return s1, s2, s3

# tiga output berurutan
s1, s2, s3 = 3681934504574973317, 4155039551524372589, 9036939555423197298
p = 15471456606036645889

x1,x2,x3 = get_3_output_from_start(p, s1,s2,s3, layers=100)
a, b, seed0 = params_from_three(x1,x2,x3,p)

r = (a * x3 + b) % p  # output ke-4 (setelah reseed pertama, inilah yang dipakai)

k = pad(l2b(r**2), 16)
iv = bytes.fromhex("6c9315b13f092fbc49adffbf1c770b54")
cipher = AES.new(k, AES.MODE_CBC, iv=iv)
ct = bytes.fromhex("af9dc7dfd04bdf4b61a1cf5ec6f9537819592e44b4a20c87455d01f67d738c035837915903330b67168ca91147299c422616390dae7be68212e37801b76a74d4")
dec = cipher.decrypt(ct)
print(dec)
```

```python
import os
import struct
from Crypto.Util.number import *
BITS = 56

FLAG = os.getenv("FLAG", "CSCG{TESTFLAG}")

tes = os.urandom(BITS//8)

A = int.from_bytes(tes, "little")
B = int.from_bytes(os.urandom(BITS//8), "little")
SEED = int.from_bytes(os.urandom(BITS//8), "little")

def rng(x, size):
    return (x*A+B) & ((2**size)-1)

def gen_random(seed, bits, mask):
    state = seed
    while True:
        state = rng(state, bits)
        yield state & mask

def main():
    print("Here are some random numbers, now guess the flag")
    rng = gen_random(SEED, BITS, 0xFF)
    for i in range(len(FLAG)):
        print(next(rng) ^ ord(FLAG[i]))

if __name__ == "__main__":
    main()

```

```python
outputs = [
    131, 133, 203, 41, 107, 11, 53, 11, 25, 236, 124, 4, 220, 107, 146, 127,
    121, 204, 156, 100, 59, 75, 242, 95, 217, 44, 44, 71, 135, 171, 85, 171,
    57, 12, 92, 167, 231, 139, 181, 139, 153, 108, 252, 132, 92, 235, 18, 255,
    249, 76, 28, 228, 188, 203, 117, 207, 89, 172, 188, 199, 7, 43, 213, 43,
    185, 140, 204, 39, 103, 11, 53, 15, 25, 236, 124, 4, 219, 107, 149, 107,
    121, 219, 140, 100, 59, 75, 242, 95, 217, 44, 44, 68, 155, 171, 85, 175,
    57, 27, 76, 164, 252, 139, 181, 143, 153, 108, 252, 135, 71, 235, 21, 239,
    249, 76, 28, 228, 187, 203, 117, 207, 89, 187, 172, 196, 27, 43, 213, 43,
    185, 140, 204, 36, 124, 11, 53, 15, 25, 236, 105, 115, 141, 91
]

flag = b"CSCG{"
BITS = 56

from math import gcd

mod = 256
y = [outputs[i] ^ flag[i] for i in range(5)]  # pakai k>=4 agar bisa verifikasi

sol = []
den = (y[1] - y[0]) % mod
if gcd(den, mod) == 1:
    a = ((y[2] - y[1]) * pow(den, -1, mod)) % mod
    b = (y[1] - a*y[0]) % mod
    # verifikasi terhadap lebih banyak titik
    if all((a*y[i] + b) % mod == y[i+1] for i in range(5-1)):
        sol.append((a,b))
else:
    # fallback brute-force
    for a in range(256):
        b = (y[1] - a*y[0]) % mod
        if all((a*y[i] + b) % mod == y[i+1] for i in range(5-1)):
            sol.append((a,b))

# [(43, 150), (171, 150)]
# print(sol) 

a = 43
b = 150

state = (y[0]*a+b)%256
for i in range(2, len(outputs)):
    state = (state*a+b)%256
    print(chr(outputs[i]^state), end="")

```
