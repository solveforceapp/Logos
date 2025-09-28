from typing import List, Dict
from .types import ModelPrompt, RawCompletion, Interpretation, ModelClient
from .postprocess import normalize_and_fuse


class Orchestrator:
    """
    Accepts multiple prompts/clients, collects outputs, and produces
    a deterministic Interpretation via post-processing.
    """
    def __init__(self, clients: Dict[str, ModelClient]) -> None:
        self.clients = clients

    def run(self, batch: List[ModelPrompt]) -> Interpretation:
        raws: List[RawCompletion] = []
        for mp in batch:
            client = self.clients.get(mp.model)
            if client is None:
                raise ValueError(f"No client configured for model: {mp.model}")
            output, meta = client.complete(mp.model, mp.prompt, **(mp.params or {}))
            raws.append(RawCompletion(model=mp.model, prompt=mp.prompt, output=output, meta=meta))
        return normalize_and_fuse(raws)
