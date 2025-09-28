from llm_adapter.adapters import simple_adapter_factory, simple_adapter


def fake_model(prompt: str) -> str:
    # deterministic mapping for test
    return "interpretation:" + prompt.splitlines()[0][:10]


def test_simple_adapter_factory():
    adapter = simple_adapter_factory([fake_model, fake_model], num_models=2)
    a = {"content_delta": {"effect": "X"}, "parent_ids": ["R-1"]}
    score = adapter(a, [])
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_simple_adapter():
    a = {"content_delta": {"intent": "Preserve"}, "parent_ids": []}
    s = simple_adapter(a, [])
    assert s in (0.5, 0.2)
