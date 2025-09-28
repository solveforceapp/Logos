from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import hashlib, json

@dataclass
class Rule:
    id: str
    status: str  # 'constitutional' or 'statutory'
    intent: str
    scope: str
    effect: str
    precedence: int
    tests: List[str]

@dataclass
class Amendment:
    id: str
    parent_ids: List[str]
    status_action: str  # 'none' | 'transmute_to_constitutional' | 'transmute_to_statutory'
    content_delta: Dict[str, Any]
    procedure_id: str
    evidence: List[str]

@dataclass
class Constitution:
    thresholds: Dict[str, float]
    procedures: List[Dict[str, Any]]

def hash_record(obj: Dict[str, Any], prev_hash: Optional[str]) -> str:
    payload = json.dumps({"obj": obj, "prev": prev_hash}, sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()

def process_batch(batch: List[Dict[str, Any]], model: str = "mock", batch_size: int = 2, interpretation: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    Process a batch of records using the specified model and batch size.
    """
    if interpretation is not None:
        if "intent" not in interpretation:
            raise ValueError("The 'intent' field is required in the interpretation dictionary.")
        if "arguments" not in interpretation:
            raise ValueError("The 'arguments' field is required in the interpretation dictionary.")
        if "tokens_min" not in interpretation["arguments"]:
            raise ValueError("The 'tokens_min' field is required in the arguments dictionary.")
        if "tokens_max" not in interpretation["arguments"]:
            raise ValueError("The 'tokens_max' field is required in the arguments dictionary.")
        if "hashes" not in interpretation["arguments"]:
            raise ValueError("The 'hashes' field is required in the arguments dictionary.")
        if "confidence" not in interpretation:
            raise ValueError("The 'confidence' field is required in the interpretation dictionary.")
    else:
        interpretation = {"intent": "summarize", "arguments": {"tokens_min": 0, "tokens_max": 100, "hashes": []}, "confidence": 0.9}

    results = []
    for i in range(0, len(batch), batch_size):
        batch_slice = batch[i:i+batch_size]
        batch_hash = [hash_record(item, None) for item in batch_slice]
        results.append({"batch": batch_slice, "hashes": batch_hash})
    return results
