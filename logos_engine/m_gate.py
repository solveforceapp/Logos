from typing import Dict, Any, List, Tuple

def blast_radius(amendment: Dict[str, Any], rules: List[Dict[str, Any]]) -> float:
    touched = set(amendment.get("parent_ids", []))
    total = max(1, len(rules))
    return min(1.0, len(touched) / total)

def traceability_score(amendment: Dict[str, Any], rules: List[Dict[str, Any]]) -> float:
    # Simple proxy: presence of parent_ids, procedure_id, and evidence implies high traceability.
    has_parents = bool(amendment.get("parent_ids"))
    has_procedure = bool(amendment.get("procedure_id"))
    has_evidence = bool(amendment.get("evidence"))
    score = 0.5
    score += 0.2 if has_parents else 0.0
    score += 0.2 if has_procedure else 0.0
    score += 0.1 if has_evidence else 0.0
    return min(1.0, score)

def accept(coherence: float, traceability: float, br: float, θC: float, θTR: float, θBR: float) -> Tuple[bool, Dict[str, float]]:
    ok = (coherence >= θC) and (traceability >= θTR) and (br <= θBR)
    return ok, {"C": coherence, "TR": traceability, "BR": br, "θC": θC, "θTR": θTR, "θBR": θBR}
