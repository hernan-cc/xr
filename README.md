# xr — X Research CLI

Research people and topics on X (Twitter) from the command line. Built for AI agents and human researchers alike.

`xr` gives AI agents (Claude Code, OpenAI Codex, custom agents) structured access to X data through simple CLI commands. Markdown output with YAML frontmatter makes results easy to parse and reason about. SQLite caching prevents redundant API calls — critical when agents run research loops.

Also works great for humans who prefer terminals over browser tabs.

## Install

```bash
pip install xr-cli
```

Or from source:

```bash
git clone https://github.com/hernan-cc/xr.git
cd xr
pip install -e .
```

## Setup

You need X API credentials (Basic tier or higher). Get them at [developer.x.com](https://developer.x.com/en/portal/dashboard).

```bash
xr auth setup
```

This saves your Consumer Key and Secret to `~/.config/xr/credentials.toml` (mode 600).

You can also use environment variables:

```bash
export XR_CONSUMER_KEY="your-key"
export XR_CONSUMER_SECRET="your-secret"
```

## Commands

### Search tweets

```bash
xr search "AI regulation" --top --max 20
xr search "from:elonmusk has:links" --max 50
xr search "startup funding" --lang en --no-rt --top
```

Supports all 47 X search operators. `--top` sorts by relevancy, default is recency. Search window is 7 days (API limitation).

### User profile

```bash
xr user elonmusk
xr user @naval
```

### Timeline

```bash
xr timeline paulg --top --no-rt --no-replies --max 20
```

`--top` sorts by likes. `--no-rt` excludes retweets. `--no-replies` excludes replies.

### Single tweet

```bash
xr tweet https://x.com/user/status/1234567890
xr tweet 1234567890
```

Accepts URLs or bare IDs.

### Thread

```bash
xr thread https://x.com/user/status/1234567890
xr thread 1234567890 --author-only
```

Reconstructs the full conversation. `--author-only` filters to just the thread author's tweets.

### Mentions

```bash
xr mentions paulg --max 20
```

### Followers / Following

```bash
xr followers naval --max 100
xr following naval --max 100
```

### Tweet volume

```bash
xr counts "bitcoin" --granularity day
xr counts "AI agents" --granularity hour
```

Shows tweet volume over time. Useful for spotting trends.

## AI Agent Usage

`xr` is designed to be called by AI agents as a tool. Output is structured markdown that LLMs parse naturally.

**Example: Claude Code skill**

The repo includes a sample skill at [`skills/research-x/SKILL.md`](skills/research-x/SKILL.md) that implements a structured research workflow:

1. Clarify scope (person, topic, or both)
2. Fetch data via `xr` commands
3. Analyze patterns and engagement
4. Save findings to a research note

**Why CLI over API wrappers:**

- **No SDK dependency** — any agent that can run shell commands can use `xr`
- **Cache prevents waste** — agents in loops don't burn credits re-fetching the same data
- **Markdown output** — LLMs parse it natively, no JSON wrangling needed
- **`--pretty` for JSON** — when agents need structured data, it's one flag away

**Example agent workflow:**

```bash
# Agent researches a person
xr user naval                                    # profile
xr timeline naval --top --no-rt --max 20         # what they post about
xr search "from:naval AI" --max 20               # their takes on a topic

# Agent researches a topic
xr search "AI regulation" --top --max 20         # top tweets
xr counts "AI regulation" --granularity day      # volume trend
```

## Global flags

| Flag | Description |
|------|-------------|
| `--pretty` | Output raw JSON instead of markdown |
| `--save` | Save output to `~/.local/share/xr/` (or `XR_SAVE_DIR`) |
| `--no-cache` | Bypass SQLite cache, force fresh API call |

## Output

Default output is markdown with YAML frontmatter:

```
---
type: x-user
username: naval
user_id: "745273"
date: 2026-02-21
source: xr v0.1.0
---

# @naval (Naval)

**Bio**: Angel investor, podcaster, ...
**Joined**: 2007-02-05
**Followers**: 2,100,000 | **Following**: 1,200
**Tweets**: 15,000 | **Likes**: 24,000
**URL**: https://x.com/naval
```

Use `--pretty` for JSON output (useful for piping to `jq`).

## Cache

API responses are cached in SQLite at `~/.cache/xr/cache.db` with sensible TTLs:

| Resource | TTL |
|----------|-----|
| Tweets | 7 days |
| Users | 24 hours |
| Searches | 1 hour |
| Counts | 1 hour |

Use `--no-cache` to force a fresh API call (still writes to cache).

## Configuration

Optional config at `~/.config/xr/config.toml`:

```toml
[output]
save_dir = "~/.local/share/xr"
default_format = "markdown"

[cache]
enabled = true
ttl_tweets = 604800
ttl_users = 86400
ttl_searches = 3600
ttl_counts = 3600
max_size_mb = 50

[search]
default_lang = ""
default_max = 20
```

## API pricing

X API v2 uses pay-per-use pricing — no monthly subscription. You buy credits in the [Developer Console](https://console.x.com) and they're deducted per request:

| Action | Cost |
|--------|------|
| Read a post | $0.005 |
| User lookup | $0.010 |
| Create a post | $0.010 |

Monthly cap: 2M post reads. Resources are deduplicated within a 24h UTC window (re-fetching the same post doesn't double-charge).

The SQLite cache helps keep costs low — repeated lookups hit local cache, not the API.

Rate limits are handled automatically — on HTTP 429, `xr` waits for the reset window and retries (up to 3 times).

## Dependencies

- `click` — CLI framework
- `requests` — HTTP client
- Python 3.11+ (uses `tomllib` from stdlib)

No heavy dependencies. Fast install.

## License

MIT
