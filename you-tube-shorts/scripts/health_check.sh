#!/bin/bash
# health_check.sh — Post-deployment infrastructure validation
# Verifies all components of the YouTube Shorts pipeline are operational.
#
# Usage: ./health_check.sh
# Exit code: 0 = all checks passed, 1 = one or more checks failed

set -o pipefail

PIPELINE_BASE="${PIPELINE_BASE_DIR:-/home/zubbyik/shorts-pipeline}"
KOKORO_URL="${KOKORO_URL:-http://127.0.0.1:8880}"
PASS=0
FAIL=0

check() {
    local name="$1"
    local result="$2"
    if [ "$result" -eq 0 ]; then
        echo "   ✅ $name"
        PASS=$((PASS + 1))
    else
        echo "   ❌ $name"
        FAIL=$((FAIL + 1))
    fi
}

echo "🏥 YouTube Shorts Pipeline — Health Check"
echo "==========================================="

# --- 1. Docker ---
echo ""
echo "🐳 Docker Services:"
docker compose ps --format "table {{.Name}}\t{{.Status}}" 2>/dev/null
docker compose ps --status running 2>/dev/null | grep -q "kokoro-tts"
check "Kokoro TTS container running" $?

# --- 2. Kokoro TTS API ---
echo ""
echo "🔊 Kokoro TTS:"
curl -fsS "${KOKORO_URL}/docs" >/dev/null 2>&1
check "Kokoro TTS API docs endpoint" $?

# Test synthesis (optional, only if API is up)
if curl -fsS "${KOKORO_URL}/docs" >/dev/null 2>&1; then
    SYNTH_RESULT=$(curl -s -o /tmp/kokoro_health_test.mp3 -w "%{http_code}" \
        -X POST "${KOKORO_URL}/v1/audio/speech" \
        -H "Content-Type: application/json" \
        -d '{
            "model": "kokoro",
            "input": "Health check test.",
            "voice": "af_sarah",
            "response_format": "mp3"
        }' 2>/dev/null)
    [ "$SYNTH_RESULT" = "200" ]
    check "Kokoro TTS synthesis test" $?
    rm -f /tmp/kokoro_health_test.mp3
else
    echo "   ⏭️  Skipping synthesis test (API not reachable)"
    FAIL=$((FAIL + 1))
fi

# --- 3. System Tools ---
echo ""
echo "🔧 System Tools:"
command -v ffmpeg >/dev/null 2>&1
check "FFmpeg installed" $?

command -v yt-dlp >/dev/null 2>&1
check "yt-dlp installed" $?

# --- 4. Pipeline Directories ---
echo ""
echo "📁 Pipeline Directories:"
[ -d "${PIPELINE_BASE}/clips" ]
check "clips/ directory exists" $?

[ -d "${PIPELINE_BASE}/audio" ]
check "audio/ directory exists" $?

[ -d "${PIPELINE_BASE}/output" ]
check "output/ directory exists" $?

[ -d "${PIPELINE_BASE}/logs" ]
check "logs/ directory exists" $?

# --- 5. Scripts ---
echo ""
echo "📜 Scripts:"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ -x "${SCRIPT_DIR}/process_short.sh" ]
check "process_short.sh is executable" $?

[ -f "${SCRIPT_DIR}/youtube_upload.py" ]
check "youtube_upload.py exists" $?

[ -f "${SCRIPT_DIR}/youtube_auth.py" ]
check "youtube_auth.py exists" $?

# --- 6. Network ---
echo ""
echo "🌐 Docker Network:"
docker network inspect openagile_openagile_network >/dev/null 2>&1
check "openagile_openagile_network exists" $?

# --- Summary ---
TOTAL=$((PASS + FAIL))
echo ""
echo "==========================================="
echo "Results: ${PASS}/${TOTAL} checks passed"
if [ "$FAIL" -gt 0 ]; then
    echo "⚠️  ${FAIL} check(s) failed"
    exit 1
else
    echo "✅ All checks passed"
    exit 0
fi
