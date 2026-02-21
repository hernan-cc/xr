"""Tests for SQLite cache."""
import json
import time
from xr.cache import Cache

def test_cache_tweet_roundtrip(tmp_path):
    cache = Cache(tmp_path / "test.db")
    data = {"id": "123", "text": "hello"}
    cache.put_tweet("123", data)
    result = cache.get_tweet("123", ttl=3600)
    assert result == data

def test_cache_tweet_expired(tmp_path):
    cache = Cache(tmp_path / "test.db")
    data = {"id": "123", "text": "hello"}
    cache.put_tweet("123", data)
    # TTL of 0 means immediately expired
    result = cache.get_tweet("123", ttl=0)
    assert result is None

def test_cache_user_roundtrip(tmp_path):
    cache = Cache(tmp_path / "test.db")
    data = {"id": "789", "username": "test"}
    cache.put_user("789", "test", data)
    result = cache.get_user("test", ttl=3600)
    assert result == data

def test_cache_search_roundtrip(tmp_path):
    cache = Cache(tmp_path / "test.db")
    cache.put_search("test query", ["1", "2", "3"])
    result = cache.get_search("test query", ttl=3600)
    assert result == ["1", "2", "3"]

def test_cache_disabled(tmp_path):
    cache = Cache(tmp_path / "test.db", enabled=False)
    cache.put_tweet("123", {"id": "123"})
    assert cache.get_tweet("123", ttl=3600) is None

def test_cache_cleanup(tmp_path):
    cache = Cache(tmp_path / "test.db")
    for i in range(100):
        cache.put_tweet(str(i), {"id": str(i), "text": "x" * 100})
    cache.cleanup(max_size_mb=0)  # Force cleanup
