# LinkedIn Ads Manager — Claude Cowork Plugin

Manage LinkedIn ad campaigns through natural conversation in Claude. This plugin gives Claude full access to the LinkedIn Ads API so you can create new ads, run campaigns, audit performance, launch ABM programs, and post content — all by just asking.

## What it can do

**Campaign & Ad Creation**
- Create new campaigns and ads from scratch — describe what you want and Claude builds it
- Clone existing campaigns as templates for new ABM programs
- Upload image and video creatives to use in new ads
- List, search, and inspect campaigns by name, status, or ID
- Pause and resume campaigns individually or in batch
- Update budgets and campaign status

**Targeting**
- Analyze campaign targeting with recommendations for missing titles, skills, and organizations
- Copy targeting from one campaign to another
- Search LinkedIn's taxonomy for organization URNs, job titles, and skills
- Add/remove targeting facets (companies, titles, skills)

**Analytics & Reporting**
- Pull performance metrics (spend, impressions, clicks, conversions) for any date range
- Generate daily snapshot reports with MTD pacing and alerts for CPC spikes or creative fatigue
- Run quick operational audits or comprehensive strategic audits with benchmarks
- Break down performance by campaign group or ad type

**Content & Organic Publishing** *(optional)*
- Post text updates and images to your LinkedIn organization page
- Publish video content to your company feed

**Built-in Strategic Knowledge**
- B2B SaaS advertising best practices, funnel architecture, and benchmarks
- ABM playbook with proven operational patterns
- Monthly audit framework with checklists
- Troubleshooting guide for common API and campaign issues

## Installation

### 1. Install the plugin in Claude Cowork

Open Claude and run:

```
/install-plugin https://github.com/twentworth12/linkedin-ads-manager-plugin
```

### 2. Set up credentials

After installing, run:

```
/linkedin-setup
```

This walks you through creating the required LinkedIn Developer apps and configuring your API tokens. You'll need:

- **A LinkedIn Developer App with the Marketing Developer Platform product**
  - Scopes: `rw_ads`, `r_ads_reporting`
  - You must also whitelist your ad account under Products → View Ad Accounts in the developer portal
- **A LinkedIn Developer App with the Community Management API product** *(optional, for posting content)*
  - Scope: `w_organization_social`
- **Your LinkedIn Ad Account ID**

> LinkedIn requires two separate apps because a single app cannot have both the Marketing Developer Platform and Community Management API products enabled.

Get tokens from: [LinkedIn Developer Apps](https://www.linkedin.com/developers/apps) → your app → Auth → OAuth 2.0 tools

Alternatively, set environment variables directly: `LINKEDIN_CAMPAIGNS_TOKEN`, `LINKEDIN_POSTS_TOKEN`, `LINKEDIN_ACCOUNT_ID`.

### 3. Verify

Ask Claude: **"List my LinkedIn campaigns"** — if credentials are configured correctly, you'll see your campaigns.

## Usage examples

Just talk to Claude naturally:

- "Create a new Sponsored Content campaign targeting DevOps engineers at Acme Corp"
- "How are my LinkedIn campaigns performing this week?"
- "Clone the ABM template campaign for Acme Corp"
- "Pause all campaigns for the holiday weekend"
- "Run a full audit of our LinkedIn ad spend"
- "What's the daily report for yesterday?"
- "Find the LinkedIn org ID for Snowflake"
- "What titles should I add to this campaign's targeting?"
- "Post this announcement to our company page"

## Requirements

- Python 3.8+
- `requests` library (`pip install requests`)
- LinkedIn Developer account with appropriate app products and permissions
