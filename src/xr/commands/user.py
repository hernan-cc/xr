"""Fetch user profile."""
from __future__ import annotations

from xr.api import XClient
from xr.cache import Cache
from xr.models import User

USER_FIELDS = "created_at,description,public_metrics,verified,profile_image_url,url,pinned_tweet_id"

def fetch_user(client: XClient, cache: Cache, username: str, ttl: int = 86400) -> User:
    cached = cache.get_user(username, ttl)
    if cached:
        return User.from_api(cached.get("data", cached))

    data = client.get(f"users/by/username/{username}", {
        "user.fields": USER_FIELDS,
    })
    cache.put_user(data["data"]["id"], username, data)
    return User.from_api(data["data"])
