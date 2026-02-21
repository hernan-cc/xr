"""Configuration management via TOML + env vars."""
from __future__ import annotations
import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_CONFIG = {
    "output": {
        "save_dir": "~/.local/share/xr",
        "default_format": "markdown",
    },
    "cache": {
        "enabled": True,
        "ttl_tweets": 604800,
        "ttl_users": 86400,
        "ttl_searches": 3600,
        "ttl_counts": 3600,
        "max_size_mb": 50,
    },
    "search": {
        "default_lang": "",
        "default_max": 20,
    },
}

def _config_path() -> Path:
    xdg = os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))
    return Path(xdg) / "xr" / "config.toml"

@dataclass
class Config:
    save_dir: Path = field(default_factory=lambda: Path(DEFAULT_CONFIG["output"]["save_dir"]).expanduser())
    default_format: str = "markdown"
    cache_enabled: bool = True
    cache_ttl_tweets: int = 604800
    cache_ttl_users: int = 86400
    cache_ttl_searches: int = 3600
    cache_ttl_counts: int = 3600
    cache_max_size_mb: int = 50
    search_default_lang: str = ""
    search_default_max: int = 20

    def __post_init__(self):
        # Env var overrides
        env_save = os.environ.get("XR_SAVE_DIR")
        if env_save:
            self.save_dir = Path(env_save)

    @classmethod
    def from_file(cls, path: Path | None = None) -> Config:
        path = path or _config_path()
        config = cls()
        if path.exists():
            with open(path, "rb") as f:
                data = tomllib.load(f)
            output = data.get("output", {})
            cache = data.get("cache", {})
            search = data.get("search", {})
            if "save_dir" in output:
                config.save_dir = Path(output["save_dir"]).expanduser()
            if "default_format" in output:
                config.default_format = output["default_format"]
            if "enabled" in cache:
                config.cache_enabled = cache["enabled"]
            if "ttl_tweets" in cache:
                config.cache_ttl_tweets = cache["ttl_tweets"]
            if "ttl_users" in cache:
                config.cache_ttl_users = cache["ttl_users"]
            if "ttl_searches" in cache:
                config.cache_ttl_searches = cache["ttl_searches"]
            if "ttl_counts" in cache:
                config.cache_ttl_counts = cache["ttl_counts"]
            if "max_size_mb" in cache:
                config.cache_max_size_mb = cache["max_size_mb"]
            if "default_lang" in search:
                config.search_default_lang = search["default_lang"]
            if "default_max" in search:
                config.search_default_max = search["default_max"]
        # Env overrides take precedence
        config.__post_init__()
        return config

    @classmethod
    def load(cls) -> Config:
        return cls.from_file()
