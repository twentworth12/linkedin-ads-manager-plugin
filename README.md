# LinkedIn Ads Manager Plugin

Programmatic LinkedIn ABM campaign management for Claude. Clone campaigns, analyze targeting, update budgets, batch pause/resume, audit spend, and search URNs — all through conversational commands.

## Components

| Component | Name | Purpose |
|-----------|------|---------|
| Skill | `linkedin-ads-manager` | Core CLI + strategic reference docs for LinkedIn campaign management |
| Command | `/linkedin-setup` | Guided credential configuration |

## Setup

After installing the plugin, run `/linkedin-setup` in Claude to configure your credentials. You'll need:

1. **A LinkedIn Developer App with Marketing Developer Platform** product
   - Scopes: `rw_ads`, `r_ads_reporting`
   - Whitelist your ad account under Products → View Ad Accounts
2. **A LinkedIn Developer App with Community Management API** product (optional, for posting)
   - Scope: `w_organization_social`
3. **Your LinkedIn Ad Account ID**

Get tokens from: https://www.linkedin.com/developers/apps → your app → Auth → OAuth 2.0 tools

Alternatively, set environment variables: `LINKEDIN_CAMPAIGNS_TOKEN`, `LINKEDIN_POSTS_TOKEN`, `LINKEDIN_ACCOUNT_ID`.

## Usage

Once credentials are configured, just ask Claude naturally:

- "How are my LinkedIn campaigns doing?"
- "Clone the ABM template for Acme Corp"
- "Pause all campaigns for the holiday"
- "Run a full audit of LinkedIn ad spend"
- "What's yesterday's daily report?"
- "Find the LinkedIn org ID for Snowflake"

## Reference Docs

The plugin includes strategic reference material:

- **BEST_PRACTICES_B2B_SAAS.md** — Full B2B SaaS playbook with funnel architecture, benchmarks, and case studies
- **PLAYBOOK.md** — Proven operational patterns for ABM campaigns
- **AUDIT_FRAMEWORK.md** — Monthly audit checklists and benchmark comparisons
- **TROUBLESHOOTING.md** — Common errors and solutions

## Requirements

- Python 3.8+
- `requests` library (`pip install requests`)
- LinkedIn Developer account with appropriate app products and permissions
