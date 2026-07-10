# Patching

Patch when the check is understood but solving is slower than forcing the good path.

## Common Bytes

```text
90                    nop
c3                    ret
31 c0                 xor eax, eax
b8 00 00 00 00        mov eax, 0
b8 01 00 00 00        mov eax, 1
74 xx                 je/jz short
75 xx                 jne/jnz short
eb xx                 jmp short
0f 84 xx xx xx xx     je/jz near
0f 85 xx xx xx xx     jne/jnz near
```

Branch flips:

```text
74 <-> 75
0f 84 <-> 0f 85
7c <-> 7d    jl <-> jge
7e <-> 7f    jle <-> jg
72 <-> 73    jb <-> jae
76 <-> 77    jbe <-> ja
```

## Patch With radare2

```bash
cp chall chall.patched
r2 -w chall.patched
```

```r2
aaa
s 0x401234
pd 8
wa nop
wa ret
wa jmp 0x401280
wx 90909090
wq
```

## Patch With Python

Use offsets from `xxd`, `rabin2 -S`, or a hex editor. Virtual address is not always file offset.

```python
from pathlib import Path

p = Path("chall")
b = bytearray(p.read_bytes())

off = 0x1234
b[off:off+2] = bytes.fromhex("90 90")

Path("chall.patched").write_bytes(b)
```

Replace one unique byte pattern:

```python
from pathlib import Path

b = bytearray(Path("chall").read_bytes())
old = bytes.fromhex("75 12 e8 aa bb cc dd")
new = bytes.fromhex("74 12 e8 aa bb cc dd")
assert b.count(old) == 1
b = b.replace(old, new)
Path("chall.patched").write_bytes(b)
```

## Convert VA To File Offset

For ELF:

```bash
readelf -l ./chall
```

Formula:

```text
file_offset = p_offset + (virtual_address - p_vaddr)
```

Pick the `LOAD` segment where:

```text
p_vaddr <= virtual_address < p_vaddr + p_memsz
```

## Patch Interpreter / RPATH

```bash
patchelf --print-interpreter ./chall
patchelf --print-rpath ./chall
patchelf --set-interpreter ./ld-linux-x86-64.so.2 ./chall
patchelf --set-rpath '$ORIGIN' ./chall
```

## IDA / Ghidra

IDA:

```text
Edit > Patch program > Assemble
Edit > Patch program > Apply patches to input file
```

Ghidra:

```text
Right click instruction > Patch Instruction
File > Export Program > Binary
```

## Patch Strategy

```text
1. Patch anti-debug first.
2. Patch noisy failure exits to return.
3. Flip exactly one final branch if the success block is clear.
4. If the binary decrypts the flag after validation, force the branch and let it decrypt.
5. If the flag is only accepted as input, solve instead of patching.
```

Do not patch away code that computes the flag.
