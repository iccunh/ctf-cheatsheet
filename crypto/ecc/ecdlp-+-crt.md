# ECDLP + CRT

Referensi: Cryptohack

```python
# bit private keynya 64
max_val = 1<<64
p = 99061670249353652702595159229088680425828208953931838069069584252923270946291
E = EllipticCurve(GF(p), [1,4]) 
G = E.gens()[0]
A = E.lift_x(87360200456784002948566700858113190957688355783112995047798140117594305287669)
order = G.order()

subresults = []
factors = []
modulus = 1
for prime, exponent in factor(order):
    if modulus >= max_val: break
    _factor = prime ** exponent
    factors.append(_factor)
    G2 = G*(order//_factor)
    A2 = A*(order//_factor)
    subresults.append(discrete_log_lambda(A2, G2, (0,_factor), '+'))
    modulus *= _factor

n = crt(subresults,factors)
assert(n * G == A)
print("found private key:", n)
```
