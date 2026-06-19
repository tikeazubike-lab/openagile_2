#!/usr/bin/env python3
"""
youtube_auth.py — YouTube OAuth2 initial setup
Run this ONCE manually to generate the token file.

Usage:
    python3 youtube_auth.py [--creds /path/to/credentials.json] [--token /path/to/token.pickle]
"""

import argparse
import os
import pickle

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

DEFAULT_PIPELINE_DIR = os.environ.get(
    "PIPELINE_BASE_DIR", "/home/zubbyik/shorts-pipeline"
)
DEFAULT_CREDS = os.path.join(DEFAULT_PIPELINE_DIR, "youtube_credentials.json")
DEFAULT_TOKEN = os.path.join(DEFAULT_PIPELINE_DIR, "youtube_token.pickle")


def main():
    parser = argparse.ArgumentParser(description="YouTube OAuth2 Setup")
    parser.add_argument(
        "--creds",
        default=DEFAULT_CREDS,
        help=f"Path to OAuth2 credentials JSON (default: {DEFAULT_CREDS})",
    )
    parser.add_argument(
        "--token",
        default=DEFAULT_TOKEN,
        help=f"Path to save token pickle (default: {DEFAULT_TOKEN})",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8090,
        help="Port for local OAuth callback server (default: 8090)",
    )
    args = parser.parse_args()

    if not os.path.exists(args.creds):
        print(f"❌ Credentials file not found: {args.creds}")
        print("   Download it from Google Cloud Console (OAuth 2.0 Desktop App)")
        raise SystemExit(1)

    flow = InstalledAppFlow.from_client_secrets_file(args.creds, SCOPES)
    creds = flow.run_local_server(port=args.port, open_browser=False)

    with open(args.token, "wb") as f:
        pickle.dump(creds, f)

    print(f"✅ Token saved to {args.token}")


if __name__ == "__main__":
    main()
