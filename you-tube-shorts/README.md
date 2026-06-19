# YouTube Shorts Creator Pipeline
**Status:** 🟢 Active  
**Last updated:** 2025-03  
**Maintainer:** zubbyik  
**Infrastructure:** OpenAgile / self-hosted

---

## What It Does

```mermaid
graph LR
    A[Trending Clip URL] --> B[yt-dlp Download]
    B --> C[Gemini Script]
    C --> D[Kokoro TTS]
    D --> E[SRT Subtitle Builder]
    E --> F[FFmpeg Compose\n9:16 + Burn Subs]
    F --> G[Telegram Preview]
    G -->|/approve| H[YouTube Upload]
    G -->|/reject|  I[Abort & Cleanup]
```

The pipeline takes a trending clip URL and a topic string, then fully automates the
creation of a YouTube Short — from voiceover scripting to upload — with a human
approval gate via Telegram before anything goes public.

---

## Pipeline Stages

| # | Stage | Script / Tool | Output |
|---|-------|--------------|--------|
| 1 | Download background clip | `yt-dlp` + Deno sandbox | `clips/testclip.mp4` |
| 2 | Generate voiceover script | Gemini API (`gemini-2.0-flash`) | JSON script object |
| 3 | Synthesize voiceover | Kokoro TTS (Docker) | `audio/testclip.mp3` |
| 4 | Build subtitle file | `build_srt()` in `main.py` | `subtitles/testclip.srt` |
| 5 | Compose final Short | FFmpeg (scale + loop + burn subs) | `output/testclip_short.mp4` |
| 6 | Preview to operator | Telegram Bot API | Video message |
| 7 | Approval gate | Telegram `/approve` or `/reject` | Pipeline continues or exits |
| 8 | Publish | `youtube_upload.py` (OAuth2) | Live YouTube Short |

---

## Content Niches

| Niche | Theme | Kokoro Voice | YouTube Category |
|-------|-------|-------------|-----------------|
| **A** | "Do you know?" — Tech History | `af_sarah` | Science & Technology |
| **B** | Football Rule Fails | `bm_george` | Sports |
| **C** | Sports Bloopers | `am_michael` | Sports |

> **Subtitle style varies by niche** — A uses clean white Helvetica at the bottom third;
> B and C use bold Impact centred mid-screen for maximum retention on mobile.

---

## Quick Start

```bash
# 1. Clone and enter the project
cd /home/zubbyik/openagile/you-tube-shorts

# 2. Copy and fill in your credentials
cp .env.example .env
nano .env

# 3. Deploy infrastructure (creates dirs, starts Kokoro, validates paths)
chmod +x deploy.sh && ./deploy.sh

# 4. One-time YouTube OAuth setup
pip3 install google-auth-oauthlib google-api-python-client
python3 scripts/youtube_auth.py

# 5. Run a Short
python3 main.py "https://youtube.com/shorts/XXXX" "A surprising tech history fact" A
```

---

## Environment Variables (`.env`)

| Key | Required | Description |
|-----|----------|-------------|
| `GEMINI_API_KEY` | ✅ | Google AI Studio API key |
| `TELEGRAM_BOT_TOKEN` | ✅ | Telegram bot token for preview/approval |
| `TELEGRAM_CHAT_ID` | ✅ | Your personal or group chat ID |
| `PIPELINE_BASE_DIR` | optional | Base directory for all pipeline assets (default: `/home/zubbyik/shorts-pipeline`) |

---

## Directory Layout

```
shorts-pipeline/              ← PIPELINE_BASE_DIR
├── clips/
│   └── testclip.mp4          ← downloaded background footage
├── audio/
│   └── testclip.mp3          ← synthesized Kokoro voiceover
├── subtitles/
│   └── testclip.srt          ← auto-generated SRT captions
└── output/
    └── testclip_short.mp4    ← final 9:16 Short, ready to publish

you-tube-shorts/              ← project root
├── GEMINI.md                 ← this file (living doc)
├── main.py                   ← orchestrator — single entry point
├── docker-compose.yml        ← Kokoro TTS service
├── deploy.sh                 ← master deployment script
├── .env.example
├── scripts/
│   ├── process_short.sh      ← (legacy) FFmpeg wrapper — superseded by main.py
│   ├── youtube_auth.py       ← OAuth2 token setup (run once)
│   ├── youtube_upload.py     ← YouTube Data API v3 client
│   └── health_check.sh       ← validates all services are running
├── n8n/                      ← (legacy) N8N workflow templates
│   └── workflow-template.json
└── docs/
    └── DEPLOYMENT_CHECKLIST.md
```

---

## Subtitle Synchronization — How It Works

This was the core bug in the original pipeline: subtitles were not time-locked to the voiceover.

**Fix:** `main.py` now:
1. Measures the exact MP3 duration using `ffprobe` after TTS synthesis.
2. Splits the script into word chunks (≤ 4 words each).
3. Distributes those chunks evenly across the audio duration to produce a timed `.srt`.
4. Burns the `.srt` directly into the video via FFmpeg's `subtitles=` filter with a 50 ms gap between captions.

The video background is looped to exactly match the audio length using `-stream_loop -1` +
`-shortest`, so there is never a mismatch between picture, sound, and text.

---

## Gemini Model Reference

| Model string | Notes |
|-------------|-------|
| `gemini-2.0-flash` | ✅ **Current default** — fast, cheap, stable |
| `gemini-1.5-flash-002` | Older 1.5 generation — use if 2.0 is unavailable |
| `gemini-1.5-flash-latest` | ❌ **Deprecated alias** — do not use, returns 404 |
| `gemini-flash-latest` | ❌ **Deprecated alias** — do not use, returns 404 |

To verify which models are live on your API key:
```bash
curl "https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY" | python3 -m json.tool | grep '"name"'
```

---

## Service Health Checks

```bash
# Kokoro TTS
curl -s http://127.0.0.1:8880/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model":"kokoro","voice":"af_sarah","input":"test","response_format":"mp3"}' \
  --output /tmp/tts_test.mp3 && echo "✅ Kokoro OK"

# Gemini API
curl -s "https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent?key=${GEMINI_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Say hello"}]}]}' | python3 -m json.tool | grep '"text"'

# FFmpeg
ffmpeg -version | head -1

# yt-dlp
/home/zubbyik/dev/yt-dlp --version
```

Or run the full check:
```bash
bash scripts/health_check.sh
```

---

## Known Issues & Decisions

| Issue | Status | Notes |
|-------|--------|-------|
| `gemini-1.5-flash-latest` 404 | ✅ Fixed | Replaced with `gemini-2.0-flash` |
| Video/audio out of sync | ✅ Fixed | SRT now built from ffprobe-measured audio duration |
| Subtitles not appearing | ✅ Fixed | Subtitles filter burned directly in FFmpeg compose step |
| Niche voice not applied | ✅ Fixed | `NICHE_VOICE` map routes correct Kokoro voice per niche |
| Background longer than voiceover | ✅ Fixed | `-stream_loop -1` + `-shortest` trims background to audio length |
| `process_short.sh` bypass | ⚠️ Legacy | The shell script is no longer called from `main.py`; FFmpeg logic lives in `merge_video()` |

---

## CI/CD

**Trigger:** Push to `you-tube-shorts/**` on `main` branch, or manual dispatch via GitHub Actions.

```yaml
# .github/workflows/deploy-youtube-shorts.yml
on:
  push:
    paths: ["you-tube-shorts/**"]
  workflow_dispatch:
```

**Deployment:** SSH → `git pull` → `./deploy.sh`

**Required GitHub Secrets:**

| Secret | Purpose |
|--------|---------|
| `SSH_PRIVATE_KEY` | Deploy access |
| `TELEGRAM_BOT_TOKEN` | Approval gate |
| `TELEGRAM_CHAT_ID` | Approval gate |

---

## Changelog

| Date | Change |
|------|--------|
| 2025-03 | Rewrote `merge_video()` — FFmpeg now crops/loops/burns subs in a single pass |
| 2025-03 | Added `build_srt()` — duration-aware subtitle generation via ffprobe |
| 2025-03 | Fixed niche-to-voice routing in `synthesize_audio()` |
| 2025-03 | Updated Gemini model to `gemini-2.0-flash`; deprecated `-latest` aliases documented |
| 2025-03 | Removed dependency on `process_short.sh` — all FFmpeg logic in `main.py` |
| Earlier | Initial N8N → native Python migration |

---

## Related Docs

- [Pipeline Spec](./prompt_draft.md)
- [N8N Workflow Guide](./n8n/README.md)
- [Deployment Checklist](./docs/DEPLOYMENT_CHECKLIST.md)
- [Infrastructure Contract](../INFRASTRUCTURE_CONTRACT.md)
- [OpenAgile Setup Guide](../docs/OPENAGILE_SETUP_GUIDE.md)