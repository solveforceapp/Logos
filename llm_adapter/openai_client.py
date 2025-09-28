import os
from typing import Dict, Any, Tuple, Optional
from openai import OpenAI

class OpenAIClient:
    """
    Env-based OpenAI client implementing ModelClient Protocol:
      - OPENAI_API_KEY (required)
      - OPENAI_BASE_URL (optional; for proxies/compat)
      - OPENAI_TIMEOUT_MS (optional)
    """
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        base_url = os.getenv("OPENAI_BASE_URL")
        timeout_s = None
        if os.getenv("OPENAI_TIMEOUT_MS"):
            try:
                timeout_s = int(os.getenv("OPENAI_TIMEOUT_MS")) / 1000.0
            except ValueError:
                pass

        # The official SDK accepts base_url; timeout handled in request kwargs
        if base_url:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            self.client = OpenAI(api_key=api_key)
        self.timeout = timeout_s

    def complete(self, model: str, prompt: str, **kwargs) -> Tuple[str, Dict[str, Any]]:
        """
        Returns (output_text, meta).
        kwargs may include temperature, top_p, max_tokens, etc.
        If `model` is empty, falls back to OPENAI_MODEL env.
        """
        mdl = model or os.getenv("OPENAI_MODEL") or "gpt-4o-mini"
        temperature = kwargs.get("temperature", 0.0)
        top_p = kwargs.get("top_p", 1.0)
        max_tokens = kwargs.get("max_tokens", 512)

        # Chat completions recommended; prompt in a single user message
        resp = self.client.chat.completions.create(
            model=mdl,
            messages=[{"role":"user","content":prompt}],
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            timeout=self.timeout  # supported by SDK
        )
        text = (resp.choices[0].message.content or "").strip()
        meta = {
            "id": resp.id,
            "model": resp.model,
            "usage": getattr(resp, "usage", None).dict() if getattr(resp, "usage", None) else None
        }
        return text, meta
