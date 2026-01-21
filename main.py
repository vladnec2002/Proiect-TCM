# main.py
import argparse

from utils import generate_blum_modulus
from ffs import keygen_ffs, authenticate, authenticate_verbose
from storage import save_public, save_private, load_private


def cmd_keygen(args: argparse.Namespace) -> int:
    # Generează Blum modulus (p,q ≡ 3 mod 4) conform Protocol 10.26
    p, q, n = generate_blum_modulus(args.bits)

    keys = keygen_ffs(n, args.k)

    pub_path = save_public(keys, args.name, keys_dir=args.keys_dir)
    priv_path = save_private(keys, args.name, keys_dir=args.keys_dir)

    print("=== KEYGEN (FFS Protocol 10.26) ===")
    print("name:", args.name)
    print("bits(p):", args.bits, "=> n bitlen:", n.bit_length())
    print("k:", args.k)
    print("p % 4 =", p % 4, "| q % 4 =", q % 4)
    print("Saved public :", pub_path)
    print("Saved private:", priv_path)
    return 0


def cmd_auth(args: argparse.Namespace) -> int:
    # Încarcă cheia privată (care include și publicele v)
    keys = load_private(args.name, keys_dir=args.keys_dir)

    print("=== AUTH (FFS Protocol 10.26) ===")
    print("name:", args.name)
    print("n bitlen:", keys.n.bit_length())
    print("k:", keys.k, "t:", args.t)
    print("mode:", "verbose" if args.verbose else "normal")

    ok = authenticate_verbose(keys, args.t) if args.verbose else authenticate(keys, args.t)

    print("\n=== REZULTAT FINAL ===")
    print("Autentificare reusita?", ok)
    return 0 if ok else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ffs",
        description="Feige–Fiat–Shamir (Protocol 10.26) - keygen + auth (JSON keys)",
    )
    parser.add_argument("--keys-dir", default="keys", help="folder pentru chei (default: keys/)")

    sub = parser.add_subparsers(dest="cmd", required=True)

    p_keygen = sub.add_parser("keygen", help="genereaza chei (public+private) si le salveaza in JSON")
    p_keygen.add_argument("--name", required=True, help="numele user-ului (ex: alice)")
    p_keygen.add_argument("--bits", type=int, default=256, help="dimensiune p,q in biti (default: 256)")
    p_keygen.add_argument("--k", type=int, default=5, help="numar secrete/publice (default: 5)")
    p_keygen.set_defaults(func=cmd_keygen)

    p_auth = sub.add_parser("auth", help="ruleaza autentificarea folosind cheia privata salvata")
    p_auth.add_argument("--name", required=True, help="numele user-ului (ex: alice)")
    p_auth.add_argument("--t", type=int, default=4, help="numar runde (default: 4)")
    p_auth.add_argument("--verbose", action="store_true", help="afiseaza detalii pe runda")
    p_auth.set_defaults(func=cmd_auth)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
