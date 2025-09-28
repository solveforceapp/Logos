# Logos Framework Reference Engine - AI Coding Guide

## Architecture Overview

This is a **governance rule engine** with LLM integration for semantic evaluation. The system processes constitutional/statutory rule amendments through a deterministic pipeline:

- **`logos_engine/`**: Core governance logic (proposal validation, rule mutation, ledger storage)
- **`llm_adapter/`**: LLM integration layer with orchestration and post-processing  
- **Dual execution paths**: `run_demo.py` (local YAML-driven) vs `run_orch.py` (LLM orchestrated)

## Key Design Patterns

### Amendment Processing Pipeline
All amendments flow through `logos_engine.nomics.propose()`:
1. **Structural validation** (required fields: `id`, `parent_ids`, `status_action`, `content_delta`, `procedure_id`, `evidence`)
2. **Juridical validation** (procedure compatibility, transmutation rules)  
3. **Semantic entropy estimation** via pluggable adapters
4. **Metrics evaluation** (coherence, traceability, blast radius)
5. **Rule mutation** and **ledger persistence** if accepted

### Adapter Pattern for LLM Integration
- **Interface**: `SEAdapter = Callable[[Dict, List[Dict]], float]` (amendment, rules → entropy score)
- **Registration**: Use `se.set_adapter(your_adapter)` to plug in custom semantic evaluators
- **Deterministic fallback**: `demo_estimate_se()` provides rule-based scoring for tests/demos

### Orchestrator Pattern 
`llm_adapter.orchestrator.Orchestrator` processes multiple model prompts → single deterministic `Interpretation`:
```python
batch = [ModelPrompt(model="openai", prompt="...", params={"temperature": 0.0})]
interp = orchestrator.run(batch)  # Returns normalized Interpretation
```

## Development Workflows

### Running Demos
```bash
# Local demo (uses YAML fixtures, deterministic adapter)
python run_demo.py

# LLM orchestrated (requires OPENAI_API_KEY or falls back to mock)
python run_orch.py --model openai --temperature 0.0 "prompt1" "prompt2"
```

### Testing
- **Guard**: `conftest.py` prevents accidental real API usage (set `ALLOW_REAL_SDK=1` to override)  
- **Adapter testing**: Register deterministic adapters via `se.set_adapter()` in test setup
- **Fixtures**: Tests expect YAML constitution/policy files in `../../../examples/`

### State Management
- **Ledger**: `logos_engine.store.Ledger` provides hash-chained JSONL persistence
- **Immutable records**: Each ledger entry includes `{ts, hash, prev_hash, obj}`
- **Rule mutation**: In-place updates to rule dictionaries after successful proposals

## Integration Points

### LLM Client Protocol
Implement `ModelClient.complete(model: str, prompt: str, **kwargs) -> Tuple[str, Dict]`
- Built-in: `OpenAIClient` (requires API key) and `MockClient` (deterministic echo)
- Registration: `make_default_clients()` auto-detects available clients

### Post-processing Pipeline
Raw LLM outputs → `RawCompletion` → `normalize_and_fuse()` → `Interpretation`
- **Deterministic fusion**: Multiple model outputs combined via entropy calculations
- **Normalized format**: `{intent: str, arguments: Dict, confidence: float}`

## Project Conventions

- **Dataclasses**: Prefer `@dataclass` for structured types (`Rule`, `Amendment`, `Constitution`)
- **Type safety**: Use `Protocol` for interfaces, explicit type hints throughout
- **Error handling**: Return `(success: bool, metrics: Dict)` tuples rather than exceptions
- **Configuration**: External YAML for constitution/policies, avoid hardcoded thresholds
- **Determinism**: All core logic must be reproducible (use `temperature=0.0`, mock adapters for tests)