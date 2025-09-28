from typing import Dict, Any, List, Callable, Sequence, Optional
from .types import AdapterType
from .postprocess import interpretations_to_entropy
from .openai_client import OpenAIClient

def simple_adapter_factory(model_callables: Sequence[Callable[[str], str]], num_models: Optional[int] = None) -> AdapterType:
    """Create an adapter that queries a sequence of model_callables.

    Each callable should accept a string prompt and return a short interpretation string.
    The returned adapter matches logos_engine.se.SEAdapter: (amendment, rules) -> float
    If num_models is None, it defaults to the length of model_callables.
    """
    if num_models is None:
        num_models = len(model_callables)

    def adapter(amendment: Dict[str, Any], rules: List[Dict[str, Any]]) -> float:
        facts = []
        for k, v in amendment.get("content_delta", {}).items():
            facts.append(f"{k}:{str(v).strip()}")
        prompt = "\n".join(facts) or "noop"

        interpretations: List[str] = []
        for i in range(min(num_models, len(model_callables))):
            try:
                resp = model_callables[i](prompt)
            except Exception:
                resp = "error"
            interpretations.append(resp)

        return interpretations_to_entropy(interpretations)

    return adapter


def simple_adapter(amendment: Dict[str, Any], rules: List[Dict[str, Any]]) -> float:
    """Trivial adapter that maps amendment facts to a deterministic interpretation set.

    This is useful for local development without external LLMs.
    """
    facts = []
    for k, v in amendment.get("content_delta", {}).items():
        facts.append(f"{k}:{str(v).strip()}")
    if not facts:
        return 0.0
    # simple heuristic: if effect or intent changed, return moderate entropy
    touches = sum(1 for f in facts if f.startswith("effect") or f.startswith("intent"))
    return 0.5 if touches else 0.2

# Alias for backwards compatibility
make_ensemble_adapter = simple_adapter_factory

- from .openai_client import OpenAIClient
+ from .clients.openai_client import OpenAIClient