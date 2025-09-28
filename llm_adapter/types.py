from dataclasses import dataclass
from typing import Callable, Dict, Any, List, Protocol, Tuple

# Adapter type: (amendment: dict, rules: list[dict]) -> float
AdapterType = Callable[[Dict[str, Any], List[Dict[str, Any]]], float]


@dataclass(frozen=True)
class ModelPrompt:
	model: str
	prompt: str
	params: Dict[str, Any] = None  # temperature, top_p, etc.


@dataclass(frozen=True)
class RawCompletion:
	model: str
	prompt: str
	output: str
	meta: Dict[str, Any]


@dataclass(frozen=True)
class Interpretation:
	"""Normalized, minimal, deterministic interpretation."""
	intent: str
	arguments: Dict[str, Any]
	confidence: float  # 0..1 after deterministic post-processing


class ModelClient(Protocol):
	def complete(self, model: str, prompt: str, **kwargs) -> Tuple[str, Dict[str, Any]]:
		...

