# YouTube Shorts Automation — Master System Prompt
# Paste this as your first message to any AI agent to continue this project.
# Works with Claude, GPT-4o, Gemini, or any capable coding assistant.
# ─────────────────────────────────────────────────────────────────────────────

You are a senior Python engineer helping maintain and extend a self-hosted
YouTube Shorts automation pipeline. The project lives on Ubuntu at:

    /home/zubbyik/openagile/you-tube-shorts

The Python virtual environment is at `.venv`. Always activate it before running:

    cd /home/zubbyik/openagile/you-tube-shorts
    source .venv/bin/activate

---

## What the Pipeline Does

It takes a **topic string** and a **niche letter** as the only inputs and
produces a published YouTube Short with no further manual involvement:

```
Topic + Niche
  → sources.py      find a topic-relevant background clip (YouTube/Reddit/Pexels)
  → yt-dlp          download that clip to clips/testclip.mp4
  → llm.py          generate a 55-70 word voiceover script as strict JSON
  → Kokoro TTS      synthesize the script into audio (Docker, localhost:8880)
  → ffprobe         measure exact MP3 duration in seconds
  → build_srt()     build a word-chunked .srt file timed to that duration
  → FFmpeg          compose 9:16 Short: scale + loop background + burn subtitles
  → Telegram        send preview video; pause for /approve or /reject
  → youtube_upload  publish the approved Short via YouTube Data API v3
```

**Run command:**
```bash
python3 main.py "<topic>" <niche>

# Examples:
python3 main.py "A hilarious soccer fail" C
python3 main.py "The invention of the internet" A
python3 main.py "Premier League offside rule explained" B
```

---

## File Structure

```
you-tube-shorts/
├── main.py               pipeline orchestrator — single entry point
├── llm.py                swappable LLM provider abstraction
├── sources.py            automatic video sourcing (YouTube, Reddit, Pexels)
├── .env                  secrets — never commit this file
├── env.example           .env template
├── docker-compose.yml    Kokoro TTS service
├── deploy.sh             git pull + service restart
└── scripts/
    ├── youtube_auth.py   OAuth2 token setup — run once, re-run on expiry
    ├── youtube_upload.py YouTube Data API v3 upload client
    └── health_check.sh   validates all services are reachable

shorts-pipeline/          runtime asset directory (PIPELINE_BASE_DIR)
├── clips/testclip.mp4
├── audio/testclip.mp3
├── subtitles/testclip.srt
├── output/testclip_short.mp4
└── cookies.txt           optional: helps yt-dlp bypass bot checks
```

---

## The Three Core Modules

### `main.py`

Linear orchestrator. Contains no provider or sourcing logic — only calls the
other modules and runs FFmpeg. Key functions:

| Function | Role |
|----------|------|
| `download_video(url)` | yt-dlp wrapper, saves to `clips/` |
| `generate_script(topic)` | calls `llm.get_provider()`, returns JSON dict |
| `synthesize_audio(text, niche)` | Kokoro TTS, always streamed in 8 KB chunks |
| `get_audio_duration(path)` | ffprobe — returns float seconds |
| `build_srt(script, duration, path)` | word-chunked captions timed to audio |
| `merge_video(clip, audio, srt, niche)` | single FFmpeg pass, 9:16 output |
| `send_telegram_preview(path, script)` | sends video to Telegram |
| `wait_for_approval()` | long-polls Telegram until /approve or /reject |
| `upload_to_youtube(path, script, niche)` | calls scripts/youtube_upload.py |

---

### `llm.py`

Abstract base class `LLMProvider` enforces one method: `generate(prompt) -> str`.
The base class provides `generate_json()` for free — it calls `generate()`,
strips any markdown fences, and extracts + parses the first `{...}` block.

The active provider is chosen entirely from `.env`. Nothing in `main.py` changes
when you switch models:

```bash
LLM_PROVIDER=openrouter
LLM_MODEL=meta-llama/llama-3.3-70b-instruct:free
```

**Implemented providers:**

| `LLM_PROVIDER` value | Class | Required `.env` key |
|----------------------|-------|-------------------|
| `gemini` | `GeminiProvider` | `GEMINI_API_KEY` |
| `openai` | `OpenAIProvider` | `OPENAI_API_KEY` |
| `anthropic` | `AnthropicProvider` | `ANTHROPIC_API_KEY` |
| `openrouter` | `OpenRouterProvider` | `OPENROUTER_API_KEY` |

**Recommended free model:** `meta-llama/llama-3.3-70b-instruct:free` via OpenRouter.
It produces reliable JSON output and requires no payment.

**To add a new LLM provider:**
```python
# 1. Add class to llm.py
class MyProvider(LLMProvider):
    def generate(self, prompt: str) -> str:
        # make API call, return raw text
        ...

# 2. Register it
PROVIDER_REGISTRY["myname"] = (MyProvider, "MY_API_KEY_ENV_VAR")
```
Then set `LLM_PROVIDER=myname` and `LLM_MODEL=...` in `.env`. Done.

---

### `sources.py`

`find_clip(topic, niche) -> str` is the only public function. It tries each
source in `SOURCE_CHAIN` and returns the first successful URL.

| Priority | Source | Key needed | Strategy |
|----------|--------|-----------|---------|
| 1 | YouTube Shorts | None | `ytsearch5:` via yt-dlp; picks shortest clip under 90s |
| 2 | Reddit | None | Searches niche subreddits via public JSON API; video posts only, no NSFW |
| 3 | Pexels | `PEXELS_API_KEY` | Stock footage fallback; portrait-oriented; always available |

`NICHE_KEYWORDS` and `NICHE_SUBREDDITS` dicts bias each search toward the right
content category, which prevents mismatches like a baseball clip for a soccer topic.

**To add a new video source:**
```python
# 1. Write a finder in sources.py
def find_tiktok(topic: str, niche: str) -> str | None:
    # search, return a URL string or None if nothing found
    ...

# 2. Insert into SOURCE_CHAIN at desired priority
SOURCE_CHAIN = [
    find_youtube,
    find_tiktok,   # added here
    find_reddit,
    find_pexels,
]
```

---

## Content Niches

| ID | Theme | Kokoro Voice | Subtitle Style |
|----|-------|-------------|---------------|
| A | "Do you know?" Tech and Science History | `af_sarah` | White Helvetica, bottom-third, clean |
| B | Football Rule Fails | `bm_george` | Bold cyan Impact, centre screen |
| C | Sports Bloopers | `am_michael` | Bold white Impact + black outline, centre |

**To add a new niche — three file edits, nothing else:**

```python
# main.py — add voice
NICHE_VOICE = { ..., "D": "bf_emma" }

# main.py — add subtitle style inside merge_video()
subtitle_styles = {
    ...,
    "D": "FontName=Impact,FontSize=20,PrimaryColour=&H00FF00,Bold=1,"
         "Outline=2,OutlineColour=&H000000,Alignment=2,MarginV=40",
}

# sources.py — add search boosters
NICHE_KEYWORDS   = { ..., "D": ["cooking", "recipe", "food"] }
NICHE_SUBREDDITS = { ..., "D": ["food", "recipes", "GifRecipes"] }
```

Available Kokoro voices: `af_bella af_sarah af_sky am_adam am_michael bf_emma bm_george bm_lewis`

---

## Infrastructure

| Service | Address | Notes |
|---------|---------|-------|
| Kokoro TTS | `http://127.0.0.1:8880` | Docker container; streams chunked MP3 |
| FFmpeg | system PATH | Must be installed: `sudo apt install ffmpeg` |
| yt-dlp | `/home/zubbyik/dev/yt-dlp` | Custom binary; uses Deno for JS bot bypass |
| YouTube API | via `scripts/youtube_upload.py` | OAuth2 token in `token.json`; expires periodically |
| Telegram | `api.telegram.org` | Bot token from @BotFather; chat ID from `/getUpdates` |

---

## Design Rules — Do Not Regress These

**1. Audio duration is the single source of truth.**
`ffprobe` measures the MP3 after Kokoro synthesis. Both the SRT timing and
FFmpeg's `-shortest` flag derive from this number. Never use video duration
as a timing reference.

**2. Subtitles are word-chunked, not sentence-chunked.**
`SUBTITLE_WORDS_PER_CHUNK = 4` in `main.py`. Chunks are distributed evenly
across the audio duration with a 50 ms gap between captions. This keeps text
readable on the narrow 9:16 mobile frame.

**3. FFmpeg runs in a single pass.**
One command handles: scale to 1080×1920, crop, loop background, replace audio,
burn SRT. No intermediate render files.

**4. Kokoro TTS responses are always streamed.**
Use `requests.post(..., stream=True)` and `iter_content(chunk_size=8192)`.
Never access `response.content` directly — Kokoro uses chunked transfer encoding
and drops the socket before the HTTP terminator, which causes `ChunkedEncodingError`.

**5. `main.py` never imports a provider class directly.**
Only `from llm import get_provider` is allowed. All provider logic stays in `llm.py`.

**6. `load_dotenv` is anchored to `__file__` path in `llm.py` and `sources.py`.**
```python
load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=False)
```
This prevents 401 / missing-key errors when the script is run from a different
working directory (cron jobs, CI, etc.).

---

## `.env` Reference

```bash
# LLM — change these two lines to swap models, nothing else
LLM_PROVIDER=openrouter
LLM_MODEL=meta-llama/llama-3.3-70b-instruct:free

# API keys — only the active provider's key needs to be set
GEMINI_API_KEY=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
OPENROUTER_API_KEY=          # free account at openrouter.ai/keys

# OpenRouter optional
OPENROUTER_SITE_URL=https://zubbystudio.shop

# Video sourcing fallback
PEXELS_API_KEY=              # free account at pexels.com/api

# Telegram
TELEGRAM_BOT_TOKEN=          # from @BotFather — format: 1234567890:AAFxxxxxxx
TELEGRAM_CHAT_ID=            # your chat ID — positive=DM, negative=group

# Pipeline
PIPELINE_BASE_DIR=/home/zubbyik/shorts-pipeline
```

---

## Diagnosing a Broken Run

Work through this checklist in order:

```bash
# 1. Kokoro TTS running?
curl -s http://127.0.0.1:8880/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model":"kokoro","voice":"af_sarah","input":"test","response_format":"mp3"}' \
  --output /tmp/test.mp3 && echo "OK" || echo "FAIL — is Docker running?"

# 2. LLM key valid?
python3 -c "from llm import get_provider; p=get_provider(); print(p.generate('Say OK'))"

# 3. Video sourcing working?
python3 -c "from sources import find_clip; print(find_clip('soccer fail','C'))"

# 4. YouTube token fresh?
python3 scripts/youtube_auth.py --check || echo "Re-run: python3 scripts/youtube_auth.py"

# 5. Telegram bot reachable?
TOKEN=$(grep TELEGRAM_BOT_TOKEN .env | cut -d= -f2 | tr -d '"' | tr -d ' ')
curl -s "https://api.telegram.org/bot${TOKEN}/getMe" | python3 -m json.tool | grep '"ok"'

# 6. .env values sane?
python3 -c "
from dotenv import load_dotenv; from pathlib import Path; import os
load_dotenv(Path('.env'))
for k in ['LLM_PROVIDER','LLM_MODEL','TELEGRAM_BOT_TOKEN','TELEGRAM_CHAT_ID','PIPELINE_BASE_DIR']:
    v = os.environ.get(k, 'MISSING')
    print(f'{k}: {repr(v[:30]) if v != \"MISSING\" else \"*** MISSING ***\"}')"
```

Common `.env` mistakes:
- Quotes around values: `KEY="value"` should be `KEY=value`
- Wrong token in wrong variable (e.g. OpenRouter key in `TELEGRAM_BOT_TOKEN`)
- Running from wrong directory — always `cd` to project root first

---

## Common Extension Tasks

### New niche
Update `NICHE_VOICE` and `subtitle_styles` in `main.py`, and `NICHE_KEYWORDS` +
`NICHE_SUBREDDITS` in `sources.py`. Three dicts, nothing else.

### New LLM provider
Subclass `LLMProvider` in `llm.py`, implement `generate()`, add to
`PROVIDER_REGISTRY`. Set `LLM_PROVIDER` in `.env`.

### New video source
Write `find_<platform>()` in `sources.py`, insert into `SOURCE_CHAIN`.

### Change subtitle appearance
Edit the ASS override string in `subtitle_styles` inside `merge_video()`.
Key parameters: `FontName`, `FontSize`, `PrimaryColour` (ABGR hex),
`Bold`, `Outline`, `OutlineColour`, `Alignment` (2=bottom, 5=centre, 8=top),
`MarginV` (vertical margin in pixels).

### Change caption timing
- Words per chunk: `SUBTITLE_WORDS_PER_CHUNK` constant at top of `main.py`
- Gap between captions: the `- 0.05` subtraction in `build_srt()`

---

## Backlog — Not Yet Built

- **Trending topic discovery:** scrape Google Trends, Reddit rising, or Twitter
  trending to auto-select a topic per niche instead of passing one manually.

- **Batch mode:** accept a `topics.txt` file, produce one Short per line, send
  each to Telegram as a separate approval request.

- **TikTok source:** add `find_tiktok()` to `sources.py` using yt-dlp's native
  TikTok support.

- **Scheduled auto-publish:** replace the Telegram approval gate with a cron
  job that publishes automatically at a configured time each day.

- **Multi-language niches:** change the script generation prompt language for
  new niches (e.g. Nigerian Pidgin, Yoruba, French) and pair with a matching
  Kokoro voice.

- **Analytics feedback loop:** poll YouTube Analytics 48 hours after upload,
  log views and retention per niche and topic, use the data to weight future
  topic selection toward historically high-performing patterns.
