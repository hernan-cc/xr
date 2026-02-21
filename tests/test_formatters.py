"""Tests for output formatters."""
from xr.models import Tweet, User, SearchResult, CountBucket, CountResult
from xr.formatters.markdown import (
    format_tweet, format_user, format_search, format_thread,
    format_counts, format_timeline, format_followers,
)

def _make_tweet(**kwargs):
    defaults = dict(
        id="123", text="Hello world", author_id="789", username="testuser",
        author_name="Test User", created_at="2026-02-21T15:00:00.000Z",
        likes=10, retweets=5, replies=2, quotes=1, bookmarks=3, impressions=1000,
        url="https://x.com/testuser/status/123",
    )
    defaults.update(kwargs)
    return Tweet(**defaults)

def test_format_tweet_markdown():
    tweet = _make_tweet()
    md = format_tweet(tweet)
    assert "# Tweet by @testuser" in md
    assert "Hello world" in md
    assert "10 likes" in md
    assert "https://x.com/testuser/status/123" in md
    assert "type: x-tweet" in md

def test_format_user_markdown():
    user = User(
        id="789", username="testuser", name="Test User", description="A bio",
        created_at="2020-01-01T00:00:00.000Z", verified=False,
        followers=100, following=50, tweet_count=500, listed_count=2,
        like_count=1000, media_count=50,
    )
    md = format_user(user)
    assert "# @testuser" in md
    assert "A bio" in md
    assert "100" in md  # followers
    assert "type: x-user" in md

def test_format_search_markdown():
    tweets = [_make_tweet(id="1", text="First"), _make_tweet(id="2", text="Second")]
    result = SearchResult(query="test query", tweets=tweets, total=2)
    md = format_search(result, sort="relevancy")
    assert "# X Search" in md
    assert "test query" in md
    assert "First" in md
    assert "Second" in md
    assert "type: x-search" in md

def test_format_counts():
    buckets = [
        CountBucket(start="2026-02-20", end="2026-02-21", count=5),
        CountBucket(start="2026-02-21", end="2026-02-22", count=12),
    ]
    result = CountResult(query="FalloBot", granularity="day", buckets=buckets, total=17)
    md = format_counts(result)
    assert "FalloBot" in md
    assert "17" in md
    assert "type: x-counts" in md
