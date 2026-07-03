# homomorphic

Referensi: Junior Crypt 2025 & FMC CTF 2025

<figure><img src="../../.gitbook/assets/image (2).png" alt=""><figcaption></figcaption></figure>

<figure><img src="../../.gitbook/assets/image (3).png" alt=""><figcaption></figcaption></figure>

```python
from Crypto.Util.number import *
from pwn import *
from json import *

script_path = os.path.join(os.path.dirname(__file__), 'crypto.py')
r = process(['python', script_path])

context.log_level = "debug"

r.recvuntil(b'Public Key (n, g) = ')
pub_key_str = r.recvline().decode().strip()
if pub_key_str.startswith('(') and pub_key_str.endswith(')'):
    pub_key_str = pub_key_str[1:-1]
n_str, g_str = pub_key_str.split(',')
n = int(n_str.strip())
g = int(g_str.strip())

r.recvuntil(b'Encrypted Balance = ')
enc_balance0 = int(r.recvline().decode().strip())

r.recvuntil(b'>> Enc(amount) = ')

n2 = n*n
enc_balance_inv =  pow(enc_balance0, -1, n2)
enc_target = pow(g, 1000000, n2)
enc_input = (enc_target * enc_balance_inv) % n2

r.sendline(str(enc_input))
r.interactive()
```

```python
from Crypto.Util.number import getPrime, bytes_to_long
import random

# Генерация ключей Paillier
def generate_keypair(bits=512):
    p = getPrime(bits)
    q = getPrime(bits)
    n = p * q
    g = n + 1  # Стандартный выбор для g в Paillier
    lambda_ = (p - 1) * (q - 1)
    mu = pow(lambda_, -1, n)
    return (n, g), (lambda_, mu)

# Шифрование
def encrypt(m, pub_key):
    n, g = pub_key
    r = random.randint(1, n - 1)
    c = (pow(g, m, n**2) * pow(r, n, n**2)) % n**2
    return c

# Дешифрование
def decrypt(c, priv_key, pub_key):
    n, g = pub_key
    lambda_, mu = priv_key
    x = pow(c, lambda_, n**2)
    l = (x - 1) // n
    m = (l * mu) % n
    return m

# Инициализация

FLAG = "grodno{Redacted_Flag}"

pub_key, priv_key = generate_keypair()
balance = random.randint(0, 999999)      # Начальный баланс
enc_balance = encrypt(balance, pub_key)
end_balance = encrypt(1000000, pub_key)

print(f"[*] Public Key (n, g) = {pub_key}")
print(f"[*] Encrypted Balance = {enc_balance}")

# Обработчик "транзакций"
def process_transaction(enc_amount):
    global enc_balance
    # Гомоморфное сложение: Enc(balance + amount)
    enc_balance = (enc_balance * enc_amount) % (pub_key[0] ** 2)
    return enc_balance

# Пример работы сервера (имитация API)
if __name__ == "__main__":
    print("\n[*] Server is running. Send your transactions as `Enc(amount)`.")
    
    while True:
        try:
            user_input = int(input(">> Enc(amount) = "))
            new_enc_balance = process_transaction(user_input)
            print(f"[+] New Encrypted Balance = {new_enc_balance}")
            if decrypt(new_enc_balance, priv_key, pub_key) == decrypt(end_balance, priv_key, pub_key):
                print (f"Flag is: {FLAG}")
                break
            elif new_enc_balance > end_balance:
                print (f"Слишком много / Too many")
                break
        except:
            print("[!] Invalid input. Use integers.")
```

another chall&#x20;

```python
from math import gcd
from Crypto.Util.number import getPrime, inverse
from random import randint
import secrets
import time

with open("flag.txt") as f:
    flag = f.readline()

class Paillier:
    def __init__(self, bits):
        self.bits = bits
        self.pub, self.priv = self.keygen()

    def lcm(self, a, b):
        return a * b // gcd(a, b)

    def keygen(self):
        while True:
            p = getPrime(self.bits)
            q = getPrime(self.bits)
            if p != q:
                break
        n = p * q
        Lambda = self.lcm(p - 1, q - 1)  
        g = n + 1  
        mu = inverse(Lambda, n) 
        return ((n, g), (Lambda, mu))

    def encrypt(self, m):
        (n, g) = self.pub
        n_sq = n * n
        while True:
            r = randint(1, n - 1)
            if gcd(r, n) == 1:
                break
        c = (pow(g, m, n_sq) * pow(r, n, n_sq)) % n_sq
        return c

    def decrypt(self, c):
        (n, g) = self.pub
        (Lambda, mu) = self.priv
        n_sq = n * n
        x = pow(c, Lambda, n_sq)  
        m = (((x - 1) // n) * mu) % n  
        return m

    def get_keys(self):
        return self.pub, self.priv

if __name__ == "__main__":

    print("Welcome to the Secure Gate Challenge!")
    paillier = Paillier(256)
    pub, priv = paillier.get_keys()
    print('(n,g)=', pub)
    nums = [secrets.randbits(16) for _ in range(4)]
    res = (nums[0] + nums[1]) + (nums[2] - nums[3])

    ciphers = [paillier.encrypt(i) for i in nums] 
    print('c1 =', ciphers[0])
    print('c2 =', ciphers[1])
    print('c3 =', ciphers[2])
    print('c4 =', ciphers[3])

    try:
        start_time = time.time()
        pass_code = int(input("Can you open the gate? If so, insert the passcode fast: "))
        if time.time() - start_time > 60:  
            print("Too slow! Time's up!")
            exit()
        pass_decode = paillier.decrypt(pass_code)
        if res == pass_decode:
            print(f"Wow! You opened it, The flag is: {flag}")
        else:
            print("Nope, Maybe next time :(")
    except Exception as e:
        print("Invalid input or error occurred:", str(e))
        exit()

```

```python
from pwn import *
from Crypto.Util.number import *

# r = remote("seal-the-deal.fmc.tf", 2003)
script_path = os.path.join(os.path.dirname(__file__), 'crypto.py')
r = process(['python', script_path])

r.recvuntil(b'= ')
temp = r.readline().decode().strip('\n')

# Paillier homomorphic
#  Karena sifat homomorfik, perkalian dari ciphertext tersebut menghasilkan:
#  c₁ * c₂ * c₃ mod n² = E(m₁ + m₂ + m₃)
# arr = list(map(int, temp.strip("()").split(", ")))
arr = list(map(int, temp.strip("()\r").split(", ")))
n = arr[0]

r.recvuntil(b'= ')
c1 = int(r.readline().decode().strip('\n'))
r.recvuntil(b'= ')
c2 = int(r.readline().decode().strip('\n'))
r.recvuntil(b'= ')
c3 = int(r.readline().decode().strip('\n'))
r.recvuntil(b'= ')
c4 = int(r.readline().decode().strip('\n'))

n2 = n*n
c4_inv =  pow(c4, -1, n2)
# enc_target = pow(g, 1000000, n2)
enc_input = (c2 *c1 *c3 *c4_inv) % n2
print(enc_input)
r.sendline(str(enc_input))
r.interactive()
```
