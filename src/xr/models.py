"""Data models for XR API responses."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Any

def _build_users_map(includes: dict) -> dict[str, dict]:
    """Build user_id -> user dict from API includes."""
    return {u["id"]: u for u in includes.get("users", [])}

@dataclass
class Tweet:
    id: str
    text: str
    author_id: str
    username: str
    author_name: str
    created_at: str
    likes: int
    retweets: int
    replies: int
    quotes: int
    bookmarks: int
    impressions: int
    conversation_id: str | None = None
    referenced_tweets: list[dict] | None = None
    entities: dict | None = None
    url: str = ""

    @classmethod
    def from_api(cls, data: dict, includes: dict | None = None) -> Tweet:
        includes = includes or {}
        users = _build_users_map(includes)
        author = users.get(data.get("author_id", ""), {})
        username = author.get("username", "unknown")
        metrics = data.get("public_metrics", {})
        return cls(
            id=data["id"],
            text=data.get("note_tweet", {}).get("text") or data.get("text", ""),
            author_id=data.get("author_id", ""),
            username=username,
            author_name=author.get("name", "Unknown"),
            created_at=data.get("created_at", ""),
            likes=metrics.get("like_count", 0),
            retweets=metrics.get("retweet_count", 0),
            replies=metrics.get("reply_count", 0),
            quotes=metrics.get("quote_count", 0),
            bookmarks=metrics.get("bookmark_count", 0),
            impressions=metrics.get("impression_count", 0),
            conversation_id=data.get("conversation_id"),
            referenced_tweets=data.get("referenced_tweets"),
            entities=data.get("entities"),
            url=f"https://x.com/{username}/status/{data['id']}",
        )

    @property
    def date(self) -> str:
        if self.created_at:
            dt = datetime.fromisoformat(self.created_at.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d")
        return "unknown"

    @property
    def datetime_str(self) -> str:
        if self.created_at:
            dt = datetime.fromisoformat(self.created_at.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d %H:%M UTC")
        return "unknown"


@dataclass
class User:
    id: str
    username: str
    name: str
    description: str
    created_at: str
    verified: bool
    followers: int
    following: int
    tweet_count: int
    listed_count: int
    like_count: int
    media_count: int
    profile_image_url: str = ""
    url: str = ""
    pinned_tweet_id: str | None = None

    @classmethod
    def from_api(cls, data: dict) -> User:
        metrics = data.get("public_metrics", {})
        return cls(
            id=data["id"],
            username=data["username"],
            name=data.get("name", ""),
            description=data.get("description", ""),
            created_at=data.get("created_at", ""),
            verified=data.get("verified", False),
            followers=metrics.get("followers_count", 0),
            following=metrics.get("following_count", 0),
            tweet_count=metrics.get("tweet_count", 0),
            listed_count=metrics.get("listed_count", 0),
            like_count=metrics.get("like_count", 0),
            media_count=metrics.get("media_count", 0),
            profile_image_url=data.get("profile_image_url", ""),
            url=data.get("url", ""),
            pinned_tweet_id=data.get("pinned_tweet_id"),
        )

    @property
    def profile_url(self) -> str:
        return f"https://x.com/{self.username}"


@dataclass
class SearchResult:
    query: str
    tweets: list[Tweet]
    total: int
    newest_id: str | None = None
    oldest_id: str | None = None
    next_token: str | None = None


@dataclass
class CountBucket:
    start: str
    end: str
    count: int

@dataclass
class CountResult:
    query: str
    granularity: str
    buckets: list[CountBucket]
    total: int


@dataclass
class Article:
    id: str
    title: str
    description: str
    url: str
    text: str
    image_url: str | None = None
    created_at: str = ""
    author_id: str = ""
    username: str = ""
    author_name: str = ""
    likes: int = 0
    retweets: int = 0
    replies: int = 0
    quotes: int = 0
    bookmarks: int = 0
    impressions: int = 0
    has_article_metadata: bool = False

    @classmethod
    def from_api(cls, data: dict, includes: dict | None = None) -> Article:
        includes = includes or {}
        users = _build_users_map(includes)
        author = users.get(data.get("author_id", ""), {})
        username = author.get("username", "unknown")
        metrics = data.get("public_metrics", {})
        article_data = data.get("article", {})
        has_article = bool(article_data)

        # Extract URL from entities if present
        entities = data.get("entities", {})
        urls = entities.get("urls", [])
        extracted_url = urls[0].get("expanded_url", "") if urls else ""

        return cls(
            id=data["id"],
            title=article_data.get("title", ""),
            description=article_data.get("description", ""),
            url=article_data.get("url", extracted_url),
            text=data.get("text", ""),
            image_url=article_data.get("image_url"),
            created_at=data.get("created_at", ""),
            author_id=data.get("author_id", ""),
            username=username,
            author_name=author.get("name", "Unknown"),
            likes=metrics.get("like_count", 0),
            retweets=metrics.get("retweet_count", 0),
            replies=metrics.get("reply_count", 0),
            quotes=metrics.get("quote_count", 0),
            bookmarks=metrics.get("bookmark_count", 0),
            impressions=metrics.get("impression_count", 0),
            has_article_metadata=has_article,
        )

    @property
    def date(self) -> str:
        if self.created_at:
            dt = datetime.fromisoformat(self.created_at.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d")
        return "unknown"

    @property
    def datetime_str(self) -> str:
        if self.created_at:
            dt = datetime.fromisoformat(self.created_at.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d %H:%M UTC")
        return "unknown"
