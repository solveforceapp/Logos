"""SE module

This module contains the deterministic demo proxy and a minimal adapter
interface so you can plug in an LLM or ensemble adjudicator.

Contract for adapters:
- Accepts (amendment: dict, rules: list[dict])
- Returns a float in [0.0, 1.0] representing estimated semantic entropy (higher = more entropy)
"""

from typing import Dict, Any, List, Callable

# Type for adapter: function(amendment, rules) -> float
SEAdapter = Callable[[Dict[str, Any], List[Dict[str, Any]]], float]


def factoidize(amendment: Dict[str, Any]) -> List[str]:
    facts: List[str] = []
    for k, v in amendment.get("content_delta", {}).items():
        facts.append(f"{k}:{str(v).strip()}")
    return facts or ["noop"]


def demo_estimate_se(amendment: Dict[str, Any], rules: List[Dict[str, Any]]) -> float:
    """Original deterministic proxy preserved as `demo_estimate_se`.

    This is easy to read and useful as a fallback or unit-test oracle.
    """
    facts = factoidize(amendment)
    # Proxy heuristic: if update touches 'effect' or 'intent', assign higher entropy weight;
    # else lower. Number of parents increases uncertainty modestly.
    touches = sum(1 for f in facts if f.startswith("effect") or f.startswith("intent"))
    base = 0.30 if touches else 0.15
    parent_bonus = min(0.25, 0.05 * len(amendment.get("parent_ids", [])))
    # Content length affects parsing risk a bit
    length_penalty = min(0.2, 0.01 * sum(len(f) for f in facts))
    se = min(0.99, base + parent_bonus + length_penalty)
    return se


def normalize_se(se: float) -> float:
    # Clamp to [0,1]
    return max(0.0, min(1.0, se))


# Default adapter points to the demo proxy. Replace this with your LLM/ensemble adapter.
_adapter: SEAdapter = demo_estimate_se


def set_adapter(adapter: SEAdapter) -> None:
    """Register a custom SE adapter.

    Example adapter signature:

    def my_adapter(amendment: dict, rules: list[dict]) -> float:
        # call LLM, compute deterministic numeric result in [0,1]
        return 0.42

    set_adapter(my_adapter)
    """
    global _adapter
    _adapter = adapter


def estimate_se(amendment: Dict[str, Any], rules: List[Dict[str, Any]]) -> float:
    """Estimate SE using the registered adapter (default: demo proxy).

    Always returns a float in [0,1].
    """
    return float(max(0.0, min(1.0, _adapter(amendment, rules))))

