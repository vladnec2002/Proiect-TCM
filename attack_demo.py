# attack_demo.py
import argparse
import secrets

from storage import load_public
from utils import generate_blum_modulus
from ffs import keygen_ffs
from storage import save_public

def attacker_round(n: int, v: list[int], k: int) -> bool:
    """
    Atacatorul NU stie s[]. Face o singură rundă:
      - ghicește e* (k biți)
      - alege y random coprim cu n
      - setează x = ± (y^2 * Π v_i^{e*_i}) mod n
      - dacă verifier trimite e == e*, răspunde cu y și trece; altfel pică.
    """
    # attacker chooses guess e*
    e_star = [secrets.randbelow(2) for _ in range(k)]

    # choose random y (coprim cu n nu e strict necesar mereu, dar e ok)
    y = secrets.randbelow(n - 2) + 2

    # compute base = y^2 * Π v^{e*}
    base = pow(y, 2, n)
    for i in range(k):
        if e_star[i] == 1:
            base = (base * v[i]) % n

    # x is allowed to be ± r^2 form in real protocol; verifier accepts z == ±x.
    # attacker can choose x = base (and rely on ± in check). We'll randomize sign:
    if secrets.randbelow(2) == 1:
        x = (-base) % n
    else:
        x = base

    # Verifier chooses real challenge e
    e = [secrets.randbelow(2) for _ in range(k)]

    # Attacker can only answer if e == e_star
    if e != e_star:
        return False

    # If guessed right, attacker sends y.
    # Verifier check:
    z = pow(y, 2, n)
    for i in range(k):
        if e[i] == 1:
            z = (z * v[i]) % n

    return (z != 0) and (z == x or z == (-x) % n)

def trial(n: int, v: list[int], k: int, t: int) -> bool:
    for _ in range(t):
        if not attacker_round(n, v, k):
            return False
    return True

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default=None, help="folosește keys/<name>_public.json dacă există")
    ap.add_argument("--keys-dir", default="keys")
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--t", type=int, default=4)
    ap.add_argument("--trials", type=int, default=2000)
    ap.add_argument("--bits", type=int, default=256, help="doar dacă nu folosești --name (generează n nou)")
    args = ap.parse_args()

    if args.name:
        pub = load_public(args.name, keys_dir=args.keys_dir)
        n = pub["n"]
        k = pub["k"]
        v = pub["v"]
    else:
        # Generează un sistem nou rapid (public key) ca să testezi atacul
        p, q, n = generate_blum_modulus(args.bits)
        keys = keygen_ffs(n, args.k)
        save_public(keys, "temp_attacksys", keys_dir=args.keys_dir)
        k = keys.k
        v = keys.v

    wins = 0
    for _ in range(args.trials):
        if trial(n, v, k, args.t):
            wins += 1

    empirical = wins / args.trials
    theoretical = 2 ** (-(k * args.t))

    print("=== ATTACK DEMO (impostor, fara secrete) ===")
    print("k =", k, "t =", args.t, "trials =", args.trials)
    print("Empiric success rate:", empirical)
    print("Teoretic approx:", theoretical)

if __name__ == "__main__":
    main()
