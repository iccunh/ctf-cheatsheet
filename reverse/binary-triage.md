# Binary Triage

Goal: identify the file, protections, strings, imports, and likely validator path before opening a decompiler.

## First Commands

```bash
file ./chall
sha256sum ./chall
checksec --file=./chall
readelf -h -l -S -s -r -d ./chall
objdump -f -p ./chall
strings -a -n 4 -tx ./chall | tee strings.txt
strings -a -el -n 4 ./chall | head
rabin2 -I ./chall
rabin2 -zz ./chall | head -200
binwalk ./chall
```

## Find Main / Entry

```bash
readelf -h ./chall | rg 'Entry'
objdump -d -M intel ./chall | less
nm -an ./chall | rg ' main$|_start|init|fini'
rabin2 -s ./chall | rg 'main|entry|sym\.|imp\.'
```

Stripped ELF path:

```gdb
gdb -q ./chall
set disassembly-flavor intel
starti
info files
b __libc_start_main
r
```

At `__libc_start_main`, the first argument is usually `main` on x86_64:

```gdb
x/i $rdi
b *$rdi
c
```

## Imports Decide Strategy

```bash
readelf -Ws ./chall | rg 'UND|strcmp|strncmp|memcmp|scanf|fgets|read|open|ptrace|mprotect|system|execve|AES|MD5|SHA|rand|srand|time'
rabin2 -i ./chall
objdump -R ./chall
```

PE imports:

```bash
rabin2 -i chall.exe
objdump -x chall.exe | rg 'DLL Name|strcmp|memcmp|MessageBox|CreateFile|ReadFile|WriteFile|IsDebuggerPresent|CheckRemoteDebuggerPresent'
strings -a -el chall.exe | rg -i 'flag|correct|wrong|serial|key'
```

| Import / Pattern | First Move |
| --- | --- |
| `strcmp`, `memcmp`, `strncmp` | Break there, dump both buffers. |
| `scanf`, `fgets`, `read` | Break after input, watch transformed buffer. |
| `rand`, `srand`, `time` | Fix seed or patch time. |
| `ptrace`, `prctl`, `getppid` | Patch anti-debug or force success in gdb. |
| `mprotect`, RWX page | Shellcode, unpacking, or self-modifying code. |
| No useful imports | Static linking, Go/Rust, packed binary, or custom syscalls. |
| `IsDebuggerPresent` | Patch return or force zero in debugger. |

## Packers / Embedded Files

```bash
upx -t ./chall
upx -d ./chall -o chall.unpacked
binwalk -e ./chall
7z l ./chall
```

High entropy or tiny import table often means packed/encrypted code. Run once under gdb and break on:

```gdb
catch syscall mprotect
catch syscall mmap
catch syscall write
```

## File-Type Clues

```bash
strings -a ./chall | rg -i 'pyinstaller|pyi-|python|go build|pclntab|rust|panic|dotnet|mscorlib|java|kotlin|android|il2cpp|mono|node|pkg|asar'
```

| Clue | Page |
| --- | --- |
| `PyInstaller`, `PYZ` | [Runtimes](runtimes.md#python--pyinstaller) |
| `mscorlib`, `.NET`, `BSJB` | [Runtimes](runtimes.md#net) |
| `PK...`, `.class`, `META-INF` | [Runtimes](runtimes.md#java--jar) |
| `AndroidManifest.xml`, `classes.dex` | [Runtimes](runtimes.md#android) |
| `gopclntab`, `Go build ID` | [Runtimes](runtimes.md#go) |
| `rust_begin_unwind`, `panic_bounds_check` | [Runtimes](runtimes.md#rust) |

## What To Extract

```text
1. Exact input read length.
2. Final compare target.
3. Transform constants: xor key, s-box, permutation, CRC table, PRNG seed.
4. Whether bytes wrap mod 256/32/64.
5. Whether check is per-byte, chained, or global.
```

If the decompiler is ugly, do not clean everything. Name only:

```text
input buffer
target bytes
transform function
compare branch
failure/success blocks
```
