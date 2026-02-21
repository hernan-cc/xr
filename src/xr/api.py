"""HTTP client for X API v2 with rate limit handling."""
from __future__ import annotations
import sys
import time
from typing import Any

import requests

API_BASE = "https://api.x.com/2"
MAX_RETRIES = 3

class APIError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(f"API error {status_code}: {message}")

class RateLimitError(APIError):
    def __init__(self, reset_at: int):
        self.reset_at = reset_at
        super().__init__(429, f"Rate limited. Resets at {reset_at}")

class XClient:
    def __init__(self, bearer_token: str):
        self.bearer_token = bearer_token

    def _url(self, endpoint: str) -> str:
        return f"{API_BASE}/{endpoint}"

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.bearer_token}",
            "User-Agent": "xr-cli/0.1.0",
        }

    def get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Make GET request with retry on rate limit."""
        url = self._url(endpoint)
        for attempt in range(MAX_RETRIES):
            resp = requests.get(url, headers=self._headers(), params=params, timeout=15)

            if resp.ok:
                return resp.json()

            if resp.status_code == 429:
                reset_at = int(resp.headers.get("x-rate-limit-reset", 0))
                if attempt < MAX_RETRIES - 1:
                    wait = max(reset_at - int(time.time()), 1) + 1
                    print(f"Rate limited. Waiting {wait}s...", file=sys.stderr)
                    time.sleep(wait)
                    continue
                raise RateLimitError(reset_at)

            raise APIError(resp.status_code, resp.text)

        raise APIError(0, "Max retries exceeded")
