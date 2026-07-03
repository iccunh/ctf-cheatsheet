# ECB

## Pick

| What you see | Go to |
| --- | --- |
| Encrypt arbitrary plaintext, unknown suffix | [Custom decrypt](custom-decrypt.md) |
| Key comes from small random/search space | [Key random](key-random.md) |
| Many correlated encrypted frames | [Frame key search](frame-key-search.md) |

## Repeated Blocks

```python
blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
for i, b in enumerate(blocks):
    print(i, b.hex(), blocks.count(b))
```
