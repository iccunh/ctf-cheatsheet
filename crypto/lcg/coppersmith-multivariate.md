# Coppersmith multivariate

referensi: Hack The Box 2025

from sage.all import \* import re

p = 0x31337313373133731337313373133731337313373133731337313373133732ad a = 0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef b = 0xdeadc0dedeadc0dedeadc0dedeadc0dedeadc0dedeadc0dedeadc0dedeadc0de

def lcg(x, a, b): while True: yield (x := a\*x + b)

trunc = 48 F = GF(p)

with open('output.txt') as o: h1 = int(o.readline().split(' = ')\[1]) h2 = int(o.readline().split(' = ')\[1])

x, e1, e2 = polygens(F, 'x, e1, e2') sym\_gen = lcg(x, a, b) p1 = next(sym\_gen) - ((h1<\<trunc) + e1)\*next(sym\_gen) p2 = next(sym\_gen) - ((h2<\<trunc) + e2)\*next(sym\_gen)

R2 = F\['e1, e2']

## resultant eliminating x, p1.resultant(p2, x) doesn't work

## because of singular

rel = R2(str(p1.sylvester\_matrix(p2, x).det()))

## use this one or any other multivariate coppersmith solver

load('https://raw.githubusercontent.com/defund/coppersmith/refs/heads/master/coppersmith.sage')

e1, e2 = small\_roots(rel, (1<\<trunc, 1<\<trunc))\[0] root = p1(e1=e1).univariate\_polynomial().roots()\[0]\[0] flag = int(root).to\_bytes(32, 'big')

print(re.search(rb'(HTB{.\*})', flag).group(1).decode())

```python
import secrets

p = 0x31337313373133731337313373133731337313373133731337313373133732ad
a = 0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef
b = 0xdeadc0dedeadc0dedeadc0dedeadc0dedeadc0dedeadc0dedeadc0dedeadc0de

def lcg(x, a, b):
    while True:
        yield (x := a*x + b)

flag = open('flag.txt', 'rb').read()
x = int.from_bytes(flag + secrets.token_bytes(30-len(flag)), 'big')
gen = lcg(x, a, b)

h1 = next(gen) * pow(next(gen), -1, p) % p
h2 = next(gen) * pow(next(gen), -1, p) % p

with open('output.txt', 'w') as o:
    trunc = 48
    # oops, i forgot the last part
    o.write(f'hint1 = {h1 >> trunc}\n')
    o.write(f'hint2 = {h2 >> trunc}\n')
```
