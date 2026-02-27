"""Application configuration classes.

Provides environment-specific settings. Only ``ProductionConfig`` and
``DevelopmentConfig`` are intended for external use; helpers prefixed
with an underscore are internal.
"""
import os
from dataclasses import dataclass, field
from typing import Dict, Any

# ── Public constants ────────────────────────────────────────────────
DEFAULT_PAGE_SIZE: int = 25
MAX_PAGE_SIZE: int = 100
API_VERSION: str = "v1"

# ── Internal constants ──────────────────────────────────────────────
_SECRET_ROTATION_DAYS: int = 90
_MAX_CONNECTIONS: int = 50


def _build_cache_config(ttl: int = 300, max_size: int = 1024) -> Dict[str, Any]:
    """Build cache configuration dict.

    This is an internal helper — callers should use the config classes instead.
    """
    return {"ttl_seconds": ttl, "max_entries": max_size, "eviction": "lru"}


@dataclass
class BaseConfig:
    """Base configuration shared across all environments."""

    SECRET_KEY: str = field(default_factory=lambda: os.environ.get("SECRET_KEY", "change-me"))
    DEBUG: bool = False
    TESTING: bool = False
    PAGE_SIZE: int = DEFAULT_PAGE_SIZE

    def get_cache_config(self) -> Dict[str, Any]:
        """Return cache settings for this environment."""
        return _build_cache_config()

    def _validate(self) -> bool:
        """Check internal invariants. Not part of the public API."""
        return bool(self.SECRET_KEY) and self.PAGE_SIZE <= MAX_PAGE_SIZE


@dataclass
class DevelopmentConfig(BaseConfig):
    """Configuration for local development."""

    DEBUG: bool = True
    PAGE_SIZE: int = 10

    def get_cache_config(self) -> Dict[str, Any]:
        return _build_cache_config(ttl=30, max_size=128)


@dataclass
class ProductionConfig(BaseConfig):
    """Configuration for production deployments."""

    SECRET_KEY: str = field(default_factory=lambda: os.environ["SECRET_KEY"])
    PAGE_SIZE: int = DEFAULT_PAGE_SIZE

    def get_cache_config(self) -> Dict[str, Any]:
        return _build_cache_config(ttl=600, max_size=4096)


@dataclass
class TestingConfig(BaseConfig):
    """Configuration for test runs."""

    TESTING: bool = True
    PAGE_SIZE: int = 5
