import builtins
import types
import pytest
import sys
from types import ModuleType
from typing import Any
from llm_adapter.openai_client import OpenAIClient

class MockChoice:
    def __init__(self, text): self.message = types.SimpleNamespace(content=text)
class DummyUsage:
    def __init__(self): pass

class MockUsage:
    def __init__(self):
        self.total_tokens = 8

class MockResponse:
    def __init__(self, txt): 
        self.choices = [MockChoice(txt)]
        self.id = "cmpl_123"
        self.model = "gpt-4o-mini"
        self.usage = MockUsage()
        self.model = "gpt-4o-mini"

class DummyChatCompletions:
    def create(self, **kwargs): return MockResponse("summary please")

class MockClient:
    def __init__(self, **_): self.chat = types.SimpleNamespace(completions=DummyChatCompletions())
    def create(self, **kwargs): return DummyResp("summary please")
@pytest.fixture(autouse=True)
def patch_openai(monkeypatch):
    # Inject MockClient as openai.OpenAI
    openai_mod = ModuleType("openai")  # type: ignore
    openai_mod.OpenAI = MockClient  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "openai", openai_mod)
    yield

@pytest.fixture(autouse=True)
def patch_openai(monkeypatch):
    # Inject DummyClient as openai.OpenAI
    openai_mod = ModuleType("openai")  # type: ignore
    openai_mod.OpenAI = DummyClient  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "openai", openai_mod)
    yield


def test_openai_client_complete_returns_text_and_meta():
def test_wrapped_openai():
    client = OpenAIClient(api_key="test-key")  # pyright: ignore[reportCallIssue]
    # our client should use MockClient
    assert isinstance(client._client, MockClient)
    assert meta["model"] == "gpt-4o-mini"
    assert meta["usage"]["total_tokens"] == 8


def test_wrapped_openai():
    client = OpenAIClient(api_key="test-key")  # pyright: ignore[reportCallIssue]
    # our client should use DummyClient
    assert isinstance(client._client, DummyClient)
