# YouTube Shorts Creator Pipeline

## Overview
Automated YouTube Shorts creation pipeline running on the OpenAgile infrastructure. Scrapes trending video content, generates AI voiceover scripts via OpenCLAW (GLM-4.7), synthesises speech with Kokoro TTS, re-edits clips with FFmpeg, and uploads to YouTube after Telegram-based operator approval.

## Features
- **3 Content Niches**: Tech History ("Do you know?"), Football Rule Fails, Sports Bloopers
- **AI Script Generation**: OpenCLAW (GLM-4.7) with niche-specific system prompts producing structured JSON
- **TTS Synthesis**: Kokoro TTS (CPU mode) with per-niche voice mapping
- **Video Processing**: FFmpeg pipeline — 9:16 vertical format, voiceover merge, caption burn-in
- **Operator Approval**: Telegram preview → /approve, /reject, /edit loop
- **YouTube Upload**: Automated via YouTube Data API v3 with OAuth2
- **Orchestration**: N8N workflow with 12-node architecture (Schedule → Fetch → Script → TTS → FFmpeg → Telegram → Upload)
- **CI/CD**: GitHub Actions deployment via SSH (following OpenAgile patterns)

## Architecture & Traffic Flow

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  N8N         │───▶│  OpenCLAW     │───▶│  Kokoro TTS  │
│  (Schedule)  │    │  (GLM-4.7)   │    │  (port 8880) │
└──────┬───────┘    └──────────────┘    └──────┬───────┘
       │                                        │
       ▼                                        ▼
┌─────────────┐                         ┌──────────────┐
│  yt-dlp      │                         │  FFmpeg       │
│  (Fetch)     │────────────────────────▶│  (Process)    │
└─────────────┘                         └──────┬───────┘
                                               │
                                               ▼
                                       ┌──────────────┐
                                       │  Telegram     │
                                       │  (Approval)   │
                                       └──────┬───────┘
                                               │ /approve
                                               ▼
                                       ┌──────────────┐
                                       │  YouTube API  │
                                       │  (Upload)     │
                                       └──────────────┘
```

## Voice-to-Niche Mapping

| Niche | Kokoro Voice | YouTube Category | GLM Prompt |
|-------|-------------|-----------------|------------|
| A — Tech History | `af_sarah` | 28 (Science & Tech) | Prompt A |
| B — Football Rule Fails | `bm_george` | 17 (Sports) | Prompt B |
| C — Sports Bloopers | `am_michael` | 17 (Sports) | Prompt C |

## Key Deployment Notes

### Resource Constraints (CPU-Only Server)
- Server has <4GB RAM; Kokoro TTS CPU synthesis takes ~15–25s per 60-word script
- Resource limits set in `docker-compose.yml` to prevent OOM alongside other services
- Pipeline runs asynchronously (daily schedule), so latency is acceptable

### Traefik Integration
The Kokoro TTS container attaches to the shared Traefik network:
```yaml
- "traefik.docker.network=openagile_openagile_network"
```

### N8N Integration
N8N (already running in main stack) orchestrates the pipeline via HTTP requests to:
- **Kokoro TTS**: `http://kokoro-tts:8880/v1/audio/speech` (Docker internal network)
- **OpenCLAW**: `http://openclaw-gateway:18789/v1/chat/completions` (Docker internal network)

### GitHub Secrets Required

| Secret | Purpose |
|--------|---------|
| `SSH_PRIVATE_KEY` | SSH deployment access |
| `TELEGRAM_BOT_TOKEN` | Telegram preview/approval bot |
| `TELEGRAM_CHAT_ID` | Operator's Telegram chat |

## File Structure

- `docker-compose.yml` — Kokoro TTS service definition
- `.env.example` — Template environment variables
- `deploy.sh` — Master deployment script
- `scripts/process_short.sh` — FFmpeg video processing
- `scripts/youtube_auth.py` — YouTube OAuth2 initial setup
- `scripts/youtube_upload.py` — YouTube upload client
- `scripts/health_check.sh` — Post-deploy infrastructure validation
- `n8n/workflow-template.json` — N8N importable workflow skeleton
- `n8n/README.md` — N8N workflow setup guide
- `agents/` — Project-specific agent definitions
- `docs/DEPLOYMENT_CHECKLIST.md` — Pre-flight verification
- `prompt_draft.md` — Original pipeline specification

## Troubleshooting

| Symptom | Root Cause | Fix |
|---------|-----------|-----|
| Kokoro TTS returns 500 | Container OOM on CPU server | Reduce concurrent requests; check `docker stats` |
| yt-dlp fails to download | Anti-bot measures updated | Run `yt-dlp -U` to update |
| YouTube upload quota exceeded | 10,000 units/day (6 uploads max) | Request quota increase from GCP |
| Telegram preview >50MB | Video bitrate too high | Lower FFmpeg CRF from 23 to 28 |
| OpenCLAW returns non-JSON | Prompt drift or model hallucination | Verify system prompt; lower temperature to 0.5 |
| N8N can't reach Kokoro | Containers on different networks | Verify both are on `openagile_openagile_network` |

