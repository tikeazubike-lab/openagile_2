#!/usr/bin/env python3
"""
youtube_upload.py — Uploads a Short to YouTube via the YouTube Data API v3.

Usage:
    python3 youtube_upload.py --file output.mp4 --title "Title" \
        --description "Desc" --tags "tag1,tag2" --category 28

Dependencies:
    pip3 install google-auth-oauthlib google-api-python-client
"""

import argparse
import os
import pickle
import sys

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

DEFAULT_PIPELINE_DIR = os.environ.get(
    "PIPELINE_BASE_DIR", "/home/zubbyik/shorts-pipeline"
)
DEFAULT_TOKEN = os.path.join(DEFAULT_PIPELINE_DIR, "youtube_token.pickle")

# YouTube category IDs:
#   22 = People & Blogs
#   24 = Entertainment
#   17 = Sports        ← Niches B and C
#   28 = Science & Tech ← Niche A
CATEGORY_MAP = {
    "A": "28",  # Science & Tech
    "B": "17",  # Sports
    "C": "17",  # Sports
}


def load_credentials(token_path):
    """Load OAuth2 credentials from pickle file."""
    if not os.path.exists(token_path):
        print(f"❌ Token file not found: {token_path}")
        print("   Run youtube_auth.py first to generate it.")
        sys.exit(1)

    with open(token_path, "rb") as f:
        creds = pickle.load(f)

    if creds.expired:
        print("⚠️  Token has expired. Re-run youtube_auth.py to refresh.")
        sys.exit(1)

    return creds


def upload(
    file_path,
    title,
    description,
    tags,
    category_id="28",
    privacy="public",
    token_path=DEFAULT_TOKEN,
):
    """Upload a video to YouTube."""
    if not os.path.exists(file_path):
        print(f"❌ Video file not found: {file_path}")
        sys.exit(1)

    creds = load_credentials(token_path)
    youtube = build("youtube", "v3", credentials=creds)

    tag_list = [t.strip() for t in tags.split(",") if t.strip()]

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tag_list,
            "categoryId": category_id,
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    print(f"📤 Uploading: {file_path}")
    print(f"   Title: {title}")
    print(f"   Privacy: {privacy}")

    response = request.execute()
    video_id = response["id"]
    url = f"https://youtube.com/shorts/{video_id}"

    print(f"✅ Uploaded: {url}")
    return video_id


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload a Short to YouTube")
    parser.add_argument("--file", required=True, help="Path to video file")
    parser.add_argument("--title", required=True, help="YouTube title (max 60 chars)")
    parser.add_argument("--description", required=True, help="YouTube description")
    parser.add_argument("--tags", required=True, help="Comma-separated tags")
    parser.add_argument(
        "--category",
        default="28",
        help="YouTube category ID (default: 28 = Science & Tech)",
    )
    parser.add_argument(
        "--niche",
        choices=["A", "B", "C"],
        help="Niche (auto-sets category if --category not specified)",
    )
    parser.add_argument(
        "--privacy",
        default="public",
        choices=["public", "private", "unlisted"],
        help="Privacy status (default: public)",
    )
    parser.add_argument(
        "--token",
        default=DEFAULT_TOKEN,
        help=f"Path to token pickle (default: {DEFAULT_TOKEN})",
    )
    args = parser.parse_args()

    # Auto-set category from niche if provided
    category = args.category
    if args.niche and args.category == "28":
        category = CATEGORY_MAP.get(args.niche, args.category)

    upload(
        args.file,
        args.title,
        args.description,
        args.tags,
        category,
        args.privacy,
        args.token,
    )
