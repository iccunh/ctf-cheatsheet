# Symbolic Execution

Use symbolic execution when the binary has a clear success string and normal reversing is slower than asking a solver for an input.

## angr Find / Avoid

```python
import angr
import claripy

BIN = "./chall"
N = 32

p = angr.Project(BIN, auto_load_libs=False)
flag = claripy.BVS("flag", N * 8)

state = p.factory.full_init_state(
    args=[BIN],
    stdin=flag.concat(claripy.BVV(b"\n")),
)

for b in flag.chop(8):
    state.solver.add(b >= 0x20, b <= 0x7e)

sim = p.factory.simgr(state)
sim.explore(
    find=lambda s: b"Correct" in s.posix.dumps(1),
    avoid=lambda s: b"Wrong" in s.posix.dumps(1),
)

if sim.found:
    s = sim.found[0]
    print(s.solver.eval(flag, cast_to=bytes))
```

## Find Addresses Instead Of Strings

```python
FIND = 0x4012ab
AVOID = [0x401240, 0x401260]
sim.explore(find=FIND, avoid=AVOID)
```

Get addresses:

```bash
objdump -d -M intel ./chall | rg -n 'Correct|Wrong|puts|printf|call'
strings -a -tx ./chall | rg 'Correct|Wrong|flag'
```

## argv Input

```python
import angr
import claripy

BIN = "./chall"
N = 24
p = angr.Project(BIN, auto_load_libs=False)
arg = claripy.BVS("arg", N * 8)
state = p.factory.full_init_state(args=[BIN, arg])

for b in arg.chop(8):
    state.solver.add(b >= 0x20, b <= 0x7e)
```

## Hook Noisy Functions

Make compare always continue, or replace expensive/hash functions with constraints.

```python
class PutsHook(angr.SimProcedure):
    def run(self, s):
        return 0

p.hook_symbol("puts", PutsHook())
```

Force `strlen(input) == N`:

```python
class StrlenHook(angr.SimProcedure):
    def run(self, s):
        return claripy.BVV(N, p.arch.bits)

p.hook_symbol("strlen", StrlenHook())
```

## Unicorn Speed

```python
state.options.add(angr.options.UNICORN)
state.options.add(angr.options.ZERO_FILL_UNCONSTRAINED_MEMORY)
state.options.add(angr.options.ZERO_FILL_UNCONSTRAINED_REGISTERS)
```

## When angr Is Wasting Time

```text
1. Avoid libc: auto_load_libs=False.
2. Use addresses instead of stdout strings.
3. Hook strcmp/memcmp/hash functions.
4. Constrain input to printable or known prefix.
5. Start from a later function with call_state() if main setup is noisy.
```

Start at a function:

```python
FUNC = 0x401180
buf = claripy.BVS("buf", 32 * 8)
state = p.factory.call_state(FUNC, buf)
```

If the validator needs a pointer:

```python
addr = 0x500000
state.memory.store(addr, buf)
state = p.factory.call_state(FUNC, addr)
```
