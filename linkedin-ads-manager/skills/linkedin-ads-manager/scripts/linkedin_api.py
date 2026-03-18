#!/usr/bin/env python3
"""
LinkedIn Ads API Client
Handles authentication and API calls for campaign management

Credential lookup order:
1. Environment variables (LINKEDIN_CAMPAIGNS_TOKEN, LINKEDIN_POSTS_TOKEN, LINKEDIN_ACCOUNT_ID)
2. .env file in --project-dir (if provided via add_project_dir_arg / load_env)
3. .env file in the current working directory
4. .env files in common Cowork project mount points (/mnt/*)
"""

import os
import requests
import json
import argparse
import sys
from pathlib import Path


def add_project_dir_arg(parser: argparse.ArgumentParser) -> None:
    """Add the --project-dir argument to any script's parser."""
    parser.add_argument(
        "--project-dir",
        help="Path to the project folder containing the .env file",
    )


def _load_creds_from_env_file(path: Path) -> dict:
    creds = {}
    if path.exists():
        try:
            for line in path.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                if key in ("LINKEDIN_CAMPAIGNS_TOKEN", "LINKEDIN_POSTS_TOKEN", "LINKEDIN_ACCOUNT_ID"):
                    creds[key] = value.strip().strip('"').strip("'")
        except OSError:
            pass
    return creds


def load_env(args: argparse.Namespace) -> None:
    """Load credentials from the .env file in --project-dir if provided."""
    if getattr(args, "project_dir", None):
        creds = _load_creds_from_env_file(Path(args.project_dir) / ".env")
        for key, value in creds.items():
            if not os.environ.get(key):
                os.environ[key] = value


def _find_creds() -> dict:
    # Check current working directory
    creds = _load_creds_from_env_file(Path.cwd() / ".env")
    if creds:
        return creds

    # Check common Cowork project mount points
    if Path("/mnt").exists():
        for mount in Path("/mnt").iterdir():
            try:
                if mount.is_dir():
                    creds = _load_creds_from_env_file(mount / ".env")
                    if creds:
                        return creds
            except (PermissionError, OSError):
                continue

    return {}


class LinkedInAdsClient:
    def __init__(self):
        self.base_url = "https://api.linkedin.com/rest"
        self.campaigns_token = None
        self.posts_token = None
        self.account_id = None
        self._load_credentials()

    def _load_credentials(self):
        # Check environment variables first, then scan for .env files
        creds = _find_creds()

        self.campaigns_token = os.environ.get("LINKEDIN_CAMPAIGNS_TOKEN") or creds.get("LINKEDIN_CAMPAIGNS_TOKEN")
        self.posts_token = os.environ.get("LINKEDIN_POSTS_TOKEN") or creds.get("LINKEDIN_POSTS_TOKEN")
        self.account_id = os.environ.get("LINKEDIN_ACCOUNT_ID") or creds.get("LINKEDIN_ACCOUNT_ID")

        if not self.campaigns_token:
            print(
                "Error: LINKEDIN_CAMPAIGNS_TOKEN not found.\n"
                "Run the linkedin-setup skill to configure credentials.",
                file=sys.stderr,
            )
            sys.exit(1)
        if not self.account_id:
            print(
                "Error: LINKEDIN_ACCOUNT_ID not found.\n"
                "Run the linkedin-setup skill to configure credentials.",
                file=sys.stderr,
            )
            sys.exit(1)

        print(f"✓ Credentials loaded: Account {self.account_id}")
        print(f"  Campaigns token: {self.campaigns_token[:10]}...")
        if self.posts_token:
            print(f"  Posts token: {self.posts_token[:10]}...")
        else:
            print(f"  Posts token: (not set - post creation will fail)")

    def _headers(self, partial_update=False, use_posts_token=False):
        """Generate request headers

        Args:
            partial_update: Add X-RestLi-Method: PARTIAL_UPDATE header
            use_posts_token: Use posts token instead of campaigns token
        """
        token = self.posts_token if use_posts_token else self.campaigns_token

        headers = {
            'Authorization': f'Bearer {token}',
            'X-Restli-Protocol-Version': '2.0.0',
            'LinkedIn-Version': '202601',
            'Content-Type': 'application/json'
        }
        if partial_update:
            headers['X-RestLi-Method'] = 'PARTIAL_UPDATE'
        return headers

    def search_campaigns(self, name_contains=None, status=None, paginate_all=True):
        """Search for campaigns by name or status

        Args:
            name_contains: Filter by campaign name (substring match after fetching)
            status: Filter by status (ACTIVE, PAUSED, etc.)
            paginate_all: If True, fetches all pages of results (default: True)
        """
        all_campaigns = []
        page_token = None

        while True:
            url = f"{self.base_url}/adAccounts/{self.account_id}/adCampaigns?q=search"

            # Add pagination token if present
            if page_token:
                url += f"&pageToken={page_token}"

            # Build search criteria (status only - name filtering done after)
            if status:
                if isinstance(status, list):
                    status_list = ','.join(status)
                else:
                    status_list = status
                url += f"&search=(status:(values:List({status_list})))"

            response = requests.get(url, headers=self._headers())

            if response.status_code != 200:
                raise Exception(f"Search failed: {response.status_code} - {response.text}")

            data = response.json()
            campaigns = data.get('elements', [])
            all_campaigns.extend(campaigns)

            # Check for next page
            page_token = data.get('metadata', {}).get('nextPageToken')

            if not page_token or not paginate_all:
                break

        # Filter by name if provided (substring match)
        if name_contains:
            all_campaigns = [
                c for c in all_campaigns
                if name_contains.lower() in c.get('name', '').lower()
            ]

        return all_campaigns

    def get_campaign(self, campaign_id):
        """Get full campaign configuration"""
        # Convert to string if integer
        if isinstance(campaign_id, int):
            campaign_id = str(campaign_id)

        # Extract ID from URN if needed
        if campaign_id.startswith('urn:li:sponsoredCampaign:'):
            campaign_id = campaign_id.split(':')[-1]

        url = f"{self.base_url}/adAccounts/{self.account_id}/adCampaigns/{campaign_id}"
        response = requests.get(url, headers=self._headers())

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Get campaign failed: {response.status_code} - {response.text}")

    def create_campaign(self, campaign_data):
        """Create a new campaign"""
        url = f"{self.base_url}/adAccounts/{self.account_id}/adCampaigns"
        response = requests.post(url, headers=self._headers(), json=campaign_data)

        if response.status_code in [200, 201]:
            # LinkedIn might return empty response with 201 Created
            if response.text:
                return response.json()
            else:
                # Extract campaign ID from Location header if available
                location = response.headers.get('x-restli-id') or response.headers.get('Location')
                return {'id': location, 'status': 'created'}
        else:
            raise Exception(f"Create campaign failed: {response.status_code} - {response.text}")

    def update_campaign(self, campaign_id, updates):
        """Update an existing campaign

        Args:
            campaign_id: Campaign ID (integer or URN)
            updates: Dictionary of fields to update
                    Will be wrapped in {"patch": {"$set": updates}} automatically
        """
        # Convert to string if integer
        if isinstance(campaign_id, int):
            campaign_id = str(campaign_id)

        if campaign_id.startswith('urn:li:sponsoredCampaign:'):
            campaign_id = campaign_id.split(':')[-1]

        # Wrap updates in patch format
        payload = {
            "patch": {
                "$set": updates
            }
        }

        url = f"{self.base_url}/adAccounts/{self.account_id}/adCampaigns/{campaign_id}"

        print(f"  Sending PARTIAL_UPDATE request to LinkedIn API...")
        response = requests.post(url, headers=self._headers(partial_update=True), json=payload)

        if response.status_code in [200, 204]:
            # 200 OK or 204 No Content both indicate success
            print(f"  ✓ API returned {response.status_code} (success)")
            return response.json() if response.text else {'status': 'updated'}
        elif response.status_code == 500:
            raise Exception(f"LinkedIn API internal error (500) - this sometimes happens with complex targeting updates. The update may have partially succeeded. Please verify the campaign.")
        else:
            error_detail = ""
            try:
                error_data = response.json()
                error_detail = error_data.get('message', response.text)
            except:
                error_detail = response.text

            raise Exception(f"Update campaign failed: {response.status_code} - {error_detail}")

    def clone_campaign(self, source_campaign_id, new_name, modifications=None):
        """Clone an existing campaign with optional modifications"""
        # Convert to string if integer
        if isinstance(source_campaign_id, int):
            source_campaign_id = str(source_campaign_id)

        # Get source campaign
        source = self.get_campaign(source_campaign_id)

        # Build new campaign data
        new_campaign = {
            'account': source['account'],
            'campaignGroup': source['campaignGroup'],
            'name': new_name,
            'type': source['type'],
            'costType': source['costType'],
            'locale': source['locale'],
            'status': 'DRAFT',  # Always start as draft for safety
            'targetingCriteria': source.get('targetingCriteria'),
            'offsiteDeliveryEnabled': source.get('offsiteDeliveryEnabled', False)
        }

        # Copy budget
        if 'dailyBudget' in source:
            new_campaign['dailyBudget'] = source['dailyBudget']
        if 'totalBudget' in source:
            new_campaign['totalBudget'] = source['totalBudget']
        if 'unitCost' in source:
            new_campaign['unitCost'] = source['unitCost']

        # Copy optional fields
        optional_fields = [
            'objectiveType', 'optimizationTargetType', 'format',
            'runSchedule', 'creativeSelection', 'pacingStrategy',
            'politicalIntent', 'audienceExpansionEnabled', 'storyDeliveryEnabled'
        ]
        for field in optional_fields:
            if field in source:
                new_campaign[field] = source[field]

        # Ensure politicalIntent is set (required field)
        if 'politicalIntent' not in new_campaign:
            new_campaign['politicalIntent'] = 'NOT_DECLARED'

        # Apply modifications
        if modifications:
            new_campaign.update(modifications)

        # Create the clone
        return self.create_campaign(new_campaign)


if __name__ == '__main__':
    # Test credentials loading
    client = LinkedInAdsClient()
    print(f"✓ Client initialized successfully")
    print(f"  Account ID: {client.account_id}")
    print(f"  Token: {client.access_token[:10]}...")
