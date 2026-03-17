#!/usr/bin/env python3
"""
Audit ABM campaigns to find which should be turned off
Checks: campaign status, creative count, creative status
"""

import requests
from linkedin_api import LinkedInAdsClient

def main():
    client = LinkedInAdsClient()

    # Get all ABM campaigns
    print("Fetching all ABM campaigns...\n")
    all_campaigns = client.search_campaigns()

    abm_campaigns = [c for c in all_campaigns if 'abm' in c.get('name', '').lower()]
    active_abm = [c for c in abm_campaigns if c.get('status') == 'ACTIVE']

    print(f"Found {len(abm_campaigns)} ABM campaigns")
    print(f"  {len(active_abm)} ACTIVE")
    print(f"  {len([c for c in abm_campaigns if c.get('status') == 'PAUSED'])} PAUSED")
    print(f"  {len([c for c in abm_campaigns if c.get('status') == 'DRAFT'])} DRAFT")
    print(f"  {len([c for c in abm_campaigns if c.get('status') == 'REMOVED'])} REMOVED")
    print()

    # Audit active campaigns
    print("ACTIVE ABM CAMPAIGN AUDIT")
    print("=" * 100)
    print(f"{'Campaign':<30} {'Budget':>10} {'Creatives':>10} {'Serving':>8} {'Recommendation'}")
    print("-" * 100)

    issues = []
    total_budget = 0

    for campaign in sorted(active_abm, key=lambda c: c.get('name', '')):
        camp_id = campaign['id']
        name = campaign['name']

        # Get budget
        budget = 0
        if 'dailyBudget' in campaign:
            budget = float(campaign['dailyBudget']['amount'])

        total_budget += budget

        # Get creatives
        url = f"{client.base_url}/adAccounts/{client.account_id}/creatives?q=criteria&campaigns=List(urn:li:sponsoredCampaign:{camp_id})"
        headers = client._headers()
        headers['X-RestLi-Method'] = 'FINDER'

        response = requests.get(url, headers=headers)

        creative_count = 0
        serving_count = 0

        if response.status_code == 200:
            creatives = response.json().get('elements', [])
            creative_count = len(creatives)
            serving_count = len([c for c in creatives if c.get('isServing', False)])

        # Determine recommendation
        recommendation = ''
        if creative_count == 0:
            recommendation = '⚠️  PAUSE - No creatives'
            issues.append({'name': name, 'issue': 'No creatives', 'budget': budget})
        elif serving_count == 0:
            recommendation = '⚠️  PAUSE - Creatives not serving'
            issues.append({'name': name, 'issue': 'Not serving', 'budget': budget})
        elif creative_count < 2:
            recommendation = '⚠️  Low creative count'
        else:
            recommendation = '✅ OK'

        print(f"{name:<30} ${budget:>9.0f}/day {creative_count:>10} {serving_count:>8} {recommendation}")

    print("-" * 100)
    print(f"{'TOTAL DAILY BUDGET':<30} ${total_budget:>9.0f}/day")
    print(f"{'MONTHLY BUDGET':<30} ${total_budget * 30:>9.0f}/mo")

    # Recommendations
    if issues:
        print("\n" + "=" * 100)
        print("CAMPAIGNS TO PAUSE")
        print("=" * 100)

        wasted_budget = sum(i['budget'] for i in issues)

        for issue in issues:
            print(f"\n❌ {issue['name']}")
            print(f"   Issue: {issue['issue']}")
            print(f"   Wasting: ${issue['budget']}/day (${issue['budget'] * 30}/month)")

        print(f"\n💡 SAVINGS IF PAUSED:")
        print(f"   ${wasted_budget}/day")
        print(f"   ${wasted_budget * 30}/month")

        # Generate pause commands
        print(f"\n🔧 PAUSE COMMANDS:")
        for issue in issues:
            # Find campaign ID
            for c in active_abm:
                if c['name'] == issue['name']:
                    print(f"   ./linkedin update-status {c['id']} --status PAUSED")

    else:
        print("\n✅ All active ABM campaigns have creatives and are serving!")

    return 0

if __name__ == '__main__':
    exit(main())
PYTHON
