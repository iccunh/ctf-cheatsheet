# ML-KEM Error Leak

Use when Kyber/ML-KEM leaks linear equations of small error coefficients.

## Recover Small Error

```python
def recover_error(samples, size=512, bound=3):
    e = [None] * size
    changed = True
    while changed:
        changed = False
        for idxs, coeffs, val in samples:
            known = 0
            unknown = []
            for i, c in zip(idxs, coeffs):
                if e[i] is None:
                    unknown.append((i, c))
                else:
                    known += e[i] * c
            if len(unknown) == 1:
                i, c = unknown[0]
                rem = val - known
                if c and rem % c == 0:
                    cand = rem // c
                    if -bound <= cand <= bound:
                        e[i] = cand
                        changed = True
    return e
```

## Solve `A*s + e = t mod q`

```python
def solve_mod(mat, vec, mod):
    n = len(vec)
    a = [row[:] for row in mat]
    b = vec[:]
    for col in range(n):
        pivot = next(r for r in range(col, n) if a[r][col] % mod)
        a[col], a[pivot] = a[pivot], a[col]
        b[col], b[pivot] = b[pivot], b[col]
        inv = pow(a[col][col], -1, mod)
        for j in range(col, n):
            a[col][j] = a[col][j] * inv % mod
        b[col] = b[col] * inv % mod
        for r in range(n):
            if r == col:
                continue
            f = a[r][col] % mod
            for j in range(col, n):
                a[r][j] = (a[r][j] - f * a[col][j]) % mod
            b[r] = (b[r] - f * b[col]) % mod
    return b

e = recover_error(samples)
t_minus_e = [(t_i - e_i) % q for t_i, e_i in zip(t, e)]
s = solve_mod(A, t_minus_e, q)
```

