---
description: Set up LinkedIn Ads API credentials
allowed-tools: Read, Write, Bash
---

## Overview

Save LinkedIn Ads credentials so all LinkedIn skills can authenticate. Credentials are stored in a `.env` file in the local folder attached to this Cowork project, so they persist between sessions.

## Workflow

### 1. Ask for credentials

Explain that LinkedIn requires **two separate developer apps** because a single app cannot have both Marketing Developer Platform and Community Management API products:

- **App 1 (Campaign Management)**: Needs Marketing Developer Platform product with scopes `rw_ads` and `r_ads_reporting`. Also must whitelist the ad account under Products → View Ad Accounts.
- **App 2 (Community Management)**: Needs Community Management API product with scope `w_organization_social`. Optional — only needed for posting content.

Direct the user to https://www.linkedin.com/developers/apps to create/find their apps, then use Auth → OAuth 2.0 tools to generate tokens.

Ask the user for:
- `LINKEDIN_CAMPAIGNS_TOKEN` — from App 1 (required)
- `LINKEDIN_ACCOUNT_ID` — their ad account ID (required)
- `LINKEDIN_POSTS_TOKEN` — from App 2 (optional)

### 2. Find the project folder

Find the local folder attached to this Cowork project:

```bash
ls /mnt/
```

Identify the user's project directory (not `.local-plugins` or other system mounts). Save this path as `PROJECT_DIR`.

### 3. Save the credentials

Pipe credentials via stdin so they don't appear in the process list or shell history:

```bash
SCRIPTS_DIR=$(find /mnt -path "*linkedin-ads-manager*/scripts/setup.py" 2>/dev/null | head -1 | xargs dirname)
printf "LINKEDIN_CAMPAIGNS_TOKEN=<token>\nLINKEDIN_ACCOUNT_ID=<account_id>\nLINKEDIN_POSTS_TOKEN=<posts_token>\n" | python "$SCRIPTS_DIR/setup.py" --project-dir <PROJECT_DIR>
```

Omit `LINKEDIN_POSTS_TOKEN` line if the user didn't provide one.

### 4. Verify credentials work

```bash
SCRIPTS_DIR=$(find /mnt -path "*linkedin-ads-manager*/scripts/setup.py" 2>/dev/null | head -1 | xargs dirname)
cd <PROJECT_DIR> && python "$SCRIPTS_DIR/linkedin_cli.py" list --limit 1
```

### 5. Confirm

If successful, tell the user they're connected and ready to manage LinkedIn Ads.

If it fails, help troubleshoot using the TROUBLESHOOTING.md reference file in the skills directory.

**Important**: Never log or echo the full token values. When confirming, only show the first 10 characters followed by `...`.
