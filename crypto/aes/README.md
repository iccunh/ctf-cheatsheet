# AES

## Pick

| What you see | Go to |
| --- | --- |
| Same nonce/IV stream, XOR-able ciphertexts | [CTR keystream reuse](ctr/keystream-reuse.md) |
| CTR decrypt oracle or malleability | [CTR padding oracle](ctr/padding-oracle.md) |
| CBC MAC with attacker-controlled messages | [CBC-MAC](cbc/cbc-mac.md) |
| Service mixes modes / exposes encryptions | [Mode confusion](mode-confusion.md) |
| Repeated blocks / block oracle | [ECB](ecb/README.md) |
| Small keyspace per frame/block | [Frame key search](ecb/frame-key-search.md) |
| GCM nonce reuse / tag equations | [GCM](gcm.md) |
| RC4-style stream cipher | [RC4](rc4.md) |

## Blocks

```python
def chunks(x, n=16):
    return [x[i:i+n] for i in range(0, len(x), n)]

for i, b in enumerate(chunks(ct)):
    print(i, b.hex())
```

```python
def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
        
cipher = list(chunks(cipher, 16))
```

## XOR

```python
from pwn import xor

pt2 = xor(ct1, ct2, known_pt1)
```
