---
name: research-x
description: "Research people and topics on X (Twitter) using the xr CLI. Wraps xr commands into a structured workflow: clarify scope, fetch data, analyze patterns, save findings. Use when user asks to research someone on X, investigate a topic on Twitter, or wants to understand engagement/sentiment around a person or keyword."
---

# /research-x

Research people and topics on X (Twitter) using the `xr` CLI.

## Usage

```
/research-x <person|topic|both> [query]
```

## Workflow

### 1. Clarify Scope

Ask the user (if not obvious from context):
- **Person research**: who? (username or name)
- **Topic research**: what keyword/phrase?
- **Both**: person + their engagement with a topic

### 2. Execute Research

**If researching a person:**

```bash
# Profile
xr user <username>

# Top original tweets (shows what they care about)
xr timeline <username> --top --no-rt --max 20

# Optional: who follows them (find related voices)
xr followers <username> --max 50
```

**If researching a topic:**

```bash
# Top recent tweets (7-day window)
xr search "<query>" --top --max 20

# Volume trend
xr counts "<query>" --granularity day

# Optional: add language filter
xr search "<query>" --lang es --top --no-rt --max 20
```

**If both (person + topic):**

```bash
# Profile first
xr user <username>

# Their tweets on the topic
xr search "from:<username> <topic>" --max 20

# General topic landscape
xr search "<topic>" --top --max 20

# Volume
xr counts "<topic>"
```

### 3. Analyze

After fetching data, synthesize:

- **Top voices**: who gets the most engagement on this topic?
- **Engagement patterns**: likes vs retweets ratio, reply volume
- **Recurring themes**: what angles keep appearing?
- **Sentiment**: positive/negative/neutral tone
- **Timing**: when is volume highest?
- **Notable tweets**: the ones worth reading or responding to

### 4. Save Findings

Create a research note:

```markdown
---
type: x-research
subject: "<person or topic>"
date: YYYY-MM-DD
source: xr + manual analysis
---

# X Research: <subject>

## Summary
[2-3 sentence overview of findings]

## Key Findings
- [bullet points]

## Top Voices
| User | Followers | Engagement | Take |
|------|-----------|------------|------|
| @... | ...       | ...        | ...  |

## Volume Trend
[paste counts output or summarize]

## Notable Tweets
[link + quote the 3-5 most relevant]

## Implications
[what does this mean for the user's goals?]
```

### 5. Suggest Next Steps

Based on findings, suggest:
- People to follow or engage with
- Content opportunities (topics with high engagement, low competition)
- Timing recommendations for posting
- Threads or tweets worth responding to

## Tips

- **Cache is your friend**: xr caches API responses. Repeated lookups don't burn API credits.
- **Pay-per-use**: $0.005/post read, $0.010/user lookup. Cache keeps costs low.
- **7-day search window**: X API only searches last 7 days.
- **47 search operators**: use `from:`, `to:`, `has:links`, `-is:retweet`, `lang:`, etc. for precision.
- **--pretty for raw data**: if you need to dig into the JSON, use `--pretty` flag.

## Examples

```
/research-x person elonmusk
/research-x topic "AI regulation"
/research-x both naval "startups"
```
