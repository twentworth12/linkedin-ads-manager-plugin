#!/usr/bin/env python3
"""
List all LinkedIn ad campaigns
Usage: python list_campaigns.py [--search PayPal] [--status ACTIVE]
"""

import argparse
from linkedin_api import LinkedInAdsClient

def main():
    parser = argparse.ArgumentParser(description='List LinkedIn ad campaigns')
    parser.add_argument('--search', help='Search for campaigns containing this text')
    parser.add_argument('--status', help='Filter by status (ACTIVE, PAUSED, DRAFT)')
    args = parser.parse_args()

    client = LinkedInAdsClient()

    print(f"Fetching campaigns from account {client.account_id}...\n")

    campaigns = client.search_campaigns(status=args.status)

    if args.search:
        campaigns = [c for c in campaigns if args.search.lower() in c.get('name', '').lower()]
        print(f"Found {len(campaigns)} campaigns matching '{args.search}'\n")
    else:
        print(f"Found {len(campaigns)} total campaigns\n")

    for i, campaign in enumerate(campaigns, 1):
        camp_id = campaign.get('id', '?')
        name = campaign.get('name', 'unnamed')
        status = campaign.get('status', '?')
        camp_type = campaign.get('type', '?')

        print(f"{i}. {name}")
        print(f"   ID: {camp_id}  Status: {status}  Type: {camp_type}")

        if 'dailyBudget' in campaign:
            budget = campaign['dailyBudget']
            print(f"   Daily Budget: ${budget['amount']} {budget['currencyCode']}")

        print()

    return 0

if __name__ == '__main__':
    exit(main())
