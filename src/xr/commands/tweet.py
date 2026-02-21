"""Fetch a single tweet."""
from __future__ import annotations
import re

import click

from xr.api import XClient
from xr.cache import Cache
from xr.models import Tweet

TWEET_FIELDS = "created_at,author_id,text,public_metrics,entities,referenced_tweets,note_tweet,conversation_id"
USER_FIELDS = "username,name,verified"

URL_PATTERN = re.compile(r'(?:x\.com|twitter\.com)/\w+/status/(\d+)')

def extract_tweet_id(input_str: str) -> str:
    m = URL_PATTERN.search(input_str)
    if m:
        return m.group(1)
    if input_str.isdigit():
        return input_str
    raise click.BadParameter(f"Invalid tweet ID or URL: {input_str}")

def fetch_tweet(client: XClient, cache: Cache, tweet_id: str, ttl: int) -> Tweet:
    cached = cache.get_tweet(tweet_id, ttl)
    if cached:
        return Tweet.from_api(cached.get("data", cached), cached.get("includes"))

    data = client.get(f"tweets/{tweet_id}", {
        "tweet.fields": TWEET_FIELDS,
        "expansions": "author_id,referenced_tweets.id",
        "user.fields": USER_FIELDS,
    })
    cache.put_tweet(tweet_id, data)
    return Tweet.from_api(data["data"], data.get("includes"))
