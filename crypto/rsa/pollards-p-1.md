# Pollard's p-1

**Ide sederhana:** Kalau sebuah faktor prima p dari n punya sifat bahwa **p−1 hanya terdiri dari faktor kecil** (disebut “B-smooth”), maka kita bisa bikin pangkat besar M yang “selaras” dengan p−1 sehingga a\*\*M ≡ 1 (mod p).

Contoh chall dari Alpaca dan solver challnya

```python
import os
import random
from math import prod
from Crypto.Util.number import isPrime, bytes_to_long

r = random.Random(0)
def deterministicGetPrime():
  while True:
    if isPrime(p := r.getrandbits(64)):
      return p

# This is not likely to fail
assert deterministicGetPrime() == 2710959347947821323, "Your Python's random module is not compatible with this challenge."

def getPrime(bit):
  factors = [deterministicGetPrime() for _ in range(bit // 64)]

  # ini ada + 1
  while True:
    p = 2 * prod(factors) + 1
    if isPrime(p):
      return p
 
    factors.remove(random.choice(factors))
    factors.append(deterministicGetPrime())

flag = os.environ.get("FLAG", "fakeflag").encode()
m = bytes_to_long(flag)

p, q = getPrime(1024), getPrime(1024)

n = p * q
e = 0x10001
c = pow(m, e, n)

print(f"{n=}")
print(f"{e=}")
print(f"{c=}")

```

```python
import  math
import  random
from  Crypto.Util.number import *

r = random.Random( 0 )
def  deterministicGetPrime ():
    while  True :
        if  isPrime(p := r.getrandbits( 64 )):
            return  p   


def  pollard (n):
    a =  2 
    while  True :
        x = deterministicGetPrime()
        a =  pow (a, x, n)
        d = math.gcd(a -  1 , n)
        if  1  < d < n:
            return  d


n=2350478429681099659482802009772446082018100644248516135321613920512468478639125995627622723613436514363575959981129347545346377683616601997652559989194209421585293503204692287227768734043407645110784759572198774750930099526115866644410725881688186477790001107094553659510391748347376557636648685171853839010603373478663706118665850493342775539671166315233110564897483927720435690486237018231160348429442602322737086330061842505643074752650924036094256703773247700173034557490511259257339056944624783261440335003074769966389878838392473674878449536592166047002406250295311924149998650337286245273761909
e=65537
c=945455686374900611982512983855180418093086799652768743864445887891673833536194784436479986018226808021869459762652060495495939514186099959619150594580806928854502608487090614914226527710432592362185466014910082946747720345943963459584430804168801787831721882743415735573097846726969566369857274720210999142004037914646773788750511310948953348263288281876918925575402242949315439533982980005949680451780931608479641161670505447003036276496409290185385863265908516453044673078999800497412772426465138742141279302235558029258772175141248590241406152365769987248447302410223052788101550323890531305166459

p = pollard(n)
assert  p  is  not  None 
q = n // p
phi = (p -  1 ) * (q -  1 )
d =  pow (e, - 1 , phi)
m =  pow (c, d, n)
print(long_to_bytes(m))
```
