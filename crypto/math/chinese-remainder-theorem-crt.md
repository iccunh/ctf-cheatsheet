# Chinese Remainder Theorem  (CRT)

Kalau punya banyak sistem persamaan kongruensi dengan semua n relatif prima (gcd = 1) serta plaintextnya sama, maka crt bisa dicoba

```python
from sympy.ntheory.modular import crt

# moduli (N), remainders (C)
K6 = crt(N, C)

# atau

def crt(remainders, moduli):
    """Iterative CRT: returns x mod M where M = prod(moduli)."""
    x, M = 0, 1
    for r, m in zip(remainders, moduli):
        # Solve M·δ ≡ (r - x) mod m
        δ = ((r - x) * pow(M, -1, m)) % m
        x += M * δ
        M *= m
    return x


# crt ciphertext, modulo
K6 = crt([C0, C1, C2], [n0, n1, n2])
```

Referensi: tjctf

```python
from Crypto.Util.number import bytes_to_long, getPrime, long_to_bytes
import time


flag = open('flag.txt', 'rb').read()
m = bytes_to_long(flag)

e = getPrime(8)
print(f'e = {e}')

def generate_key():
    p, q = getPrime(256), getPrime(256)
    while (p - 1) % e == 0:
        p = getPrime(256)
    while (q - 1) % e == 0:
        q = getPrime(256)
    return p * q
    
for i in range(e):
    n = generate_key()
    c = pow(m, e, n)
    print(f'n{i} = {n}')
    print(f'c{i} = {c}')
```

Referensi: watctf

```python
from pwn import *
from sage.all import *
import gmpy2
from Crypto.Util.number import *

ps = []
ms = []
# r.interactive()
while True:
    r = remote("challs.watctf.org", 2340)

    r.recvuntil(b" = ")
    ct = int(r.readline().decode().strip('\n'))
    r.recvuntil(b" = ")
    e = int(r.readline().decode().strip('\n'))

    # 2^e
    r.recvuntil(b" = ")
    a = int(r.readline().decode().strip('\n'))
    # 3^e
    r.recvuntil(b" = ")
    b = int(r.readline().decode().strip('\n'))
    # 4^e
    r.recvuntil(b" = ")
    c = int(r.readline().decode().strip('\n'))
    # 5^e
    r.recvuntil(b" = ")
    cd = int(r.readline().decode().strip('\n'))
    # 6^e
    r.recvuntil(b" = ")
    d = int(r.readline().decode().strip('\n'))

    # gcd  -> a = 2^e - k p (ini pangkat dua supaya bisa kurangi ini ->) c = 2^2e - k p
    # gcd  -> d = 2^e . 3^e - k p (ini dikurangi a dan b agar 6^e nya habis)
    eq1 = (a**2 - c)
    eq2 = ((a*b) - d)
    # print(eq1)
    # print(eq2)

    from math import gcd

    # print("p", gcd(eq1, eq2))
    p = gcd(eq1, eq2)

    i = 2
    while not isPrime(p):
        tes = p // i
        if isPrime(tes):
            p = tes
            break
        i += 1

    # crt
    m = int(GF(p)(ct).nth_root(e))

    ps.append(Integer(p))
    ms.append(Integer(m))
    print(ps)
    print(ms)

# m**e ≡ ct ( mod p)

# Dan karena persamaan di atas sama dengan flag**e, kita dapat menyimpulkan bahwa: 
# m≡flag(modp) -> karena ct akar e itu flag bede

    flag = crt(ms, ps)

    if b'ctf' in long_to_bytes(int(flag)):
        print(long_to_bytes(int(flag)))
        exit()
```

```python
from math import gcd
from Crypto.Util.number import *

ct1 = 37844264930843890898893580989239916705366775397411309374882916364724047905820508623344817821611147759719803463551163711748945964953508438092640704975322410674376310451491466018854638417846403949970055673017956614790849541769189856229901445053311930191101113141352577296808591262282903492916570981464721683170
e1 = 95367126360491998289580891681995064146568692640075321101731153832671220263097
two_e1 = 4149978437655769407793132042713164838681099155918471319044748350209256004282122184011994449783808479443506545819870176546399400847828354633808316718877209
three_e1 = 7869506884661205498280229622716788325298106349989204536048270811807350351516539428625165750377565705979848710876601979413888629169813007622553539031860145
four_e1 = 4126974558121526873091536670785142908981516054611449669351219001588683527777760205133773716826953881669967807253813668649925101310906264438756696015310326
six_e1 = 3587819792430293084948828625326039526479477057981033608204840578917852996913427284713350050239787436800845696467352695356754395941218265799409999751980243


ct2 = 67137501367988320420726728251642629370742939368116909097111242218913253230706635639424749400692966474288381339662734254493350633445112027389363599174246724744557109603985411603835044629938422430421407325661154316131063150518032585238266748406393677336699082042736902217991724629928437253926219435546138276252
e2 = 67617031409935137660819638555291165108618889122238394052402881225177522506281
two_e2 = 938095258993720272100621626704681330175094802179763121900560043736225590385210353899346241161826685284953500450001025229799599782763305020674622041164842
three_e2 = 11333600198766531364562418061598434392170300680062362247468210754749964569068587947794745553427895343873855895439519595162462376425252260123434734301869287
four_e2 = 7626217611352239098126632219444448346537089222798101402153570297486413533017871195051737247018055975874084104715593594582851081816382153110358195702601541
six_e2 = 10799860861761050101816046167527520013371514870591528374812424565223044581602600724352554370714746384316787778583104204238459634262665512858503404060624738

# Recover p1
d1_1 = six_e1 - (two_e1 * three_e1)
d1_2 = four_e1 - (two_e1 * two_e1)
p1 = gcd(d1_1, d1_2)

# Recover p2
d2_1 = six_e2 - (two_e2 * three_e2)
d2_2 = four_e2 - (two_e2 * two_e2)
p2 = gcd(d2_1, d2_2)

# Ensure p1 and p2 are primes (or factor out small integers if necessary)
print(f"Recovered p1: {p1}")
print(f"Recovered p2: {p2}")

# Compute private keys
d1 = inverse(e1, p1 - 1)
d2 = inverse(e2, p2 - 1)

# Decrypt ciphertexts
m1 = pow(ct1, d1, p1)
m2 = pow(ct2, d2, p2)

# Use CRT to recover m
from sympy.ntheory.modular import crt

m, _ = crt([p1, p2], [m1, m2])
print(f"Recovered m: {long_to_bytes(m)}")
```

```python
#!/usr/local/bin/python

from Crypto.Util.number import getPrime, bytes_to_long
import math

with open('flag.txt', 'rb') as f:
    flag = f.read().strip()
    pt = bytes_to_long(flag)
    assert pt.bit_length() > 800

def try_gen():
    p = getPrime(512)
    q = getPrime(512)
    e = getPrime(256)
    N = p*q

    phi = (p-1)*(q-1)
    if math.gcd(phi, e) != 1:
        # restart
        try_gen()

    ct = pow(pt, e, N)
    print('ct =', ct)
    print('e =', e)
    for i in [2,3,4,5,6]:
        print(f'{i}^e mod p =', pow(i, e, p))

try_gen()

```
