# Basic Small

referensi: Brunner CTF 2025

```
# The numbers are small, solve discrete logarithm using sage:
p  = 14912432766367177751
g  = 2784687438861268863
h  = 8201777436716393968
c1 = 12279519522290406516
c2 = 10734305369677133991

# h = g ^ x mod p
# s = h ^ y mod p
# c1 = g ^ y mod p
# c2 = m * s mod p
R = Integers(p)
x = R(h).log(g)
s = pow(c1, x, p)
m = c2 * pow(s, -1, p) % p
print(bytes.fromhex(hex(m)[2:]))
```

```python
from sage.all import *

# SageMath snippet
P  = 14912432766367177751
g  = 2784687438861268863
h  = 8201777436716393968
c1 = 12279519522290406516
c2 = 10734305369677133991

F = GF(P)

# Baby-step giant-step algorithm
def baby_step(g, h, n):
    m = ceil(sqrt(n))
    m2 = m // 2

    # We split into 2 halves because the full table does not fit in RAM...
    # Also, we start with the 2nd half, which contains the log we look for in the largest prime

    # 2nd half
    tbl = {}
    for j in range(m2, m):
        tbl[int(g**j)] = j
    a = g ** (-m)
    y = h
    for i in range(m):
        yy = int(y)
        if yy in tbl:
            return i*m + tbl[yy]
        y = y * a

    # 1st half
    tbl = {}
    for j in range(m2):
        tbl[int(g**j)] = j
    a = g ** (-m)
    y = h
    for i in range(m):
        yy = int(y)
        if yy in tbl:
            return i*m + tbl[yy]
        y = y * a

# Discrete logarithm in group of order p^e
def prime_power(g, h, p, e):
    x = 0
    gamma = g ** (p ** (e-1))
    for k in range(e):
        hi = ((g ** (-x)) * h) ** (p ** (e-1-k))
        d = baby_step(gamma, hi, p)
        print("tes", d, p, k)
        x = x + d * (p ** k)
    return x

# Pohlig-Hellman algorithm in any group
def pohlig_hellman(g, h, n):
    fact = list(factor(n))
    print('Factors of P-1:', fact)
    a = []
    b = []
    for p, e in fact:
        print('Solving log mod ' + str(p) + '^' + str(e))
        gi = g ** (n / (p ** e))
        hi = h ** (n / (p ** e))
        xi = prime_power(gi, hi, p, e)
        v = int(gi ** xi) % (p ** e)
        w = int(hi) % (p ** e)
        a.append(xi)
        b.append(p**e)
    return crt(a, b)

g = F(g)
h = F(h)

# x = pohlig_hellman(g, h, P-1)
x = 6111408178511075141


# shared secret s = c1^x
s = pow(c1, x, p)
s_inv = inv_mod(s, p)

m = (c2 * s_inv) % p
m_bytes = int_to_bytes(m)
plaintext = try_decode_bytes(m_bytes)

# print("[*] ord(g) =", ord_g)
print("[*] secret x =", x)
print("[*] m (int)  =", m)
print("[*] m (hex)  =", m.to_bytes((m.bit_length()+7)//8, 'big').hex())
print("[*] m (text) =", plaintext)
print(f"Flag: brunner{{{plaintext}}}")
```
