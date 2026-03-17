#!/usr/bin/env python3
"""
Update campaign targeting to different organization
Usage: python update_targeting.py --campaign 475510294 --organization "urn:li:organization:20740"
"""

import argparse
import requests
from linkedin_api import LinkedInAdsClient

def main():
    parser = argparse.ArgumentParser(description='Update campaign organization targeting')
    parser.add_argument('--campaign', required=True, help='Campaign ID')
    parser.add_argument('--organization', required=True, help='Organization URN or ID')
    parser.add_argument('--organization-name', help='Organization name (for display)')

    args = parser.parse_args()

    client = LinkedInAdsClient()

    # Ensure org URN format
    if not args.organization.startswith('urn:li:organization:'):
        org_urn = f"urn:li:organization:{args.organization}"
    else:
        org_urn = args.organization

    print(f"Updating campaign {args.campaign} targeting...")
    print(f"  New organization: {org_urn}")
    if args.organization_name:
        print(f"  Name: {args.organization_name}")
    print()

    # Get current campaign
    campaign = client.get_campaign(args.campaign)

    # Update targeting
    targeting = campaign.get('targetingCriteria', {})

    # Find and update employers facet
    include_and = targeting.get('include', {}).get('and', [])

    for facet in include_and:
        if 'urn:li:adTargetingFacet:employers' in facet.get('or', {}):
            old_orgs = facet['or']['urn:li:adTargetingFacet:employers']
            print(f"  Current targeting: {old_orgs}")
            facet['or']['urn:li:adTargetingFacet:employers'] = [org_urn]
            print(f"  Updated to: {[org_urn]}")
            break

    # Update campaign
    updates = {'targetingCriteria': targeting}

    try:
        result = client.update_campaign(args.campaign, updates)
        print(f"\n✅ Campaign targeting updated successfully!")
        print(f"\n🔗 View in Campaign Manager:")
        campaign_id = str(args.campaign)
        print(f"  https://www.linkedin.com/campaignmanager/accounts/{client.account_id}/campaigns/{campaign_id}")

        return 0

    except Exception as e:
        print(f"\n❌ Update failed: {e}")
        return 1

if __name__ == '__main__':
    exit(main())
