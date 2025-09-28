import os
import pytest

# Guard: prevent tests from using real SDK keys unless explicitly allowed.
@pytest.fixture(autouse=True)
def no_real_sdk(monkeypatch):
    key = os.environ.get('OPENAI_API_KEY')
    allow = os.environ.get('ALLOW_REAL_SDK')
    if key and allow != '1':
        pytest.exit('OPENAI_API_KEY is set. Tests must not use real API keys. Set ALLOW_REAL_SDK=1 to override.', returncode=2)
    yield

pytest_plugins = [
    "pytest_asyncio",
    "pytest_mock",
    "pytest_cov",
]

# Required packages
# pytest>=7.0.0
# pytest-asyncio
# pytest-mock
# pytest-cov  # for coverage reports
