# Heap

## Triage Steps

When you see a note/arena/vault program with `add`/`edit`/`show`/`delete`, run through these checks in order:

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

| Check | What to test | What it might be |
|

-|

-|

|
| Add two, delete one, show it | Call `delete(0)`, then `show(0)` | Use-after-free (UAF) |
| Delete same index twice | Call `delete(0)` twice | Double free |
| Edit after delete | Call `delete(0)`, then `edit(0, data)` | UAF write |
| Resize check | Resize a chunk, then read it | Stale pointer / overlap |
| Free >0x410, show it | `add(0, 0x500)`, `delete(0)`, `show(0)` | Unsorted bin -> libc leak |

### Glibc version matters

- **< 2.26:** Fastbin, no tcache
- **2.26 - 2.28:** Tcache introduced, no key/double-free check
- **2.29 - 2.33:** Tcache key added (double-free detection), safe-linking in 2.32+
- **2.34+:** `__free_hook`/`__malloc_hook` removed. Use FSOP or tcache poison to `_IO_2_1_stdout_`

Check with:

```bash
ldd ./chall
./ld-linux-x86-64.so.2 --version
strings ./libc.so.6 | grep "GNU C Library"
```
