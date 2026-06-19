"""
llm.py — Swappable LLM provider abstraction for the OpenCLAW pipeline.

Configure entirely from .env — no code changes needed to swap models:

    LLM_PROVIDER=gemini          # gemini | openai | anthropic | openrouter
    LLM_MODEL=gemini-2.0-flash   # any model string valid for that provider

Supported providers:
    gemini      — Google Gemini (generativelanguage.googleapis.com)
    openai      — OpenAI + any OpenAI-compatible endpoint (Codex, GPT-4o, etc.)
    anthropic   — Anthropic Claude (claude-opus-4-5, claude-sonnet-4-5, etc.)
    openrouter  — OpenRouter unified gateway (openrouter.ai); gives access to
                  hundreds of models — including free-tier ones — through a
                  single API key and OpenAI-compatible interface.
                  Example free model: nvidia/nemotron-super-49b-v1:free

Adding a new provider:
    1. Subclass LLMProvider and implement generate(prompt) -> str
    2. Add an entry to PROVIDER_REGISTRY at the bottom of this file
    That's it — main.py picks it up automatically.
"""

from __future__ import annotations

import os
import json
import re
import requests
from abc import ABC, abstractmethod
from pathlib import Path
from dotenv import load_dotenv

# Load .env relative to this file, not the cwd — fixes 401s when running from
# a different directory. Falls back gracefully if .env is not found there.
_ENV_PATH = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH, override=False)



# ─── Base interface ───────────────────────────────────────────────────────────

class LLMProvider(ABC):
    """All providers must implement a single method: generate(prompt) -> str."""

    def __init__(self, model: str, api_key: str):
        self.model = model
        self.api_key = api_key

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Send prompt, return raw text response."""
        ...

    def generate_json(self, prompt: str) -> dict:
        """
        Call generate(), then extract and parse the first JSON object found.
        Strips markdown fences automatically.
        Raises ValueError if no valid JSON can be found.
        """
        raw = self.generate(prompt).strip()

        # Strip ```json ... ``` or ``` ... ``` fences
        raw = re.sub(r"^```[a-z]*\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw)

        # Extract the outermost {...} block
        start = raw.find("{")
        end   = raw.rfind("}")
        if start == -1 or end == -1:
            raise ValueError(f"No JSON object found in LLM response:\n{raw}")

        return json.loads(raw[start : end + 1])

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self.model!r})"


# ─── Gemini ───────────────────────────────────────────────────────────────────

class GeminiProvider(LLMProvider):
    """
    Google Gemini via the generativelanguage REST API.
    Recommended models: gemini-2.0-flash, gemini-1.5-flash-002, gemini-1.5-pro
    """

    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

    def generate(self, prompt: str) -> str:
        url = f"{self.BASE_URL}/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.7,
            },
        }
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30,
        )
        if response.status_code != 200:
            raise RuntimeError(f"Gemini API error: {response.text}")

        return response.json()["candidates"][0]["content"]["parts"][0]["text"]


# ─── OpenAI / Codex / OpenAI-compatible ──────────────────────────────────────

class OpenAIProvider(LLMProvider):
    """
    OpenAI Chat Completions API.
    Also works with any OpenAI-compatible endpoint (Codex, local Ollama, etc.)
    by setting OPENAI_BASE_URL in .env.

    Recommended models: gpt-4o, gpt-4o-mini, o1, o3-mini
    Codex (if re-released): set OPENAI_BASE_URL to the Codex endpoint.
    """

    DEFAULT_BASE_URL = "https://api.openai.com/v1"

    def __init__(self, model: str, api_key: str):
        super().__init__(model, api_key)
        self.base_url = os.environ.get("OPENAI_BASE_URL", self.DEFAULT_BASE_URL).rstrip("/")

    def generate(self, prompt: str) -> str:
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
        }
        response = requests.post(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            json=payload,
            timeout=30,
        )
        if response.status_code != 200:
            raise RuntimeError(f"OpenAI API error: {response.text}")

        return response.json()["choices"][0]["message"]["content"]


# ─── Anthropic Claude ─────────────────────────────────────────────────────────

class AnthropicProvider(LLMProvider):
    """
    Anthropic Messages API.
    Recommended models: claude-opus-4-5, claude-sonnet-4-5, claude-haiku-4-5
    """

    BASE_URL = "https://api.anthropic.com/v1/messages"
    API_VERSION = "2023-06-01"

    def generate(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
        }
        response = requests.post(
            self.BASE_URL,
            headers={
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": self.API_VERSION,
            },
            json=payload,
            timeout=30,
        )
        if response.status_code != 200:
            raise RuntimeError(f"Anthropic API error: {response.text}")

        return response.json()["content"][0]["text"]


# ─── OpenRouter ───────────────────────────────────────────────────────────────

class OpenRouterProvider(LLMProvider):
    """
    OpenRouter unified gateway (https://openrouter.ai).

    OpenRouter exposes hundreds of models — including free-tier ones — through
    a single OpenAI-compatible Chat Completions endpoint. Any model listed on
    https://openrouter.ai/models can be used by setting LLM_MODEL to its
    model ID string exactly as shown on that page.

    Free-tier models (append ':free' to the model ID, no credits needed):
        nvidia/nemotron-super-49b-v1:free
        nvidia/nemotron-3-super-120b-a12b:free   ← your current trial model
        meta-llama/llama-3.3-70b-instruct:free
        mistralai/mistral-7b-instruct:free
        google/gemma-3-27b-it:free

    Paid models (billed per token via your OpenRouter credits):
        anthropic/claude-opus-4-5
        openai/gpt-4o
        google/gemini-2.0-flash
        ... and hundreds more at openrouter.ai/models

    Required .env key:  OPENROUTER_API_KEY
    Optional .env key:  OPENROUTER_SITE_URL   (sent as HTTP-Referer header;
                        helps OpenRouter attribute usage — use your domain or
                        any descriptive string, e.g. https://zubbystudio.shop)
    """

    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self, model: str, api_key: str):
        super().__init__(model, api_key)
        # Optional: shown in OpenRouter dashboard under your API usage
        self.site_url = os.environ.get("OPENROUTER_SITE_URL", "https://zubbystudio.shop")

    def generate(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
        }
        response = requests.post(
            self.BASE_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                # OpenRouter uses these headers for usage attribution & rate-limit
                # tiers — always send them even if blank
                "HTTP-Referer": self.site_url,
                "X-Title": "OpenCLAW Shorts Pipeline",
            },
            json=payload,
            timeout=60,   # free-tier models can be slower under load
        )
        if response.status_code != 200:
            raise RuntimeError(f"OpenRouter API error: {response.text}")

        data = response.json()

        # Surface any provider-level error that OpenRouter wraps in a 200
        if "error" in data:
            raise RuntimeError(f"OpenRouter upstream error: {data['error']}")

        return data["choices"][0]["message"]["content"]


# ─── Registry & factory ───────────────────────────────────────────────────────

# Maps the LLM_PROVIDER env value → (ProviderClass, env key for the API key)
PROVIDER_REGISTRY: dict[str, tuple[type[LLMProvider], str]] = {
    "gemini":      (GeminiProvider,      "GEMINI_API_KEY"),
    "openai":      (OpenAIProvider,      "OPENAI_API_KEY"),
    "anthropic":   (AnthropicProvider,   "ANTHROPIC_API_KEY"),
    "openrouter":  (OpenRouterProvider,  "OPENROUTER_API_KEY"),
}


def get_provider() -> LLMProvider:
    """
    Build the active LLMProvider from environment variables.

    Required .env keys:
        LLM_PROVIDER — one of: gemini, openai, anthropic, openrouter
        LLM_MODEL    — model string valid for that provider

    Plus the provider-specific API key. Only the active provider's key needs
    to be set:
        GEMINI_API_KEY
        OPENAI_API_KEY
        ANTHROPIC_API_KEY
        OPENROUTER_API_KEY
    """
    provider_name = os.environ.get("LLM_PROVIDER", "openrouter").lower().strip()
    model         = os.environ.get("LLM_MODEL", "nvidia/nemotron-3-super-120b-a12b:free").strip()

    if provider_name not in PROVIDER_REGISTRY:
        supported = ", ".join(PROVIDER_REGISTRY)
        raise ValueError(
            f"Unknown LLM_PROVIDER='{provider_name}'. Supported: {supported}"
        )

    provider_cls, key_env = PROVIDER_REGISTRY[provider_name]
    api_key = os.environ.get(key_env)

    if not api_key:
        raise ValueError(
            f"LLM_PROVIDER='{provider_name}' requires {key_env} to be set in .env"
        )

    provider = provider_cls(model=model, api_key=api_key)
    return provider