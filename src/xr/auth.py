"""Credential loading and bearer token generation."""
from __future__ import annotations
import base64
import os
import tomllib
from pathlib import Path

import requests

class CredentialError(Exception):
    pass

def _credentials_path() -> Path:
    xdg = os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))
    return Path(xdg) / "xr" / "credentials.toml"

def load_credentials(
    path: Path | None = None,
) -> tuple[str, str]:
    """Load consumer key and secret. Priority: env vars > toml."""
    # 1. Environment variables
    env_key = os.environ.get("XR_CONSUMER_KEY")
    env_secret = os.environ.get("XR_CONSUMER_SECRET")
    if env_key and env_secret:
        return env_key, env_secret

    # 2. TOML credentials file
    cred_path = path or _credentials_path()
    if cred_path.exists():
        with open(cred_path, "rb") as f:
            data = tomllib.load(f)
        creds = data.get("credentials", {})
        key = creds.get("consumer_key")
        secret = creds.get("consumer_secret")
        if key and secret:
            return key, secret

    raise CredentialError(
        "No X API credentials found. Run 'xr auth setup' or set "
        "XR_CONSUMER_KEY and XR_CONSUMER_SECRET environment variables."
    )

def get_bearer_token(consumer_key: str, consumer_secret: str) -> str:
    """Generate OAuth 2.0 Bearer Token from consumer credentials."""
    credentials = f"{consumer_key}:{consumer_secret}"
    b64 = base64.b64encode(credentials.encode()).decode()
    resp = requests.post(
        "https://api.x.com/oauth2/token",
        headers={
            "Authorization": f"Basic {b64}",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        },
        data="grant_type=client_credentials",
        timeout=10,
    )
    if not resp.ok:
        raise CredentialError(f"Failed to get bearer token: {resp.status_code} {resp.text}")
    return resp.json()["access_token"]
