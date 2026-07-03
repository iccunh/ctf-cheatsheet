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

### References

* [https://sylvie.fyi/posts/bloatware/](https://sylvie.fyi/posts/bloatware/)
