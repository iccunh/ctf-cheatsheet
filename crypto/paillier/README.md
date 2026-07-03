# Paillier

```python
def encrypt(m, n, g):
    r = random.randint(1, n - 1)
    c = (pow(g, m, n**2) * pow(r, n, n**2)) % n**2
    return c
```

```python
# decrypt
lambda_ = lcm(p - 1, q - 1)

# L(x) function for Paillier
def L(u, n):
    return (u - 1) // n

# Decrypt
u = pow(c, lambda_, n2)
L_u = L(u, n)
L_g = L(pow(g, lambda_, n2), n)
m = (L_u * inverse(L_g, n)) % n
```
