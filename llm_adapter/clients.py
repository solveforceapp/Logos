from typing import Dict, Any
import os
# Removed unused import of ModelClient

def make_default_clients() -> Dict[str, Any]:
    """
    Builds a registry from env. If OPENAI_API_KEY is present,
    registers 'openai' key mapped to OpenAIClient().
    """
    clients: Dict[str, Any] = {}
    try:
        from .openai_client import OpenAIClient
        if os.getenv("OPENAI_API_KEY"):
            clients["openai"] = OpenAIClient()
    except Exception as e:
        # Log the exception for debugging; tests can still run with mocks
        import logging
        logging.warning(f"Could not import OpenAIClient: {e}")
        pass
    return clients
