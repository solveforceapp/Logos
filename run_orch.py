#!/usr/bin/env python3
import os, sys, json, argparse
from typing import Dict
from llm_adapter.orchestrator import Orchestrator
from llm_adapter.clients import make_default_clients
from llm_adapter.types import ModelPrompt, ModelClient

class MockClient:
    def complete(self, model: str, prompt: str, **kwargs):
        # Echo-style mock: returns the prompt so fusion stays deterministic
        return prompt, {"mock": True}


def build_clients() -> Dict[str, ModelClient]:
    clients = make_default_clients()
    if "openai" not in clients:
        clients["mock"] = MockClient()
    return clients


def main():
    ap = argparse.ArgumentParser(description="Run deterministic orchestrator fusion")
    ap.add_argument("--model", default=None, help='Model key ("openai" or "mock"). If omitted, picks "openai" if OPENAI_API_KEY is set, else "mock".')
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--top_p", type=float, default=1.0)
    ap.add_argument("--max_tokens", type=int, default=256)
    ap.add_argument("prompts", nargs="+", help="One or more prompts")
    args = ap.parse_args()

    clients = build_clients()
    chosen = args.model or ("openai" if os.getenv("OPENAI_API_KEY") else "mock")
    if chosen not in clients:
        print(f'No client for model "{chosen}". Available: {list(clients.keys())}', file=sys.stderr)
        sys.exit(2)

    orch = Orchestrator(clients)
    batch = [ModelPrompt(model=chosen, prompt=p, params={
        "temperature": args.temperature,
        "top_p": args.top_p,
        "max_tokens": args.max_tokens
    }) for p in args.prompts]

    inter = orch.run(batch)
    print(json.dumps({
        "model": chosen,
        "batch_size": len(batch),
        "interpretation": {
            "intent": inter.intent,
            "arguments": inter.arguments,
            "confidence": inter.confidence
        }
    }, indent=2))


if __name__ == "__main__":
    main()
