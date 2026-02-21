"""Search recent tweets."""
from __future__ import annotations

from xr.api import XClient
from xr.cache import Cache
from xr.models import Tweet, SearchResult
from xr.commands.tweet import TWEET_FIELDS, USER_FIELDS

def fetch_search(
    client: XClient, cache: Cache, query: str,
    max_results: int = 20, sort: str = "recency",
    ttl_search: int = 3600, ttl_tweet: int = 604800,
) -> SearchResult:
    # Check search cache
    cached_ids = cache.get_search(query, ttl_search)
    if cached_ids is not None:
        tweets = []
        for tid in cached_ids:
            cached_tweet = cache.get_tweet(tid, ttl_tweet)
            if cached_tweet:
                tweets.append(Tweet.from_api(
                    cached_tweet.get("data", cached_tweet),
                    cached_tweet.get("includes"),
                ))
        if len(tweets) == len(cached_ids):
            return SearchResult(query=query, tweets=tweets, total=len(tweets))

    # Fresh fetch
    params = {
        "query": query,
        "tweet.fields": TWEET_FIELDS,
        "expansions": "author_id",
        "user.fields": USER_FIELDS,
        "max_results": max(min(max_results, 100), 10),
    }
    if sort == "relevancy":
        params["sort_order"] = "relevancy"

    data = client.get("tweets/search/recent", params)

    includes = data.get("includes", {})
    tweets = []
    tweet_ids = []
    for t in data.get("data", []):
        tweet = Tweet.from_api(t, includes)
        tweets.append(tweet)
        tweet_ids.append(tweet.id)
        cache.put_tweet(tweet.id, {"data": t, "includes": includes})

    cache.put_search(query, tweet_ids)
    meta = data.get("meta", {})

    return SearchResult(
        query=query, tweets=tweets, total=meta.get("result_count", len(tweets)),
        newest_id=meta.get("newest_id"), oldest_id=meta.get("oldest_id"),
        next_token=meta.get("next_token"),
    )
