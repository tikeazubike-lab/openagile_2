#!/bin/bash
# deploy.sh — Master deployment script for YouTube Shorts Pipeline
# Run this on the server or via CI/CD to set up the pipeline infrastructure.
#
# Usage: ./deploy.sh
#
# Prerequisites:
#   - Docker + Docker Compose installed
#   - .env file present (copy from .env.example)
#   - openagile_openagile_network exists (main stack must be running)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIPELINE_BASE="${PIPELINE_BASE_DIR:-/home/zubbyik/shorts-pipeline}"

echo "🎬 YouTube Shorts Pipeline — Deployment"
echo "========================================="

# --- Step 1: Create pipeline directories ---
echo ""
echo "📁 Step 1: Creating pipeline directory structure..."
mkdir -p "${PIPELINE_BASE}/clips"
mkdir -p "${PIPELINE_BASE}/audio"
mkdir -p "${PIPELINE_BASE}/output"
mkdir -p "${PIPELINE_BASE}/logs"
chmod 755 "${PIPELINE_BASE}"
echo "   ✅ Directories created at ${PIPELINE_BASE}"

# --- Step 2: Verify prerequisites ---
echo ""
echo "🔍 Step 2: Checking prerequisites..."

# Check Docker
if ! command -v docker &>/dev/null; then
    echo "   ❌ Docker not found. Install Docker first."
    exit 1
fi
echo "   ✅ Docker: $(docker --version | head -1)"

# Check Docker Compose
if ! docker compose version &>/dev/null; then
    echo "   ❌ Docker Compose not found."
    exit 1
fi
echo "   ✅ Docker Compose: $(docker compose version --short)"

# Check FFmpeg
if ! command -v ffmpeg &>/dev/null; then
    echo "   ⚠️  FFmpeg not found. Installing..."
    sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg
fi
echo "   ✅ FFmpeg: $(ffmpeg -version 2>/dev/null | head -1)"

# Check yt-dlp
if ! command -v yt-dlp &>/dev/null; then
    echo "   ⚠️  yt-dlp not found. Installing..."
    curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp \
        -o /usr/local/bin/yt-dlp 2>/dev/null || \
    curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp \
        -o "${HOME}/.local/bin/yt-dlp" 2>/dev/null
    chmod a+rx /usr/local/bin/yt-dlp 2>/dev/null || \
    chmod a+rx "${HOME}/.local/bin/yt-dlp" 2>/dev/null
fi
echo "   ✅ yt-dlp: $(yt-dlp --version 2>/dev/null || echo 'installed')"

# Check external network
if ! docker network inspect openagile_openagile_network &>/dev/null; then
    echo "   ❌ External network 'openagile_openagile_network' not found."
    echo "      Start the main OpenAgile stack first: cd .. && docker compose up -d"
    exit 1
fi
echo "   ✅ Network: openagile_openagile_network exists"

# --- Step 3: Make scripts executable ---
echo ""
echo "🔧 Step 3: Setting script permissions..."
chmod +x "${SCRIPT_DIR}/scripts/process_short.sh" 2>/dev/null || true
chmod +x "${SCRIPT_DIR}/scripts/health_check.sh" 2>/dev/null || true
echo "   ✅ Scripts are executable"

# --- Step 4: Deploy Kokoro TTS ---
echo ""
echo "🚀 Step 4: Deploying Kokoro TTS container..."
cd "${SCRIPT_DIR}"
docker compose pull
docker compose up -d --remove-orphans
echo "   ✅ Kokoro TTS container started"

# --- Step 5: Wait for Kokoro health ---
echo ""
echo "⏳ Step 5: Waiting for Kokoro TTS to be healthy (up to 120s)..."
KOKORO_HEALTHY=false
for i in $(seq 1 24); do
    if curl -fsS http://127.0.0.1:8880/docs &>/dev/null; then
        KOKORO_HEALTHY=true
        break
    fi
    echo "   Waiting... (${i}/24)"
    sleep 5
done

if [ "$KOKORO_HEALTHY" = true ]; then
    echo "   ✅ Kokoro TTS is healthy"
else
    echo "   ⚠️  Kokoro TTS health check timed out (may still be loading models)"
    echo "      Check: docker compose logs kokoro-tts"
fi

# --- Step 6: Run health check ---
echo ""
echo "🏥 Step 6: Running full health check..."
if [ -f "${SCRIPT_DIR}/scripts/health_check.sh" ]; then
    bash "${SCRIPT_DIR}/scripts/health_check.sh" || echo "   ⚠️  Some health checks failed (see above)"
else
    echo "   ⚠️  health_check.sh not found, skipping"
fi

# --- Summary ---
echo ""
echo "========================================="
echo "✅ Deployment complete!"
echo ""
echo "Pipeline directories: ${PIPELINE_BASE}/"
echo "Kokoro TTS: http://127.0.0.1:8880"
echo ""
echo "Next steps:"
echo "  1. Set up YouTube API credentials (run scripts/youtube_auth.py)"
echo "  2. Import N8N workflow from n8n/workflow-template.json"
echo "  3. Configure Telegram bot token in N8N"
echo "  4. Run a manual test with: scripts/health_check.sh"
echo ""
docker compose ps
