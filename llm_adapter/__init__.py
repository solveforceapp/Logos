"""LLM adapter convenience package for Logos Framework (Python).

Exported helpers let you create/register adapters that conform to the
`engine/python/logos_engine/se.py` adapter contract.
"""

from .adapters import simple_adapter_factory, simple_adapter
from .postprocess import interpretations_to_entropy, normalize_and_fuse
from .types import AdapterType
from .orchestrator import Orchestrator

__all__ = [
	"simple_adapter_factory",
	"simple_adapter",
	"interpretations_to_entropy",
	"normalize_and_fuse",
	"AdapterType",
	"Orchestrator",
]
