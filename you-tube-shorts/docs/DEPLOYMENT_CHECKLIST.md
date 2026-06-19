# Deployment Checklist — YouTube Shorts Pipeline

Before running the pipeline for the first time, verify every item below.

---

## Infrastructure

- [ ] Kokoro TTS container is running (`docker compose ps` shows healthy)
- [ ] Kokoro TTS synthesis test passes:
  ```bash
  curl -X POST http://localhost:8880/v1/audio/speech \
    -H "Content-Type: application/json" \
    -d '{"model":"kokoro","input":"Do you know that in 1956, IBM built the first hard drive the size of two refrigerators?","voice":"af_sarah","response_format":"mp3"}' \
    --output /tmp/kokoro_test.mp3
  # Verify: /tmp/kokoro_test.mp3 is valid, ~8-12 seconds
  ```
- [ ] yt-dlp is installed and returns a version: `yt-dlp --version`
- [ ] FFmpeg is installed: `ffmpeg -version`
- [ ] Pipeline directory structure created:
  ```
  /home/zubbyik/shorts-pipeline/clips/
  /home/zubbyik/shorts-pipeline/audio/
  /home/zubbyik/shorts-pipeline/output/
  /home/zubbyik/shorts-pipeline/logs/
  ```
- [ ] `process_short.sh` is executable and produces valid output on a test clip
- [ ] `openagile_openagile_network` Docker network exists
- [ ] Health check passes: `scripts/health_check.sh`

## YouTube API

- [ ] Google Cloud project created with YouTube Data API v3 enabled
- [ ] OAuth 2.0 credentials downloaded as `youtube_credentials.json`
- [ ] `youtube_auth.py` has been run and `youtube_token.pickle` exists
- [ ] Test upload completed successfully (use `--privacy private`):
  ```bash
  python3 scripts/youtube_upload.py \
    --file /path/to/test.mp4 \
    --title "Test Upload" \
    --description "Test" \
    --tags "test" \
    --privacy private
  ```
- [ ] Channel is not in a restricted state (new channels need 24h before API upload)
- [ ] OAuth token has not expired (re-run `youtube_auth.py` if needed)

## OpenCLAW

- [ ] All three system prompts saved as named agent configurations in OpenCLAW
- [ ] GLM-4.7 set as default model for script generation agents
- [ ] GLM-4.5-Air set for metadata and utility agents
- [ ] OpenCLAW Telegram bot connected and responds to commands
- [ ] Test API call returns valid JSON:
  ```bash
  curl -X POST http://openclaw-gateway:18789/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{"model":"glm-4-plus","messages":[{"role":"user","content":"Hello"}]}'
  ```

## N8N

- [ ] Workflow imported from `n8n/workflow-template.json`
- [ ] All credential references resolved (Telegram bot token, chat ID)
- [ ] Kokoro URL resolves correctly inside Docker network
- [ ] OpenCLAW API URL resolves correctly inside Docker network
- [ ] Webhook URL for approval (`/shorts-approval`) is reachable
- [ ] Schedule trigger set to 08:00 and tested with manual trigger first
- [ ] System prompts pasted into the "Generate Script" node

## Telegram

- [ ] Bot token configured in N8N Telegram credential
- [ ] Chat ID set correctly for operator's Telegram
- [ ] Bot can send messages to the chat
- [ ] Webhook forwarding from Telegram bot to N8N is working

## GitHub Actions

- [ ] `SSH_PRIVATE_KEY` secret set in repository
- [ ] `TELEGRAM_BOT_TOKEN` secret set in repository
- [ ] `TELEGRAM_CHAT_ID` secret set in repository
- [ ] Manual workflow dispatch runs successfully

---

## First Run Procedure

1. **Manual trigger first** — Do NOT leave the pipeline unattended until you have approved at least 3 Shorts end-to-end
2. Review Kokoro voice quality for each niche; adjust voice IDs if needed
3. Tune OpenCLAW prompt temperature (start at 0.7, lower to 0.5 if unpredictable)
4. After 2 weeks of stable operation, add TikTok/Instagram sources
5. Monitor YouTube API quota usage (6 uploads/day max at default quota)
