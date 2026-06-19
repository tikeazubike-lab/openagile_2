#!/usr/bin/env python3
"""
main.py — OpenCLAW Native Python Video Automation Orchestrator

To swap LLM providers, edit two lines in .env:
    LLM_PROVIDER=gemini          # gemini | openai | anthropic
    LLM_MODEL=gemini-2.0-flash   # any model string valid for that provider

No changes to this file are ever needed to switch models.
"""

import os
import sys
import json
import time
import subprocess
import math
import requests
from dotenv import load_dotenv

from llm     import get_provider     # ← the only LLM import needed
from sources import find_clip        # ← automatic topic-relevant video sourcing

# ─── Environment ─────────────────────────────────────────────────────────────
load_dotenv()

TELEGRAM_BOT_TOKEN  = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID    = os.environ.get("TELEGRAM_CHAT_ID")
PIPELINE_BASE_DIR   = os.environ.get("PIPELINE_BASE_DIR", "/home/zubbyik/shorts-pipeline")

# ─── Service endpoints ────────────────────────────────────────────────────────
KOKORO_API = "http://127.0.0.1:8880/v1/audio/speech"

# ─── Binary paths ─────────────────────────────────────────────────────────────
DEFAULT_COOKIES = os.path.join(PIPELINE_BASE_DIR, "cookies.txt")
YT_DLP_BIN      = "/home/zubbyik/dev/yt-dlp"
DENO_BIN        = "/home/zubbyik/.deno/bin/deno"
FFPROBE_BIN     = "ffprobe"
FFMPEG_BIN      = "ffmpeg"

# ─── Niche voice map ──────────────────────────────────────────────────────────
NICHE_VOICE = {
    "A": "af_sarah",
    "B": "bm_george",
    "C": "am_michael",
}

SUBTITLE_WORDS_PER_CHUNK = 4


# ═══════════════════════════════════════════════════════════════════════════════
# Utilities
# ═══════════════════════════════════════════════════════════════════════════════

def log(msg: str) -> None:
    print(f"[*] {msg}", flush=True)


def execute_cmd(cmd_list: list, cwd: str = None) -> subprocess.CompletedProcess:
    log(f"Triggering Process: {' '.join(str(c) for c in cmd_list)}")
    try:
        result = subprocess.run(cmd_list, check=True, cwd=cwd,
                                capture_output=True, text=True)
        return result
    except subprocess.CalledProcessError as e:
        log(f"CRITICAL ERROR: {e}")
        log(f"  stdout: {e.stdout}")
        log(f"  stderr: {e.stderr}")
        sys.exit(1)


def get_audio_duration(audio_path: str) -> float:
    result = execute_cmd([
        FFPROBE_BIN, "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path,
    ])
    return float(result.stdout.strip())


# ═══════════════════════════════════════════════════════════════════════════════
# Step 1 — Download background clip
# ═══════════════════════════════════════════════════════════════════════════════

def download_video(url: str) -> str:
    """
    Download a video from any yt-dlp-supported URL to the clips directory.
    The URL is found automatically by sources.find_clip() before this is called.
    """
    log(f"Downloading clip from {url} ...")
    output_path = os.path.join(PIPELINE_BASE_DIR, "clips", "testclip.mp4")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    cmd = [
        YT_DLP_BIN,
        "--js-runtime", f"deno:{DENO_BIN}",
        "--no-playlist",
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
        "--merge-output-format", "mp4",
        "-o", output_path,
    ]

    if os.path.exists(DEFAULT_COOKIES):
        log("Cookies detected — injecting residential bypass.")
        cmd.extend(["--cookies", DEFAULT_COOKIES])
    else:
        log("Warning: no cookies.txt — relying on Deno sandbox only.")

    cmd.append(url)
    execute_cmd(cmd)
    return output_path


# ═══════════════════════════════════════════════════════════════════════════════
# Step 2 — Generate script (provider-agnostic)
# ═══════════════════════════════════════════════════════════════════════════════

def generate_script(topic: str) -> dict:
    provider = get_provider()
    log(f"Generating script via {provider} (topic: {topic})")

    prompt = (
        f"Write a 55-70 word YouTube Short voiceover script strictly about: {topic}. "
        "ALWAYS open with 'Do you know...'. "
        "ONLY output perfect RAW JSON in this exact structure and nothing else: "
        '{"hook": "...", "body": "...", "closer": "...", '
        '"full_script": "[hook+body+closer together]", "title": "...", '
        '"description": "...", "tags": ["tag1", "tag2"]}'
    )

    try:
        script_json = provider.generate_json(prompt)
    except Exception as e:
        log(f"⚠️  LLM REQUEST FAILED ({provider}): {e}")
        log("⚠️  Injecting failsafe dummy script.")
        script_json = {
            "hook": "Do you know the most embarrassing sports moment ever?",
            "body": (
                "This soccer player thought he had a clear shot at goal. "
                "He wound up for a dramatic kick... and completely missed the ball. "
                "His foot kicked nothing but air as he tumbled to the ground."
            ),
            "closer": "That's what happens when you show off.",
            "title": "Hilarious Soccer Epic Fail 😂",
            "description": "The funniest soccer miss of all time! #shorts #fail",
            "tags": ["soccer", "fail", "funny"],
        }

    # Reconstruct full_script from parts — canonical source of truth
    script_json["full_script"] = (
        f"{script_json.get('hook', '')} "
        f"{script_json.get('body', '')} "
        f"{script_json.get('closer', '')}".strip()
    )

    log(f"Script ready:\n{json.dumps(script_json, indent=2)}")
    return script_json


# ═══════════════════════════════════════════════════════════════════════════════
# Step 3 — Synthesize voiceover (Kokoro TTS)
# ═══════════════════════════════════════════════════════════════════════════════

def synthesize_audio(text: str, niche: str) -> str:
    voice = NICHE_VOICE.get(niche.upper(), "af_bella")
    log(f"Synthesizing TTS | niche={niche} | voice={voice}")

    if not text or len(text.strip()) < 5:
        log("CRITICAL: Script is empty — cannot synthesize audio.")
        sys.exit(1)

    payload = {
        "model": "kokoro",
        "voice": voice,
        "response_format": "mp3",
        "input": text,
    }

    output_path = os.path.join(PIPELINE_BASE_DIR, "audio", "testclip.mp3")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # stream=True reads the response body in chunks as it arrives rather than
    # buffering it all at once. This prevents ChunkedEncodingError / premature
    # connection drops from Kokoro's Docker container, which sends audio via
    # chunked transfer encoding and can close the socket before requests has
    # finished reading if you try to access response.content directly.
    bytes_written = 0
    try:
        with requests.post(KOKORO_API, json=payload, timeout=120, stream=True) as response:
            if response.status_code != 200:
                log(f"Kokoro TTS failed [{response.status_code}]: {response.text}")
                sys.exit(1)

            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep-alive empty chunks
                        f.write(chunk)
                        bytes_written += len(chunk)

    except requests.exceptions.ChunkedEncodingError as e:
        # Kokoro occasionally drops the connection after sending all audio data
        # but before sending the final chunk terminator. If we already received
        # a meaningful amount of audio, treat it as a success.
        if bytes_written > 1024:
            log(f"Warning: Kokoro closed connection early but {bytes_written} bytes received — continuing.")
        else:
            log(f"CRITICAL: Kokoro connection dropped after only {bytes_written} bytes: {e}")
            sys.exit(1)

    log(f"Audio saved → {output_path} ({bytes_written / 1024:.1f} KB)")
    return output_path


# ═══════════════════════════════════════════════════════════════════════════════
# Step 4 — Build SRT subtitle file
# ═══════════════════════════════════════════════════════════════════════════════

def _srt_timestamp(seconds: float) -> str:
    h  = int(seconds // 3600)
    m  = int((seconds % 3600) // 60)
    s  = int(seconds % 60)
    ms = int(round((seconds - math.floor(seconds)) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def build_srt(full_script: str, audio_duration: float, srt_path: str) -> str:
    words = full_script.split()
    if not words:
        open(srt_path, "w").close()
        return srt_path

    chunks = [
        " ".join(words[i : i + SUBTITLE_WORDS_PER_CHUNK])
        for i in range(0, len(words), SUBTITLE_WORDS_PER_CHUNK)
    ]
    time_per_chunk = audio_duration / len(chunks)

    lines = []
    for idx, chunk in enumerate(chunks):
        start = idx * time_per_chunk
        end   = start + time_per_chunk - 0.05
        lines += [str(idx + 1), f"{_srt_timestamp(start)} --> {_srt_timestamp(end)}", chunk, ""]

    os.makedirs(os.path.dirname(srt_path), exist_ok=True)
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    log(f"SRT built ({len(chunks)} captions, {audio_duration:.2f}s) → {srt_path}")
    return srt_path


# ═══════════════════════════════════════════════════════════════════════════════
# Step 5 — Merge video + audio + burned subtitles via FFmpeg
# ═══════════════════════════════════════════════════════════════════════════════

def merge_video(input_clip: str, audio_clip: str, srt_path: str, niche: str) -> str:
    log("Composing final Short via FFmpeg ...")

    subtitle_styles = {
        "A": "FontName=Helvetica,FontSize=18,PrimaryColour=&HFFFFFF,Bold=0,"
             "Outline=2,OutlineColour=&H000000,Alignment=2,MarginV=60",
        "B": "FontName=Impact,FontSize=22,PrimaryColour=&H00FFFF,Bold=1,"
             "Outline=2,OutlineColour=&H000000,Alignment=2,MarginV=40",
        "C": "FontName=Impact,FontSize=22,PrimaryColour=&HFFFFFF,Bold=1,"
             "Outline=3,OutlineColour=&H000000,Alignment=2,MarginV=40",
    }
    style_str   = subtitle_styles.get(niche.upper(), subtitle_styles["A"])
    srt_escaped = srt_path.replace("\\", "/").replace(":", "\\:")
    short_path  = os.path.join(PIPELINE_BASE_DIR, "output", "testclip_short.mp4")
    os.makedirs(os.path.dirname(short_path), exist_ok=True)

    cmd = [
        FFMPEG_BIN, "-y",
        "-stream_loop", "-1",
        "-i", input_clip,
        "-i", audio_clip,
        "-filter_complex",
        (
            "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
            f"crop=1080:1920,"
            f"subtitles='{srt_escaped}':force_style='{style_str}'[vout]"
        ),
        "-map", "[vout]",
        "-map", "1:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        short_path,
    ]
    execute_cmd(cmd)
    log(f"Short rendered → {short_path}")
    return short_path


# ═══════════════════════════════════════════════════════════════════════════════
# Step 6 — Telegram preview
# ═══════════════════════════════════════════════════════════════════════════════

def send_telegram_preview(video_path: str, script_data: dict) -> None:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        log("No Telegram config — skipping preview.")
        return

    log("Shipping Short to Telegram for approval ...")
    caption = (
        f"🎬 *Pre-render complete!*\n\n"
        f"*Title:* {script_data['title']}\n\n"
        "Send /approve to publish, /reject to discard."
    )
    with open(video_path, "rb") as vf:
        response = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo",
            data={"chat_id": TELEGRAM_CHAT_ID, "caption": caption, "parse_mode": "Markdown"},
            files={"video": vf},
            timeout=120,
        )
    if response.status_code != 200:
        log(f"Telegram upload failed: {response.text}")
    else:
        log("Telegram preview delivered.")


# ═══════════════════════════════════════════════════════════════════════════════
# Step 7 — Approval gate
# ═══════════════════════════════════════════════════════════════════════════════

def wait_for_approval() -> bool:
    log("Pipeline paused — waiting for /approve on Telegram ...")
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"

    response = requests.get(url, timeout=30).json()
    last_update_id = 0
    if response.get("ok") and response.get("result"):
        last_update_id = response["result"][-1]["update_id"]

    while True:
        res = requests.get(f"{url}?offset={last_update_id + 1}", timeout=30).json()
        if res.get("ok") and res.get("result"):
            for update in res["result"]:
                last_update_id = update["update_id"]
                msg_text = update.get("message", {}).get("text", "").strip().lower()
                if msg_text == "/approve":
                    log("✅ Approved — continuing to upload.")
                    return True
                elif msg_text in ("/reject", "/cancel"):
                    log("❌ Rejected — aborting.")
                    sys.exit(0)
        time.sleep(5)


# ═══════════════════════════════════════════════════════════════════════════════
# Step 8 — YouTube upload
# ═══════════════════════════════════════════════════════════════════════════════

def upload_to_youtube(video_path: str, script_data: dict, niche: str) -> None:
    log("Executing YouTube upload sequence ...")
    cmd = [
        "python3",
        "/home/zubbyik/openagile/you-tube-shorts/scripts/youtube_upload.py",
        "--file",        video_path,
        "--title",       script_data["title"],
        "--description", script_data["description"],
        "--tags",        ",".join(script_data["tags"]),
        "--niche",       niche,
    ]
    execute_cmd(cmd)


# ═══════════════════════════════════════════════════════════════════════════════
# Entrypoint
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:   python3 main.py \"<topic>\" [niche: A/B/C]")
        print("Example: python3 main.py \"A hilarious soccer fail\" C")
        print()
        print("The pipeline finds a relevant video automatically.")
        print("Niches: A=Tech History  B=Football Fails  C=Sports Bloopers")
        sys.exit(1)

    topic = sys.argv[1]
    niche = sys.argv[2].upper() if len(sys.argv) > 2 else "A"

    if niche not in NICHE_VOICE:
        log(f"Unknown niche '{niche}' — defaulting to A.")
        niche = "A"

    log("═══ INITIALISING OPENCLAW SHORTS PIPELINE ═══")
    log(f"  topic    : {topic}")
    log(f"  niche    : {niche}  ({NICHE_VOICE[niche]})")
    log(f"  provider : {os.environ.get('LLM_PROVIDER', 'gemini')}  /  {os.environ.get('LLM_MODEL', 'gemini-2.0-flash')}")

    # Auto-source a topic-relevant clip — no manual URL needed
    source_url  = find_clip(topic=topic, niche=niche)
    input_clip  = download_video(source_url)
    script_data = generate_script(topic)
    audio_clip  = synthesize_audio(script_data["full_script"], niche)

    srt_path  = os.path.join(PIPELINE_BASE_DIR, "subtitles", "testclip.srt")
    audio_dur = get_audio_duration(audio_clip)
    build_srt(script_data["full_script"], audio_dur, srt_path)

    final_short = merge_video(input_clip, audio_clip, srt_path, niche)

    send_telegram_preview(final_short, script_data)
    wait_for_approval()
    upload_to_youtube(final_short, script_data, niche)

    log("🎉 Pipeline complete — extraction → synthesis → subtitles → deploy!")