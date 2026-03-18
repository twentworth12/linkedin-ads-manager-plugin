#!/usr/bin/env python3
"""Save LinkedIn Ads credentials to a .env file in the project folder.

Credentials are read from stdin as KEY=VALUE lines to avoid exposing
them in process lists or shell history.

Usage:
    printf "LINKEDIN_CAMPAIGNS_TOKEN=xxx\nLINKEDIN_ACCOUNT_ID=yyy\n" | python setup.py --project-dir /path/to/project
"""

import argparse
import sys
from pathlib import Path

ENV_FILE = ".env"

CREDENTIAL_KEYS = [
    "LINKEDIN_CAMPAIGNS_TOKEN",
    "LINKEDIN_POSTS_TOKEN",
    "LINKEDIN_ACCOUNT_ID",
]


def main():
    parser = argparse.ArgumentParser(description="Save LinkedIn Ads credentials")
    parser.add_argument("--project-dir", required=True, help="Path to the Cowork project folder")
    args = parser.parse_args()

    # Parse KEY=VALUE pairs from stdin
    new_creds = {}
    for line in sys.stdin.read().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key in CREDENTIAL_KEYS:
            new_creds[key] = value.strip()

    if not new_creds:
        print("Error: no credentials provided on stdin.", file=sys.stderr)
        sys.exit(1)

    env_path = Path(args.project_dir) / ENV_FILE

    # Read existing .env, strip out any old LinkedIn keys
    if env_path.exists():
        lines = [l for l in env_path.read_text().splitlines()
                 if not any(l.startswith(f"{k}=") for k in CREDENTIAL_KEYS)]
    else:
        lines = []

    for key, value in new_creds.items():
        lines.append(f"{key}={value}")

    env_path.write_text("\n".join(lines) + "\n")
    env_path.chmod(0o600)

    print(f"Credentials saved to {env_path}")
    for key in new_creds:
        print(f"  {key}: {new_creds[key][:10]}...")
    print("Done.")


if __name__ == "__main__":
    main()
