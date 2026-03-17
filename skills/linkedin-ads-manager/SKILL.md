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

## Setup

Before using this skill, credentials must be configured. Run `/linkedin-setup` or set environment variables:

- `LINKEDIN_CAMPAIGNS_TOKEN` — OAuth token from Marketing Developer Platform app (scopes: `rw_ads`, `r_ads_reporting`)
- `LINKEDIN_POSTS_TOKEN` — OAuth token from Community Management API app (scope: `w_organization_social`)
- `LINKEDIN_ACCOUNT_ID` — Your LinkedIn ad account ID

Get tokens from https://www.linkedin.com/developers/apps → Auth → OAuth 2.0 tools.

**Why two tokens:** LinkedIn doesn't allow a single app to have both Marketing Developer Platform AND Community Management API products. You need separate apps.

## Usage

Run the CLI wrapper from the skill directory:

```bash
chmod +x ${CLAUDE_PLUGIN_ROOT}/skills/linkedin-ads-manager/linkedin
${CLAUDE_PLUGIN_ROOT}/skills/linkedin-ads-manager/linkedin [command] [options]
```

## Command Reference

### Campaign Management

```bash
./linkedin list [--name SEARCH] [--status ACTIVE,PAUSED] [--limit 20]
./linkedin get CAMPAIGN_ID [--json]
./linkedin clone --source CAMPAIGN --name NEW_NAME [--clone-creatives] [--budget 50]
./linkedin update-status CAMPAIGN_ID --status PAUSED|ACTIVE|DRAFT
./linkedin update-budget CAMPAIGN_ID --budget 100
./linkedin pause-all [--name FILTER] [--dry-run]
./linkedin resume-all [--dry-run]
```

### Targeting Operations

```bash
./linkedin analyze CAMPAIGN_ID [--recommend]
./linkedin update-targeting CAMPAIGN_ID [--add-organization ORG_ID] [--add-titles IDS] [--add-skills IDS]
./linkedin copy-targeting --source CAMPAIGN_ID --target CAMPAIGN_ID
./linkedin recommend-skills [--campaign-id CAMPAIGN_ID]
```

### Search & Discovery

```bash
./linkedin find-org "Company Name"
./linkedin find-skill "Kubernetes"
./linkedin find-title "DevOps Engineer"
```

### Analytics

```bash
./linkedin performance --campaign-id CAMPAIGN_ID [--days 30]
./linkedin performance --name "ABM" [--days 7]
./linkedin daily                                    # Yesterday's snapshot + MTD pacing + alerts
./linkedin daily --date 2026-03-10                  # Specific date report
./linkedin daily --month-budget 25000               # Override monthly budget for pacing
./linkedin audit                                    # Quick operational check
./linkedin audit-v2                                 # Comprehensive strategic audit
./linkedin campaign-group --group-id GROUP_ID [--by-type] [--active-only]
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
./linkedin find-org "Company Name"
./linkedin clone --source TEMPLATE_CAMPAIGN --name "ABM_CompanyName" --clone-creatives
./linkedin update-targeting NEW_ID --add-organization ORG_ID --org-name "Company Name"
./linkedin analyze NEW_ID
```

### Fix Underperforming Campaign

```bash
./linkedin analyze CAMPAIGN_ID
./linkedin copy-targeting --source WINNING_ID --target CAMPAIGN_ID
./linkedin update-targeting CAMPAIGN_ID --add-organization ORG_ID --org-name "Company Name"
```

### Batch Pause for Holidays

```bash
./linkedin pause-all --dry-run
./linkedin pause-all
# ... after holiday ...
./linkedin resume-all --dry-run
./linkedin resume-all
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
