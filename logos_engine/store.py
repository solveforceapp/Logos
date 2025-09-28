from __future__ import annotations
import json, os, time
from typing import Dict, Any, Optional
from .types import hash_record

class Ledger:
    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(self.path):
            open(self.path, "w").close()

    def last_hash(self) -> Optional[str]:
        prev = None
        with open(self.path, "r") as f:
            for line in f:
                if line.strip():
                    rec = json.loads(line)
                    prev = rec.get("hash")
        return prev

    def append(self, obj: Dict[str, Any]) -> str:
        prev = self.last_hash()
        h = hash_record(obj, prev)
        rec = {"ts": time.time(), "hash": h, "prev": prev, "obj": obj}
        with open(self.path, "a") as f:
            f.write(json.dumps(rec) + "\n")
        return h
