"""Shared test fixtures."""
import pytest
import json

SAMPLE_TWEET_RESPONSE = {
    "data": {
        "id": "123456",
        "text": "Hello world",
        "author_id": "789",
        "created_at": "2026-02-21T15:00:00.000Z",
        "public_metrics": {
            "like_count": 10,
            "retweet_count": 5,
            "reply_count": 2,
            "quote_count": 1,
            "bookmark_count": 3,
            "impression_count": 1000,
        },
        "edit_history_tweet_ids": ["123456"],
    },
    "includes": {
        "users": [
            {
                "id": "789",
                "name": "Test User",
                "username": "testuser",
                "verified": False,
            }
        ]
    },
}

SAMPLE_USER_RESPONSE = {
    "data": {
        "id": "789",
        "name": "Test User",
        "username": "testuser",
        "description": "A test bio",
        "created_at": "2020-01-01T00:00:00.000Z",
        "verified": False,
        "public_metrics": {
            "followers_count": 100,
            "following_count": 50,
            "tweet_count": 500,
            "listed_count": 2,
            "like_count": 1000,
            "media_count": 50,
        },
        "profile_image_url": "https://pbs.twimg.com/profile_images/123/photo_normal.jpg",
    }
}

SAMPLE_SEARCH_RESPONSE = {
    "data": [SAMPLE_TWEET_RESPONSE["data"]],
    "includes": SAMPLE_TWEET_RESPONSE["includes"],
    "meta": {
        "newest_id": "123456",
        "oldest_id": "123456",
        "result_count": 1,
    },
}

@pytest.fixture
def sample_tweet():
    return SAMPLE_TWEET_RESPONSE

@pytest.fixture
def sample_user():
    return SAMPLE_USER_RESPONSE

@pytest.fixture
def sample_search():
    return SAMPLE_SEARCH_RESPONSE

@pytest.fixture
def tmp_config(tmp_path):
    """Provide a temporary config directory."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    return config_dir

@pytest.fixture
def tmp_cache(tmp_path):
    """Provide a temporary cache directory."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    return cache_dir
