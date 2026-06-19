#!/bin/bash
# process_short.sh — Converts a raw clip + voiceover into a YouTube Short
# Usage: ./process_short.sh <input_clip> <voiceover_mp3> <output_file> [niche]
#
# Arguments:
#   input_clip    — path to the downloaded source video
#   voiceover_mp3 — path to the Kokoro-generated audio file
#   output_file   — path for the finished Short
#   niche         — A, B, or C (used for caption styling, optional)

set -e

INPUT_CLIP="$1"
VOICEOVER="$2"
OUTPUT="$3"
NICHE="${4:-A}"

if [ -z "$INPUT_CLIP" ] || [ -z "$VOICEOVER" ] || [ -z "$OUTPUT" ]; then
    echo "Usage: $0 <input_clip> <voiceover_mp3> <output_file> [niche]"
    exit 1
fi

if [ ! -f "$INPUT_CLIP" ]; then
    echo "Error: Input clip not found: $INPUT_CLIP"
    exit 1
fi

if [ ! -f "$VOICEOVER" ]; then
    echo "Error: Voiceover file not found: $VOICEOVER"
    exit 1
fi

# Target dimensions for YouTube Shorts (9:16 vertical)
TARGET_W=1080
TARGET_H=1920

echo "🎬 Processing Short..."
echo "   Input:     $INPUT_CLIP"
echo "   Voiceover: $VOICEOVER"
echo "   Output:    $OUTPUT"
echo "   Niche:     $NICHE"

# Step 1: Scale and pad source clip to 9:16 without cropping content
# Step 2: Replace original audio with Kokoro voiceover
# Step 3: Limit duration to voiceover length (Shorts max 60s)
ffmpeg -y \
  -i "$INPUT_CLIP" \
  -i "$VOICEOVER" \
  -filter_complex "
    [0:v]scale=${TARGET_W}:${TARGET_H}:force_original_aspect_ratio=decrease,
    pad=${TARGET_W}:${TARGET_H}:(ow-iw)/2:(oh-ih)/2:black[v]
  " \
  -map "[v]" \
  -map "1:a" \
  -c:v libx264 \
  -preset fast \
  -crf 23 \
  -c:a aac \
  -b:a 192k \
  -shortest \
  -movflags +faststart \
  "$OUTPUT"

echo "✅ Short processed: $OUTPUT"
echo "   Size: $(du -h "$OUTPUT" | cut -f1)"
