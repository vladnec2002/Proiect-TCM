# ffs.py
# Implementare 100% conform Handbook of Applied Cryptography, Chapter 10,
# Protocol 10.26: Feige–Fiat–Shamir identification protocol (in Z_n).
# :contentReference[oaicite:1]{index=1}

import secrets
from dataclasses import dataclass
from math import gcd

from utils import modinv, random_coprime


@dataclass
class FFSKeys:
    """
    Cheile pentru Feige–Fiat–Shamir (Protocol 10.26):
      - n: modul comun (Blum integer n = p*q, p≡q≡3 mod 4)
      - k: numărul de secrete (și publice) per utilizator
      - s: lista secretelor s1..sk (private key)
      - v: lista publicelor v1..vk (public key), unde
           v_i = (-1)^{b_i} * (s_i^2)^(-1) mod n
    """
    n: int
    k: int
    s: list[int]
    v: list[int]


def keygen_ffs(n: int, k: int) -> FFSKeys:
    """
    Step 2 din Protocol 10.26 (Selection of per-entity secrets).
    Alege s1..sk și b1..bk, apoi calculează publicele v1..vk.

    (a) Select k random integers s1..sk, 1<=si<=n-1, gcd(si,n)=1
        Select k random bits b1..bk
    (b) Compute v_i = (-1)^{b_i} * (s_i^2)^(-1) mod n
    """
    if k <= 0:
        raise ValueError("k trebuie sa fie >= 1")

    s_list: list[int] = []
    v_list: list[int] = []

    for _ in range(k):
        # alege s_i cu gcd(s_i, n) = 1 (cerință explicită în protocol)
        while True:
            si = secrets.randbelow(n - 2) + 2  # [2, n-1]
            if gcd(si, n) == 1:
                break

        bi = secrets.randbelow(2)  # 0 sau 1

        # inv_sq = (s_i^2)^(-1) mod n
        inv_sq = modinv((si * si) % n, n)

        # v_i = (-1)^{b_i} * inv_sq mod n
        vi = inv_sq if bi == 0 else (-inv_sq) % n

        s_list.append(si)
        v_list.append(vi)

    return FFSKeys(n=n, k=k, s=s_list, v=v_list)


def ffs_round(keys: FFSKeys) -> bool:
    """
    O rundă (din t) conform Step 4 din Protocol 10.26.

    (a) Prover A: alege r random, 1<=r<=n-1 și bit b; calculează
        x = (-1)^b * r^2 mod n; trimite x (witness).
    (b) Verifier B: trimite challenge vector (e1..ek), ei in {0,1}.
    (c) Prover A: răspunde cu
        y = r * Π s_j^{e_j} mod n
    (d) Verifier B: calculează
        z = y^2 * Π v_j^{e_j} mod n
        acceptă dacă z = ±x și z != 0
    """
    n = keys.n
    k = keys.k

    # (a) Prover: commitment r și semn b
    r = random_coprime(n)  # random r, gcd(r,n)=1 (sigur), 1<=r<=n-1
    b = secrets.randbelow(2)

    # x = (-1)^b * r^2 mod n
    x = pow(r, 2, n)
    if b == 1:
        x = (-x) % n

    # (b) Verifier: challenge e vector
    e = [secrets.randbelow(2) for _ in range(k)]

    # (c) Prover: y = r * Π s_j^{e_j} mod n
    y = r % n
    for j in range(k):
        if e[j] == 1:
            y = (y * keys.s[j]) % n

    # (d) Verifier: z = y^2 * Π v_j^{e_j} mod n
    z = pow(y, 2, n)
    for j in range(k):
        if e[j] == 1:
            z = (z * keys.v[j]) % n

    # verifică z = ±x și z != 0
    return (z != 0) and (z == x or z == (-x) % n)


def authenticate(keys: FFSKeys, t: int) -> bool:
    """
    Rulează t runde; acceptă doar dacă toate runde reușesc.
    (Protocol 10.26: "B accepts A’s identity if all t rounds succeed.")
    """
    if t <= 0:
        raise ValueError("t trebuie sa fie >= 1")

    for _ in range(t):
        if not ffs_round(keys):
            return False
    return True


# =========================
# Variante VERBOSE (pentru prezentare / debug)
# =========================

def ffs_round_verbose(keys: FFSKeys, round_no: int = 1) -> bool:
    """
    Exact aceeași rundă ca ffs_round(), dar printează toate valorile relevante
    (x, e, y, z) și verificările z==x / z==-x mod n.
    """
    n = keys.n
    k = keys.k

    r = random_coprime(n)
    b = secrets.randbelow(2)

    x = pow(r, 2, n)
    if b == 1:
        x = (-x) % n

    e = [secrets.randbelow(2) for _ in range(k)]

    y = r % n
    for j in range(k):
        if e[j] == 1:
            y = (y * keys.s[j]) % n

    z = pow(y, 2, n)
    for j in range(k):
        if e[j] == 1:
            z = (z * keys.v[j]) % n

    ok = (z != 0) and (z == x or z == (-x) % n)

    print(f"\n--- Runda {round_no} ---")
    print("b =", b)
    print("x =", x)
    print("e =", e)
    print("y =", y)
    print("z =", z)
    print("cond: z == x ?", z == x)
    print("cond: z == -x mod n ?", z == (-x) % n)
    print("OK ?", ok)

    return ok


def authenticate_verbose(keys: FFSKeys, t: int) -> bool:
    """
    Autentificare cu output pe fiecare rundă.
    """
    if t <= 0:
        raise ValueError("t trebuie sa fie >= 1")

    for i in range(1, t + 1):
        if not ffs_round_verbose(keys, round_no=i):
            return False
    return True
