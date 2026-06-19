# N8N Workflow — YouTube Shorts Creator Pipeline

## Overview
This directory contains an N8N-importable workflow template that orchestrates the full YouTube Shorts creation pipeline. The workflow runs daily at 08:00 and processes clips through 12 nodes.

## Importing the Workflow

1. Open N8N at https://n8n.zubbystudio.shop
2. Go to **Workflows** → **Import from File**
3. Select `workflow-template.json`
4. The workflow will appear with all 12 nodes connected

## Node Architecture

```
Schedule (08:00)
  → Set Variables (niche configs)
    → Fetch Clips (yt-dlp)
      → Generate Script (OpenCLAW/GLM-4.7)
        → Synthesize Voice (Kokoro TTS)
          → FFmpeg Processing (9:16 + voiceover)
            → Telegram Preview
              → Wait for Approval (Webhook)
                → IF /approve → YouTube Upload → Telegram Confirm → Cleanup
                → IF /reject  → Cleanup
                → IF /edit    → Loop back to Generate Script
```

## Required Credentials

Configure these in N8N **Settings → Credentials** before activating:

| Credential | Type | Where to Get |
|-----------|------|-------------|
| Telegram Bot | Telegram API | @BotFather on Telegram |

## Variables to Configure

After import, update the **Set Niche Variables** node (Node 2) with:

| Variable | Value |
|----------|-------|
| `kokoro_url` | `http://kokoro-tts:8880/v1/audio/speech` |
| `openclaw_url` | `http://openclaw-gateway:18789/v1/chat/completions` |
| `clips_dir` | `/home/zubbyik/shorts-pipeline/clips` |
| `audio_dir` | `/home/zubbyik/shorts-pipeline/audio` |
| `output_dir` | `/home/zubbyik/shorts-pipeline/output` |

## Post-Import Steps

1. **Paste system prompts**: In the "Generate Script" node (Node 4), replace the placeholder with the full niche-specific system prompt from `prompt_draft.md`
2. **Configure Telegram**: Add your bot token and chat ID
3. **Set webhook URL**: The approval webhook path is `/shorts-approval` — ensure this is reachable from your Telegram bot
4. **Test manually**: Use the "Execute Workflow" button before enabling the schedule
5. **Start with private uploads**: Set `--privacy private` in the YouTube Upload node until verified
