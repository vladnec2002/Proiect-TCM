# utils.py
# Utilitare pentru implementarea Feige–Fiat–Shamir (Protocol 10.26).
# Include:
#  - invers modular
#  - random coprime
#  - test primalitate Miller-Rabin
#  - generare Blum primes (p ≡ 3 mod 4)
# :contentReference[oaicite:1]{index=1}

import secrets
from math import gcd


def modinv(a: int, n: int) -> int:
    """Invers modular a^{-1} mod n (Python 3.8+)."""
    return pow(a, -1, n)


def random_coprime(n: int) -> int:
    """Alege random x in [2, n-1] astfel incat gcd(x, n) = 1."""
    while True:
        x = secrets.randbelow(n - 2) + 2
        if gcd(x, n) == 1:
            return x


def is_probable_prime(n: int, rounds: int = 16) -> bool:
    """
    Test probabilistic Miller–Rabin.
    rounds=16 e suficient pentru proiect (probabilitate foarte mică de eroare).
    """
    if n < 2:
        return False

    # small primes quick check
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    for p in small_primes:
        if n == p:
            return True
        if n % p == 0:
            return False

    # write n-1 = d * 2^s
    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2

    # witness loop
    for _ in range(rounds):
        a = secrets.randbelow(n - 3) + 2  # [2, n-2]
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue

        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False

    return True


def generate_prime(bits: int, require_mod4_eq_3: bool = False) -> int:
    """
    Generează un prim de 'bits' biți.
    Dacă require_mod4_eq_3=True, generează Blum prime: p ≡ 3 (mod 4),
    conform Protocol 10.26 (p și q congruente cu 3 mod 4). :contentReference[oaicite:2]{index=2}
    """
    if bits < 16:
        raise ValueError("bits trebuie sa fie >= 16")

    while True:
        # Asigură: bitul MSB = 1 (dimensiune corectă) și număr impar
        p = secrets.randbits(bits) | (1 << (bits - 1)) | 1

        if require_mod4_eq_3 and (p % 4 != 3):
            continue

        if is_probable_prime(p):
            return p


def generate_blum_modulus(bits: int) -> tuple[int, int, int]:
    """
    Generează p,q Blum primes (p≡q≡3 mod 4) și n=p*q.
    Returnează (p, q, n). Conform Step 1, Protocol 10.26. :contentReference[oaicite:3]{index=3}
    """
    p = generate_prime(bits, require_mod4_eq_3=True)
    q = generate_prime(bits, require_mod4_eq_3=True)
    while q == p:
        q = generate_prime(bits, require_mod4_eq_3=True)
    n = p * q
    return p, q, n
