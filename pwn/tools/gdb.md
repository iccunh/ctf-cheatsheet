# GDB

## Breakpoints

```gdb
b main                    # function
b *main+42                # offset from symbol
b 0x555555555123          # absolute address
b calc if $rax==0         # conditional
b *$rebase(0x1234)        # PIE-aware (pwndbg/gef)

info break    / i b       # list
delete        / d         # delete all
d 1                       # delete #1
disable 1                 # disable #1 (keep it)
enable 1                  # re-enable
```

## Running

```gdb
r           # run
r < input.txt             # with input
c           # continue
n           # next (step over, source line)
ni          # next instruction
s           # step into
si          # step instruction
fin         # finish function
until 0x...               # run until address
start       # break at main, run
```

## Print / Examine

```gdb
# Print formats
p/x $rax       # hex
p/d $rax       # decimal
p/t $rax       # binary
p/s $rdi       # string
p/c $rax       # char
p/a $rip       # as address (symbol+offset)

# Examine memory  (x/<count><format><size>)
x/10gx $rsp    # 10 qwords (8B) in hex
x/20wx $rbp    # 20 words (4B) in hex
x/s $rdi       # string
x/i $rip       # one instruction
x/10i $rip     # 10 instructions
x/32bx $rsp    # 32 bytes
```

| Size | Meaning       |
| ---- | ------------- |
| b    | byte (1B)     |
| h    | halfword (2B) |
| w    | word (4B)     |
| g    | giant (8B)    |

## Registers & Memory

```gdb
info registers     / i r    # all regs
i r rax rbx rcx             # specific

set $rax = 0                # modify register
set {long}$rsp = 0xdeadbeef # write to memory
set *((char*)0x...)=0x90    # patch byte

# Jump anywhere
jump *0x...
set $rip = 0x...
```

## Stack / Backtrace

```gdb
bt          # backtrace
frame 0     / fr 0     # switch to frame
up          # parent frame
down        # child frame

info frame  # current frame details
info locals # local variables
info args   # function arguments
```

## Searching

```gdb
search /bin/sh                    # pwndbg
search-pattern /bin/sh            # gef
find 0x7ffff7... 0x7ffff7..., "/bin/sh"
```

## Memory Map

```gdb
vmmap         # pwndbg/gef
info proc map # vanilla GDB
```

## pwndbg-specific

```gdb
telescope $rsp    # dump stack with arrows
telescope $rsp 30 # 30 entries
canary            # show canary
checksec          # show protections
hexdump $rsp      # hex + ASCII
got               # GOT entries
plt               # PLT entries
procinfo          # process info
$base             # PIE base address
$rebase(0x1234)   # convert offset to actual addr
```

## GDB Inline ROP

```gdb
# After hitting breakpoint with overflow
p pop_rdi_ret = 0x401016
p bin_sh = 0x7ffff7...
p system = 0x7ffff7...

# Manually build ROP on stack
set {long}$rsp = pop_rdi_ret
set {long}($rsp+8) = bin_sh
set {long}($rsp+0x10) = system
# Then continue
c
```
