"""Fetch tweet volume counts."""
from __future__ import annotations

from xr.api import XClient
from xr.cache import Cache
from xr.models import CountBucket, CountResult

def fetch_counts(
    client: XClient, cache: Cache, query: str,
    granularity: str = "day", ttl: int = 3600,
) -> CountResult:
    cached = cache.get_counts(query, granularity, ttl)
    if cached:
        buckets = [CountBucket(**b) for b in cached.get("buckets", [])]
        return CountResult(query=query, granularity=granularity, buckets=buckets, total=cached.get("total", 0))

    data = client.get("tweets/counts/recent", {
        "query": query,
        "granularity": granularity,
    })

    buckets = [
        CountBucket(start=b["start"], end=b["end"], count=b["tweet_count"])
        for b in data.get("data", [])
    ]
    total = data.get("meta", {}).get("total_tweet_count", sum(b.count for b in buckets))

    cache.put_counts(query, granularity, {
        "buckets": [{"start": b.start, "end": b.end, "count": b.count} for b in buckets],
        "total": total,
    })

    return CountResult(query=query, granularity=granularity, buckets=buckets, total=total)
