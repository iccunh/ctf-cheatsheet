# Many Primes

```python
phi = 1
nCopy = n
for p in range(3, 2**16, 2):
    if nCopy%p == 0:
        reps = 0
        while nCopy%p == 0:
            reps+=1
            nCopy //=p
        phi *= p**(reps-1)*(p-1)

d = pow(e, -1, phi)
message = pow(flag, d, n)
```
