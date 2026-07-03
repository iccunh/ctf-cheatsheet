# d mod (p-1)

referensi: Pearl CTF

```python
from pwn import *
from gmpy2 import gcd
from sympy import factorint
from Crypto.Util.number import *
from random import *

# context.log_level = 'error'

# dp leak
# 3 encrypt tanpa ditau e untuk gcd n GCD N
# FERMAT
# pow(a,p,p) = a, pow(a,p-1,p) = 1
io = remote('encryption-oracle.ctf.pearlctf.in', 30012)

def encrypt_message(num):
    io.sendlineafter(b"> ",b"1")
    msg = hex(num)[2:]
    io.sendlineafter(b"Enter hex message: ",msg.encode())
    return int(io.recvline().split()[-1],16)

def get_flag():
    io.sendlineafter(b"> ",b"2")
    tmp= io.recvline().strip().decode()
    tmp = tmp.split(":")[-1].strip()
    tmp = int(tmp,16)
    return tmp

def get_leak():
    io.sendlineafter(b"> ",b"3")
    tmp= io.recvline().strip().decode()
    tmp = tmp.split(":")[-1].strip()
    tmp = int(tmp)
    return tmp

# A = 3**600
A = getrandbits(624)
B = A**2
C = A**3

r1 = encrypt_message(A)
r2 = encrypt_message(B)
r3 = encrypt_message(C)

d1 = (r1**2 - r2)
d2 = (r1**3 - r3)

n = gcd(d1, d2)

print(n)

dp = get_leak()
flag = get_flag()

kp = A - pow(r1, dp, n)
p = gcd(n, kp)
print(p)

q = n//p
print(n == (p*q))

# d_hasilmod = pow()
pt = long_to_bytes(pow(flag, dp, p))
print(pt)

```

```python
#!/usr/local/bin/python
import random
from Crypto.Util.number import getPrime, bytes_to_long, long_to_bytes
import math


p = getPrime(1024)
q = getPrime(1024)
n = p * q
phi = (p - 1) * (q - 1)


e = getPrime(20)
while math.gcd(e, phi) != 1:
    e = getPrime(20)

d = pow(e, -1, phi)  
leak = d % (p-1)

flag="pearl{fake_flag}"
flag_int = bytes_to_long(flag.encode())
encrypted_flag = pow(flag_int, e, n)

count = 0

while True:
    print("\n1. Encrypt message (3 times max)")
    print("2. Show encrypted flag")
    print("3. Show leak (d mod (p-1))")
    print("4. Exit")
    
    choice = input("> ")
    
    if choice == "1":
        if count >= 3:
            print("No more encryptions allowed")
            continue
        
        hex_msg = input("Enter hex message: ")
        try:
            msg = int(hex_msg, 16)
            if msg.bit_length() < 600:
                print(f"Message too short ({msg.bit_length()} bits, need 600+)")
                continue
            
            encrypted = pow(msg, e, n)
            count += 1
            print(f"Encrypted (hex): {encrypted:x}")
            print(f"Encryptions used: {count}/3")
        except:
            print("Invalid input")
    
    elif choice == "2":
        print(f"Encrypted flag: {encrypted_flag:x}")
    
    elif choice == "3":
        print(f"Leak (d mod (p-1)): {leak}")
    
    elif choice == "4":
        print("Exiting")
        break
    
    else:
        print("Invalid choice")

```
