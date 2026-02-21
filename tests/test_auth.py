"""Tests for authentication."""
from pathlib import Path
from xr.auth import load_credentials, CredentialError
import pytest

def test_load_from_toml(tmp_path):
    cred_file = tmp_path / "credentials.toml"
    cred_file.write_text('[credentials]\nconsumer_key = "testkey"\nconsumer_secret = "testsecret"\n')
    key, secret = load_credentials(cred_file)
    assert key == "testkey"
    assert secret == "testsecret"

def test_load_from_env(monkeypatch, tmp_path):
    monkeypatch.setenv("XR_CONSUMER_KEY", "envkey")
    monkeypatch.setenv("XR_CONSUMER_SECRET", "envsecret")
    key, secret = load_credentials(tmp_path / "nonexistent.toml")
    assert key == "envkey"
    assert secret == "envsecret"

def test_load_missing_raises(monkeypatch, tmp_path):
    monkeypatch.delenv("XR_CONSUMER_KEY", raising=False)
    monkeypatch.delenv("XR_CONSUMER_SECRET", raising=False)
    with pytest.raises(CredentialError):
        load_credentials(tmp_path / "nonexistent.toml")
