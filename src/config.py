"""Externalized configuration for the Phishing Email Scanner.

All thresholds, model paths, and feature flags are configurable via
environment variables with the SCANNER_ prefix.
"""

import os
from dataclasses import dataclass, field


def _env_int(key: str, default: int) -> int:
    return int(os.environ.get(key, default))


def _env_bool(key: str, default: bool) -> bool:
    val = os.environ.get(key, str(default)).lower()
    return val in ("true", "1", "yes")


def _env_str(key: str, default: str) -> str:
    return os.environ.get(key, default)


@dataclass(frozen=True)
class ScannerConfig:
    safe_threshold: int = field(default_factory=lambda: _env_int("SCANNER_SAFE_THRESHOLD", 45))
    phishing_threshold: int = field(default_factory=lambda: _env_int("SCANNER_PHISHING_THRESHOLD", 70))
    model_path: str = field(default_factory=lambda: _env_str("SCANNER_MODEL_PATH", "data/model/classifier.joblib"))
    llm_enabled: bool = field(default_factory=lambda: _env_bool("SCANNER_LLM_ENABLED", True))
    llm_model: str = field(default_factory=lambda: _env_str("SCANNER_LLM_MODEL", "gemini-2.5-flash"))
    random_seed: int = field(default_factory=lambda: _env_int("SCANNER_RANDOM_SEED", 42))

    # High-impact context keyword lists (externalized per analysis finding F1)
    finance_keywords: tuple[str, ...] = (
        "invoice", "payment", "wire transfer", "bank account", "tax", "billing",
    )
    hr_keywords: tuple[str, ...] = (
        "benefits", "payroll", "salary", "termination", "offer letter",
    )
    executive_keywords: tuple[str, ...] = (
        "ceo", "cfo", "board", "confidential",
    )
