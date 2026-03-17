#!/usr/bin/env python3
"""
Clone a LinkedIn ad campaign
Usage: python clone_campaign.py --source "ABM_PayPal" --name "New Campaign Name"
"""

import argparse
import json
from linkedin_api import LinkedInAdsClient

def main():
    parser = argparse.ArgumentParser(description='Clone a LinkedIn ad campaign')
    parser.add_argument('--source', required=True, help='Source campaign name or ID')
    parser.add_argument('--name', required=True, help='New campaign name')
    parser.add_argument('--budget', type=float, help='Override daily budget (USD)')
    parser.add_argument('--status', default='DRAFT', choices=['DRAFT', 'ACTIVE', 'PAUSED'],
                       help='Campaign status (default: DRAFT for safety)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be created without creating')

    args = parser.parse_args()

    # Initialize client
    print(f"Initializing LinkedIn Ads client...")
    client = LinkedInAdsClient()

    # Search for source campaign
    print(f"\nSearching for campaign: {args.source}")

    # Try as name first
    campaigns = client.search_campaigns(name_contains=args.source)

    if not campaigns:
        # Try as ID
        try:
            source_campaign = client.get_campaign(args.source)
            campaigns = [source_campaign]
        except Exception as e:
            print(f"❌ Campaign not found: {args.source}")
            print(f"   Error: {e}")
            return 1

    if len(campaigns) > 1:
        print(f"\n⚠️  Multiple campaigns found matching '{args.source}':")
        for i, camp in enumerate(campaigns):
            print(f"  {i+1}. {camp['name']} (ID: {camp['id']}, Status: {camp['status']})")
        print(f"\nPlease be more specific with the campaign name")
        return 1

    source_campaign = campaigns[0]
    print(f"✓ Found source campaign: {source_campaign['name']}")
    print(f"  ID: {source_campaign['id']}")
    print(f"  Status: {source_campaign['status']}")
    print(f"  Type: {source_campaign['type']}")

    # Build modifications
    modifications = {'status': args.status}
    if args.budget:
        modifications['dailyBudget'] = {
            'amount': str(args.budget),
            'currencyCode': 'USD'
        }

    # Show what will be created
    print(f"\n📋 Clone Configuration:")
    print(f"  Source: {source_campaign['name']}")
    print(f"  New name: {args.name}")
    print(f"  Status: {args.status}")

    if 'dailyBudget' in source_campaign:
        budget = args.budget if args.budget else source_campaign['dailyBudget']['amount']
        print(f"  Daily budget: ${budget} USD")

    if 'targetingCriteria' in source_campaign:
        print(f"  Targeting: (inherited from source)")

    if args.dry_run:
        print(f"\n🔍 DRY RUN - Campaign would be created with this configuration:")
        print(json.dumps({
            'name': args.name,
            'type': source_campaign['type'],
            'status': args.status,
            'modifications': modifications
        }, indent=2))
        return 0

    # Clone the campaign
    print(f"\n🚀 Creating campaign...")
    try:
        source_id = source_campaign['id']
        # Convert to string if integer
        if isinstance(source_id, int):
            source_id = str(source_id)
        if source_id.startswith('urn:li:sponsoredCampaign:'):
            source_id = source_id.split(':')[-1]

        result = client.clone_campaign(
            source_campaign_id=source_id,
            new_name=args.name,
            modifications=modifications
        )

        print(f"\n✅ Campaign cloned successfully!")
        print(f"  Campaign ID: {result['id']}")
        print(f"  Name: {args.name}")
        print(f"  Status: {args.status}")

        # Generate Campaign Manager URL
        campaign_id = result['id']
        # Convert to string if integer
        if isinstance(campaign_id, int):
            campaign_id = str(campaign_id)
        if campaign_id.startswith('urn:li:sponsoredCampaign:'):
            campaign_id = campaign_id.split(':')[-1]

        url = f"https://www.linkedin.com/campaignmanager/accounts/{client.account_id}/campaigns/{campaign_id}"
        print(f"\n🔗 View in Campaign Manager:")
        print(f"  {url}")

        return 0

    except Exception as e:
        print(f"\n❌ Failed to clone campaign:")
        print(f"  {e}")
        return 1

if __name__ == '__main__':
    exit(main())
