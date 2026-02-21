"""Tests for command logic."""
from unittest.mock import MagicMock
from xr.commands.tweet import fetch_tweet
from xr.commands.user import fetch_user
from xr.commands.search import fetch_search

def test_fetch_tweet(sample_tweet):
    client = MagicMock()
    client.get.return_value = sample_tweet
    cache = MagicMock()
    cache.get_tweet.return_value = None

    tweet = fetch_tweet(client, cache, "123456", ttl=3600)
    assert tweet.id == "123456"
    assert tweet.text == "Hello world"
    client.get.assert_called_once()
    cache.put_tweet.assert_called_once()

def test_fetch_tweet_cached(sample_tweet):
    client = MagicMock()
    cache = MagicMock()
    cache.get_tweet.return_value = sample_tweet

    tweet = fetch_tweet(client, cache, "123456", ttl=3600)
    assert tweet.id == "123456"
    client.get.assert_not_called()  # Should use cache

def test_fetch_user(sample_user):
    client = MagicMock()
    client.get.return_value = sample_user
    cache = MagicMock()
    cache.get_user.return_value = None

    user = fetch_user(client, cache, "testuser", ttl=86400)
    assert user.username == "testuser"
    assert user.followers == 100

def test_fetch_search(sample_search):
    client = MagicMock()
    client.get.return_value = sample_search
    cache = MagicMock()
    cache.get_search.return_value = None
    cache.get_tweet.return_value = None

    result = fetch_search(client, cache, "test query", max_results=10, ttl_search=3600, ttl_tweet=604800)
    assert result.total == 1
    assert result.tweets[0].text == "Hello world"
