"""Tests for data models."""
from xr.models import Tweet, User, SearchResult, CountBucket

def test_tweet_from_api(sample_tweet):
    tweet = Tweet.from_api(sample_tweet["data"], sample_tweet["includes"])
    assert tweet.id == "123456"
    assert tweet.text == "Hello world"
    assert tweet.username == "testuser"
    assert tweet.author_name == "Test User"
    assert tweet.likes == 10
    assert tweet.retweets == 5
    assert tweet.replies == 2
    assert tweet.url == "https://x.com/testuser/status/123456"

def test_user_from_api(sample_user):
    user = User.from_api(sample_user["data"])
    assert user.id == "789"
    assert user.username == "testuser"
    assert user.followers == 100
    assert user.following == 50
    assert user.tweet_count == 500

def test_tweet_from_api_missing_includes():
    """Tweet with no includes should use fallback values."""
    data = {"id": "1", "text": "hi", "author_id": "2", "created_at": "2026-01-01T00:00:00.000Z",
            "public_metrics": {"like_count": 0, "retweet_count": 0, "reply_count": 0, "quote_count": 0, "bookmark_count": 0, "impression_count": 0},
            "edit_history_tweet_ids": ["1"]}
    tweet = Tweet.from_api(data, {})
    assert tweet.username == "unknown"
    assert tweet.author_name == "Unknown"
