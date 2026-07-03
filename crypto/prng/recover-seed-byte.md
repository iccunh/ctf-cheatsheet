# Recover Seed Byte

Referensi: FMC CTF 2025 & [https://github.com/StackeredSAS/python-random-playground](https://github.com/StackeredSAS/python-random-playground)

```python
import math
import functools

reduce = functools.reduce
gcd = math.gcd

def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, x, y = egcd(b % a, a)
        return (g, y - (b // a) * x, x)

def modinv(b, n):
    g, x, _ = egcd(b, n)
    if g == 1:
        return x % n

def crack_unknown_increment(states, modulus, multiplier):
    increment = (states[1] - states[0]*multiplier) % modulus
    return modulus, multiplier, increment

def crack_unknown_multiplier(states, modulus):
    multiplier = (states[2] - states[1]) * modinv(states[1] - states[0], modulus) % modulus
    return crack_unknown_increment(states, modulus, multiplier)

def crack_unknown_modulus(states):
    diffs = [s1 - s0 for s0, s1 in zip(states, states[1:])]
    zeroes = [t2*t0 - t1*t1 for t0, t1, t2 in zip(diffs, diffs[1:], diffs[2:])]
    modulus = abs(reduce(gcd, zeroes))
    return crack_unknown_multiplier(states, modulus)
```

```python
from pwn import *
from randcrack import RandCrack
import random
from Crypto.Cipher import AES
from Crypto.Util.number import *
from functions import untemper, invertStep, recover_Kj_from_Ii
from Crypto.Util.Padding import pad, unpad

# recover seed, PRNG lah + randcrack dijalankan di folder randcrack
while 1:
    try:
        r = remote("superguesser.fmc.tf", 2002)

        r.recvuntil(b"flag: \n")
        flag_hex = r.recvline().decode().strip()
        print("Encrypted flag:", flag_hex)
        flag = bytes.fromhex(flag_hex)
        print(flag)

        indices = [3, 4, 5, 6, 230, 231, 232, 233]
        hints = []

        for i in indices:
            r.sendlineafter(b'): ', str(i).encode())

            r.recvuntil(b": ")
            b = int(r.readline().decode().strip('\n'))
            # print(b)
            hints.append(b)

        S = [untemper(a) for a in hints]

        I_230_, I_231 = invertStep(S[0], S[4])
        I_231_, I_232 = invertStep(S[1], S[5])
        I_232_, I_233 = invertStep(S[2], S[6])
        I_233_, I_234 = invertStep(S[3], S[7])

        I_231 += I_231_
        I_232 += I_232_
        I_233 += I_233_


        seed_l = recover_Kj_from_Ii(I_233, I_232, I_231, 233) - 16
        seed_h1 = recover_Kj_from_Ii(I_234, I_233, I_232, 234) - 17
        seed_h2 = recover_Kj_from_Ii(I_234+0x80000000, I_233, I_232, 234) - 17

        seed1 = (seed_h1 << 32) + seed_l
        seed2 = (seed_h2 << 32) + seed_l

        print(bytes.fromhex(hex(seed1)[2:]))
        print(bytes.fromhex(hex(seed2)[2:]))

        recovered_seed = bytes.fromhex(hex(seed2)[2:])
        print("rs", recovered_seed)

        random.seed(recovered_seed)
        rc = RandCrack()

        # print(hints)

        for i in range(624):
            b = random.getrandbits(32)
            rc.submit(b)

        key = rc.predict_getrandbits(128).to_bytes(16, 'big')
        iv = recovered_seed
        # print("Recovered key:", key)
        # print("Recovered iv:", iv)

        def decrypt_flag(flag, key, iv):
            cipher = AES.new(key, AES.MODE_CBC, iv*2)

            pt_padded = cipher.decrypt(flag)
            print(pt_padded)
            pt = unpad(pt_padded, AES.block_size)
            print("Flag:", pt.decode())
            return pt

        print(decrypt_flag(flag, key, iv))

        r.interactive()
    except:
        print("masih")
```

```python
#!/usr/local/bin/python

import os
import random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

MAX_ATTEMPTS = 10

def encrypt_flag(flag, iv):
    key = random.getrandbits(128).to_bytes(16, 'big')
    cipher = AES.new(key, AES.MODE_CBC, iv*2)
    encrypted = cipher.encrypt(pad(flag.encode(), AES.block_size))
    return encrypted

def main():
    secureSeed = os.urandom(8)
    random.seed(secureSeed)
    hints = [random.getrandbits(32) for _ in range(624)]
    encrypted_flag = encrypt_flag(open('./flag.txt').read(), secureSeed)

    print("\n✨ Welcome to the **Guess the Number Challenge v2**! ✨")
    print("🕵️‍♂️ Your mission: Decode the encrypted flag by uncovering critical hints.")
    print("📊 We've precomputed 624 random numbers using a secure PRNG.")
    print(f"❗ But there's a catch: You can only access {MAX_ATTEMPTS} of them.")
    print("🔑 Choose your indices wisely to uncover the key!")
    print("\n📜 Instructions:")
    print("1️⃣ You have 624 unique random numbers that are critical for decrypting the flag.")
    print("2️⃣ Enter an index (0-623) to reveal a hint.")
    print(f"3️⃣ You only have {MAX_ATTEMPTS} attempts, so choose wisely!")
    print("4️⃣ Use your understanding of randomness to crack the secure seed.")

    print(f"\n🔒 Here is your encrypted flag: \n{encrypted_flag.hex()}")
    print(f"\nGood luck! You have {MAX_ATTEMPTS} attempts to guess the correct index.\n")

    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"Attempt {attempt}/{MAX_ATTEMPTS}")
        try:
            index = int(input("Enter an index (0-624): ").strip())
            if 0 <= index < 624:
                print(f"Hint at index {index}: {hints[index]}\n")
            else:
                print("❌ Invalid index! Please enter a number between 0 and 624.\n")
        except ValueError:
            print("❌ Invalid input! Please enter a valid integer.\n")
    print("✨ Your attempts are over! Good luck solving the challenge!\n")
    print("🔍 Remember, the flag is encrypted. Use your hints wisely. Goodbye!")

if __name__ == "__main__":
    main()

```

