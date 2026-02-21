"""Fetch user's mentions."""
from __future__ import annotations

from xr.api import XClient
from xr.cache import Cache
from xr.models import Tweet, User
from xr.commands.user import fetch_user
from xr.commands.tweet import TWEET_FIELDS, USER_FIELDS as TWEET_USER_FIELDS

def fetch_mentions(
    client: XClient, cache: Cache, username: str,
    max_results: int = 20, ttl_user: int = 86400, ttl_tweet: int = 604800,
) -> tuple[list[Tweet], User]:
    user = fetch_user(client, cache, username, ttl_user)

    data = client.get(f"users/{user.id}/mentions", {
        "tweet.fields": TWEET_FIELDS,
        "expansions": "author_id",
        "user.fields": TWEET_USER_FIELDS,
        "max_results": min(max_results, 100),
    })
    includes = data.get("includes", {})

    tweets = []
    for t in data.get("data", []):
        tweet = Tweet.from_api(t, includes)
        tweets.append(tweet)
        cache.put_tweet(tweet.id, {"data": t, "includes": includes})

    return tweets, user
