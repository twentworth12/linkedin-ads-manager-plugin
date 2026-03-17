---
description: Set up LinkedIn Ads API credentials
allowed-tools: Read, Write, Bash
---

Walk the user through configuring their LinkedIn Ads API credentials. This is required before any other LinkedIn Ads Manager commands will work.

## Steps

1. Explain that LinkedIn requires **two separate developer apps** because a single app cannot have both Marketing Developer Platform and Community Management API products:
   - **App 1 (Campaign Management)**: Needs Marketing Developer Platform product with scopes `rw_ads` and `r_ads_reporting`. Also must whitelist the ad account under Products → View Ad Accounts.
   - **App 2 (Community Management)**: Needs Community Management API product with scope `w_organization_social`. This token is optional — only needed for posting content.

2. Direct the user to https://www.linkedin.com/developers/apps to create/find their apps, then use Auth → OAuth 2.0 tools to generate tokens.

3. Ask the user for three values:
   - `LINKEDIN_CAMPAIGNS_TOKEN` — from App 1
   - `LINKEDIN_POSTS_TOKEN` — from App 2 (optional)
   - `LINKEDIN_ACCOUNT_ID` — their ad account ID

4. Once the user provides the values, create a `.credentials` file at `~/.config/linkedin-ads/.credentials` (creating the directory if needed) with the format:

```
LINKEDIN_CAMPAIGNS_TOKEN=<value>
LINKEDIN_POSTS_TOKEN=<value>
LINKEDIN_ACCOUNT_ID=<value>
```

This path persists across sessions. The plugin also checks the legacy path `${CLAUDE_PLUGIN_ROOT}/skills/linkedin-ads-manager/scripts/.credentials` and environment variables as fallbacks.

5. Test the credentials by running:
```bash
${CLAUDE_PLUGIN_ROOT}/skills/linkedin-ads-manager/linkedin list --limit 1
```

6. If the test succeeds, confirm setup is complete. If it fails, help the user troubleshoot using `${CLAUDE_PLUGIN_ROOT}/skills/linkedin-ads-manager/references/TROUBLESHOOTING.md`.

**Important**: Never log or echo the full token values. When confirming, only show the first 10 characters followed by `...`.
