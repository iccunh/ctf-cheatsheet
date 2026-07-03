# Hill Cipher (Known-Plaintext)

## Challenge Source

### CBC 2025 cabin-on-the-hill

```python
H = HillCryptosystem(AlphabeticStrings(), 3)
K = H.random_key()
M = H.encoding("WARNINGIFYOUCANREADTHISYOUSTILLHAVEACHANCETOLIVEWALKFASTERANDDONTLOOKBACKIREPEATDONOTLOOKBACK")
cipher = H.enciphering(K, M)
print("Ciphertet:", cipher)
print("Plaintet:", H.deciphering(K, cipher))
print("Key:", K)
print(H.deciphering(K, H.enciphering(K, M)) == M)
#Ciphertet: RRVXGQYTDXYKPDTLHNPJTZAKREIWNHFWUSOLZYCNYBXJNMPTKFLPALGGPAQTGRONBLCLKGUDYTHFUJMMAINZVHIWNXGO
#Plaintet: WARNINGIFYOUCANREADTHISYOUSTILLHAVEACHANCETOLIVEWALKFASTERANDDONTLOOKBACKIREPEATDONTLOOKBACK
# Flag = CBC{WARNINGIFYOUCANREADTHISYOUSTILLHAVEACHANCETOLIVEWALKFASTERANDDONTLOOKBACKIREPEATDONTLOOKBACK}
#Key: [23  3  0  6]
#[10 10  4 15]
#[24 17 15 15]
#[15 22  8 16]
```

## How It Works

C = K · P mod m - matrix multiplication over Zₘ.

## Solution

Need `n²` known plaintext chars for an `n×n` key matrix.

```
K = C · P⁻¹  mod m
```

**Requirement**: plaintext matrix P must be `n×n` invertible (det(P) coprime with m).

```python
import numpy as np

def recover_key(pt, ct, n, m=256):
    P = np.array([ord(c) for c in pt]).reshape(n, n)
    C = np.array([ord(c) for c in ct]).reshape(n, n)
    det = int(round(np.linalg.det(P))) % m
    adj = det * np.linalg.inv(P)  # adjugate matrix
    P_inv = (pow(det, -1, m) * adj) % m
    K = (C @ P_inv) % m
    return K
```

If `det(P)` shares gcd with `m`, try different known-plaintext pairings or gather more chars.
