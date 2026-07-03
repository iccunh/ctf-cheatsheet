# 2 ct - 2 e - 1 n

```python
def extended_gcd(a, b):
    if b == 0:
        return a, 1, 0
    gcd, x1, y1 = extended_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    return gcd, x, y

# Cari a dan b
gcd, a, b = extended_gcd(exp1, exp2)

# -32768 32769
print(a, b)

plaintext = (pow(cip1, a, n) * pow(cip2, b, n)) % n
decoded_flag = long_to_bytes(plaintext)
```
