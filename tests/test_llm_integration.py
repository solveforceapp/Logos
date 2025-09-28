from llm_adapter.postprocess import normalize_and_fuse
from llm_adapter.types import RawCompletion

def rc(txt):  # helper
    return RawCompletion(model="mock", prompt="p", output=txt, meta={})


def test_majority_vote_and_confidence():
    raws = [rc("Summarize this."), rc("summary please"), rc("classify text")]
    inter = normalize_and_fuse(raws)
    assert inter.intent == "summarize"
    assert 0.5 <= inter.confidence <= 1.0
    assert "tokens_min" in inter.arguments
    assert "tokens_max" in inter.arguments
    assert len(inter.arguments["hashes"]) == 3


from llm_adapter.orchestrator import Orchestrator
from llm_adapter.types import ModelPrompt


class MockClient:
    def __init__(self, mapping):
        self.mapping = mapping

    def complete(self, model: str, prompt: str, **kwargs):
        return self.mapping.get((model, prompt), "summary please"), {"mock": True}


def test_orchestrator_runs_and_fuses():
    clients = {"gpt": MockClient({("gpt", "p1"): "summarize X", ("gpt", "p2"): "classify Y"})}
    orch = Orchestrator(clients)
    inter = orch.run([ModelPrompt(model="gpt", prompt="p1"), ModelPrompt(model="gpt", prompt="p2")])
    assert inter.intent in {"summarize", "classify"}
    assert 0.0 <= inter.confidence <= 1.0
