# Dynamic Analysis

Use dynamic analysis when the binary already tells you the answer at runtime: compare buffers, decrypted strings, generated keys, or branch outcomes.

## GDB Setup

```gdb
set disassembly-flavor intel
set pagination off
set confirm off
set follow-fork-mode child
set detach-on-fork off
set disable-randomization on
```

Run with input:

```gdb
r <<< "AAAA"
r < input.txt
set args arg1 arg2
```

## Break On Checks

```gdb
b strcmp
b strncmp
b memcmp
b puts
b printf
b exit
r
```

Dump compare args on x86_64:

```gdb
x/s $rdi
x/s $rsi
x/64bx $rdi
x/64bx $rsi
finish
```

Dump compare args on i386:

```gdb
x/s *(char **)($esp+4)
x/s *(char **)($esp+8)
x/64bx *(char **)($esp+4)
x/64bx *(char **)($esp+8)
```

## Catch Syscalls

```gdb
catch syscall open
catch syscall openat
catch syscall read
catch syscall write
catch syscall ptrace
catch syscall mprotect
catch syscall mmap
r
```

Useful at a syscall stop:

```gdb
p/x $rax
p/x $rdi
p/x $rsi
p/x $rdx
x/s $rdi
x/80bx $rsi
```

## Watch Buffer Changes

```gdb
b *main
r
watch *(char[32]*)0xADDR
awatch *(char*)0xADDR
c
```

If the input buffer address is in `$rbp-0x40`:

```gdb
x/64bx $rbp-0x40
watch *(char*)($rbp-0x40)
```

## Trace Without GDB

```bash
ltrace -f -s 200 ./chall
strace -f -s 200 -o trace.txt ./chall
rg 'open|read|write|ptrace|mprotect|mmap|flag|strcmp|memcmp' trace.txt
```

Feed input:

```bash
printf 'AAAA\n' | ltrace -f -s 200 ./chall
printf 'AAAA\n' | strace -f -s 200 ./chall
```

## Force Branch Result

At a compare return:

```gdb
finish
set $rax=0
c
```

For `ptrace(PTRACE_TRACEME)` anti-debug:

```gdb
catch syscall ptrace
r
finish
set $rax=0
c
```

For a `test eax, eax; jne fail` style check:

```gdb
set $eax=0
set $eflags = $eflags & ~0x40
```

## Record Every Compare

```gdb
commands
silent
printf "strcmp/memcmp hit\n"
x/s $rdi
x/s $rsi
x/32bx $rdi
x/32bx $rsi
c
end
```

If symbols are stripped, break on PLT addresses:

```bash
objdump -d -M intel ./chall | rg '<(strcmp|memcmp|strncmp)@plt>'
```

```gdb
b *0xADDR
```

## LD_PRELOAD Compare Logger

```c
#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdio.h>
#include <string.h>

int strcmp(const char *a, const char *b) {
    static int (*real)(const char *, const char *);
    if (!real) real = dlsym(RTLD_NEXT, "strcmp");
    fprintf(stderr, "strcmp(%s, %s)\n", a, b);
    return real(a, b);
}

int memcmp(const void *a, const void *b, size_t n) {
    static int (*real)(const void *, const void *, size_t);
    if (!real) real = dlsym(RTLD_NEXT, "memcmp");
    fprintf(stderr, "memcmp n=%zu\n", n);
    fwrite(a, 1, n, stderr); fputc('\n', stderr);
    fwrite(b, 1, n, stderr); fputc('\n', stderr);
    return real(a, b, n);
}
```

```bash
gcc -shared -fPIC hook.c -o hook.so -ldl
LD_PRELOAD=$PWD/hook.so ./chall
```
