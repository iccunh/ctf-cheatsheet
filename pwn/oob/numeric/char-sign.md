# Signed Char Modulo Bypass

**When:** Input is transformed to lowercase letters via `(ch % 26) + 0x61`, but `char` is signed (-128 to 127).

**How it works:** Bytes 0x80-0xFF are negative values when cast to signed `char`. Taking `% 26` of a negative number produces unexpected results (typically negative remainder). This can produce shell metacharacters after the transform.

```c
input[i] = (input[i] % 26) + 0x61;  // char may be signed!
```

For example, byte `0xFF` (signed -1): `(-1 % 26) + 0x61 = -1 + 0x61 = 0x60` = backtick `` ` ``. Used for shell command substitution.

```python
# Find bytes that map to useful chars
for b in range(0x80, 0x100):
    result = ((b % 26) + 0x61) & 0xff
    if chr(result) in ';$|`\n':
        print(hex(b), '->', repr(chr(result)))
```
