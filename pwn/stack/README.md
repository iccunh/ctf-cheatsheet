# Stack

## overflow/ — Return address overwrite (all stack pivots start here)

| Technique                                  | When                                                    | Prerequisites                          |
| ------------------------------------------ | ------------------------------------------------------- | -------------------------------------- |
| [ret2win](overflow/ret2win.md)             | Binary has a win/shell function                         | No canary, known win address           |
| [ret2libc](overflow/ret2libc.md)           | No win function, need `system("/bin/sh")`               | libc leak, pop rdi                     |
| [ret2shellcode](overflow/ret2shellcode.md) | NX disabled                                             | RWX region, shellcode address          |
| [ROP basics](overflow/basics.md)           | Gadget finding, chain building, one_gadget, ld-only ROP | Overflow to start chain                |
| [ORW ROP](overflow/orw.md)                 | `execve`/`system` blocked by seccomp                    | open/read/write PLT, pop rdi/rsi/rdx   |
| [ret2dlresolve](overflow/dlresolve.md)     | No libc leak, dynamic linking available                 | Partial RELRO, BSS for fake structures |
| [ret2csu](overflow/csu.md)                 | Missing pop rdi/rsi/rdx gadgets                         | `__libc_csu_init` present              |
| [SROP](overflow/srop.md)                   | Need full register control, few gadgets                 | syscall gadget, way to set rax=15      |

## data/ — Non-return-address overwrite

| Technique                            | When                                                  | Prerequisites                                  |
| ------------------------------------ | ----------------------------------------------------- | ---------------------------------------------- |
| [local-var](data/local-var.md)       | Adjacent variable on stack after buffer               | Variable near buffer                           |
| [caller-frame](data/caller-frame.md) | Overflow reaches caller's frame to corrupt check data | Overflow large enough to reach caller's locals |
