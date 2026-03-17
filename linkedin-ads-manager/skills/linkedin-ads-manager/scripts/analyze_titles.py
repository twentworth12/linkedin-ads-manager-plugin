#!/usr/bin/env python3
"""
Analyze job title targeting for a campaign
Usage: python analyze_titles.py --campaign 475510294
"""

import argparse
import requests
from linkedin_api import LinkedInAdsClient

def search_title(client, query):
    """Search for job titles and return URN mappings"""
    url = f"{client.base_url}/adTargetingEntities?q=typeahead&facet=urn%3Ali%3AadTargetingFacet%3Atitles&query={query}&queryVersion=QUERY_USES_URNS"

    response = requests.get(url, headers=client._headers())

    if response.status_code != 200:
        return []

    data = response.json()
    results = []

    for elem in data.get('elements', []):
        urn = elem.get('urn', '')
        name = elem.get('name', '')
        title_id = int(urn.split(':')[-1]) if ':' in urn else None

        if title_id:
            results.append({'id': title_id, 'urn': urn, 'name': name})

    return results

def decode_titles(client, title_urns):
    """Decode title URNs by searching for common SRE-related terms"""
    # Common search terms for site reliability roles
    search_terms = [
        "Site Reliability Engineer", "DevOps Engineer", "Platform Engineer",
        "Infrastructure Engineer", "Cloud Engineer", "Reliability Engineer",
        "Production Engineer", "Systems Engineer",
        "Engineering Manager", "Director of Engineering", "VP Engineering",
        "CTO", "Head of DevOps", "Director of DevOps",
        "DevOps Architect", "Platform Architect", "Staff Engineer",
        "Principal Engineer", "Technical Lead", "Senior Engineer"
    ]

    # Build lookup map
    title_map = {}

    print(f"Decoding {len(title_urns)} title URNs...")
    print("Searching common SRE-related terms...\n")

    for search_term in search_terms:
        results = search_title(client, search_term)

        for result in results:
            if result['id'] in title_urns and result['id'] not in title_map:
                title_map[result['id']] = result['name']

    return title_map

def analyze_sre_coverage(title_map):
    """Analyze coverage of site reliability roles"""
    # Critical SRE/DevOps IC roles
    critical_ic_roles = {
        25764: "DevOps Engineer",
        6483: "Platform Engineer",
        30006: "Cloud Engineer",
        2922: "Infrastructure Engineer",
        2083: "Reliability Engineer",
        22848: "Site Reliability Engineer",
        25890: "Senior Site Reliability Engineer"
    }

    # Recommended additional roles
    recommended_roles = {
        30004: "DevOps Architect",
        10259: "Platform Architect",
        6995: "Senior Production Engineer",
        12715: "Production Support Engineer",
        30003: "DevOps Consultant",
        6983: "Senior Infrastructure Engineer",
        26382: "Cloud Support Engineer"
    }

    # Analyze coverage
    critical_covered = {tid: name for tid, name in critical_ic_roles.items() if tid in title_map}
    critical_missing = {tid: name for tid, name in critical_ic_roles.items() if tid not in title_map}

    recommended_covered = {tid: name for tid, name in recommended_roles.items() if tid in title_map}
    recommended_missing = {tid: name for tid, name in recommended_roles.items() if tid not in title_map}

    return {
        'critical_covered': critical_covered,
        'critical_missing': critical_missing,
        'recommended_covered': recommended_covered,
        'recommended_missing': recommended_missing
    }

def main():
    parser = argparse.ArgumentParser(description='Analyze campaign job title targeting')
    parser.add_argument('--campaign', required=True, help='Campaign ID')
    parser.add_argument('--recommend', action='store_true', help='Show targeting recommendations')

    args = parser.parse_args()

    client = LinkedInAdsClient()

    # Get campaign targeting
    print(f"Fetching campaign {args.campaign}...\n")
    campaign = client.get_campaign(args.campaign)

    targeting = campaign.get('targetingCriteria', {})
    include_and = targeting.get('include', {}).get('and', [])

    # Extract title URNs
    title_urns = []
    for facet in include_and:
        if 'urn:li:adTargetingFacet:titles' in facet.get('or', {}):
            titles = facet['or']['urn:li:adTargetingFacet:titles']
            title_urns = [int(urn.split(':')[-1]) for urn in titles]
            break

    print(f"Campaign: {campaign['name']}")
    print(f"Status: {campaign['status']}")
    print(f"Targeting {len(title_urns)} job titles\n")

    # Decode titles
    title_map = decode_titles(client, title_urns)

    print(f"✓ Decoded {len(title_map)} titles\n")
    print("=" * 80)
    print("CURRENT TARGETING")
    print("=" * 80)

    # Categorize
    leadership = {}
    managers = {}
    ics = {}
    unknown = []

    for tid, name in sorted(title_map.items(), key=lambda x: x[1]):
        if any(x in name for x in ['CTO', 'VP', 'Vice President', 'Chief']):
            leadership[tid] = name
        elif any(x in name for x in ['Director', 'Head of']):
            managers[tid] = name
        elif 'Manager' in name:
            managers[tid] = name
        else:
            ics[tid] = name

    # Unknown titles
    unknown = [tid for tid in title_urns if tid not in title_map]

    if leadership:
        print(f"\nC-Level / VPs ({len(leadership)}):")
        for tid, name in sorted(leadership.items(), key=lambda x: x[1]):
            print(f"  ✓ {tid:6} | {name}")

    if managers:
        print(f"\nDirectors / Managers ({len(managers)}):")
        for tid, name in sorted(managers.items(), key=lambda x: x[1]):
            print(f"  ✓ {tid:6} | {name}")

    if ics:
        print(f"\nIndividual Contributors ({len(ics)}):")
        for tid, name in sorted(ics.items(), key=lambda x: x[1]):
            print(f"  ✓ {tid:6} | {name}")

    if unknown:
        print(f"\nUnknown Titles ({len(unknown)}):")
        print(f"  {unknown[:20]}")

    if args.recommend:
        print("\n" + "=" * 80)
        print("TARGETING RECOMMENDATIONS")
        print("=" * 80)

        analysis = analyze_sre_coverage(title_map)

        if analysis['critical_missing']:
            print(f"\n❌ CRITICAL GAPS - Add These Immediately:")
            for tid, name in sorted(analysis['critical_missing'].items(), key=lambda x: x[1]):
                print(f"  ✗ {tid:6} | {name}")

            print(f"\n💡 These are high-volume IC roles essential for site reliability targeting.")

        if analysis['recommended_missing']:
            print(f"\n⚠️  RECOMMENDED - Consider Adding:")
            for tid, name in sorted(analysis['recommended_missing'].items(), key=lambda x: x[1]):
                print(f"  ○ {tid:6} | {name}")

        # Coverage assessment
        total_critical = len(analysis['critical_covered']) + len(analysis['critical_missing'])
        coverage_pct = (len(analysis['critical_covered']) / total_critical * 100) if total_critical > 0 else 0

        print(f"\n📊 Coverage Assessment:")
        print(f"  Critical SRE/DevOps roles: {len(analysis['critical_covered'])}/{total_critical} ({coverage_pct:.0f}%)")

        if coverage_pct < 70:
            print(f"  ⚠️  WARNING: Missing major IC roles - audience may be too senior")
        elif coverage_pct < 90:
            print(f"  ✓ Good coverage, some gaps remain")
        else:
            print(f"  ✓✓ Excellent coverage")

        print(f"\n💡 Recommendation:")
        if analysis['critical_missing']:
            missing_ids = [str(tid) for tid in analysis['critical_missing'].keys()]
            print(f"  Add {len(missing_ids)} critical titles to expand audience ~40-50%:")
            print(f"  {', '.join(missing_ids)}")
        else:
            print(f"  ✓ All critical titles covered")

    return 0

if __name__ == '__main__':
    exit(main())
