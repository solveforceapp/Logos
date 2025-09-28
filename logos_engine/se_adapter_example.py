"""Example ensemble SE adapter (deterministic simulation).

This file provides a small, deterministic example showing one way to
convert multiple model judgments into a distribution over interpretations
and compute a normalized semantic entropy in [0,1].

It uses only the Python standard library and is deterministic (hash-based)
so it's suitable for unit tests and as a blueprint for a real LLM ensemble.

Usage:
    from logos_engine import se
    from logos_engine.se_adapter_example import ensemble_estimate_se

    se.set_adapter(ensemble_estimate_se)

Adapter signature: func(amendment: dict, rules: list[dict]) -> float
"""

from typing import Dict, Any, List
import hashlib, json, math


def _deterministic_choice(seed_bytes: bytes, choices: List[str]) -> str:
    # Map deterministic bytes -> index
    idx = int.from_bytes(seed_bytes, "big") % len(choices)
    return choices[idx]


def _model_interpretation(amendment: Dict[str, Any], facts: List[str], model_idx: int) -> str:
    # Create a deterministic pseudo-random interpretation string for a model
    key = (amendment.get("id", "") + "|" + json.dumps(facts, sort_keys=True) + f"|{model_idx}").encode("utf-8")
    h = hashlib.sha256(key).digest()
    # Candidate interpretation templates derived from facts
    base = facts[0] if facts else "noop"
    choices = [f"{base}:noop", f"{base}:minor", f"{base}:moderate", f"{base}:major", f"{base}:intent_change"]
    return _deterministic_choice(h, choices)


def _shannon_entropy(probs: List[float]) -> float:
    # Natural-log based entropy
    return -sum(p * math.log(p) for p in probs if p > 0.0)


def ensemble_estimate_se(amendment: Dict[str, Any], rules: List[Dict[str, Any]], num_models: int = 7) -> float:
    """Simulate an ensemble of `num_models` deterministic judgments and return
    normalized semantic entropy in [0,1].

    Steps:
    - extract factoids (re-uses logos_engine.se.factoidize if available)
    - generate per-model interpretation strings deterministically
    - compute frequency distribution, probabilities
    - compute Shannon entropy and normalize by log(num_models)
    """
    # Defensive defaults
    if num_models <= 1:
        return 0.0

    # Try to use the packaged factoidize if available for parity
    try:
        from logos_engine.se import factoidize
    except Exception:
        # fallback local extraction
        facts = []
        for k, v in amendment.get("content_delta", {}).items():
            facts.append(f"{k}:{str(v).strip()}")
        facts = facts or ["noop"]
    else:
        facts = factoidize(amendment)

    interpretations: List[str] = []
    for i in range(num_models):
        interpretations.append(_model_interpretation(amendment, facts, i))

    # Frequency -> probs
    freq: Dict[str, int] = {}
    for it in interpretations:
        freq[it] = freq.get(it, 0) + 1

    probs = [count / num_models for count in freq.values()]

    # Entropy normalized by log(num_models) so max entropy -> 1.0
    H = _shannon_entropy(probs)
    H_max = math.log(num_models)
    normalized = 0.0 if H_max <= 0.0 else min(1.0, H / H_max)
    return float(max(0.0, min(1.0, normalized)))


if __name__ == "__main__":
    # Simple demo when run as script
    a = {"id": "A-demo", "content_delta": {"effect": "Change X"}, "parent_ids": ["R-1"]}
    print("ensemble SE:", ensemble_estimate_se(a, []))
