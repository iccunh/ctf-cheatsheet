# Recover Parameter

Referensi: Cryptohack ECC

```python
from collections import namedtuple
from Crypto.Util.number import bytes_to_long, long_to_bytes
from sage.all import GF, EllipticCurve, discrete_log

# Parameter yang diberikan.
p = 4368590184733545720227961182704359358435747188309319510520316493183539079703

# Titik dasar G (diberikan dalam challenge)
gx = 8742397231329873984594235438374590234800923467289367269837473862487362482
gy = 225987949353410341392975247044711665782695329311463646299187580326445253608

# Public key Q = d * G
Qx = 2582928974243465355371953056699793745022552378548418288211138499777818633265
Qy = 2421683573446497972507172385881793260176370025964652384676141384239699096612

# Hitung parameter a dan b dari persamaan:
# y^2 = x^3 + a*x + b, dengan kedua titik G dan Q berada pada kurva tersebut.
# Rumus: a = ((gy^2 - Qy^2) - (gx^3 - Qx^3)) / (gx - Qx)  (mod p)
#       b = gy^2 - gx^3 - a*gx  (mod p)

# https://github.com/jvdsn/crypto-attacks/blob/master/attacks/ecc/parameter_recovery.py
a = (((gy**2 - Qy**2) - (gx**3 - Qx**3)) * pow(gx - Qx, -1, p)) % p
b = (gy**2 - gx**3 - a * gx) % p

print("Nilai a:", a)
print("Nilai b:", b)

# Karena kurva singular kita berbentuk:
# y^2 = x^3 + 0*x^2 + a*x + b, kita set:
a2 = 0
a4 = a
a6 = b

def attack(p, a2, a4, a6, Gx, Gy, Px, Py):
    """
    Menyelesaikan masalah discrete logarithm pada kurva singular 
    (y^2 = x^3 + a2*x^2 + a4*x + a6).
    
    Parameter:
      - p: bilangan prima untuk field
      - a2, a4, a6: parameter-parameter kurva
      - Gx, Gy: koordinat titik dasar G
      - Px, Py: koordinat titik P = d*G
    Return:
      - l sedemikian sehingga l * G == P
    """
    x = GF(p)["x"].gen()
    f = x ** 3 + a2 * x ** 2 + a4 * x + a6
    roots = f.roots()
    
    # Kasus singularitas berupa cusp: hanya ada satu akar (dengan multiplicity 3)
    if len(roots) == 1:
        alpha = roots[0][0]
        u = (Gx - alpha) / Gy
        v = (Px - alpha) / Py
        return int(v / u)
    
    # Kasus singularitas berupa node: ada dua akar, salah satunya ber-multiplicity 2
    if len(roots) == 2:
        if roots[0][1] == 2:
            alpha = roots[0][0]
            beta = roots[1][0]
        elif roots[1][1] == 2:
            alpha = roots[1][0]
            beta = roots[0][0]
        else:
            raise ValueError("Diharapkan salah satu akar memiliki multiplicity 2.")
        t = (alpha - beta).sqrt()
        u = (Gy + t * (Gx - alpha)) / (Gy - t * (Gx - alpha))
        v = (Py + t * (Px - alpha)) / (Py - t * (Px - alpha))
        return int(v.log(u))
    
    raise ValueError(f"Jumlah akar yang tidak terduga: {len(roots)}.")

# Gunakan attack() untuk mendapatkan nilai d (yang merupakan representasi integer flag).
# https://github.com/jvdsn/crypto-attacks/blob/master/attacks/ecc/singular_curve.py
d = attack(p, a2, a4, a6, gx, gy, Qx, Qy)
print("Nilai d (integer):", d)

# Konversikan integer d ke bytes dan tampilkan flag.
flag_bytes = long_to_bytes(d)
print("Flag:", flag_bytes)
```
