# Pwn

### Quick Patching

```bash
# Patch binary to use custom libc
patchelf --set-interpreter ./ld-2.31.so --set-rpath . ./binary

# NOP out a byte
python3 -c "
binary = open('./binary', 'r+b')
binary.seek(0x1234)
binary.write(b'\x90')
binary.close()
"

# Patch bytes
printf '\x90\x90\x90' | dd of=binary bs=1 seek=$((0x1234)) conv=notrunc
```

### References

* [https://ir0nstone.gitbook.io/notes](https://ir0nstone.gitbook.io/notes)

