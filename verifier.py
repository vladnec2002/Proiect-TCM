# verifier.py
import argparse
import json
import subprocess
import sys
from typing import Any, Dict

from storage import load_public

def send(proc: subprocess.Popen, msg: Dict[str, Any]) -> None:
    proc.stdin.write(json.dumps(msg) + "\n")
    proc.stdin.flush()

def recv(proc: subprocess.Popen) -> Dict[str, Any]:
    line = proc.stdout.readline()
    if not line:
        raise EOFError("Prover closed stdout (EOF).")
    return json.loads(line)

def verifier_check(n: int, v: list[int], x: int, e: list[int], y: int) -> bool:
    # z = y^2 * Π v_j^{e_j} mod n; accept if z = ±x and z != 0
    z = pow(y, 2, n)
    for j in range(len(v)):
        if e[j] == 1:
            z = (z * v[j]) % n
    return (z != 0) and (z == x or z == (-x) % n)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--keys-dir", default="keys")
    ap.add_argument("--t", type=int, default=4)
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--python", default=sys.executable, help="python executable (default: current)")
    args = ap.parse_args()

    pub = load_public(args.name, keys_dir=args.keys_dir)
    n = pub["n"]
    k = pub["k"]
    v = pub["v"]

    # Start prover as subprocess
    proc = subprocess.Popen(
        [args.python, "prover.py", "--name", args.name, "--keys-dir", args.keys_dir, "--t", str(args.t)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    try:
        hello = recv(proc)
        if args.verbose:
            print("Prover says:", hello)

        ok_all = True

        for round_no in range(1, args.t + 1):
            msg = recv(proc)
            if msg.get("type") != "commit" or msg.get("round") != round_no:
                print("Bad commit from prover:", msg)
                ok_all = False
                break

            x = int(msg["x"])

            # Verifier chooses random challenge vector e
            e = [0] * k
            # make it random
            import secrets
            e = [secrets.randbelow(2) for _ in range(k)]

            send(proc, {"type": "challenge", "round": round_no, "e": e})

            msg2 = recv(proc)
            if msg2.get("type") != "response" or msg2.get("round") != round_no:
                print("Bad response from prover:", msg2)
                ok_all = False
                break

            y = int(msg2["y"])

            ok = verifier_check(n, v, x, e, y)

            if args.verbose:
                # compute z for display
                z = pow(y, 2, n)
                for j in range(k):
                    if e[j] == 1:
                        z = (z * v[j]) % n
                print(f"\n--- Runda {round_no} ---")
                print("x =", x)
                print("e =", e)
                print("y =", y)
                print("z =", z)
                print("z==x?", z == x)
                print("z==-x mod n?", z == (-x) % n)
                print("OK?", ok)

            send(proc, {"type": "result", "round": round_no, "ok": ok})

            if not ok:
                ok_all = False
                break

        done = recv(proc)
        if args.verbose:
            print("\nProver done:", done)

        print("\n=== VERIFIER FINAL ===")
        print("Accepted?", ok_all)

        return 0 if ok_all else 1

    finally:
        try:
            proc.terminate()
        except Exception:
            pass

if __name__ == "__main__":
    raise SystemExit(main())
