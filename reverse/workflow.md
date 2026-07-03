# Reverse Workflow

## Triage

```bash
file ./chall
readelf -h ./chall
objdump -f ./chall
strings -n 4 ./chall | head
rabin2 -I ./chall
rabin2 -zz ./chall
binwalk -e ./chall
```

Check hidden execution paths:

```text
.init_array
__libc_start_main wrapper
C++ exception handlers
signal handlers
constructor/destructor functions
```

## Static Flow

1. Find compare: `memcmp`, `strcmp`, `strncmp`, byte loop, hash compare.
2. Walk backward from compare to transform.
3. Dump constants: s-box, CRC table, custom base64 alphabet, PRNG seed.
4. Rebuild transform in Python.
5. Invert directly, brute-force with pruning, or solve with Z3.

## Dynamic

```gdb
b memcmp
b strcmp
b strncmp
r
x/32bx $rdi
x/32bx $rsi
```

Patch noisy exits or anti-debug checks:

```asm
nop
ret
xor eax, eax
mov eax, 1
```

Useful x86/x64 bytes:

```text
90                  ; nop
c3                  ; ret
31 c0               ; xor eax, eax
b8 01 00 00 00      ; mov eax, 1
74 xx / 75 xx       ; jz / jnz short
eb xx               ; jmp short
```

## IDA Patch

1. `Edit > Patch program > Assemble`
2. Flip branch: `jz fail` <-> `jnz fail`
3. Kill exit: `call exit` -> `nop` bytes
4. Save: `Edit > Patch program > Apply patches to input file`

## Red Flags

* Real logic in init/exception/signal handler.
* Swap/shuffle after validator returns.
* Custom CRC polynomial or custom base64 alphabet.
* PRNG seed from time, env, PID, or file metadata.
* Decompression or embedded payload hidden behind magic bytes.
