# Reverse Workflow

## Triage

```bash
file ./chall
checksec --file=./chall
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

If the binary is not native C/C++, go to [Runtimes](runtimes.md) before cleaning decompiler output.

## Dynamic

```gdb
b memcmp
b strcmp
b strncmp
r
x/32bx $rdi
x/32bx $rsi
```

Auto-dump common compares on x86_64:

```gdb
set pagination off
set disassembly-flavor intel

b memcmp
commands
silent
printf "memcmp len=%ld\n", $rdx
x/64bx $rdi
x/64bx $rsi
c
end

b strcmp
commands
silent
printf "strcmp\n"
x/s $rdi
x/s $rsi
c
end

b strncmp
commands
silent
printf "strncmp len=%ld\n", $rdx
x/s $rdi
x/s $rsi
c
end
```

Fast syscall/import tracing:

```bash
ltrace -s 200 ./chall
strace -f -e trace=openat,read,write,execve,mmap,mprotect ./chall
rabin2 -zz ./chall | rg -i 'flag|correct|wrong|fail|success|key|serial'
readelf -Ws ./chall | rg 'strcmp|strncmp|memcmp|scanf|fgets|read|rand|srand|time|ptrace'
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
* `strcmp` never appears because comparison is inlined byte-by-byte.
* Success string is encrypted and only appears after the right branch.
* The input is transformed in place, so the original buffer is gone by compare time.

## Solver Choice

| Shape | Fast Approach |
| --- | --- |
| Per-byte independent checks | brute force each byte. |
| XOR/add/rol chain | invert transforms in reverse order. |
| Prefix sum / rolling state | recover first byte, then walk forward/backward. |
| Permutation / shuffle | build inverse permutation. |
| S-box | invert table. |
| CRC/hash compare | identify polynomial or brute force short chunks. |
| Nonlinear bit-vector math | Z3 BitVec, not Int. |
| Split input halves | meet-in-the-middle. |
| Anti-debug only blocks run | patch branch or force return value. |

## Terraform / Declarative Validators

Terraform challenge files often hide a byte transform in `locals {}` blocks and reveal only:

```hcl
output "result" {
  value = local.ok ? "ACCESS GRANTED" : "ACCESS DENIED"
}
```

Workflow:

```text
1. Start from the final boolean, e.g. local.ok = local.final_array == local.target_array.
2. Build the dependency chain backward: final_array -> transform_3 -> transform_2 -> transform_1 -> var.flag.
3. Ignore locals that do not flow into the final boolean.
4. Invert each operation in Python.
```

Common inverse operations:

```python
# rotate / index shift
for i, v in enumerate(target):
    prev[(i + shift) % n] = v

# prefix sums: y[i] = sum(x[:i+1]) mod 256
prev = 0
x = []
for v in y:
    x.append((v - prev) % 256)
    prev = v

# modular multiply by odd constant
x = [(v * pow(k[i % len(k)], -1, 256)) % 256 for i, v in enumerate(y)]

# permutation: y[i] = x[perm[i]]
x = [0] * len(y)
for i, p in enumerate(perm):
    x[p] = y[i]

# S-box
inv_sbox = {v: i for i, v in enumerate(sbox)}
x = [inv_sbox[v] for v in y]

# additive mask
x = [(v - mask[i % len(mask)]) % 256 for i, v in enumerate(y)]
```

Verify by writing recovered bytes as `flag=[...]` in `.tfvars` and running:

```bash
terraform apply -var-file=flag.tfvar
```
