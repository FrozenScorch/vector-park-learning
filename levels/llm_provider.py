"""Small OpenAI-compatible provider helper for Level 1 demos."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from openai import OpenAI


@dataclass(frozen=True)
class LLMConfig:
    provider: str
    base_url: str
    api_key: str
    model: str
    max_tokens: int | None = None
    top_p: float | None = None
    extra_body: dict[str, Any] | None = None


PROVIDER_DEFAULTS = {
    "nvidia": {
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api_key_env": "NVIDIA_API_KEY",
        "model": "google/gemma-4-31b-it",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "api_key_env": "DEEPSEEK_API_KEY",
        "model": "deepseek-v4-flash",
    },
    "ollama": {
        "base_url": "http://localhost:11434/v1",
        "api_key_env": "OLLAMA_API_KEY",
        "model": "llama3.1:8b",
        "fallback_api_key": "ollama",
    },
    "openai-compatible": {
        "base_url": "http://localhost:11434/v1",
        "api_key_env": "LLM_API_KEY",
        "model": "llama3.1:8b",
        "fallback_api_key": "local",
    },
}


def load_llm_config() -> LLMConfig:
    provider = os.getenv("LLM_PROVIDER", "nvidia").strip().lower()
    if provider not in PROVIDER_DEFAULTS:
        supported = ", ".join(sorted(PROVIDER_DEFAULTS))
        raise RuntimeError(f"Unsupported LLM_PROVIDER '{provider}'. Use one of: {supported}.")

    defaults = PROVIDER_DEFAULTS[provider]
    base_url = os.getenv("LLM_BASE_URL", defaults["base_url"]).strip()
    model = os.getenv("LLM_MODEL", os.getenv("NVIDIA_LLM_MODEL", defaults["model"])).strip()
    max_tokens = _optional_int("LLM_MAX_TOKENS")
    top_p = _optional_float("LLM_TOP_P")

    api_key_env = defaults["api_key_env"]
    api_key = os.getenv("LLM_API_KEY") or os.getenv(api_key_env) or defaults.get("fallback_api_key", "")
    if not api_key:
        raise RuntimeError(
            f"Missing API key. Set LLM_API_KEY or {api_key_env} in your .env file. "
            "For local Ollama, set LLM_PROVIDER=ollama and no real key is required."
        )

    extra_body = None
    if provider == "nvidia":
        enable_thinking = _optional_bool("NVIDIA_ENABLE_THINKING")
        if enable_thinking is not None:
            extra_body = {"chat_template_kwargs": {"enable_thinking": enable_thinking}}

    if provider == "deepseek":
        thinking = os.getenv("DEEPSEEK_THINKING", "disabled").strip().lower()
        if thinking not in {"enabled", "disabled"}:
            raise RuntimeError("DEEPSEEK_THINKING must be 'enabled' or 'disabled'.")
        extra_body = {"thinking": {"type": thinking}}

    return LLMConfig(
        provider=provider,
        base_url=base_url,
        api_key=api_key,
        model=model,
        max_tokens=max_tokens,
        top_p=top_p,
        extra_body=extra_body,
    )


def _optional_int(name: str) -> int | None:
    value = os.getenv(name)
    if value is None or not value.strip():
        return None
    try:
        return int(value)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer.") from exc


def _optional_float(name: str) -> float | None:
    value = os.getenv(name)
    if value is None or not value.strip():
        return None
    try:
        return float(value)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be a number.") from exc


def _optional_bool(name: str) -> bool | None:
    value = os.getenv(name)
    if value is None or not value.strip():
        return None
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise RuntimeError(f"{name} must be true or false.")


def make_llm_client() -> tuple[OpenAI, LLMConfig]:
    config = load_llm_config()
    return OpenAI(base_url=config.base_url, api_key=config.api_key), config
