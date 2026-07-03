# Custom decrypt

referensi: utflag 2025

```python
#!/usr/bin/env python3

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
key = open("/src/key", "rb").read()
secret = open("/src/flag.txt", "r").read()
cipher = AES.new(key, AES.MODE_ECB)

while 1:
    print('Enter text to be encrypted: ', end='')
    x = input()
    chksum = sum(ord(c) for c in x) % (len(x)+1)
    pt = x[:chksum] + secret + x[chksum:]
    ct = cipher.encrypt(pad(pt.encode('utf-8'), AES.block_size))
    print(hex(int.from_bytes(ct, byteorder='big')))
```

```python
import string
from pwn import *

MAX_FLAG_LEN = 128

#context.log_level = "debug"
import os
SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "crypto.py")
p = process(["python", SCRIPT_PATH])
# p = process(["venv/bin/python3", "./crypto.py"])
# p = remote("challenge.utctf.live", 7150)
# 
# make_plaintext ensures that our prefix is appended to the flag...
# ...by adding a suffix such that:
# chksum = sum(ord(c) for c in x) % (len(x)+1)
# assert(chksum == len(prefix))
#
# which makes:
# pt = x[:chksum] + secret + x[chksum:]
#
# become:
# pt = prefix + secret + suffix
#
# we can ignore the suffix and so this becomes:
# pt = prefix + secret
# ...which is the standard form for ecb byte-at-a-time decryption

def make_plaintext(prefix):
    attempt = 0
    x = prefix
    while True:
        if sum(ord(c) for c in x) % (len(x)+1) == len(prefix):
            return x
        x = prefix + string.ascii_letters[attempt]
        attempt += 1

# note that if your connection dies before you know the entire flag...
# ... you can add what you know to known_pt to save yourself some time
# e.g. ecb_byte_at_a_time(known_pt="utflag{st0p_")...
# ... continues discovery after the _

def ecb_byte_at_a_time(known_pt=""):
    known_pt = ("A" * 16) + known_pt

    # we're not given an alphabet so pick a sensible one...
    alphabet = string.ascii_letters + string.digits + "_!?}{"

    def read_ct():
        ct = int(p.readline().decode(), 16)
        ct = ct.to_bytes(length=(ct.bit_length()+7)//8, byteorder="big")
        return ct

    for i in range(MAX_FLAG_LEN):
        padding = 15 - (i % 16)
        pt = make_plaintext("A" * padding)
        p.sendlineafter(b"to be encrypted: ", pt.encode())
        ct = read_ct()

        dict_cts = {}
        for c in alphabet:
            dict_known_pt = known_pt[len(known_pt)-16+1:len(known_pt)]
            dict_pt = make_plaintext(dict_known_pt + c)
            p.sendlineafter(b"to be encrypted: ", dict_pt.encode())
            dict_cts[c] = read_ct()

        block_to_attack = (padding + i) // 16
        ct_block_to_attack = ct[block_to_attack * 16: (block_to_attack + 1) * 16]

        for c in alphabet:
            match = True
            for j in range(16):
                if ct_block_to_attack[j] != dict_cts[c][j]:
                    match = False
                    break

            if match:
                known_pt += c
                print(f"{known_pt[16:]}")
                break

        if "}" in known_pt:
            return known_pt[16:]

flag = ecb_byte_at_a_time(known_pt="utflag{")
print(flag)

```
