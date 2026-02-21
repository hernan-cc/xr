"""Fetch followers and following lists."""
from __future__ import annotations

from xr.api import XClient
from xr.cache import Cache
from xr.models import User
from xr.commands.user import fetch_user, USER_FIELDS

def fetch_followers(
    client: XClient, cache: Cache, username: str,
    max_results: int = 100, ttl_user: int = 86400,
) -> tuple[list[User], User]:
    target = fetch_user(client, cache, username, ttl_user)

    data = client.get(f"users/{target.id}/followers", {
        "user.fields": USER_FIELDS,
        "max_results": min(max_results, 1000),
    })

    users = [User.from_api(u) for u in data.get("data", [])]
    for u in users:
        cache.put_user(u.id, u.username, {"data": data})

    return users, target

def fetch_following(
    client: XClient, cache: Cache, username: str,
    max_results: int = 100, ttl_user: int = 86400,
) -> tuple[list[User], User]:
    target = fetch_user(client, cache, username, ttl_user)

    data = client.get(f"users/{target.id}/following", {
        "user.fields": USER_FIELDS,
        "max_results": min(max_results, 1000),
    })

    users = [User.from_api(u) for u in data.get("data", [])]
    return users, target
