"""
sources.py — Automatic topic-relevant video sourcing for the OpenCLAW pipeline.

Replaces the manual URL argument. Given a topic string and niche, this module
searches multiple platforms and returns the URL of the most relevant clip.

Source priority (first successful result wins):
    1. YouTube Shorts  — via yt-dlp search (no API key needed)
    2. Reddit          — r/sports, r/soccer, r/nfl etc. via Reddit JSON API
    3. Pexels          — stock footage fallback (requires PEXELS_API_KEY in .env)

Adding a new source:
    1. Write a function  find_<platform>(query, niche) -> str | None
       that returns a direct URL or None if nothing relevant was found.
    2. Add it to SOURCE_CHAIN at the bottom of this file.

Usage:
    from sources import find_clip
    url = find_clip(topic="A hilarious soccer fail", niche="C")
"""

from __future__ import annotations

import os
import re
import json
import random
import subprocess
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=False)

PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")
YT_DLP_BIN     = os.environ.get("YT_DLP_BIN", "/home/zubbyik/dev/yt-dlp")
DENO_BIN       = os.environ.get("DENO_BIN",   "/home/zubbyik/.deno/bin/deno")

# ─── Niche → search keyword boosters ─────────────────────────────────────────
# These are appended to the topic to bias searches toward relevant footage.
NICHE_KEYWORDS = {
    "A": ["tech", "science", "history", "education", "facts"],
    "B": ["football", "soccer", "goal", "match", "referee"],
    "C": ["sports", "blooper", "fail", "funny", "moment"],
}

# Reddit subreddits to search per niche (in priority order)
NICHE_SUBREDDITS = {
    "A": ["todayilearned", "interestingasfuck", "science", "technology"],
    "B": ["soccer", "football", "sports"],
    "C": ["sports", "funny", "WatchPeopleDieInside", "soccer", "nfl"],
}


def _build_query(topic: str, niche: str) -> str:
    """Combine topic with niche-specific booster keywords for better results."""
    boosters = NICHE_KEYWORDS.get(niche.upper(), [])
    # Only add boosters that aren't already implied by the topic
    extras = [kw for kw in boosters[:2] if kw.lower() not in topic.lower()]
    return f"{topic} {' '.join(extras)}".strip()


def log(msg: str) -> None:
    print(f"[sources] {msg}", flush=True)


# ═══════════════════════════════════════════════════════════════════════════════
# Source 1 — YouTube Shorts (yt-dlp search, no API key needed)
# ═══════════════════════════════════════════════════════════════════════════════

def find_youtube(topic: str, niche: str) -> str | None:
    """
    Search YouTube for a relevant short clip using yt-dlp's built-in
    ytsearch feature. Returns the URL of the best match, or None.

    Filters:
      - Max duration 90s  (keeps clips punchy; Shorts are ≤60s but we allow
        a little headroom so FFmpeg can trim)
      - Prefers results tagged #shorts when possible
    """
    query = _build_query(topic, niche)
    # ytsearchX pulls the top X results; we take 5 and pick the shortest
    search_query = f"ytsearch5:{query} shorts"

    log(f"Searching YouTube: {search_query!r}")

    try:
        result = subprocess.run(
            [
                YT_DLP_BIN,
                "--js-runtime", f"deno:{DENO_BIN}",
                "--no-playlist",
                "--match-filter", "duration <= 90",
                "--print", "%(webpage_url)s\t%(duration)s\t%(title)s",
                "--no-download",
                search_query,
            ],
            capture_output=True, text=True, timeout=30,
        )

        if result.returncode != 0 or not result.stdout.strip():
            log(f"YouTube search returned nothing: {result.stderr[:120]}")
            return None

        # Parse tab-separated lines: url \t duration \t title
        candidates = []
        for line in result.stdout.strip().splitlines():
            parts = line.split("\t", 2)
            if len(parts) == 3:
                url, duration, title = parts
                try:
                    candidates.append((url, int(duration), title))
                except ValueError:
                    pass

        if not candidates:
            return None

        # Pick the shortest clip that's still at least 10s long
        valid = [c for c in candidates if c[1] >= 10]
        if not valid:
            valid = candidates

        best = min(valid, key=lambda c: c[1])
        log(f"YouTube selected: {best[2]!r} ({best[1]}s) — {best[0]}")
        return best[0]

    except subprocess.TimeoutExpired:
        log("YouTube search timed out.")
        return None
    except Exception as e:
        log(f"YouTube search error: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# Source 2 — Reddit (JSON API, no key needed, video posts only)
# ═══════════════════════════════════════════════════════════════════════════════

def find_reddit(topic: str, niche: str) -> str | None:
    """
    Search relevant subreddits for video posts matching the topic.
    Uses Reddit's public JSON search endpoint — no API key required.
    Returns a reddit.com post URL (yt-dlp can download reddit-hosted videos).
    """
    subreddits = NICHE_SUBREDDITS.get(niche.upper(), ["sports", "funny"])
    query      = _build_query(topic, niche)

    for sub in subreddits:
        url = (
            f"https://www.reddit.com/r/{sub}/search.json"
            f"?q={requests.utils.quote(query)}&restrict_sr=1&sort=top&t=month&limit=10"
        )
        headers = {"User-Agent": "openclaw-pipeline/1.0"}

        log(f"Searching Reddit r/{sub}: {query!r}")
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200:
                continue

            posts = resp.json().get("data", {}).get("children", [])

            for post in posts:
                data = post.get("data", {})
                # Only video posts; skip text/image/link posts
                if not data.get("is_video"):
                    continue
                # Skip NSFW
                if data.get("over_18"):
                    continue
                post_url = "https://www.reddit.com" + data.get("permalink", "")
                log(f"Reddit selected: {data.get('title', '')!r} — {post_url}")
                return post_url

        except Exception as e:
            log(f"Reddit r/{sub} error: {e}")
            continue

    log("Reddit: no matching video posts found.")
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# Source 3 — Pexels stock footage (API key required, always available)
# ═══════════════════════════════════════════════════════════════════════════════

def find_pexels(topic: str, niche: str) -> str | None:
    """
    Search Pexels for royalty-free stock footage matching the topic.
    This is the most reliable fallback — Pexels always has something,
    even if it's generic footage rather than a viral clip.

    Requires PEXELS_API_KEY in .env. Free tier: 200 req/hour, 20,000/month.
    Get a key at: https://www.pexels.com/api/
    """
    if not PEXELS_API_KEY:
        log("Pexels: PEXELS_API_KEY not set — skipping.")
        return None

    query = _build_query(topic, niche)
    log(f"Searching Pexels: {query!r}")

    try:
        resp = requests.get(
            "https://api.pexels.com/videos/search",
            headers={"Authorization": PEXELS_API_KEY},
            params={"query": query, "per_page": 5, "orientation": "portrait"},
            timeout=10,
        )

        if resp.status_code != 200:
            log(f"Pexels API error {resp.status_code}: {resp.text[:120]}")
            return None

        videos = resp.json().get("videos", [])
        if not videos:
            log("Pexels: no results found.")
            return None

        # Pick the video whose duration is closest to 30s (ideal for Shorts)
        best = min(videos, key=lambda v: abs(v.get("duration", 0) - 30))

        # Get the highest-quality MP4 file link
        files = best.get("video_files", [])
        mp4_files = [f for f in files if f.get("file_type") == "video/mp4"]
        if not mp4_files:
            return None

        # Sort by resolution descending, pick best
        mp4_files.sort(key=lambda f: f.get("width", 0) * f.get("height", 0), reverse=True)
        direct_url = mp4_files[0]["link"]

        log(f"Pexels selected: {best.get('url')} — direct MP4: {direct_url[:60]}...")
        return direct_url

    except Exception as e:
        log(f"Pexels error: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# Source chain — ordered list of finders, first success wins
# ═══════════════════════════════════════════════════════════════════════════════

SOURCE_CHAIN = [
    find_youtube,   # best: real viral clips, no key needed
    find_reddit,    # good: community clips, no key needed
    find_pexels,    # fallback: stock footage, requires free API key
]


def find_clip(topic: str, niche: str) -> str:
    """
    Try each source in order and return the first URL found.
    Raises RuntimeError if all sources are exhausted with no result.
    """
    log(f"Finding clip for topic={topic!r} niche={niche!r}")

    for finder in SOURCE_CHAIN:
        url = finder(topic, niche)
        if url:
            return url

    raise RuntimeError(
        f"All video sources exhausted for topic={topic!r}. "
        "Check your network, or add PEXELS_API_KEY to .env as a reliable fallback."
    )