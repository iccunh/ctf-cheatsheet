# Keystream Reuse

Referensi: CSGS 2025

```python
#!/usr/bin/env pypy3

import os
from pydoc import plain
from sys import byteorder
from Crypto.Cipher import AES
from Crypto.Util import Counter
import hashlib

# Create a secret.py file with a variable `FLAG` for local testing :)
from secret import FLAG

secret_key = os.urandom(16)

def encrypt(plaintext, counter):
    m = hashlib.sha256()
    m.update(counter.to_bytes(8, byteorder="big"))

    alg = AES.new(secret_key, AES.MODE_CTR, nonce=m.digest()[0:8])
    ciphertext = alg.encrypt(plaintext)

    return ciphertext.hex()


def main():
    print("DES is broken, long live the secure AES encryption!")
    print("Give me a plaintext and I'll encrypt it a few times for you. For more security of course!")

    try:
        plaintext = bytes.fromhex(input("Enter some plaintext (hex): "))
    except ValueError:
        print("Please enter a hex string next time.")
        exit(0)
    
    for i in range(0, 255):
        print(f"Ciphertext {i:03d}: {encrypt(plaintext, i)}")
    
    print("Flag:", encrypt(FLAG.encode("ascii"), int.from_bytes(os.urandom(1), byteorder="big")))

if __name__ == "__main__":
    main()

```

```python
import re
import sys
from pwn import *

context.log_level = "debug"
ZERO_LEN = 256  # perkirakan > panjang FLAG

def xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def pick_candidates(pt):
    s = pt.decode()
    # flag di sini
    return any(tag in s for tag in ["testing{"])

def solve(io):
    # baca sampai prompt input
    io.recvuntil(b"Enter some plaintext (hex): ")
    zero_hex = b"00" * ZERO_LEN
    io.sendline(zero_hex)

    # tampung semua line output
    data = io.recvall(timeout=2).decode(errors="ignore")

    # parse ciphertexts i=000..254
    ct_map = {}
    for m in re.finditer(r"Ciphertext\s+(\d{3}):\s*([0-9a-fA-F]+)", data):
        idx = int(m.group(1))
        ct_map[idx] = bytes.fromhex(m.group(2))

    # parse flag ciphertext
    mflag = re.search(r"Flag:\s*([0-9a-fA-F]+)", data)
    if not mflag:
        print("Tidak menemukan baris Flag.")
        sys.exit(1)

    ct_flag = bytes.fromhex(mflag.group(1))

    if not ct_map:
        print("Tidak ada ciphertext i yang diparse. Coba tingkatkan timeout/regex.")
        sys.exit(1)

    # keystream untuk plaintext nol = ciphertext (dipotong sepanjang flag)
    candidates = []
    for i in sorted(ct_map):
        ks_i = ct_map[i][:len(ct_flag)]
        pt_i = xor(ct_flag, ks_i)
        if pick_candidates(pt_i):
            candidates.append((i, pt_i))

    if candidates:
        for i, pt in candidates:
            print(f"[HIT] counter={i:03d}  plaintext≈ {pt!r}")
        best = max(candidates, key=lambda t: sum(32 <= c <= 126 for c in t[1]))
        try:
            print("\nDekripsi (teks):", best[1].decode())
        except:
            print("\nDekripsi (repr):", best[1])
    else:
        print("Tidak ada kandidat yang kelihatan wajar. Mungkin counter flag = 255 (kasus edge).")

if __name__ == "__main__":
    script_path = os.path.join(os.path.dirname(__file__), 'crypto.py')
    io = process(['python', script_path])
    solve(io)

```

Referensi: CBC 2025 aes-000

```python
from Crypto.Cipher import AES
from Crypto.Util import Counter
import os
import random
key = os.urandom(16)

def encrypt(msg):
    cipher = AES.new(key, AES.MODE_CTR, counter=Counter.new(128))
    return cipher.encrypt(msg).hex()

flag = open("flag.txt", "rb").read()
txt = open("hamlet soliloquy.txt", "rb").read().splitlines()

enc = [encrypt(flag)]
for line in txt:
    enc.append(encrypt(line))
random.shuffle(enc)

print("enc =", enc)

```

```python
from pwn import *

enc = ['587e2affe80490a2e50d518f41472fabe5a23daf24defdfa8710a55e044a4630c7cf9a9f59647ea207f4af3c7563', '4a793dffe90fd1a4f94144cc5a4e6aaffbe672bd6cdfb8ef9b17f05a0d455630cddc8b8b467632ef15e5e03c717d42fe', '4e633bfff40990a4b154588909467dafeaa23db42a9baee1821aa4450c4a4530c8c89a8f592576e715e8a873', '45656face9029abcf84554cc46056ab8abb174af249ba9e68a5fa04c09410273c8dd9aca446332f61cf3b53876640b', '5b7f3bb7a000d1b2f05255cc4b4d6ba1e2a822fb1bd3b2ae9810a54101044471dbca8b86582570e715eeec', '42796fb2ef1394ebb1415e88094076eaeae66eb729deadae9b10f05e045d0267cc8e8b844f', '587e2afff30d98bef653108d47462fabf9b472ac3f9bb2e8cf10a55917454575c6db9dca4d6a60f601f2a573', '4f540ca4b556c6e4a81304dd48446eaebef524ec7f82ecbbda1ab21f531414739b9793', '41633caba00698a6f400459f09526ebff8a3ff5bd8cfb5eb9d1af75e45504a7589dc8b995b6071f6', '487339b0f5159da9b1545fcc4b472fbde2b575fc2895fdda805fb44400080264c68e9d864e6062b9', '587e2eb1a0079da9b1545fcc465667aff9b53daf24daa9ae981af0460b4b5530c7c19aca44632d', '5b7f3bb7a01599b9e20042894e437daeabb275be25c9fded9a0da2480b505130dddb9c840b6465f00d', '58796fbde54dd1bfe3005e835d027ba5aba478f76ccfb5ef9b5fb95e45504a7589df9b8f58717bed1aa6', '5b7e2ab1a01694f0f9414689095167bfeda071be289bb2e8895fa4450c57027dc6dc9a8b472571ed1df0ec', '42796fabf20087b5fd4c559e09506abefeb473a8609badfb9505bc4816045678cc8e998347693e', '4d782bfff40984a3b1545889094c6ebee2b078fb24ceb8ae8019f05f00574d7cdcda878545', '587e3aaca0029ebee243598947416aeaefa969b36cd6bce58a5fb34212455074da8e818c0b7061a215f0ac73', '4d782bffe50f85b5e35042855a477ceae4a03dbc3edebcfacf0fb9590d04437ecd8e838546607cf6', '4d782bffe218d1bfe1505f9f404c68eaeea879fb38d3b8e3c15f844245404b754b2e7a9e442561ee11f9b073', '5b7e2aabe80483f0b654599f094c60a8e7a36ffb25d5fdfa871af0400c4a4630ddc1ce995e6374e706', '4a793dfff7099ef0e64f45804d026dafeab43daf24defdf98716a05e45454c7489dd8d85596b61a21bfae02b777d42fe', '43646fabef4185b1fa45108d5b4f7ceaeaa17cb222c8a9ae8e5fa34804044d7689da9c855e677ee707', '587e2affe90f82bffd455e8f4c0260acaba97bbd25d8b8a2cf1ebe4945504a7589dd9e9f596b61', '587e2afff0009fb7e2005f8a094666b9fbb474a16bdffde28009b50145504a7589c28f9d0c7632e611f0a12632', '58796facec0494a0bd0040895b4167abe5a578fb38d4fdea9d1ab14087a4b671d082ce9e436060e753efe02b767507a0bb641a', '4d782bffed009ab5e200459f09506ebee3a36ffb2edebcfccf0bb84216410279c5c29dca5c6032ea15eaa5', '587e68b0f01183b5e2535f9e0e512fbdf9a973bc609ba9e68a5fa05f0a514630c4cf80cd582571ed1ae8b5327b7c5efe', '587e2eaba00c90bbf453108f484e6ea7e2b264fb23ddfdfd805fbc420b43027cc0c88bc4', '5b7e2ab1a00994f0f9495d9f4c4e69eae6af7ab3389bb5e79c5fa1580c415665da8e838b4060', '58796fb8f2149fa4b1415e88095178afeab23dae22dfb8fccf1ef05a0045506989c2878c4e29', '587e2afff50f95b9e2435f9a4c506aedefe67eb439d5a9fc9653f04b174b4f30dec681994e2570ed01eeae', '4d782bffec0e82b5b1545889094c6ea7eee672bd6cdabefa8610be03', '587e2eaba01190a4f8455e98094f6ab8e2b23db42a9ba9e6c80abe5a0a565678d08e9a8b406061ae', '587e2eaba0079db5e24810855a0267afe2b43daf2381fda99b16a30d0404417fc7dd9b87466466eb1bf2']
enc = [bytes.fromhex(e) for e in enc]

# txt = open("./src/hamlet soliloquy.txt", "rb").read().splitlines()

# Solution one
# for i in range(len(enc)):
#     for j in range(4):
#         key = xor(enc[i][:4], b'CBC{')
#         pt = xor(key, enc[j][:4])
#         print(pt)

#     print(i)
#     print()

# flag_enc = enc[7]
# for i in range(len(enc)):
#     for j in range(len(txt)):
#         key = xor(enc[i], txt[j])
#         pt = xor(key, flag_enc)
#         if b'CBC{' in pt and b'}' in pt:
#             print(pt)

# Solution two
# for i in range(len(enc)):
#     for j in range(len(txt)):
#         for k in range(len(enc)):
#             key = xor(enc[i], txt[j])
#             pt = xor(key, enc[k])
#             if b'CBC{' in pt and b'}' in pt:
#                 print(pt)

# Sadly hamlet soliloquy.txt not provided in dist so we need find another way

for i in range(len(enc)):
    for j in range(4):
        key = xor(enc[i][:4], b'CBC{')
        pt = xor(key, enc[j][:4])
        print(j)
        print(pt)

    print(i)
    print()

# Since we can recover first 4 bytes and we can search for halmet soliloquy.txt in google,
# so we can know the plaintext
# 0
# b'The '
# 1
# b'For '
# 2
# b'But '
# 3
# b'Is s'
# Is sicklied o'er with the pale cast of thought,

flag_enc = enc[7]
key = xor(enc[3], b'Is sicklied o\'er with the pale cast of thought,')
pt = xor(key, flag_enc)
print(pt)

```

### Explaination

```
CTR:    c = p ⊕ ks          (ks = AES(key, counter) || AES(key, counter+1) || ...)

Two msgs, same ks:
  c1 = p1 ^ ks
  c2 = p2 ^ ks

  c1 ^ c2 = (p1 ^ ks) ^ (p2 ^ ks)
          = p1 ^ p2 ^ (ks ^ ks)
          = p1 ^ p2 <- ks cancels out!
```

#### Known-plaintext recovery

If you know `p2`, you get `p1`:

```
p1 = c1 ^ c2 ^ p2
```

Or recover the keystream first, then decrypt anything:

```
ks = c2 ^ p2
p1 = c1 ^ ks
```

#### In practice

```python
def xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

ks = xor(enc[known_idx], known_plaintext)

flag = xor(enc[flag_idx], ks)
flag = xor(enc[flag_idx], xor(enc[known_idx], known_plaintext))
```
