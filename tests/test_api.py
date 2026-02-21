"""Tests for API client."""
import pytest
from unittest.mock import patch, MagicMock
from xr.api import XClient, RateLimitError, APIError

@pytest.fixture
def client():
    return XClient(bearer_token="test-token")

def test_client_builds_url(client):
    assert client._url("tweets/123") == "https://api.x.com/2/tweets/123"

def test_client_sets_auth_header(client):
    assert client._headers()["Authorization"] == "Bearer test-token"

def test_rate_limit_raises(client):
    mock_resp = MagicMock()
    mock_resp.status_code = 429
    mock_resp.headers = {"x-rate-limit-reset": "0"}
    mock_resp.ok = False
    mock_resp.text = "rate limited"
    with patch("requests.get", return_value=mock_resp), \
         patch("time.sleep"):
        with pytest.raises(RateLimitError):
            client.get("tweets/123")

def test_not_found_raises(client):
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_resp.ok = False
    mock_resp.text = "not found"
    with patch("requests.get", return_value=mock_resp):
        with pytest.raises(APIError, match="404"):
            client.get("tweets/123")
