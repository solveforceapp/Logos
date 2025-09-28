import os, json, yaml
from pathlib import Path
from logos_engine.store import Ledger
from logos_engine.nomics import propose

PROJECT_ROOT = Path(__file__).parent.parent.parent
constitution = yaml.safe_load(open(PROJECT_ROOT / "examples" / "constitution.yaml"))
policies = yaml.safe_load(open(PROJECT_ROOT / "examples" / "policies.yaml"))
amendments = yaml.safe_load(open(PROJECT_ROOT / "examples" / "amendments.yaml"))

rules = policies["rules"]
thresholds = constitution["thresholds"]
procedures = constitution["procedures"]
ledger = Ledger(path=PROJECT_ROOT / "engine" / "python" / "state" / "ledger.jsonl")

def run_all():
    for a in amendments["amendments"]:
        ok, metrics = propose(a, rules, thresholds, procedures, ledger)
        status = "ACCEPT" if ok else "REJECT"
        print(f"[{status}] {a['id']} metrics={metrics}")

    print("\nFinal rules:")
    print(json.dumps(rules, indent=2))

if __name__ == "__main__":
    run_all()
