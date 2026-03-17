#!/usr/bin/env python3
"""
Find LinkedIn organization ID by company name
Usage: python find_organization.py "British Airways"
"""

import argparse
import requests
from urllib.parse import quote
from linkedin_api import LinkedInAdsClient

def search_organization(client, company_name):
    """Search for organization by name using ad targeting typeahead"""
    encoded_name = quote(company_name)
    url = (
        f"{client.base_url}/adTargetingEntities"
        f"?q=typeahead"
        f"&query={encoded_name}"
        f"&facet=urn%3Ali%3AadTargetingFacet%3Aemployers"
    )

    response = requests.get(url, headers=client._headers())

    if response.status_code != 200:
        print(f"Search failed: {response.status_code}")
        print(response.text[:300])
        return None

    data = response.json()
    elements = data.get('elements', [])

    if not elements:
        print(f"No organizations found matching '{company_name}'")
        return None

    return elements

def main():
    parser = argparse.ArgumentParser(description='Find LinkedIn organization ID')
    parser.add_argument('company_name', help='Company name to search for')
    args = parser.parse_args()

    client = LinkedInAdsClient()

    print(f"Searching for: {args.company_name}\n")

    results = search_organization(client, args.company_name)

    if results:
        print(f"Found {len(results)} matching organizations:\n")

        for i, org in enumerate(results, 1):
            org_urn = org.get('urn') or org.get('id', '')
            org_name = org.get('name', 'Unknown')
            numeric_id = org_urn.split(':')[-1] if ':' in org_urn else org_urn

            print(f"  {i}. {org_name}")
            print(f"     URN: {org_urn}")
            print(f"     ID: {numeric_id}")
            print()

        return 0
    else:
        return 1

if __name__ == '__main__':
    exit(main())
