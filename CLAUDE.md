# xr — Development Guide

## What this is

`xr` is a CLI tool for researching people and topics on X (Twitter) via the v2 API. Python package, pip-installable as `xr-cli`.

## Project structure

```
src/xr/
  __init__.py          # version
  cli.py               # click entry point, wires all commands
  auth.py              # credential loading (TOML, env) + bearer token
  config.py            # TOML config with XDG paths + env overrides
  api.py               # HTTP client with rate limit retry
  cache.py             # SQLite cache with TTL per resource type
  models.py            # dataclasses: Tweet, User, SearchResult, CountResult
  commands/
    tweet.py           # single tweet fetch + URL parsing
    thread.py          # conversation reconstruction via search
    search.py          # recent tweet search with caching
    user.py            # profile lookup
    timeline.py        # user timeline with filters
    mentions.py        # user mentions
    followers.py       # followers/following lists
    counts.py          # tweet volume over time
  formatters/
    markdown.py        # markdown with YAML frontmatter
    json_fmt.py        # JSON output
tests/
  conftest.py          # shared fixtures (sample API responses)
  test_models.py
  test_config.py
  test_auth.py
  test_api.py
  test_cache.py
  test_formatters.py
  test_commands.py
  test_cli.py
```

## Key patterns

- **Commands expose `fetch_*` functions** — business logic separated from CLI wiring. `cli.py` imports and calls them.
- **Cache-first**: every fetch function checks cache before hitting the API. Cache writes happen even with `--no-cache` (only reads are bypassed).
- **Models parse API responses** via `from_api()` classmethods. Raw JSON stored in cache, models built at read time.
- **Formatters are pure functions** — take model objects, return strings. No side effects.
- **Rate limit retry** in `api.py` — auto-waits on 429, up to 3 attempts.

## Running tests

```bash
python3 -m pytest tests/ -v
```

All tests use mocks for API calls. No live API access needed for tests.

## Auth

Two credential sources, checked in order:
1. Environment: `XR_CONSUMER_KEY` / `XR_CONSUMER_SECRET`
2. TOML: `~/.config/xr/credentials.toml`

Bearer token is generated fresh each session via OAuth 2.0 client_credentials flow.

## X API constraints

- **Pay-per-use**: $0.005/post read, $0.010/user lookup, 2M post reads/month cap
- **Search window**: 7 days only (recent search, not full archive)
- **max_results**: minimum 10, maximum 100 per request
- **Liked tweets endpoint**: requires User Context OAuth (not supported, app-only auth only)

## Adding a new command

1. Create `src/xr/commands/newcmd.py` with a `fetch_*` function
2. Add click command in `cli.py` that calls it
3. Add formatter function in `formatters/markdown.py` if needed
4. Add cache methods in `cache.py` if caching a new resource type
5. Write tests in `tests/test_commands.py`

## Dependencies

Minimal on purpose: `click`, `requests`, and stdlib (`tomllib`, `sqlite3`, `json`). No async, no ORM, no heavy frameworks.

## Build and publish

```bash
pip install build twine
python3 -m build
twine upload dist/*
```

PyPI package name: `xr-cli`
