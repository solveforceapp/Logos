from typing import List, Dict, Any
import math
import hashlib
try:
    from llm_adapter.types import RawCompletion, Interpretation
except ImportError:
    from typing import Dict, Any
    from dataclasses import dataclass

    @dataclass
    class RawCompletion:
        output: str

    @dataclass
    class Interpretation:
        intent: str
        arguments: Dict[str, Any]
        confidence: float


def _shannon_entropy(probs: List[float]) -> float:
    if not probs:
        return 0.0
    return -sum(p * math.log2(p) for p in probs if p > 0 and p <= 1)


def interpretations_to_entropy(interpretations: List[str]) -> float:
    """Convert a list of interpretation strings (from ensemble members) into
    a normalized entropy value in [0,1].

    Normalization uses log(N) where N is the number of ensemble members.
    """
    if not interpretations:
        return 0.0
    freq = {}
    for it in interpretations:
        freq[it] = freq.get(it, 0) + 1
    n = len(interpretations)
    probs = [count / n for count in freq.values()]
    H = _shannon_entropy(probs)
    N_unique = len(freq)
    H_max = math.log2(N_unique) if N_unique > 1 else 1.0
    if H_max == 0:
        return 0.0
    return float(max(0.0, min(1.0, H / H_max)))


def _stable_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _extract_naive_intent(text: str) -> Dict[str, Any]:
    """
    Deterministic, regex-free heuristic:
    - lowercasing
    - simple keyword buckets
    - stable argument ordering
    """
    t = text.strip().lower()
    intent = "unknown"
    args: Dict[str, Any] = {}

    if "summarize" in t or "summary" in t:
        intent = "summarize"
    elif "classify" in t or "label" in t:
        intent = "classify"
    elif "extract" in t or "pull out" in t:
        intent = "extract"
    elif "plan" in t or "roadmap" in t:
        intent = "plan"

    # very simple deterministic arguments
    args["tokens"] = len(t.split())
    args["hash"] = _stable_hash(t)[:12]
    return {"intent": intent, "arguments": args}


def normalize_and_fuse(raws: List[RawCompletion]) -> Interpretation:
    """
    Deterministic fusion:
    1) Normalize each output → (intent, arguments).
    2) Majority vote on intent; tie-breaker: lexicographically smallest intent.
    3) Confidence = (#winners / #total) adjusted by agreement on token-count parity.
    4) Arguments merged deterministically by sorted keys and min/max consensus.
    """
    if not raws:
        return Interpretation(intent="unknown", arguments={}, confidence=0.0)

    normals = []
    for rc in raws:
        x = _extract_naive_intent(rc.output)
        normals.append((rc, x["intent"], x["arguments"]))

    # vote
    tally: Dict[str, int] = {}
    for _, intent, _ in normals:
        tally[intent] = tally.get(intent, 0) + 1
    if tally:
        max_votes = max(tally.values())
        winners = sorted([k for k, v in tally.items() if v == max_votes])
        chosen_intent = winners[0]
        votes = tally[chosen_intent]
    else:
        chosen_intent = "unknown"
        votes = 0
    n = len(raws)

    # token parity agreement bonus
    parities = [arguments["tokens"] % 2 for _, _, arguments in normals]
    parity_agree = 1.0 if len(set(parities)) == 1 else 0.0

    confidence = round((votes / n) * 0.9 + 0.1 * parity_agree, 3)

    # deterministic arg merge (token stats and hashes)
    tokens = sorted([arguments["tokens"] for _, _, arguments in normals])
    merged_args = {
        "tokens_min": tokens[0],
        "tokens_max": tokens[-1],
        "hashes": sorted([arguments["hash"] for _, _, arguments in normals]),
    }

    return Interpretation(intent=chosen_intent, arguments=merged_args, confidence=confidence)
