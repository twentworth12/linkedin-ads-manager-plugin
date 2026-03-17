#!/usr/bin/env python3
"""
LinkedIn Ads API Client
Handles authentication and API calls for campaign management
"""

import os
import requests
import json
from pathlib import Path

class LinkedInAdsClient:
    def __init__(self):
        self.base_url = "https://api.linkedin.com/rest"
        self.campaigns_token = None
        self.posts_token = None
        self.account_id = None
        self.load_credentials()

    def load_credentials(self):
        """Load credentials from persistent config, .env file, legacy .credentials, or environment variables"""
        import os

        # Priority order: persistent config > project .env > local .credentials
        persistent_file = Path.home() / '.config' / 'linkedin-ads' / '.credentials'
        project_root = Path(__file__).parent.parent.parent.parent
        env_file = project_root / '.env'
        legacy_file = Path(__file__).parent / '.credentials'

        creds_file = None
        for candidate in [persistent_file, env_file, legacy_file]:
            if candidate.exists():
                creds_file = candidate
                break

        if creds_file:
            with open(creds_file) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('#') or not line or '=' not in line:
                        continue
                    key, value = line.split('=', 1)
                    if key == 'LINKEDIN_CAMPAIGNS_TOKEN':
                        self.campaigns_token = value
                    elif key == 'LINKEDIN_POSTS_TOKEN':
                        self.posts_token = value
                    elif key == 'LINKEDIN_ACCOUNT_ID':
                        self.account_id = value

        # Fall back to environment variables (for Claude Code web/Slack sessions)
        if not self.campaigns_token:
            self.campaigns_token = os.environ.get('LINKEDIN_CAMPAIGNS_TOKEN')
        if not self.posts_token:
            self.posts_token = os.environ.get('LINKEDIN_POSTS_TOKEN')
        if not self.account_id:
            self.account_id = os.environ.get('LINKEDIN_ACCOUNT_ID')

        if not self.campaigns_token:
            raise ValueError("LINKEDIN_CAMPAIGNS_TOKEN not found in .env, .credentials, or environment")
        if not self.account_id:
            raise ValueError("LINKEDIN_ACCOUNT_ID not found in .env, .credentials, or environment")

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
