from typing import Dict, Any, List, Tuple
from .se import estimate_se, normalize_se
from .m_gate import blast_radius, traceability_score, accept
from .store import Ledger

def validate_structural(amendment: Dict[str, Any]) -> bool:
    required = ["id", "parent_ids", "status_action", "content_delta", "procedure_id", "evidence"]
    return all(k in amendment for k in required)

def validate_juridical(amendment: Dict[str, Any], procedures: List[Dict[str, Any]], rules: List[Dict[str, Any]]) -> bool:
    pid = amendment.get("procedure_id")
    proc = next((p for p in procedures if p["id"] == pid), None)
    if not proc:
        return False
    if amendment.get("status_action") != "none" and not proc.get("transmutation_allowed", False):
        return False
    return True

def propose(amendment: Dict[str, Any], rules: List[Dict[str, Any]], thresholds: Dict[str, float], procedures: List[Dict[str, Any]], ledger: Ledger) -> Tuple[bool, Dict[str, float]]:
    if not validate_structural(amendment):
        return False, {"parse/typing": 0.0}

    if not validate_juridical(amendment, procedures, rules):
        return False, {"error": "procedure/hierarchy"}

    se = estimate_se(amendment, rules)
    C = 1.0 - normalize_se(se)
    TR = traceability_score(amendment, rules)
    BR = blast_radius(amendment, rules)

    ok, metrics = accept(C, TR, BR, thresholds["coherence"], thresholds["traceability"], thresholds["blast_radius"])
    if ok:
        # Apply delta (very simplified): update fields on parent rules
        for rid in amendment.get("parent_ids", []):
            for r in rules:
                if r["id"] == rid:
                    r.update(amendment.get("content_delta", {}))
                    if amendment.get("status_action") == "transmute_to_constitutional":
                        r["status"] = "constitutional"
                    elif amendment.get("status_action") == "transmute_to_statutory":
                        r["status"] = "statutory"
        ledger.append({"amendment": amendment, "metrics": metrics})
        return True, metrics  # metrics: Dict[str, float]
    else:
        parent_ids = amendment.get("parent_ids", [])
        if not parent_ids:
            # use a 0.0 score instead of a string
            return False, {"procedure/hierarchy": 0.0}
        return False, metrics
