# LSB DLP Recover r

referensi: Junior Crypt 2025

<figure><img src="../../.gitbook/assets/image (5).png" alt=""><figcaption></figcaption></figure>

```python
from pwn import *
import math

def solve_bsgs(base, result, modulus, search_space_n):
    """
    Solves the discrete logarithm problem (base^x = result (mod modulus))
    using the Baby-step giant-step algorithm.
    This is efficient for finding x within a known, relatively small search space.
    """
    N = search_space_n
    m = int(math.sqrt(N)) + 1
    
    info(f"Starting BSGS with search space N={N}, m={m}")

    # Baby steps: store (base^j mod modulus, j) in a table.
    baby_steps = {}
    val = 1
    for j in range(m):
        if val not in baby_steps:
            baby_steps[val] = j
        val = (val * base) % modulus

    # Giant steps:
    # Precompute base^(-m) mod modulus
    base_inv_m = pow(base, -m, modulus)
    
    giant_step_val = result
    for i in range(m):
        # Check if the current giant step value is in our baby steps table
        if giant_step_val in baby_steps:
            j = baby_steps[giant_step_val]
            x = i * m + j
            info(f"Found solution x = {x}")
            return x
        # Move to the next giant step
        giant_step_val = (giant_step_val * base_inv_m) % modulus
        
    error("BSGS failed to find a solution.")
    return None

def find_r(g, p, C, leak):
    """
    Recovers the full nonce 'r' using the leaked lower bits.
    r = r_high * 2^464 + leak
    We solve for r_high (which we call 'k') using BSGS.
    """
    n_leak_bits = 464
    
    # The equation is: g^(k * 2^464 + leak) = C (mod p)
    # Rearranging gives: (g^(2^464))^k = C * (g^leak)^-1 (mod p)
    # This is a DLP we can solve for k.
    
    # The base for our DLP
    base = pow(g, 2**n_leak_bits, p)
    
    # The result for our DLP
    g_inv_leak = pow(g, -leak, p)
    result = (C * g_inv_leak) % p
    
    # The search space for k is the number of possible high bits
    search_space_k = (p - 1) // (2**n_leak_bits) + 2
    
    k = solve_bsgs(base, result, p, search_space_k)
    
    if k is not None:
        r = k * (2**n_leak_bits) + leak
        info(f"Successfully recovered r: {r}")
        return r
    else:
        error("Failed to recover r.")
        return None

def main():
    # Connect to the remote service
    conn = remote('ctf.mf.grsu.by', 9052)

    # --- Parse Initial Parameters ---
    conn.recvuntil(b'p=')
    p = int(conn.recvline().strip())
    conn.recvuntil(b'g=')
    g = int(conn.recvline().strip())
    conn.recvuntil(b'y=')
    y = int(conn.recvline().strip())
    info(f"p = {p}")
    info(f"g = {g}")
    info(f"y = {y}")

    # --- Round 1: Recover the secret 'x' ---
    conn.recvuntil(b'=== Round 1 ===')
    log.info("Starting Round 1: Intentionally failing to learn the secret.")
    
    conn.recvuntil(b'C = g^r mod p: ')
    C1 = int(conn.recvline().strip())
    conn.recvuntil(b'leak(r): ')
    leak1 = int(conn.recvline().strip())
    conn.recvuntil(b'e = ')
    e1 = int(conn.recvline().strip())

    # Step 1: Recover the full nonce r1
    r1 = find_r(g, p, C1, leak1)

    # Step 2: Send a dummy value to fail the check
    conn.sendlineafter(b'mod (p-1):', b'1')
    
    # Step 3: Read the correct 's' value leaked by the server
    conn.recvuntil(b'Correct s is: ')
    s1_correct = int(conn.recvline().strip())
    info(f"Leaked correct s1: {s1_correct}")

    # Step 4: Calculate the secret x
    # s1 = (r1 + e1*x) mod (p-1)  =>  x = (s1 - r1) * (e1^-1) mod (p-1)
    p_minus_1 = p - 1
    e1_inv = pow(e1, -1, p_minus_1)
    x = ((s1_correct - r1) * e1_inv) % p_minus_1
    success(f"Recovered secret x: {x}")

    # Verification (optional): check if our x is correct
    if pow(g, x, p) == y:
        success("Secret x verified successfully!")
    else:
        error("Verification of x failed!")
        conn.close()
        return

    # --- Round 2: Forge the proof using 'x' ---
    conn.recvuntil(b'=== Round 2 ===')
    log.info("Starting Round 2: Using the secret to forge the proof.")

    conn.recvuntil(b'C = g^r mod p: ')
    C2 = int(conn.recvline().strip())
    conn.recvuntil(b'leak(r): ')
    leak2 = int(conn.recvline().strip())
    conn.recvuntil(b'e = ')
    e2 = int(conn.recvline().strip())

    # Step 1: Recover the full nonce r2
    r2 = find_r(g, p, C2, leak2)

    # Step 2: Calculate the correct s2 using our recovered secret x
    s2 = (r2 + e2 * x) % p_minus_1
    info(f"Calculated correct s2: {s2}")

    # Step 3: Send the correct s2 to pass the round
    conn.sendlineafter(b'mod (p-1):', str(s2).encode())

    # --- Get the Flag ---
    conn.recvuntil(b'Success! Flag: ')
    flag = conn.recvline().strip().decode()
    success(f"Flag: {flag}")
    
    conn.close()

if __name__ == "__main__":
    main()
```

```python
#! /usr/bin/python3 -u

from random import randint
from Crypto.Util.number import getPrime

# Конфигурация
FLAG = 'CTF{zkp_basic_secret_123}'
ROUNDS = 2

# Параметры протокола
p = getPrime(512)   # Простое число
g = 2               # Генератор группы Zp*
x = randint(1,p-2)  # Секрет (g^x mod p = y)
y = pow(g, x, p)    # y

n_leak = 464

def main():

        print(f"\n=== Zero-Knowledge Proof: Prove You Know x ===")
        print(f"Параметры / Parameters: \np={p}, \ng={g}, \ny={y}\n")
        print(f"Докажите, что знаете x, такой что g^x ≡ y mod p\n")
        print(f"Всего раундов / Rounds: {ROUNDS}\n")

        err_flag = False
        for round_num in range(1, ROUNDS+1):
            print(f"=== Round {round_num} ===\n")

            # 1. Проверяющий генерирует r, отправляет C = g^r mod p. 
            #    Однако, в результате утечки, к Доказывающему приходит еще и 464 младших бита r
            r = randint(1, p-1)  # Случайный nonce
            C = pow(g, r, p)
            leak = r % 2**n_leak    # Утечка 

            print(f"C = g^r mod p: {C}")
            print(f"Утечка / leak(r): {leak}") # 464 младших бита r

            # 2. Проверяющий генерирует и отправляет  challenge e
            e = randint(1, 2**32)
            print(f"e = {e}")


            # 3. Доказывающий восстанавливает r и присылает s = (r + e*x) mod (p-1)
            print(f"Вычислите / Calculate s = (r + e*x) mod (p-1):")
            s = int(input().strip())

            # 4. Верификация
            left = pow(g, s, p)
            right = (C * pow(y, e, p)) % p
            if left != right:
                print(f"\nОшибка верификации / Verification failed!")
                print (f"Правильный s / Correct s is: {(r + e * x) % (p-1)}")
                print (f"Рaунд не пройден / Round not passed\n")
            else:
                print("Рaунд пройден / Round passed\n\n")
                err_flag = True
        
        # Все раунды пройдены
        if err_flag:
            print(f"Success! Flag: {FLAG}")
        else:
            print ("Не беда. Решите следующий раз ... / No problem. Decide next time ...")


if __name__ == "__main__":
    
    main()
```

