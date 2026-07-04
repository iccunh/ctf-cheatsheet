# Z3 Solver

| Type                    | Use               | Example                                         |
| ----------------------- | ----------------- | ----------------------------------------------- |
| `BitVec(name, n)`       | n-bit bitvector   | `x = BitVec('x', 8)`                            |
| `Int(name)`             | Unbounded integer | `i = Int('i')`                                  |
| `Real(name)`            | Real number       | `r = Real('r')`                                 |
| `Bool(name)`            | Boolean           | `b = Bool('b')`                                 |
| `Array(name, dom, rng)` | Array / memory    | `a = Array('a', BitVecSort(32), BitVecSort(8))` |

```python
from z3 import *

s = Solver()
x, y = BitVecs('x y', 8)

s.add(x > 10)
s.add(y == x + 5)

if s.check() == sat:
    m = s.model()
    print(m[x], m[y])      # concrete values
    print(m.eval(x + y))   # evaluate expression under model
else:
    print("unsat")
```

* `sat` / `unsat` / `unknown`
* `s.reason_unknown()` if `unknown`

### The `eval` Trick

Use Python `eval` on strings valid in both Python and target language.

```python
# Parse target constraints as Python strings
expr = "0x1*(inp[0] & ~inp[1]) + 0x1*inp[1] + -0x1*(inp[0] | inp[1]) == 0"

# Brute-force concrete values with eval
inp = [0] * 1950
inp[0], inp[1] = 123, 45
assert eval(expr, {"inp": inp})   # fast concrete test

# Bind same string to Z3 symbols for solving
inp_sym = [BitVec(f"inp_{i}", 16) for i in range(1950)]
solver.add(eval(expr, {"inp": inp_sym}))
```

Store constraints as text in a file, then `eval` against plain arrays (brute-force probing) or Z3 BitVec arrays (solving).

### Quick Reference Script

```python
from z3 import *

n = 100
xs = [BitVec(f"x{i}", 8) for i in range(n)]
s = Solver()

# length, printable, prefix
s.add(xs[0] == ord('f'), xs[1] == ord('l'), xs[2] == ord('a'), xs[3] == ord('g'))
for x in xs:
    s.add(And(x >= 0x20, x <= 0x7e))

# add eval'd constraints here
# s.add(eval(your_expr, {"inp": xs}))

if s.check() == sat:
    m = s.model()
    print(''.join(chr(int(str(m[x]))) for x in xs))
else:
    print("unsat")
```

### BitVec Patterns

```python
u8  = BitVec('u8', 8)
u32 = BitVec('u32', 32)
u64 = BitVec('u64', 64)

s.add((u32 + 0x1337) == BitVecVal(0xdeadbeef, 32))
s.add((u32 ^ 0x41414141) == 0x12345678)
s.add(LShR(u32, 7) == 0x1234)      # unsigned right shift
s.add(Extract(15, 8, u32) == 0x41) # byte/bit slice
s.add(ZeroExt(24, u8) + 1 == u32)  # unsigned widen
s.add(SignExt(24, u8) < 0)         # signed widen
```

### Rotates / Endian

```python
x = BitVec('x', 64)
s.add(RotateLeft(x, 13) ^ 0xfeedface == 0x1337133713371337)
s.add(RotateRight(x, 7) == 0x1122334455667788)

le32 = Concat(xs[3], xs[2], xs[1], xs[0])
be32 = Concat(xs[0], xs[1], xs[2], xs[3])
s.add(le32 == 0x67616c66) # b"flag" little endian
```

### Common Constraints

```python
# prefix
for i, c in enumerate(b"flag{"):
    s.add(xs[i] == c)

# checksum
s.add(Sum([ZeroExt(24, x) for x in xs]) == 0x9ab)

# xor chain
for i in range(n - 1):
    s.add((xs[i] ^ xs[i + 1]) == known[i])

# symbolic table lookup
table = [0x63, 0x7c, 0x77, 0x7b]
idx = xs[0]
val = BitVecVal(table[0], 8)
for i, t in enumerate(table):
    val = If(idx == i, BitVecVal(t, 8), val)
s.add(val == 0x77)
```

### Multiple Solutions

```python
while s.check() == sat:
    m = s.model()
    out = bytes(m.eval(x, model_completion=True).as_long() for x in xs)
    print(out)
    s.add(Or([x != m.eval(x, model_completion=True) for x in xs]))
```

### Debug / Pitfalls

```python
print(s.sexpr())
print(s.model())
print(simplify(expr))
s.push(); s.add(test); print(s.check()); s.pop()
s.set("timeout", 5000)
```

* Use `BitVec`, not `Int`, for xor/shift/overflow.
* Use `LShR` for C unsigned right shift.
* Use `m.eval(x, model_completion=True)` when model values are missing.
* Mask Python concrete arithmetic if you emulate fixed-width code outside Z3.

### Oracle Recovery (Sample -> Recover -> Solve)

> **Source:** CBC 2026 Round Robin — `dig` challenge

When a binary lets you query a hidden function and you know its form (e.g. polynomial), sample it at known points to recover the coefficients, then solve for the desired input.

**Challenge:** A "dig" binary computes:

$$
s(x) = ((a \cdot x + b) \cdot x + c) \bmod 2^{16}
$$

where $a, b, c$ are random 16-bit values set at startup ($a$ is odd). You have **4 digs**. Find the site $x \in [1, 65535]$ where $s(x) = 1337$ to get the flag.

By construction $s(\text{target}) = 1337$ — the target is picked randomly and $c$ is computed to make this hold.

#### Solver with Z3

`BitVec(16)` handles modular wrapping automatically.

```python
from pwn import *
from z3 import *

io = process('./dig')

io.sendlineafter(b'>', b'dig 1')
io.recvuntil(b'sensor: ')
v1 = int(io.recvline().strip().decode().split(']')[0], 16)

io.sendlineafter(b'>', b'dig 2')
io.recvuntil(b'sensor: ')
v2 = int(io.recvline().strip().decode().split(']')[0], 16)

io.sendlineafter(b'>', b'dig 3')
io.recvuntil(b'sensor: ')
v3 = int(io.recvline().strip().decode().split(']')[0], 16)

s = Solver()
a, b, c, x = BitVecs('a b c x', 16)
s.add((a * 1 + b) * 1 + c == v1)
s.add((a * 2 + b) * 2 + c == v2)
s.add((a * 3 + b) * 3 + c == v3)
s.add((a * x + b) * x + c == 1337)

assert s.check() == sat
m = s.model()
io.sendlineafter(b'>', f'dig {m[x]}'.encode())
io.interactive()
```

#### Manual Solver (Finite Differences)

Sample $f(x) = ax^2 + bx + c \pmod{2^{16}}$ at $x = 1, 2, 3$:

$$
\begin{aligned}
v_1 &= a + b + c \\
v_2 &= 4a + 2b + c \\
v_3 &= 9a + 3b + c
\end{aligned}
$$

First difference eliminates $c$, second eliminates $b$:

$$
\begin{aligned}
\Delta(1) &= v_2 - v_1 = 3a + b \\
\Delta(2) &= v_3 - v_2 = 5a + b \\[4pt]
\Delta(2) - \Delta(1) &= 2a
\end{aligned}
$$

So:

$$
\begin{aligned}
2a &\equiv v_3 - 2v_2 + v_1 \pmod{2^{16}} \\
a &= (v_3 - 2v_2 + v_1) \,/\, 2 \\
b &\equiv v_2 - v_1 - 3a \pmod{2^{16}} \\
c &\equiv v_1 - a - b \pmod{2^{16}}
\end{aligned}
$$

> **Note:** $2a \bmod 2^{16}$ gives two candidates for $a$ (differing by $2^{15}$), but both produce the same $f(x)$ because $2^{15} \cdot x(x-1) \equiv 0 \pmod{2^{16}}$ — $x(x-1)$ is always even, making it a multiple of $2^{15} \cdot 2 = 2^{16}$.

```python
from pwn import *

io = process('./dig')

io.sendlineafter(b'>', b'dig 1')
io.recvuntil(b'sensor: ')
v1 = int(io.recvline().strip().decode().split(']')[0], 16)

io.sendlineafter(b'>', b'dig 2')
io.recvuntil(b'sensor: ')
v2 = int(io.recvline().strip().decode().split(']')[0], 16)

io.sendlineafter(b'>', b'dig 3')
io.recvuntil(b'sensor: ')
v3 = int(io.recvline().strip().decode().split(']')[0], 16)

k = (v3 - 2 * v2 + v1) % 65536
a = k // 2
b = (v2 - v1 - 3 * a) % 65536
c = (v1 - a - b) % 65536

target = next(x for x in range(1, 65536)
              if ((a * x + b) * x + c) & 0xFFFF == 1337)

io.sendlineafter(b'>', f'dig {target}'.encode())
print(io.recvall().decode())
```

### References

* [https://sylvie.fyi/posts/bloatware/](https://sylvie.fyi/posts/bloatware/)
