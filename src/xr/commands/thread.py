"""Fetch a conversation thread."""
from __future__ import annotations

from xr.api import XClient
from xr.cache import Cache
from xr.models import Tweet
from xr.commands.tweet import TWEET_FIELDS, USER_FIELDS, extract_tweet_id, fetch_tweet

def fetch_thread(
    client: XClient, cache: Cache, tweet_id: str,
    author_only: bool = False, ttl_tweet: int = 604800, ttl_search: int = 3600,
) -> tuple[list[Tweet], str]:
    """Returns (sorted tweets, conversation_id)."""
    # Get initial tweet for conversation_id
    initial = fetch_tweet(client, cache, tweet_id, ttl_tweet)
    conversation_id = initial.conversation_id or tweet_id

    # Search conversation
    data = client.get("tweets/search/recent", {
        "query": f"conversation_id:{conversation_id}",
        "tweet.fields": TWEET_FIELDS,
        "expansions": "author_id",
        "user.fields": USER_FIELDS,
        "max_results": 100,
        "sort_order": "recency",
    })

    includes = data.get("includes", {})
    all_tweets = [initial]
    for t in data.get("data", []):
        tweet = Tweet.from_api(t, includes)
        cache.put_tweet(tweet.id, {"data": t, "includes": includes})
        all_tweets.append(tweet)

    # Deduplicate
    seen = set()
    unique = []
    for t in all_tweets:
        if t.id not in seen:
            seen.add(t.id)
            unique.append(t)

    # Sort chronologically
    unique.sort(key=lambda t: t.created_at)

    if author_only:
        author_id = initial.author_id
        unique = [t for t in unique if t.author_id == author_id]

    return unique, conversation_id
