# Diskriminan

Ketika bisa didapatkan sebuah persamaan:

```
Aq**2+Bq+C=0
```

Maka kita bisa menggunakan cara diskriminan untuk mendapatkan nilai q nya.

Contoh chall dari Alpaca dan solver chall menggunakan diskriminan

```python
import os
from Crypto.Util.number import bytes_to_long, getRandomNBitInteger, isPrime

def nextPrime(n):
    while not isPrime(n := n + 1):
        continue
    return n

def gen():
    while True:
        q = getRandomNBitInteger(256)
        r = getRandomNBitInteger(256)
        p = q * nextPrime(r) + nextPrime(q) * r
        if isPrime(p) and isPrime(q):
            return p, q, r

flag = os.environ.get("FLAG", "fakeflag").encode()
m = bytes_to_long(flag)

p, q, r = gen()
n = p * q

phi = (p - 1) * (q - 1)
e = 0x10001
d = pow(e, -1, phi)
c = pow(m, e, n)

print(f"{n=}")
print(f"{e=}")
print(f"{c=}")
print(f"{r=}")
```

```python
from itertools import combinations
from Crypto.Util.number import *
from gmpy2 import iroot

def nextPrime(n):
    while not isPrime(n := n + 1):
        continue
    return n

r=30736331670163278077316573297195977299089049174626053101058657011068283335270
r2 = nextPrime(r)
n=200697881793620389197751143658858424075492240536004468937396825699483210280999214674828938407830171522000573896259413231953182108686782019862906633259090814783111593304404356927145683840948437835426703183742322171552269964159917779


from Crypto.Util.number import isPrime
from gmpy2 import iroot

def find_q(r2, r, n):
    for i in range(2, 10000):
        A = r+r+179
        B = i*r 
        C = -n
        
        # Hitung diskriminan
        discriminant = B**2 - 4 * A * C
        if discriminant < 0:
            # return None  # Tidak ada solusi real
            continue
        
        # Coba kedua solusi kuadrat
        sqrt_discriminant, exact = iroot(discriminant, 2)
        if not exact:  # Jika akar bukan bilangan bulat
            # return None
            continue
        
        # Hitung nilai q
        q1 = (-B + sqrt_discriminant) // (2 * A)
        q2 = (-B - sqrt_discriminant) // (2 * A)
        
        # Periksa apakah q adalah bilangan prima
        if isPrime(q1):
            print("q1 ->", q1)
            print(i)
            return q1
        if isPrime(q2):
            print("q2 ->", q2)
            print(i)
            return q2
        
        # return None  # Tidak ada nilai q yang valid
        continue

q = find_q(r2, r, n)

# q = 57138703210086603216917938147752779170509477993762976004506899310197198907231
p = n//q
print((p*q) == n)
c=77163248552037496974551155836778067107086838375316358094323022740486805320709021643760063197513767812819672431278113945221579920669369599456818771428377647053211504958874209832487794913919451387978942636428157218259130156026601708
e = 65537
d = inverse(e, (p-1)*(q-1))
print(long_to_bytes(pow(c, d, n)))
```
