from llm_adapter.postprocess import interpretations_to_entropy


def test_entropy_uniform():
    interpretations = ["a", "b", "c", "d"]
    s = interpretations_to_entropy(interpretations)
    assert 0.99 <= s <= 1.0


def test_entropy_single():
    interpretations = ["same", "same", "same"]
    s = interpretations_to_entropy(interpretations)
    assert s == 0.0
