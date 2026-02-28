"""Fetch an article (tweet with article metadata)."""
from __future__ import annotations
import re

import click

from xr.api import XClient
from xr.cache import Cache
from xr.models import Article

TWEET_FIELDS = "created_at,author_id,text,public_metrics,entities,article"
USER_FIELDS = "username,name,verified"

URL_PATTERN = re.compile(r'(?:x\.com|twitter\.com)/\w+/status/(\d+)')

def extract_article_id(input_str: str) -> str:
    m = URL_PATTERN.search(input_str)
    if m:
        return m.group(1)
    if input_str.isdigit():
        return input_str
    raise click.BadParameter(f"Invalid article ID or URL: {input_str}")

def fetch_article(client: XClient, cache: Cache, article_id: str, ttl: int) -> Article:
    cached = cache.get_article(article_id, ttl)
    if cached and "data" in cached:
        return Article.from_api(cached["data"], cached.get("includes"))

    data = client.get(f"tweets/{article_id}", {
        "tweet.fields": TWEET_FIELDS,
        "expansions": "author_id",
        "user.fields": USER_FIELDS,
    })

    # Check for errors in response
    if "errors" in data:
        error_msg = data["errors"][0].get("detail", "Unknown error")
        raise click.ClickException(error_msg)

    if "data" not in data:
        raise click.ClickException(f"No data returned for article {article_id}")

    cache.put_article(article_id, data)
    return Article.from_api(data["data"], data.get("includes"))
