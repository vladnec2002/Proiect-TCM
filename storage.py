# storage.py
import json
from pathlib import Path
from typing import Any, Dict

from ffs import FFSKeys


def _to_str_int(x: int) -> str:
    # JSON nu are problemă cu int-uri mari în Python, dar unele tool-uri au.
    # Ca să fie robust și portabil, salvăm ca string.
    return str(x)


def _from_str_int(x: str) -> int:
    return int(x)


def ensure_keys_dir(keys_dir: str = "keys") -> Path:
    p = Path(keys_dir)
    p.mkdir(parents=True, exist_ok=True)
    return p


def save_public(keys: FFSKeys, name: str, keys_dir: str = "keys") -> Path:
    """
    Salvează cheia publică: n, k, v[]
    """
    d: Dict[str, Any] = {
        "type": "ffs_public",
        "n": _to_str_int(keys.n),
        "k": keys.k,
        "v": [_to_str_int(x) for x in keys.v],
    }
    out_dir = ensure_keys_dir(keys_dir)
    path = out_dir / f"{name}_public.json"
    path.write_text(json.dumps(d, indent=2), encoding="utf-8")
    return path


def save_private(keys: FFSKeys, name: str, keys_dir: str = "keys") -> Path:
    """
    Salvează cheia privată: n, k, s[], v[]
    (În practică ai păstra s și poate n,k; păstrăm și v ca să fie simplu.)
    """
    d: Dict[str, Any] = {
        "type": "ffs_private",
        "n": _to_str_int(keys.n),
        "k": keys.k,
        "s": [_to_str_int(x) for x in keys.s],
        "v": [_to_str_int(x) for x in keys.v],
    }
    out_dir = ensure_keys_dir(keys_dir)
    path = out_dir / f"{name}_private.json"
    path.write_text(json.dumps(d, indent=2), encoding="utf-8")
    return path


def load_public(name: str, keys_dir: str = "keys") -> Dict[str, Any]:
    """
    Încarcă cheia publică și o returnează ca dict:
      { n:int, k:int, v:list[int] }
    """
    path = Path(keys_dir) / f"{name}_public.json"
    d = json.loads(path.read_text(encoding="utf-8"))
    if d.get("type") != "ffs_public":
        raise ValueError("Fisierul nu pare a fi o cheie publica FFS.")
    return {
        "n": _from_str_int(d["n"]),
        "k": int(d["k"]),
        "v": [_from_str_int(x) for x in d["v"]],
    }


def load_private(name: str, keys_dir: str = "keys") -> FFSKeys:
    """
    Încarcă cheia privată ca FFSKeys (include și publicele v).
    """
    path = Path(keys_dir) / f"{name}_private.json"
    d = json.loads(path.read_text(encoding="utf-8"))
    if d.get("type") != "ffs_private":
        raise ValueError("Fisierul nu pare a fi o cheie privata FFS.")
    n = _from_str_int(d["n"])
    k = int(d["k"])
    s = [_from_str_int(x) for x in d["s"]]
    v = [_from_str_int(x) for x in d["v"]]
    return FFSKeys(n=n, k=k, s=s, v=v)
