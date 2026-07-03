# Key Random

Referensi: wolvctf

```python
#!/usr/local/bin/python3
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import random

f = open('./flag.txt','r')
flag = f.read()

def encrypt(message):
    global flag
    message = message.encode()
    message += flag.encode()
    key = random.getrandbits(256)
    key = key.to_bytes(32,'little')
    cipher = AES.new(key, AES.MODE_ECB)
    ciphertext = cipher.encrypt(pad(message, AES.block_size))
    return(ciphertext.hex())

print("Welcome to my secure encryption machine!")
print("I'll encrypt all your messages (and add a little surprise at the end)")

while(True):
    print("Do you have a message to encrypt? [Y|N]")
    response = input()
    if(response == 'Y'):
        print("Gimme your message:")
        message = input()
        print("Your message is: ",encrypt(message))
    else:
        exit(0)

```

```python
#!/usr/bin/env python3

import string
from pwn import *

#context.log_level = "debug"

MAX_FLAG_LEN = 90

# we're not given an alphabet so pick a sensible one...
ALPHABET = string.ascii_letters + string.digits + "-_}{@!?$%^&*()~#/"

#p = process(["venv/bin/python3", "./chal.py"])
p = remote("ecbpp.kctf-453514-codelab.kctf.cloud", 1337)

p.readline()
p.readline()

def ecb_byte_at_a_time(known_pt=""):
    known_pt = known_pt

    def enc(pt):
        p.sendline(b"Y")
        p.sendlineafter(b"message:", pt.encode())
        p.readuntil(b"Your message is:  ")
        ct = bytes.fromhex(p.readline().decode())
        return ct

    for i in range(MAX_FLAG_LEN):
        padding = 15 - (i % 16)

        pt = ""
        for c in ALPHABET:
            pt += ("A" * padding) + known_pt + c

        dict_block_sizes = len(("A" * padding) + known_pt + "A")
        prefix_len = len(pt)

        pt += "A" * padding
        ct = enc(pt)

        dict_cts = {}
        for j in range(len(ALPHABET)):
            c = ALPHABET[j]
            dict_cts[c] = ct[j*dict_block_sizes:(j+1)*dict_block_sizes][-16:]

        ct = ct[len(ALPHABET)*dict_block_sizes:]

        block_to_attack = (padding + i) // 16
        ct_block_to_attack = ct[block_to_attack * 16: (block_to_attack + 1) * 16]

        for c in ALPHABET:
            match = True
            for j in range(16):
                if ct_block_to_attack[j] != dict_cts[c][j]:
                    match = False
                    break

            if match:
                known_pt += c
                #print(f"{known_pt}")
                break

    return known_pt

flag = ecb_byte_at_a_time(known_pt="wctf{")
print(flag)
```
