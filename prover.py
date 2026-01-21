# prover.py
import argparse
import secrets

from storage import load_private
from utils import random_coprime
from wire import send, recv

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--keys-dir", default="keys")
    ap.add_argument("--t", type=int, default=4)
    args = ap.parse_args()

    keys = load_private(args.name, keys_dir=args.keys_dir)
    n = keys.n
    k = keys.k

    send({"type": "hello", "role": "prover", "name": args.name, "k": k, "t": args.t})

    for round_no in range(1, args.t + 1):
        # Prover chooses r, b and computes x = (-1)^b * r^2 mod n
        r = random_coprime(n)
        b = secrets.randbelow(2)
        x = pow(r, 2, n)
        if b == 1:
            x = (-x) % n

        send({"type": "commit", "round": round_no, "x": str(x)})

        msg = recv()
        if msg.get("type") != "challenge" or msg.get("round") != round_no:
            send({"type": "error", "round": round_no, "message": "Expected challenge"})
            return 2

        e = msg["e"]
        if not (isinstance(e, list) and len(e) == k and all(bit in (0, 1) for bit in e)):
            send({"type": "error", "round": round_no, "message": "Bad challenge format"})
            return 2

        # y = r * Π s_j^{e_j} mod n
        y = r % n
        for j in range(k):
            if e[j] == 1:
                y = (y * keys.s[j]) % n

        send({"type": "response", "round": round_no, "y": str(y)})

        msg2 = recv()
        if msg2.get("type") != "result" or msg2.get("round") != round_no:
            send({"type": "error", "round": round_no, "message": "Expected result"})
            return 2

        if not msg2.get("ok", False):
            # verifier rejected; end early
            send({"type": "done", "ok": False})
            return 1

    send({"type": "done", "ok": True})
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
