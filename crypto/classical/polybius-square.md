# Polybius Square (8×8)

## Challenge Source

### CBC 2025 8-polybius-square

```python
import random

def create_polybius_square():
    chrMap  = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz{_ ,.!'#*58}"
    polybius_square = [list(chrMap[i:i+8]) for i in range(0, 64, 8)]

    keyMap = list(range(8))
    random.shuffle(keyMap)

    shuffled_polybius = []
    for i in range(8):
        shuffled_row = []
        for j in range(8):
            shuffled_row.append(polybius_square[keyMap[i]][j])
        shuffled_polybius.append(shuffled_row)

    return shuffled_polybius

def find_position(c, polybius_square):
    for i in range(8):
        for j in range(8):
            if polybius_square[i][j] == c:
                return (i, j)

def encrypt(text, polybius_square):
    cipher = ""
    for char in text:
        r, c = find_position(char, polybius_square)
        cipher += str(r) + str(c)
    return cipher

polybius_square = create_polybius_square()
plaintext = "I cant encrypt my flag using The Classic _5x5_ grid. An _8x8_ polybius square Became the perfect Choice for my flag! Anyway, here's the flag you're looking for CBC{CheckmAtE_on_the_CIphEr_BOArd}"
cipher = encrypt(plaintext, polybius_square)

print(f"cipher = '{cipher}'")
print(f"hint = '{plaintext[:118]}'")
```

## How It Works

8×8 grid of 64 chars (A-Z, a-z, 0-9, `+`, `/`). Each plaintext char → 2-digit (row, col).

```
  0 1 2 3 4 5 6 7
0 A B C D E F G H
1 I J K L M N O P
2 Q R S T U V W X
3 Y Z a b c d e f
4 g h i j k l m n
5 o p q r s t u v
6 w x y z 0 1 2 3
7 4 5 6 7 8 9 + /
```

`H` → `07`, `x` → `62`

## Solution

Given known plaintext-ciphertext pairs, reconstruct mapping:

```python
def recover_grid(pt, ct):
    mapping = {}
    for p, c in zip(pt, ct):
        mapping[p] = (int(c[0]), int(c[1]))
    grid = [['']*8 for _ in range(8)]
    for ch, (r, c) in mapping.items():
        grid[r][c] = ch
    return grid
```
