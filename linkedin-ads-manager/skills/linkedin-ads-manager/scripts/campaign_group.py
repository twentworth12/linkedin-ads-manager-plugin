#!/usr/bin/env python3
"""
Get campaigns in a campaign group and their performance
Usage: python campaign_group.py --group-id 636435743 [--days 30]
"""

import argparse
from linkedin_api import LinkedInAdsClient

def main():
    parser = argparse.ArgumentParser(description='Get campaigns in a campaign group')
    parser.add_argument('--group-id', required=True, help='Campaign group ID')
    parser.add_argument('--days', type=int, default=30, help='Days of performance data')
    parser.add_argument('--by-type', action='store_true', help='Group results by ad type')
    parser.add_argument('--active-only', action='store_true', help='Show only active campaigns')
    args = parser.parse_args()

    # Initialize client
    client = LinkedInAdsClient()

    # Get all campaigns
    print(f"Fetching campaigns in group {args.group_id}...")
    all_campaigns = client.search_campaigns(paginate_all=True)

    # Filter for campaigns in this group
    group_urn = f'urn:li:sponsoredCampaignGroup:{args.group_id}'
    group_campaigns = [c for c in all_campaigns if c.get('campaignGroup') == group_urn]

    if not group_campaigns:
        print(f"❌ No campaigns found in group {args.group_id}")
        return 1

    if args.active_only:
        group_campaigns = [c for c in group_campaigns if c['status'] == 'ACTIVE']

    print(f"✓ Found {len(group_campaigns)} campaigns in group\n")

    if args.by_type:
        # Group by type
        by_type = {}
        for c in group_campaigns:
            camp_type = c.get('type', 'UNKNOWN')
            if camp_type not in by_type:
                by_type[camp_type] = []
            by_type[camp_type].append(c)

        # Display by type
        for camp_type, campaigns in sorted(by_type.items()):
            print(f"{camp_type} ({len(campaigns)} campaigns):")
            print("="*80)
            for c in campaigns:
                camp_id = str(c['id'])
                budget = ''
                if 'dailyBudget' in c:
                    budget = f"${c['dailyBudget']['amount']}/day"
                elif 'totalBudget' in c:
                    budget = f"${c['totalBudget']['amount']} total"

                print(f"  {c['name'][:65]}")
                print(f"    ID: {camp_id} | Status: {c['status']} | Budget: {budget}")
            print()
    else:
        # Simple list
        for c in group_campaigns:
            camp_id = str(c['id'])
            print(f"{c['name']}")
            print(f"  ID: {camp_id}")
            print(f"  Status: {c['status']}")
            print(f"  Type: {c.get('type', 'UNKNOWN')}")
            if 'dailyBudget' in c:
                print(f"  Budget: ${c['dailyBudget']['amount']}/day")
            print()

    return 0

if __name__ == '__main__':
    exit(main())
