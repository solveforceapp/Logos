import os
import yaml

# Import the `propose` function from the nomics submodule
from logos_engine.nomics import propose

from logos_engine.store import Ledger
from logos_engine.se_adapter_example import ensemble_estimate_se, se



def test_propose_with_ensemble_adapter(tmp_path):
    """
    Tests the `propose` function using a deterministic ensemble adapter.
    This test:
    - Registers a deterministic ensemble adapter for the test session.
    - Loads example YAML fixtures for constitution, policies, and amendments.
    - Verifies that the example files exist.
    - Loads the constitution, policies, and amendments data from the YAML files.
    - Extracts rules, thresholds, and procedures from the loaded data.
    - Initializes a temporary ledger for recording proposals.
    - Runs the `propose` function on the first amendment and checks:
        - The return value `ok` is a boolean.
        - The return value `metrics` is a dictionary.
    Args:
        tmp_path (pathlib.Path): Temporary directory provided by pytest for file operations.
    Raises:
        FileNotFoundError: If any of the required example YAML files are missing.
    """
    # Register deterministic ensemble adapter for test
    se.set_adapter(lambda a, r: ensemble_estimate_se(a, r, num_models=5))
    examples_dir = tmp_path / "examples"
    examples_dir.mkdir(exist_ok=True)

    # Copy example YAML files from source to tmp_path for isolation
    from pathlib import Path
    src_base = Path(__file__).parent.parent.parent / "examples"
    for fname in ["constitution.yaml", "policies.yaml", "amendments.yaml"]:
        src = src_base / fname
        dst = examples_dir / fname
        if not src.exists():
            raise FileNotFoundError(f"Example YAML file not found: {src}")
        with open(src, "rb") as fsrc, open(dst, "wb") as fdst:
            fdst.write(fsrc.read())

    constitution_path = examples_dir / "constitution.yaml"
    policies_path = examples_dir / "policies.yaml"
    amendments_path = examples_dir / "amendments.yaml"

    with open(constitution_path) as f:
        constitution = yaml.safe_load(f)
    with open(policies_path) as f:
        policies = yaml.safe_load(f)
    with open(amendments_path) as f:
        amendments = yaml.safe_load(f)

    rules = policies["rules"]
    thresholds = constitution["thresholds"]
    procedures = constitution["procedures"]

    ledger_path = tmp_path / "ledger.jsonl"
    ledger = Ledger(path=str(ledger_path))

    # Run first amendment from examples and ensure propose returns a boolean and metrics dict
    a = amendments["amendments"][0]
    ok, metrics = propose(a, rules, thresholds, procedures, ledger)
    assert isinstance(ok, bool)
    assert isinstance(metrics, dict)

"""
Removed invalid helper test_propose_basic; use test_propose_with_ensemble_adapter instead.
"""
