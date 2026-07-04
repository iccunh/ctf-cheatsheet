# Pwn

## Quick Patching

```bash
patchelf --set-interpreter ./ld-2.31.so --set-rpath . ./binary
python3 -c "open('./binary', 'r+b').seek(0x1234); open('./binary', 'r+b').write(b'\x90')"
printf '\x90\x90\x90' | dd of=binary bs=1 seek=$((0x1234)) conv=notrunc
```

## Techniques by Category

### [Stack](stack/)

| File                                             | What                                                         |
| ------------------------------------------------ | ------------------------------------------------------------ |
| [ret2win](stack/overflow/ret2win.md)             | Ret2win, stack diagram, alignment fix                        |
| [ret2libc](stack/overflow/ret2libc.md)           | Ret2libc (no PIE, PIE+leak, multi-connection), stack diagram |
| [ret2shellcode](stack/overflow/ret2shellcode.md) | Ret2shellcode + mprotect chain, stack diagram                |
| [ROP basics](stack/overflow/basics.md)           | Gadget finding (ROPgadget/pwntools), one_gadget, ld-only ROP |
| [ORW ROP](stack/overflow/orw.md)                 | Open/read/write chain (seccomp bypass), stack diagram        |
| [ret2dlresolve](stack/overflow/dlresolve.md)     | Fake relocation, no libc leak                                |
| [ret2csu](stack/overflow/csu.md)                 | Universal gadget, stack diagram                              |
| [SROP](stack/overflow/srop.md)                   | Sigreturn frame, full register control, stack diagram        |
| [local-var](stack/data/local-var.md)             | Adjacent variable overwrite (auth flag, etc.)                |
| [caller-frame](stack/data/caller-frame.md)       | Inter-frame overflow to corrupt caller's data                |

### [Heap](heap/)

| File                             | What                                                           |
| -------------------------------- | -------------------------------------------------------------- |
| [triage](heap/README.md)         | Triage steps (add/edit/show/delete), glibc version differences |
| [uaf-tcache](heap/uaf-tcache.md) | Unsorted bin leak, safe-linking, tcache poison to GOT/hooks    |
| [fsop](heap/fsop.md)             | FSOP: why (hooks removed), tcache poison to stdout, fake FILE  |

### [Shellcode](shellcode/)

| File                                    | What                                                  |
| --------------------------------------- | ----------------------------------------------------- |
| [start](shellcode/start.md)             | Shellcraft, staged read, ret2shellcode, i386          |
| [constrained](shellcode/constrained.md) | 10B stub, bad bytes, syscall blacklist, ORW, sendfile |

### [OOB](oob/)

| File                                      | What                                               |
| ----------------------------------------- | -------------------------------------------------- |
| [unchecked-index](oob/unchecked-index.md) | Bug shapes, index math, targets by protection      |
| [struct-field](oob/struct-field.md)       | Off-by-one to function ptr, memcpy overflow        |
| [wrap](oob/numeric/wrap.md)               | Unsigned overflow / ID collision                   |
| [strcmp-null](oob/numeric/strcmp-null.md) | Null byte strcmp bypass on random password         |
| [char-sign](oob/numeric/char-sign.md)     | Signed char modulo to produce shell metacharacters |

### [Injection](injection/)

| File                                        | What                                           |
| ------------------------------------------- | ---------------------------------------------- |
| [format-string](injection/format-string.md) | Recon, offset find, arbitrary r/w via %s/%n    |
| [command](injection/command.md)             | System() injection, blacklist/whitelist bypass |

### [Race](race/)

| File                     | What                                                |
| ------------------------ | --------------------------------------------------- |
| [README](race/README.md) | TOCTOU symlink swap, validate-after-use thread race |

### [Kernel](kernel/)

| File                       | What                                                           |
| -------------------------- | -------------------------------------------------------------- |
| [README](kernel/README.md) | QEMU setup, kernel UAF, physmap spray + core_pattern overwrite |

### [Tools](tools/)

| File                          | What                                                                   |
| ----------------------------- | ---------------------------------------------------------------------- |
| [gadgets](tools/gadgets.md)   | ROPgadget + pwntools, ELF/libc symbols, auto/manual chains, one_gadget |
| [gdb](tools/gdb.md)           | Breakpoints, examine, registers, pwndbg, inline ROP                    |
| [template](tools/template.md) | Full exploit template: auto offset, libc leak, shell                   |

## References

- [https://ir0nstone.gitbook.io/notes](https://ir0nstone.gitbook.io/notes)
