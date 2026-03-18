# LinkedIn Ads Manager Plugin for Claude Cowork

Manage LinkedIn ad campaigns through natural conversation in Claude Cowork — create ads, audit performance, launch ABM programs, and post content without leaving your workflow.

## What this plugin does

### Skills

| Skill | What it does |
|-------|-------------|
| `linkedin-ads-manager` | Full campaign lifecycle: create, clone, pause, budget, targeting, analytics, and organic posting |

### Commands

| Command | What it does |
|---------|-------------|
| `/linkedin-setup` | Connect your LinkedIn account by saving your API credentials |

## Getting started

### 1. Create a local folder for the plugin

Create a folder on your Mac to store your LinkedIn credentials. This folder holds your tokens in a `.env` file that persists between Cowork sessions.

```bash
mkdir -p ~/linkedin-ads
```

### 2. Add the folder to your Cowork project

In Claude Cowork, attach the folder you just created as a local folder for your project. This is what allows your credentials to persist — the folder is mounted from your Mac into the Cowork VM.

### 3. Install the plugin

1. Open Claude Cowork and click **Customize** in the left sidebar
2. Select **Add marketplace by URL**
3. Enter the following URL and click **Sync**:
   ```
   https://github.com/twentworth12/linkedin-ads-manager-plugin.git
   ```
4. Once synced, find **LinkedIn Ads Manager** in the marketplace and click **Install**

### 4. Connect your LinkedIn account

Run the setup command in Cowork:

```
/linkedin-setup
```

Claude will walk you through creating the required LinkedIn Developer apps and saving your tokens. You'll need:

- **A LinkedIn Developer App with the Marketing Developer Platform product**
  - Scopes: `rw_ads`, `r_ads_reporting`
  - Whitelist your ad account under Products → View Ad Accounts in the developer portal
- **Your LinkedIn Ad Account ID**
- **A LinkedIn Developer App with the Community Management API product** *(optional, for posting content)*
  - Scope: `w_organization_social`

> LinkedIn requires two separate apps because a single app cannot have both the Marketing Developer Platform and Community Management API products enabled.

Get tokens from: [LinkedIn Developer Apps](https://www.linkedin.com/developers/apps) → your app → Auth → OAuth 2.0 tools

### 5. Start managing campaigns

Use the skill by typing `/` in a Cowork conversation, or just describe what you want:

- *"How are my LinkedIn campaigns performing this week?"*
- *"Clone the ABM template campaign for Acme Corp"*
- *"Pause all campaigns for the holiday weekend"*
- *"Run a full audit of our LinkedIn ad spend"*
- *"Find the LinkedIn org ID for Snowflake"*
- *"Post this announcement to our company page"*

## How credential storage works

Your tokens are stored in a `.env` file inside the local folder you attached to your Cowork project. Because this folder lives on your Mac (not inside the ephemeral Cowork VM), credentials persist between sessions.

```
~/linkedin-ads/.env          <- on your Mac, persists forever
  ├── LINKEDIN_CAMPAIGNS_TOKEN=your_token_here
  ├── LINKEDIN_ACCOUNT_ID=your_account_id
  └── LINKEDIN_POSTS_TOKEN=your_posts_token  (optional)
```

The `.env` file has owner-only read permissions (`chmod 600`) so it won't be readable by other users.

To revoke access, delete your tokens in the [LinkedIn Developer Portal](https://www.linkedin.com/developers/apps), or remove the `.env` file:

```bash
rm ~/linkedin-ads/.env
```

## Requirements

- A LinkedIn Developer account with the appropriate app products and permissions
- Claude Cowork (available on Pro, Max, Team, and Enterprise plans)
- A local folder attached to your Cowork project (for credential persistence)
- Python 3.8+ with the `requests` library (`pip install requests`)
