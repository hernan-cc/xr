"""Tests for configuration."""
from pathlib import Path
from xr.config import Config, DEFAULT_CONFIG

def test_default_config():
    config = Config()
    assert config.save_dir is not None
    assert config.cache_enabled is True
    assert config.cache_ttl_tweets == 604800

def test_config_from_toml(tmp_path):
    config_file = tmp_path / "config.toml"
    config_file.write_text('''
[output]
save_dir = "/tmp/xr-test"

[cache]
enabled = false
    ''')
    config = Config.from_file(config_file)
    assert config.save_dir == Path("/tmp/xr-test")
    assert config.cache_enabled is False

def test_config_env_override(monkeypatch, tmp_path):
    monkeypatch.setenv("XR_SAVE_DIR", str(tmp_path / "env-dir"))
    config = Config()
    assert config.save_dir == tmp_path / "env-dir"
