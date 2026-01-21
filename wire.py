# wire.py
import json
import sys
from typing import Any, Dict

def send(msg: Dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()

def recv() -> Dict[str, Any]:
    line = sys.stdin.readline()
    if not line:
        raise EOFError("No more input (EOF).")
    return json.loads(line)
