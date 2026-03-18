---
name: linkedin-ads-manager
description: >
  This skill should be used when the user asks to "manage LinkedIn ads",
  "check LinkedIn campaign performance", "clone a LinkedIn campaign",
  "pause LinkedIn ads", "audit LinkedIn spend", "launch an ABM campaign",
  "update LinkedIn targeting", or needs help with LinkedIn advertising
  operations, budget management, or campaign analytics.
version: 0.1.0
---

# LinkedIn Ads Manager

Manage LinkedIn ad campaigns programmatically via a Python CLI. Full campaign lifecycle: creation, cloning, budget management, targeting configuration, performance analytics, and batch operations.

## Credential Handling

Before asking the user for any API credentials, tokens, or account IDs, **always check the `.env` file in the project root first**:
```bash
cat .env 2>/dev/null
```

If the required credentials are present, load them silently and proceed — do not ask the user to provide them. Only ask for credentials if they are genuinely missing from `.env`.

## Setup

Before using this skill, credentials must be configured. Run `/linkedin-setup` or set environment variables:

- `LINKEDIN_CAMPAIGNS_TOKEN` — OAuth token from Marketing Developer Platform app (scopes: `rw_ads`, `r_ads_reporting`)
- `LINKEDIN_POSTS_TOKEN` — OAuth token from Community Management API app (scope: `w_organization_social`)
- `LINKEDIN_ACCOUNT_ID` — Your LinkedIn ad account ID

Get tokens from https://www.linkedin.com/developers/apps → Auth → OAuth 2.0 tools.

**Why two tokens:** LinkedIn doesn't allow a single app to have both Marketing Developer Platform AND Community Management API products. You need separate apps.

## Usage

The CLI script lives on a read-only filesystem — always invoke it with `bash` directly (do not use `chmod +x`):

```bash
bash ${CLAUDE_PLUGIN_ROOT}/skills/linkedin-ads-manager/linkedin [command] [options]
```

## Command Reference

### Campaign Management

```bash
bash ${CLAUDE_PLUGIN_ROOT}/skills/linkedin-ads-manager/linkedin list [--name SEARCH] [--status ACTIVE,PAUSED] [--limit 20]
bash ${CLAUDE_PLUGIN_ROOT}/skills/linkedin-ads-manager/linkedin get CAMPAIGN_ID [--json]
bash ${CLAUDE_PLUGIN_ROOT}/skills/linkedin-ads-manager/linkedin clone --source CAMPAIGN --name NEW_NAME [--clone-creatives] [--budget 50]
bash ${CLAUDE_PLUGIN_ROOT}/skills/linkedin-ads-manager/linkedin update-status CAMPAIGN_ID --status PAUSED|ACTIVE|DRAFT
bash ${CLAUDE_PLUGIN_ROOT}/skills/linkedin-ads-manager/linkedin update-budget CAMPAIGN_ID --budget 100
bash ${CLAUDE_PLUGIN_ROOT}/skills/linkedin-ads-manager/linkedin pause-all [--name FILTER] [--dry-run]
bash ${CLAUDE_PLUGIN_ROOT}/skills/linkedin-ads-manager/linkedin resume-all [--dry-run]
```

### Targeting Operations

```bash
bash ${CLAUDE_PLUGIN_ROOT}/skills/linkedin-ads-manager/linkedin analyze CAMPAIGN_ID [--recommend]
bash ${CLAUDE_PLUGIN_ROOT}/skills/linkedin-ads-manager/linkedin update-targeting CAMPAIGN_ID [--add-organization ORG_ID] [--add-titles IDS] [--add-skills IDS]
bash ${CLAUDE_PLUGIN_ROOT}/skills/linkedin-ads-manager/linkedin copy-targeting --source CAMPAIGN_ID --target CAMPAIGN_ID
bash ${CLAUDE_PLUGIN_ROOT}/skills/linkedin-ads-manager/linkedin recommend-skills [--campaign-id CAMPAIGN_ID]
```

### Search & Discovery

```bash
bash ${CLAUDE_PLUGIN_ROOT}/skills/linkedin-ads-manager/linkedin find-org "Company Name"
bash ${CLAUDE_PLUGIN_ROOT}/skills/linkedin-ads-manager/linkedin find-skill "Kubernetes"
bash ${CLAUDE_PLUGIN_ROOT}/skills/linkedin-ads-manager/linkedin find-title "DevOps Engineer"
```

### Analytics

```bash
bash ${CLAUDE_PLUGIN_ROOT}/skills/linkedin-ads-manager/linkedin performance --campaign-id CAMPAIGN_ID [--days 30]
bash ${CLAUDE_PLUGIN_ROOT}/skills/linkedin-ads-manager/linkedin performance --name "ABM" [--days 7]
bash ${CLAUDE_PLUGIN_ROOT}/skills/linkedin-ads-manager/linkedin daily                                    # Yesterday's snapshot + MTD pacing + alerts
bash ${CLAUDE_PLUGIN_ROOT}/skills/linkedin-ads-manager/linkedin daily --date 2026-03-10                  # Specific date report
bash ${CLAUDE_PLUGIN_ROOT}/skills/linkedin-ads-manager/linkedin daily --month-budget 25000               # Override monthly budget for pacing
bash ${CLAUDE_PLUGIN_ROOT}/skills/linkedin-ads-manager/linkedin audit                                    # Quick operational check
bash ${CLAUDE_PLUGIN_ROOT}/skills/linkedin-ads-manager/linkedin audit-v2                                 # Comprehensive strategic audit
bash ${CLAUDE_PLUGIN_ROOT}/skills/linkedin-ads-manager/linkedin campaign-group --group-id GROUP_ID [--by-type] [--active-only]
```

## When to Use Each Command

- **campaign-group**: Breakdown by ad type, campaign group performance, BoFu/MoFu/ToFu analysis.
- **analyze**: Campaign targeting questions, role coverage, recommendations for missing titles/skills.
- **daily**: Yesterday's snapshot, MTD pacing, morning check-in, creative fatigue/CPC spike detection.
- **audit**: Quick operational check (~30 seconds), simple pause recommendations.
- **audit-v2**: Comprehensive health assessment, monthly strategic review, benchmarks, prioritized action plan.
- **pause-all/resume-all**: Holiday pausing, budget holds, emergency pause. **NOT for weekend pausing** — disrupts LinkedIn's learning algorithm.
- **clone**: New ABM campaign for a company. Do NOT use `--clone-creatives` by default (each campaign needs custom creatives).
- **performance**: Specific campaign metrics, spend/conversion data, last N days.

**Key pattern**: Before writing a custom script, check if an existing command handles the use case.

## Common Workflows

### Launch ABM Campaign for New Account

```bash
bash ${CLAUDE_PLUGIN_ROOT}/skills/linkedin-ads-manager/linkedin find-org "Company Name"
bash ${CLAUDE_PLUGIN_ROOT}/skills/linkedin-ads-manager/linkedin clone --source TEMPLATE_CAMPAIGN --name "ABM_CompanyName" --clone-creatives
bash ${CLAUDE_PLUGIN_ROOT}/skills/linkedin-ads-manager/linkedin update-targeting NEW_ID --add-organization ORG_ID --org-name "Company Name"
bash ${CLAUDE_PLUGIN_ROOT}/skills/linkedin-ads-manager/linkedin analyze NEW_ID
```

### Fix Underperforming Campaign

```bash
bash ${CLAUDE_PLUGIN_ROOT}/skills/linkedin-ads-manager/linkedin analyze CAMPAIGN_ID
bash ${CLAUDE_PLUGIN_ROOT}/skills/linkedin-ads-manager/linkedin copy-targeting --source WINNING_ID --target CAMPAIGN_ID
bash ${CLAUDE_PLUGIN_ROOT}/skills/linkedin-ads-manager/linkedin update-targeting CAMPAIGN_ID --add-organization ORG_ID --org-name "Company Name"
```

### Batch Pause for Holidays

```bash
bash ${CLAUDE_PLUGIN_ROOT}/skills/linkedin-ads-manager/linkedin pause-all --dry-run
bash ${CLAUDE_PLUGIN_ROOT}/skills/linkedin-ads-manager/linkedin pause-all
# ... after holiday ...
bash ${CLAUDE_PLUGIN_ROOT}/skills/linkedin-ads-manager/linkedin resume-all --dry-run
bash ${CLAUDE_PLUGIN_ROOT}/skills/linkedin-ads-manager/linkedin resume-all
```

## Reference Documents

For deeper strategic guidance, read the reference files:

- `references/BEST_PRACTICES_B2B_SAAS.md` — Full strategic playbook: funnel architecture, ICP-first targeting, creative refresh cycles, benchmarks
- `references/PLAYBOOK.md` — Proven operational patterns for ABM campaigns, targeting diagnostics
- `references/AUDIT_FRAMEWORK.md` — Monthly audit checklists and benchmark comparison frameworks
- `references/TROUBLESHOOTING.md` — Common errors and solutions

## API Gotchas

- **Pagination mandatory**: API returns max 100 results. Always paginate with `nextPageToken`.
- **Integer IDs**: API returns campaign IDs as integers. Always convert with `str()` before string operations.
- **`politicalIntent` required**: Creating campaigns without it causes 422. Always include `"politicalIntent": "NOT_DECLARED"`.
- **Empty response on create**: 201 Created returns empty body. Check `x-restli-id` header for new ID.
- **Account whitelisting**: Having `rw_ads` scope isn't enough — must add account ID in Developer Portal → Products → View Ad Accounts.

## Required Permissions

**OAuth Scopes:** `rw_ads` (read/write campaigns), `r_ads_reporting` (analytics)

**Account Role:** ACCOUNT_MANAGER, CAMPAIGN_MANAGER, or ACCOUNT_BILLING_ADMIN
