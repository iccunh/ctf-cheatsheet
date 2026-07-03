# CBC

## Pick

| What you see | Go to |
| --- | --- |
| MAC is CBC over attacker-controlled message | [CBC-MAC](cbc-mac.md) |

## Checks

```text
fixed IV?
IV attacker-controlled?
padding error differs from MAC/decrypt error?
same key used for encryption and MAC?
can append blocks to a signed message?
```
