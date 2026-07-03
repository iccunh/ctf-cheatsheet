# HNP Recover d

Jika r s tidak sama tetapi nonce-nya bias (seperti contoh ini 160 bit). Bisa pakai HNP

referensi: Cryptohack dan [https://github.com/jvdsn/crypto-attacks/blob/master/attacks/hnp/lattice\_attack.py](https://github.com/jvdsn/crypto-attacks/blob/master/attacks/hnp/lattice_attack.py)

```python
#!/usr/bin/env sage -python
import hashlib
from Crypto.Util.number import bytes_to_long, long_to_bytes
from ecdsa.ecdsa import curve_256, generator_256
from ecdsa import ellipticcurve
from sage.all import *

# ----------------------------------------------------------------
# Data Tantangan (challenge data)
# ----------------------------------------------------------------
hidden_flag = (16807196250009982482930925323199249441776811719221084165690521045921016398804,
               72892323560996016030675756815328265928288098939353836408589138718802282948311)

pubkey_point = (48780765048182146279105449292746800142985733726316629478905429239240156048277,
                74172919609718191102228451394074168154654001177799772446328904575002795731796)

sig1 = {
    'msg': 'I have hidden the secret flag as a point of an elliptic curve using my private key.',
    'r': int("0x91f66ac7557233b41b3044ab9daf0ad891a8ffcaf99820c3cd8a44fc709ed3ae", 16),
    's': int("0x1dd0a378454692eb4ad68c86732404af3e73c6bf23a8ecc5449500fcab05208d", 16)
}
sig2 = {
    'msg': 'The discrete logarithm problem is very hard to solve, so it will remain a secret forever.',
    'r': int("0xe8875e56b79956d446d24f06604b7705905edac466d5469f815547dea7a3171c", 16),
    's': int("0x582ecf967e0e3acf5e3853dbe65a84ba59c3ec8a43951bcff08c64cb614023f8", 16)
}
sig3 = {
    'msg': 'Good luck!',
    'r': int("0x566ce1db407edae4f32a20defc381f7efb63f712493c3106cf8e85f464351ca6", 16),
    's': int("0x9e4304a36d2c83ef94e19a60fb98f659fa874bfb999712ceb58382e2ccda26ba", 16)
}

# Parameter kurva
G = generator_256
q = G.order()

# Fungsi nonce deterministik seperti pada tantangan
def nonce_for_msg(d, msg):
    hsh = hashlib.sha1(msg.encode()).digest()
    data = long_to_bytes(d) + hsh
    return int(hashlib.sha1(data).hexdigest(), 16)

# Fungsi bantu untuk mengubah hash pesan ke integer
def sha1_to_int(msg):
    return bytes_to_long(hashlib.sha1(msg.encode()).digest())

# ----------------------------------------------------------------
# Kelas PartialInteger sederhana untuk HNP attack
# Karena kita tidak tahu bit MSB sama sekali, kita anggap nilai known = 0.
# Total bit nonce = 160 (SHA-1 output).
# ----------------------------------------------------------------
class PartialInteger:
    def __init__(self, bit_length, known_msb=0):
        self.bit_length = bit_length
        self.known_msb = known_msb  # tidak ada informasi, jadi 0
    def get_known_msb(self):
        return (self.known_msb, 0)  # (nilai, panjang bit yang diketahui)
    def get_unknown_lsb(self):
        return self.bit_length  # semua 160 bit tidak diketahui
    def get_known_lsb(self):
        return (0, 0)
    def get_unknown_msb(self):
        return 0
    def get_known_middle(self):
        return (0, self.bit_length)
    def sub(self, values):
        # Pada kasus sederhana, nilai nonce utuh adalah nilai yang dipulihkan.
        return values[0]

# ----------------------------------------------------------------
# Kode HNP Lattice Attack berbasis Sage
# (diadaptasi dari kode yang kamu berikan)
# ----------------------------------------------------------------
import os
import sys
from sage.all import QQ, ZZ, matrix, vector

def shortest_vectors(B):
    # Gunakan LLL bawaan Sage untuk mendapatkan basis yang direduksi,
    # dan kembalikan vektor–vektor pendek (di sini sebagai iterator)
    B_lll = B.LLL()
    for row in B_lll.rows():
        yield row

def attack(a, b, m, X):
    """
    Membentuk lattice dan mencari solusi pendek.
    a: list dari list koefisien (misalnya, [ [s_i^-1 * r_i mod n] ])
    b: list konstanta (misalnya, s_i^-1 * h_i mod n)
    m: modulus (n)
    X: batas atas untuk nilai nonce (di sini 2^160)
    """
    n1 = len(a)
    n2 = len(a[0])
    B = matrix(QQ, n1 + n2 + 1, n1 + n2 + 1)
    for i in range(n1):
        for j in range(n2):
            B[n1 + j, i] = a[i][j]
        B[i, i] = m
        B[n1 + n2, i] = b[i] - X // 2
    for j in range(n2):
        B[n1 + j, n1 + j] = X / QQ(m)
    B[n1 + n2, n1 + n2] = X
    for v in shortest_vectors(B):
        xs = [int(v[i] + X // 2) for i in range(n1)]
        ys = [(int(v[n1 + j] * m) // X) % m for j in range(n2)]
        if all(y != 0 for y in ys) and v[n1 + n2] == X:
            yield xs, ys

def dsa_known_msb(n, h, r, s, k):
    """
    Menggunakan informasi MSB nonce (di sini tidak diketahui sama sekali)
    untuk memulihkan private key.
    n: modulus (q)
    h, r, s: list nilai–nilai dari signature (dengan h = sha1(msg) sebagai integer)
    k: list PartialInteger untuk nonce (di sini semua 160 bit unknown)
    """
    a = []
    b = []
    X = 0
    for hi, ri, si, ki in zip(h, r, s, k):
        msb, msb_bit_length = ki.get_known_msb()  # (0, 0)
        shift = 2 ** ki.get_unknown_lsb()          # shift = 2^160
        a.append([(pow(si, -1, n) * ri) % n])
        b.append((pow(si, -1, n) * hi - shift * msb) % n)
        X = max(X, shift)
    for k_, x in attack(a, b, n, X):
        yield x[0], [ki.sub([ki_]) for ki, ki_ in zip(k, k_)]

# ----------------------------------------------------------------
# Persiapan data untuk HNP attack
# ----------------------------------------------------------------
h_list = [sha1_to_int(sig1['msg']), sha1_to_int(sig2['msg']), sha1_to_int(sig3['msg'])]
r_list = [sig1['r'], sig2['r'], sig3['r']]
s_list = [sig1['s'], sig2['s'], sig3['s']]

# Buat list PartialInteger untuk nonce (panjang 160 bit, known = 0)
k_partial = [PartialInteger(160) for _ in range(3)]

# ----------------------------------------------------------------
# Fungsi untuk memulihkan private key d menggunakan HNP lattice attack
# ----------------------------------------------------------------
def recover_private_key():
    for d_candidate, nonce_candidates in dsa_known_msb(q, h_list, r_list, s_list, k_partial):
        # Verifikasi candidate d dengan memeriksa salah satu persamaan signature
        valid = True
        for sig in [sig1, sig2, sig3]:
            # Perhitungan nonce deterministik (meski sebenarnya dalam attack kita pulihkan informasi parsial)
            k_calc = nonce_for_msg(d_candidate, sig['msg'])
            # Persamaan: s * k ≡ h + d * r (mod q)
            if (sig['s'] * k_calc - (sha1_to_int(sig['msg']) + d_candidate * sig['r'])) % q != 0:
                valid = False
                break
        if valid:
            return d_candidate
    return None

# ----------------------------------------------------------------
# Main exploit: pulihkan d lalu hitung flag
# ----------------------------------------------------------------
def main():
    print("[*] Memulai HNP lattice attack dengan Sage...")
    d = recover_private_key()
    if d is None:
        print("[!] Gagal memulihkan private key.")
        return
    print("[*] Private key d berhasil dipulihkan =", d)
    inv_d = inverse_mod(d, q)
    T = ellipticcurve.Point(curve_256, hidden_flag[0], hidden_flag[1])
    Q = inv_d * T
    flag_int = int(Q.x())
    flag_bytes = long_to_bytes(flag_int)
    print("[*] Flag ditemukan:", flag_bytes)

if __name__ == '__main__':
    main()

'''
[*] Memulai HNP lattice attack dengan Sage...
[*] Private key d berhasil dipulihkan = 110104254168941847244659959021870001852301044662581657616531508669991620749093
[*] Flag ditemukan: b'crypto{3mbrac3_r4nd0mn3ss}'
'''
```
