"""Markdown output formatters."""
from __future__ import annotations
from datetime import date
from xr import __version__
from xr.models import Tweet, User, SearchResult, CountResult, Article

def _frontmatter(type_: str, **extra) -> str:
    lines = ["---", f"type: {type_}"]
    for k, v in extra.items():
        lines.append(f"{k}: {v}")
    lines.extend([f"date: {date.today().isoformat()}", f"source: xr v{__version__}", "---"])
    return "\n".join(lines)

def format_tweet(tweet: Tweet) -> str:
    fm = _frontmatter("x-tweet", tweet_id=f'"{tweet.id}"', username=tweet.username)
    lines = [
        fm, "",
        f"# Tweet by @{tweet.username} ({tweet.date})", "",
        tweet.text, "",
        f"**Author**: @{tweet.username} ({tweet.author_name})",
        f"**Date**: {tweet.datetime_str}",
        f"**URL**: {tweet.url}",
        f"**Metrics**: {tweet.likes} likes · {tweet.retweets} retweets · {tweet.replies} replies",
    ]
    if tweet.impressions:
        lines.append(f"**Impressions**: {tweet.impressions:,}")
    return "\n".join(lines) + "\n"

def format_user(user: User) -> str:
    fm = _frontmatter("x-user", username=user.username, user_id=f'"{user.id}"')
    joined = user.created_at[:10] if user.created_at else "unknown"
    lines = [
        fm, "",
        f"# @{user.username} ({user.name})", "",
        f"**Bio**: {user.description}" if user.description else "",
        f"**Joined**: {joined}",
        f"**Followers**: {user.followers:,} | **Following**: {user.following:,}",
        f"**Tweets**: {user.tweet_count:,} | **Likes**: {user.like_count:,}",
        f"**URL**: {user.profile_url}",
    ]
    return "\n".join(line for line in lines if line is not None) + "\n"

def format_search(result: SearchResult, sort: str = "recency") -> str:
    fm = _frontmatter("x-search", query=f'"{result.query}"', results=result.total, sort=sort)
    lines = [fm, "", f'# X Search: "{result.query}"', ""]
    lines.append(f"## Results ({result.total} tweets, sorted by {sort})\n")
    for i, tweet in enumerate(result.tweets, 1):
        lines.append(f"### {i}. @{tweet.username} — {tweet.date}")
        lines.append(f"> {tweet.text}\n")
        lines.append(f"{tweet.likes} likes · {tweet.retweets} retweets · {tweet.replies} replies")
        lines.append(tweet.url)
        lines.append("\n---\n")
    return "\n".join(lines)

def format_thread(tweets: list[Tweet], conversation_id: str) -> str:
    if not tweets:
        return "No tweets in thread.\n"
    author = tweets[0].username
    fm = _frontmatter("x-thread", username=author, conversation_id=f'"{conversation_id}"', tweets=len(tweets))
    lines = [fm, "", f"# Thread by @{author} ({len(tweets)} tweets)\n"]
    for i, tweet in enumerate(tweets, 1):
        lines.append(f"## {i}. @{tweet.username} ({tweet.datetime_str})\n")
        lines.append(f"{tweet.text}\n")
        lines.append(f"*{tweet.likes} likes · {tweet.retweets} retweets · {tweet.replies} replies*\n")
        lines.append("---\n")
    lines.append(f"\n**Thread author**: @{author}")
    lines.append(f"**Conversation ID**: {conversation_id}")
    lines.append(f"**URL**: https://x.com/{author}/status/{conversation_id}")
    return "\n".join(lines) + "\n"

def format_timeline(tweets: list[Tweet], username: str) -> str:
    fm = _frontmatter("x-timeline", username=username, tweets=len(tweets))
    lines = [fm, "", f"# Timeline: @{username} ({len(tweets)} tweets)\n"]
    for i, tweet in enumerate(tweets, 1):
        lines.append(f"### {i}. {tweet.date}")
        lines.append(f"> {tweet.text}\n")
        lines.append(f"{tweet.likes} likes · {tweet.retweets} retweets · {tweet.replies} replies")
        lines.append(tweet.url)
        lines.append("\n---\n")
    return "\n".join(lines)

def format_followers(users: list[User], target_username: str, direction: str = "followers") -> str:
    fm = _frontmatter(f"x-{direction}", username=target_username, count=len(users))
    label = "Followers" if direction == "followers" else "Following"
    lines = [fm, "", f"# {label}: @{target_username} ({len(users)})\n"]
    for user in users:
        bio = f" — {user.description[:80]}..." if user.description and len(user.description) > 80 else f" — {user.description}" if user.description else ""
        lines.append(f"- **@{user.username}** ({user.followers:,} followers){bio}")
    return "\n".join(lines) + "\n"

def format_counts(result: CountResult) -> str:
    fm = _frontmatter("x-counts", query=f'"{result.query}"', granularity=result.granularity)
    lines = [fm, "", f'# Tweet Volume: "{result.query}"\n']
    lines.append("| Date | Count |")
    lines.append("|------|-------|")
    for bucket in result.buckets:
        lines.append(f"| {bucket.start[:10]} | {bucket.count} |")
    lines.append(f"\n**Total**: {result.total} tweets")
    return "\n".join(lines) + "\n"


def format_article(article: Article) -> str:
    fm = _frontmatter(
        "x-article",
        article_id=f'"{article.id}"',
        username=article.username,
        has_article_metadata=article.has_article_metadata
    )

    if article.has_article_metadata and article.title:
        # Format as article with full metadata
        lines = [
            fm, "",
            f"# {article.title}", "",
            f"**Author**: @{article.username} ({article.author_name})",
            f"**Date**: {article.datetime_str}",
        ]
        if article.url:
            lines.append(f"**Article URL**: {article.url}")
        if article.description:
            lines.extend(["", "## Description", "", article.description])
        if article.text:
            lines.extend(["", "## Tweet Text", "", article.text])
    else:
        # Format as tweet with extracted URL
        lines = [
            fm, "",
            f"# Article/Link Tweet by @{article.username}", "",
            article.text, "",
            f"**Author**: @{article.username} ({article.author_name})",
            f"**Date**: {article.datetime_str}",
        ]
        if article.url:
            lines.append(f"**Shared URL**: {article.url}")

    if article.image_url:
        lines.extend(["", f"**Image**: {article.image_url}"])

    lines.extend([
        "",
        f"**Metrics**: {article.likes:,} likes · {article.retweets:,} retweets · {article.replies:,} replies",
    ])
    if article.impressions:
        lines.append(f"**Impressions**: {article.impressions:,}")

    lines.append(f"\n**Tweet URL**: https://x.com/{article.username}/status/{article.id}")

    return "\n".join(lines) + "\n"
