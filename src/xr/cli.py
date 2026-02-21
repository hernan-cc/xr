"""CLI entry point for XR."""
from __future__ import annotations
import json
import sys
from pathlib import Path

import click

from xr import __version__
from xr.auth import load_credentials, get_bearer_token, CredentialError
from xr.api import XClient, APIError, RateLimitError
from xr.cache import Cache
from xr.config import Config
from xr.formatters.markdown import (
    format_tweet, format_user, format_search, format_thread,
    format_timeline, format_followers, format_counts,
)
from xr.formatters.json_fmt import format_json

def _get_client_and_cache(ctx) -> tuple[XClient, Cache]:
    config = ctx.obj.get("config") or Config.load()
    ctx.obj["config"] = config
    try:
        key, secret = load_credentials()
    except CredentialError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
    token = get_bearer_token(key, secret)
    client = XClient(token)
    no_cache = ctx.obj.get("no_cache", False)
    cache = Cache(enabled=config.cache_enabled and not no_cache)
    return client, cache

def _output(ctx, content: str, filename: str | None = None):
    """Print to stdout and optionally save."""
    click.echo(content)
    if ctx.obj.get("save") and filename:
        config = ctx.obj["config"]
        save_dir = Path(config.save_dir).expanduser()
        save_dir.mkdir(parents=True, exist_ok=True)
        path = save_dir / filename
        path.write_text(content)
        click.echo(f"Saved: {path}", err=True)

@click.group()
@click.version_option(__version__, prog_name="xr")
@click.option("--pretty", is_flag=True, help="Output raw JSON")
@click.option("--save", is_flag=True, help="Save to configured directory")
@click.option("--no-cache", is_flag=True, help="Bypass cache")
@click.pass_context
def main(ctx, pretty, save, no_cache):
    """XR — X (Twitter) Research CLI."""
    ctx.ensure_object(dict)
    ctx.obj["pretty"] = pretty
    ctx.obj["save"] = save
    ctx.obj["no_cache"] = no_cache

@main.command()
@click.argument("input_str")
@click.pass_context
def tweet(ctx, input_str):
    """Fetch a single tweet by ID or URL."""
    from xr.commands.tweet import fetch_tweet, extract_tweet_id
    client, cache = _get_client_and_cache(ctx)
    config = ctx.obj["config"]
    tweet_id = extract_tweet_id(input_str)
    if ctx.obj["pretty"]:
        data = client.get(f"tweets/{tweet_id}", {
            "tweet.fields": "created_at,author_id,text,public_metrics,entities,referenced_tweets,note_tweet,conversation_id",
            "expansions": "author_id,referenced_tweets.id",
            "user.fields": "username,name,verified",
        })
        _output(ctx, format_json(data), f"tweet-{tweet_id}.json")
    else:
        t = fetch_tweet(client, cache, tweet_id, config.cache_ttl_tweets)
        md = format_tweet(t)
        _output(ctx, md, f"tweet-{t.username}-{t.id}.md")

@main.command()
@click.argument("input_str")
@click.option("--author-only", is_flag=True, help="Only thread author's tweets")
@click.pass_context
def thread(ctx, input_str, author_only):
    """Fetch a conversation thread."""
    from xr.commands.tweet import extract_tweet_id
    from xr.commands.thread import fetch_thread
    client, cache = _get_client_and_cache(ctx)
    config = ctx.obj["config"]
    tweet_id = extract_tweet_id(input_str)
    tweets, conv_id = fetch_thread(client, cache, tweet_id, author_only, config.cache_ttl_tweets, config.cache_ttl_searches)
    if ctx.obj["pretty"]:
        _output(ctx, format_json([{"id": t.id, "text": t.text, "username": t.username} for t in tweets]))
    else:
        md = format_thread(tweets, conv_id)
        suffix = "-author-only" if author_only else ""
        _output(ctx, md, f"thread-{tweets[0].username if tweets else 'unknown'}-{conv_id}{suffix}.md")

@main.command()
@click.argument("query")
@click.option("--lang", default="", help="Filter by language (e.g., es, en)")
@click.option("--no-rt", is_flag=True, help="Exclude retweets")
@click.option("--top", is_flag=True, help="Sort by relevancy instead of recency")
@click.option("--max", "max_results", default=20, help="Max results (default: 20)")
@click.pass_context
def search(ctx, query, lang, no_rt, top, max_results):
    """Search recent tweets (7-day window)."""
    from xr.commands.search import fetch_search
    client, cache = _get_client_and_cache(ctx)
    config = ctx.obj["config"]

    # Build query with operators
    q = query
    if lang:
        q += f" lang:{lang}"
    if no_rt:
        q += " -is:retweet"

    sort = "relevancy" if top else "recency"
    result = fetch_search(client, cache, q, max_results, sort, config.cache_ttl_searches, config.cache_ttl_tweets)
    if ctx.obj["pretty"]:
        _output(ctx, format_json({"query": q, "total": result.total, "tweets": [{"id": t.id, "text": t.text, "username": t.username, "likes": t.likes} for t in result.tweets]}))
    else:
        md = format_search(result, sort)
        _output(ctx, md, f"search-{query[:50].replace(' ', '-')}.md")

@main.command()
@click.argument("username")
@click.pass_context
def user(ctx, username):
    """Fetch user profile."""
    from xr.commands.user import fetch_user
    client, cache = _get_client_and_cache(ctx)
    config = ctx.obj["config"]
    username = username.lstrip("@")
    u = fetch_user(client, cache, username, config.cache_ttl_users)
    if ctx.obj["pretty"]:
        _output(ctx, format_json({"id": u.id, "username": u.username, "name": u.name, "followers": u.followers, "following": u.following, "tweets": u.tweet_count}))
    else:
        md = format_user(u)
        _output(ctx, md, f"user-{u.username}.md")

@main.command()
@click.argument("username")
@click.option("--top", is_flag=True, help="Sort by likes")
@click.option("--no-rt", is_flag=True, help="Exclude retweets")
@click.option("--no-replies", is_flag=True, help="Exclude replies")
@click.option("--max", "max_results", default=20, help="Max results")
@click.pass_context
def timeline(ctx, username, top, no_rt, no_replies, max_results):
    """Fetch user's recent tweets."""
    from xr.commands.timeline import fetch_timeline
    client, cache = _get_client_and_cache(ctx)
    config = ctx.obj["config"]
    username = username.lstrip("@")
    tweets, u = fetch_timeline(client, cache, username, max_results, no_rt, no_replies, top, config.cache_ttl_users, config.cache_ttl_tweets)
    if ctx.obj["pretty"]:
        _output(ctx, format_json([{"id": t.id, "text": t.text, "likes": t.likes} for t in tweets]))
    else:
        md = format_timeline(tweets, u.username)
        _output(ctx, md, f"timeline-{u.username}.md")

@main.command()
@click.argument("username")
@click.option("--max", "max_results", default=20, help="Max results")
@click.pass_context
def mentions(ctx, username, max_results):
    """Fetch user's recent mentions."""
    from xr.commands.mentions import fetch_mentions
    client, cache = _get_client_and_cache(ctx)
    config = ctx.obj["config"]
    username = username.lstrip("@")
    tweets, u = fetch_mentions(client, cache, username, max_results, config.cache_ttl_users, config.cache_ttl_tweets)
    if ctx.obj["pretty"]:
        _output(ctx, format_json([{"id": t.id, "text": t.text, "username": t.username} for t in tweets]))
    else:
        md = format_timeline(tweets, f"{u.username} (mentions)")
        _output(ctx, md, f"mentions-{u.username}.md")

@main.command()
@click.argument("username")
@click.option("--max", "max_results", default=100, help="Max results")
@click.pass_context
def followers(ctx, username, max_results):
    """Fetch user's followers."""
    from xr.commands.followers import fetch_followers
    client, cache = _get_client_and_cache(ctx)
    config = ctx.obj["config"]
    username = username.lstrip("@")
    users, target = fetch_followers(client, cache, username, max_results, config.cache_ttl_users)
    if ctx.obj["pretty"]:
        _output(ctx, format_json([{"username": u.username, "followers": u.followers} for u in users]))
    else:
        md = format_followers(users, target.username, "followers")
        _output(ctx, md, f"followers-{target.username}.md")

@main.command()
@click.argument("username")
@click.option("--max", "max_results", default=100, help="Max results")
@click.pass_context
def following(ctx, username, max_results):
    """Fetch who a user follows."""
    from xr.commands.followers import fetch_following
    client, cache = _get_client_and_cache(ctx)
    config = ctx.obj["config"]
    username = username.lstrip("@")
    users, target = fetch_following(client, cache, username, max_results, config.cache_ttl_users)
    if ctx.obj["pretty"]:
        _output(ctx, format_json([{"username": u.username, "followers": u.followers} for u in users]))
    else:
        md = format_followers(users, target.username, "following")
        _output(ctx, md, f"following-{target.username}.md")

@main.command()
@click.argument("query")
@click.option("--granularity", type=click.Choice(["day", "hour"]), default="day", help="Bucket size")
@click.pass_context
def counts(ctx, query, granularity):
    """Show tweet volume over time."""
    from xr.commands.counts import fetch_counts
    client, cache = _get_client_and_cache(ctx)
    config = ctx.obj["config"]
    result = fetch_counts(client, cache, query, granularity, config.cache_ttl_counts)
    if ctx.obj["pretty"]:
        _output(ctx, format_json({"query": query, "total": result.total, "buckets": [{"date": b.start, "count": b.count} for b in result.buckets]}))
    else:
        md = format_counts(result)
        _output(ctx, md, f"counts-{query[:50].replace(' ', '-')}.md")

@main.group()
def auth():
    """Manage API credentials."""
    pass

@auth.command("setup")
def auth_setup():
    """Interactive credential setup."""
    click.echo("XR — X API Credential Setup")
    click.echo("Get your credentials at: https://developer.x.com/en/portal/dashboard\n")
    key = click.prompt("Consumer Key (API Key)")
    secret = click.prompt("Consumer Secret (API Secret)", hide_input=True)

    import os
    from pathlib import Path
    xdg = os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))
    config_dir = Path(xdg) / "xr"
    config_dir.mkdir(parents=True, exist_ok=True)
    cred_path = config_dir / "credentials.toml"
    cred_path.write_text(f'[credentials]\nconsumer_key = "{key}"\nconsumer_secret = "{secret}"\n')
    cred_path.chmod(0o600)
    click.echo(f"\nCredentials saved to {cred_path} (mode 600)")

    # Test connection
    try:
        from xr.auth import get_bearer_token
        get_bearer_token(key, secret)
        click.echo("Connection test: OK")
    except Exception as e:
        click.echo(f"Connection test failed: {e}", err=True)
