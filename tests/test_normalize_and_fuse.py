"""
Tests for normalize_and_fuse in llm_adapter.postprocess
"""

from llm_adapter.postprocess import normalize_and_fuse
from llm_adapter.types import RawCompletion

def rc(txt):
    return RawCompletion(model="mock", prompt="p", output=txt, meta={})


def test_determinism_same_inputs_repeatable():
    raws = [rc("please summarize this text"), rc("summary please")]
    a = normalize_and_fuse(raws)
    for _ in range(5):
        assert normalize_and_fuse(raws) == a


def test_tie_breaker_is_lexicographic():
    raws = [rc("classify this"), rc("plan this")]
    r = normalize_and_fuse(raws)
    # Ensure 'intent' exists before accessing
    assert hasattr(r, "intent")
    assert r.intent == sorted(["classify","plan"])[0]
