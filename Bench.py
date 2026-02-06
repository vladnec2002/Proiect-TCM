# bench_simple.py
import time
import secrets
import argparse
from math import gcd

from storage import load_private
from ffs import authenticate
from utils import generate_prime, modinv


def rsa_keygen(bits):
    e = 65537
    while True:
        p = generate_prime(bits, require_mod4_eq_3=False)
        q = generate_prime(bits, require_mod4_eq_3=False)
        if p == q:
            continue
        phi = (p - 1) * (q - 1)
        if gcd(e, phi) == 1:
            n = p * q
            d = modinv(e, phi)
            return n, e, d


# -------- ARGUMENTE CLI --------
parser = argparse.ArgumentParser(description="FFS vs RSA-2048 signature benchmark")
parser.add_argument("--t", type=int, default=4, help="numar runde FFS (default: 4)")
parser.add_argument("--user", type=str, default="alice", help="nume cheie FFS (default: alice)")
# 1024-bit primes => n ~ 2048-bit
parser.add_argument("--rsa-bits", type=int, default=1024,
                    help="bits pentru p,q RSA (default: 1024 => n ~ 2048 bits)")
args = parser.parse_args()

# -------- FFS --------
keys = load_private(args.user)
start = time.perf_counter()
authenticate(keys, args.t)
ffs_time = time.perf_counter() - start

# -------- RSA SIGN + VERIFY --------
n, e, d = rsa_keygen(args.rsa_bits)
m = secrets.randbelow(n - 1) + 1

start = time.perf_counter()
sig = pow(m, d, n)       # semnare
pow(sig, e, n)           # verificare
rsa_time = time.perf_counter() - start

print(f"FFS authenticate (t={args.t}) : {ffs_time * 1000:.3f} ms")
print(f"RSA sign+verify (n~{2*args.rsa_bits}b) : {rsa_time * 1000:.3f} ms")
