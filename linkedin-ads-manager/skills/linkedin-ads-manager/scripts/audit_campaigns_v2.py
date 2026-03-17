#!/usr/bin/env python3
"""
Enhanced LinkedIn Ads Audit - Based on 2025-2026 Best Practices

Comprehensive campaign health assessment including:
- Performance vs. benchmarks (CTR, CPC, CPL)
- Creative age and fatigue detection
- Targeting quality (AND/OR logic, ICP alignment)
- Budget efficiency analysis
- Health score calculation
- Prioritized action recommendations

Run from repository root:
    python3 .claude/skills/linkedin-ads-manager/audit_campaigns_v2.py

Or via CLI wrapper:
    ./linkedin audit-v2
"""

import requests
from linkedin_api import LinkedInAdsClient
from datetime import datetime, timedelta
import json

# 2025-2026 B2B SaaS Benchmarks
BENCHMARKS = {
    'ctr': {'median': 0.0053, 'top_quartile': 0.0070},  # 0.53%, 0.70%
    'cpc': {'median': 6.43, 'top_quartile': 5.00},      # $6.43, $5.00
    'cpl': {'median': 112.50, 'top_quartile': 90.00},   # $112.50, $90.00
    'form_conversion': {'median': 0.08, 'top_quartile': 0.10},  # 8%, 10%
}

def calculate_health_score(metrics):
    """
    Calculate overall health score (0-100) based on 6 categories

    Categories and weights:
    - Performance vs. Benchmarks: 25%
    - Creative Health: 20%
    - Targeting Quality: 20%
    - Budget Efficiency: 15%
    - Strategic Coverage: 10%
    - Advanced Optimization: 10%
    """
    score = 0

    # Performance vs. Benchmarks (25 points)
    if metrics.get('ctr', 0) >= BENCHMARKS['ctr']['median']:
        score += 5
    if metrics.get('ctr', 0) >= BENCHMARKS['ctr']['top_quartile']:
        score += 2  # Bonus for top quartile

    if metrics.get('cpc', 999) <= BENCHMARKS['cpc']['median']:
        score += 5
    if metrics.get('cpc', 999) <= BENCHMARKS['cpc']['top_quartile']:
        score += 2

    if metrics.get('cpl', 999) <= BENCHMARKS['cpl']['median']:
        score += 5
    if metrics.get('conversions', 0) > 0:
        score += 3  # Has conversions

    # Creative Health (20 points)
    creative_age_avg = metrics.get('creative_age_avg', 999)
    if creative_age_avg <= 14:
        score += 5  # Fresh creatives
    elif creative_age_avg <= 21:
        score += 3  # Acceptable

    creative_count = metrics.get('creative_count', 0)
    if creative_count >= 3:
        score += 5  # Good diversity
    elif creative_count >= 2:
        score += 3

    if metrics.get('serving_count', 0) > 0:
        score += 5  # Creatives are serving

    creative_decay = metrics.get('ctr_decay_pct', 0)
    if creative_decay < 10:
        score += 5  # No fatigue
    elif creative_decay < 20:
        score += 3

    # Targeting Quality (20 points)
    if not metrics.get('has_restrictive_and_logic', False):
        score += 5  # No AND logic issues

    audience_size = metrics.get('audience_size', 0)
    if 20000 <= audience_size <= 100000:
        score += 5  # Optimal audience size
    elif 10000 <= audience_size < 200000:
        score += 3

    if metrics.get('has_critical_skills', False):
        score += 5  # Critical targeting elements present

    if metrics.get('has_icp_alignment', False):
        score += 5  # ICP-aligned targeting

    # Budget Efficiency (15 points)
    if metrics.get('budget', 0) >= 15:
        score += 5  # Sufficient budget

    wasted_spend_pct = metrics.get('wasted_spend_pct', 100)
    if wasted_spend_pct < 10:
        score += 5  # Low waste
    elif wasted_spend_pct < 20:
        score += 3

    if metrics.get('has_conversions_recent', False):
        score += 5  # Converting recently

    # Strategic Coverage (10 points)
    # (These need program-level data, placeholder for now)
    score += 5  # Placeholder for full-funnel coverage
    score += 5  # Placeholder for retargeting infrastructure

    # Advanced Optimization (10 points)
    # (These need additional data, placeholder for now)
    score += 10  # Placeholder

    return min(score, 100)  # Cap at 100

def format_status(value, benchmark_median, benchmark_top, lower_is_better=False):
    """Format value with color-coded status vs benchmarks"""
    if lower_is_better:
        if value <= benchmark_top:
            return f"🟢 {value}"
        elif value <= benchmark_median:
            return f"🟡 {value}"
        else:
            return f"🔴 {value}"
    else:
        if value >= benchmark_top:
            return f"🟢 {value}"
        elif value >= benchmark_median:
            return f"🟡 {value}"
        else:
            return f"🔴 {value}"

def get_campaign_analytics(client, campaign_id, days=30):
    """Fetch analytics for a campaign"""
    try:
        url = f"{client.base_url}/adAnalytics"
        params = {
            'q': 'analytics',
            'campaigns': f'urn:li:sponsoredCampaign:{campaign_id}',
            'dateRange.start.day': (datetime.now() - timedelta(days=days)).day,
            'dateRange.start.month': (datetime.now() - timedelta(days=days)).month,
            'dateRange.start.year': (datetime.now() - timedelta(days=days)).year,
            'dateRange.end.day': datetime.now().day,
            'dateRange.end.month': datetime.now().month,
            'dateRange.end.year': datetime.now().year,
            'timeGranularity': 'DAILY',
            'pivot': 'CAMPAIGN',
            'fields': 'externalWebsiteConversions,clicks,impressions,costInLocalCurrency'
        }

        response = requests.get(url, headers=client._headers(), params=params)

        if response.status_code != 200:
            return None

        elements = response.json().get('elements', [])
        if not elements:
            return None

        # Aggregate across days
        total_impressions = 0
        total_clicks = 0
        total_cost = 0
        total_conversions = 0

        for element in elements:
            total_impressions += element.get('impressions', 0)
            total_clicks += element.get('clicks', 0)
            total_cost += float(element.get('costInLocalCurrency', 0))
            total_conversions += element.get('externalWebsiteConversions', 0)

        if total_impressions == 0:
            return None

        ctr = (total_clicks / total_impressions) if total_impressions > 0 else 0
        cpc = (total_cost / total_clicks) if total_clicks > 0 else 0
        cpl = (total_cost / total_conversions) if total_conversions > 0 else 0

        return {
            'impressions': total_impressions,
            'clicks': total_clicks,
            'cost': total_cost,
            'conversions': total_conversions,
            'ctr': ctr,
            'cpc': cpc,
            'cpl': cpl if total_conversions > 0 else None
        }
    except Exception as e:
        print(f"    ⚠️ Analytics fetch error: {e}")
        return None

def analyze_targeting_logic(campaign):
    """Check for restrictive AND logic between titles and skills"""
    targeting = campaign.get('targetingCriteria', {})
    include = targeting.get('include', {})
    and_groups = include.get('and', [])

    has_titles = False
    has_skills = False
    same_group = False

    for facet_group in and_groups:
        facets = facet_group.get('or', {})
        group_has_titles = 'urn:li:adTargetingFacet:titles' in facets
        group_has_skills = 'urn:li:adTargetingFacet:skills' in facets

        if group_has_titles:
            has_titles = True
        if group_has_skills:
            has_skills = True
        if group_has_titles and group_has_skills:
            same_group = True

    # Restrictive if titles AND skills in different groups
    has_restrictive_and = has_titles and has_skills and not same_group

    return {
        'has_restrictive_and_logic': has_restrictive_and,
        'has_titles': has_titles,
        'has_skills': has_skills,
        'same_group': same_group
    }

def check_critical_skills(campaign):
    """Check if campaign has critical SRE/DevOps skills"""
    targeting = campaign.get('targetingCriteria', {})
    include = targeting.get('include', {})
    and_groups = include.get('and', [])

    # Critical skills for SRE/DevOps targeting
    critical_skills = {
        '55983',    # PagerDuty
        '56845',    # Opsgenie
        '1952',     # Incident Management
        '4008',     # Incident Response
        '18442',    # DevOps
        '55383',    # Site Reliability Engineering
        '55158',    # Kubernetes
        '1500290',  # Docker
        '10798',    # AWS
    }

    campaign_skills = set()
    for facet_group in and_groups:
        facets = facet_group.get('or', {})
        if 'urn:li:adTargetingFacet:skills' in facets:
            skills = facets['urn:li:adTargetingFacet:skills']
            for skill in skills:
                skill_id = skill.split(':')[-1]
                campaign_skills.add(skill_id)

    overlap = campaign_skills.intersection(critical_skills)
    coverage = len(overlap) / len(critical_skills) if critical_skills else 0

    return {
        'has_critical_skills': len(overlap) >= 5,  # At least 5 of 9 critical skills
        'skill_count': len(campaign_skills),
        'critical_skill_coverage': coverage
    }

def main():
    client = LinkedInAdsClient()

    print("=" * 120)
    print("LINKEDIN ADS COMPREHENSIVE AUDIT")
    print("Based on 2025-2026 B2B SaaS Best Practices")
    print("=" * 120)
    print()

    # Get all campaigns
    print("📊 Fetching campaign data...\n")
    all_campaigns = client.search_campaigns()

    # Filter to ABM campaigns
    abm_campaigns = [c for c in all_campaigns if 'abm' in c.get('name', '').lower()]
    active_abm = [c for c in abm_campaigns if c.get('status') == 'ACTIVE']

    print(f"Found {len(abm_campaigns)} ABM campaigns")
    print(f"  {len(active_abm)} ACTIVE")
    print(f"  {len([c for c in abm_campaigns if c.get('status') == 'PAUSED'])} PAUSED")
    print(f"  {len([c for c in abm_campaigns if c.get('status') == 'DRAFT'])} DRAFT")
    print()

    # === SECTION 1: PERFORMANCE VS. BENCHMARKS ===
    print("=" * 120)
    print("1. PERFORMANCE VS. BENCHMARKS")
    print("=" * 120)
    print()

    print(f"{'Campaign':<30} {'CTR':>8} {'CPC':>10} {'Conv':>6} {'CPL':>10} {'Spend':>10} {'Health':>8} {'Status'}")
    print("-" * 120)

    campaign_metrics = []
    total_budget = 0
    total_spend = 0
    total_impressions = 0
    total_clicks = 0
    total_conversions = 0

    for campaign in sorted(active_abm, key=lambda c: c.get('name', '')):
        camp_id = campaign['id']
        name = campaign['name'][:28]

        # Get budget
        budget = 0
        if 'dailyBudget' in campaign:
            budget = float(campaign['dailyBudget']['amount'])
        total_budget += budget

        # Get analytics
        analytics = get_campaign_analytics(client, camp_id, days=30)

        if analytics:
            ctr = analytics['ctr']
            cpc = analytics['cpc']
            cpl = analytics['cpl']
            conversions = analytics['conversions']
            spend = analytics['cost']

            total_spend += spend
            total_impressions += analytics['impressions']
            total_clicks += analytics['clicks']
            total_conversions += conversions

            # Calculate preliminary health score
            health = 0
            if ctr >= BENCHMARKS['ctr']['median']:
                health += 35
            if ctr >= BENCHMARKS['ctr']['top_quartile']:
                health += 10
            if cpc <= BENCHMARKS['cpc']['median']:
                health += 35
            if cpc <= BENCHMARKS['cpc']['top_quartile']:
                health += 10
            if conversions > 0:
                health += 10

            # Status determination
            status = '🟢 Good'
            if ctr < 0.004 or cpc > 15 or (spend > 200 and conversions == 0):
                status = '🔴 Critical'
            elif ctr < BENCHMARKS['ctr']['median'] or cpc > BENCHMARKS['cpc']['median']:
                status = '🟡 Fair'

            ctr_display = f"{ctr*100:.2f}%"
            cpc_display = f"${cpc:.2f}"
            cpl_display = f"${cpl:.0f}" if cpl else "N/A"
            spend_display = f"${spend:.0f}"

            # Color-code based on benchmarks
            if ctr >= BENCHMARKS['ctr']['top_quartile']:
                ctr_display = f"🟢{ctr*100:.2f}%"
            elif ctr >= BENCHMARKS['ctr']['median']:
                ctr_display = f"🟡{ctr*100:.2f}%"
            else:
                ctr_display = f"🔴{ctr*100:.2f}%"

            if cpc <= BENCHMARKS['cpc']['top_quartile']:
                cpc_display = f"🟢${cpc:.2f}"
            elif cpc <= BENCHMARKS['cpc']['median']:
                cpc_display = f"🟡${cpc:.2f}"
            else:
                cpc_display = f"🔴${cpc:.2f}"

            print(f"{name:<30} {ctr_display:>12} {cpc_display:>12} {conversions:>6} {cpl_display:>10} {spend_display:>10} {health:>7}% {status}")

            campaign_metrics.append({
                'id': camp_id,
                'name': campaign['name'],
                'budget': budget,
                'analytics': analytics,
                'health': health,
                'status': status
            })
        else:
            print(f"{name:<30} {'N/A':>12} {'N/A':>12} {'0':>6} {'N/A':>10} {'$0':>10} {'0':>7}% 🔴 No data")

    # Program-level summary
    print("-" * 120)
    overall_ctr = (total_clicks / total_impressions) if total_impressions > 0 else 0
    overall_cpc = (total_spend / total_clicks) if total_clicks > 0 else 0
    overall_cpl = (total_spend / total_conversions) if total_conversions > 0 else 0

    print(f"{'PROGRAM TOTALS':<30} {overall_ctr*100:>7.2f}% ${overall_cpc:>9.2f} {total_conversions:>6} ${overall_cpl:>9.0f} ${total_spend:>9.0f}")
    print(f"{'BENCHMARKS (Median)':<30} {'0.53%':>12} {'$6.43':>12} {'':>6} {'$112':>10}")
    print(f"{'BENCHMARKS (Top Quartile)':<30} {'0.70%':>12} {'$5.00':>12} {'':>6} {'$90':>10}")
    print()

    # === SECTION 2: CREATIVE HEALTH ===
    print("=" * 120)
    print("2. CREATIVE HEALTH & FATIGUE ANALYSIS")
    print("=" * 120)
    print()

    creative_issues = []

    print(f"{'Campaign':<30} {'Creatives':>10} {'Serving':>8} {'Avg Age':>10} {'Status'}")
    print("-" * 120)

    for campaign in sorted(active_abm, key=lambda c: c.get('name', '')):
        camp_id = campaign['id']
        name = campaign['name'][:28]

        # Get creatives
        url = f"{client.base_url}/adAccounts/{client.account_id}/creatives"
        params = {
            'q': 'criteria',
            'campaigns': f'urn:li:sponsoredCampaign:{camp_id}'
        }

        response = requests.get(url, headers=client._headers(), params=params)

        creative_count = 0
        serving_count = 0
        creative_ages = []

        if response.status_code == 200:
            creatives = response.json().get('elements', [])
            creative_count = len(creatives)
            serving_count = len([c for c in creatives if c.get('isServing', False)])

            # Calculate creative ages (approximate)
            for creative in creatives:
                created_time = creative.get('createdAt', 0)
                if created_time:
                    created_date = datetime.fromtimestamp(created_time / 1000)
                    age_days = (datetime.now() - created_date).days
                    creative_ages.append(age_days)

        avg_age = sum(creative_ages) / len(creative_ages) if creative_ages else 0

        # Determine status
        status = '✅ Good'
        if creative_count == 0:
            status = '🔴 URGENT - No creatives'
            creative_issues.append({
                'name': campaign['name'],
                'issue': 'No creatives',
                'priority': 'P0',
                'action': 'Add creatives immediately'
            })
        elif serving_count == 0:
            status = '🔴 URGENT - Not serving'
            creative_issues.append({
                'name': campaign['name'],
                'issue': 'Creatives not serving',
                'priority': 'P0',
                'action': 'Check creative approval status'
            })
        elif avg_age > 21:
            status = '🔴 URGENT - Ad fatigue'
            creative_issues.append({
                'name': campaign['name'],
                'issue': f'Creatives {avg_age:.0f} days old',
                'priority': 'P0',
                'action': 'Pause and refresh creatives NOW'
            })
        elif avg_age > 14:
            status = '🟡 Refresh needed'
            creative_issues.append({
                'name': campaign['name'],
                'issue': f'Creatives {avg_age:.0f} days old',
                'priority': 'P1',
                'action': 'Schedule creative refresh within 7 days'
            })
        elif creative_count < 2:
            status = '🟡 Low diversity'
            creative_issues.append({
                'name': campaign['name'],
                'issue': 'Only 1 creative',
                'priority': 'P2',
                'action': 'Add 2-3 more creative variants for A/B testing'
            })

        print(f"{name:<30} {creative_count:>10} {serving_count:>8} {avg_age:>9.0f}d {status}")

    print()

    # === SECTION 3: TARGETING QUALITY ===
    print("=" * 120)
    print("3. TARGETING QUALITY ANALYSIS")
    print("=" * 120)
    print()

    targeting_issues = []

    print(f"{'Campaign':<30} {'Strategy':>20} {'Logic':>15} {'Skills':>8} {'Status'}")
    print("-" * 120)

    for campaign in sorted(active_abm, key=lambda c: c.get('name', '')):
        name = campaign['name'][:28]

        # Analyze targeting logic
        logic_analysis = analyze_targeting_logic(campaign)
        skills_analysis = check_critical_skills(campaign)

        # Determine strategy
        if logic_analysis['has_skills'] and not logic_analysis['has_titles']:
            strategy = "Skills-only ✅"
        elif logic_analysis['has_titles'] and not logic_analysis['has_skills']:
            strategy = "Titles-only ⚠️"
        elif logic_analysis['same_group']:
            strategy = "Hybrid (same group) ✅"
        elif logic_analysis['has_restrictive_and_logic']:
            strategy = "Titles AND Skills 🔴"
        else:
            strategy = "Unknown"

        # Determine logic
        logic = "Inclusive OR ✅" if not logic_analysis['has_restrictive_and_logic'] else "Restrictive AND 🔴"

        # Skills count
        skill_count = skills_analysis['skill_count']

        # Overall status
        status = '🟢 Good'
        if logic_analysis['has_restrictive_and_logic']:
            status = '🔴 Fix AND logic'
            targeting_issues.append({
                'name': campaign['name'],
                'issue': 'Restrictive AND logic (titles AND skills separate)',
                'priority': 'P0',
                'action': f'./linkedin copy-targeting --source 447062324 --target {campaign["id"]}',
                'expected_impact': '2-3× more clicks, 30-40% lower CPC'
            })
        elif skill_count < 10:
            status = '🟡 Few skills'
            targeting_issues.append({
                'name': campaign['name'],
                'issue': f'Only {skill_count} skills (recommend 20-35)',
                'priority': 'P2',
                'action': f'./linkedin recommend-skills --campaign-id {campaign["id"]}',
                'expected_impact': '20-40% larger audience'
            })
        elif not skills_analysis['has_critical_skills']:
            status = '🟡 Missing key skills'

        print(f"{name:<30} {strategy:>20} {logic:>15} {skill_count:>8} {status}")

    print()

    # === SECTION 4: BUDGET EFFICIENCY ===
    print("=" * 120)
    print("4. BUDGET EFFICIENCY & WASTED SPEND")
    print("=" * 120)
    print()

    budget_issues = []
    wasted_daily = 0

    print(f"{'Campaign':<30} {'Daily Budget':>12} {'30d Spend':>12} {'Conversions':>12} {'CPA':>10} {'Status'}")
    print("-" * 120)

    for metric in campaign_metrics:
        campaign = next((c for c in active_abm if c['id'] == metric['id']), None)
        if not campaign:
            continue

        name = metric['name'][:28]
        budget = metric['budget']
        analytics = metric['analytics']

        spend_30d = analytics['cost']
        conversions = analytics['conversions']
        cpa = analytics['cpl'] if analytics['cpl'] else 0

        # Determine budget status
        status = '🟢 Efficient'

        if budget < 15:
            status = '🟡 Underfunded'
            budget_issues.append({
                'name': metric['name'],
                'issue': f'Budget too low (${budget:.0f}/day < $15 minimum)',
                'priority': 'P2',
                'action': f'Increase to $25-50/day or consolidate with another campaign'
            })

        if spend_30d > 200 and conversions == 0:
            status = '🔴 PAUSE - No conversions'
            wasted_daily += budget
            budget_issues.append({
                'name': metric['name'],
                'issue': f'Zero conversions after ${spend_30d:.0f} spend',
                'priority': 'P0',
                'action': f'./linkedin update-status {metric["id"]} --status PAUSED',
                'expected_savings': f'${budget:.0f}/day = ${budget * 30:.0f}/month'
            })

        if analytics['cpc'] > 40:
            status = '🔴 PAUSE - High CPC'
            wasted_daily += budget
            budget_issues.append({
                'name': metric['name'],
                'issue': f'CPC ${analytics["cpc"]:.2f} >> $15 benchmark',
                'priority': 'P0',
                'action': f'./linkedin update-status {metric["id"]} --status PAUSED',
                'expected_savings': f'${budget:.0f}/day = ${budget * 30:.0f}/month'
            })

        if budget > 100:
            status = '🟡 High spend'
            budget_issues.append({
                'name': metric['name'],
                'issue': f'Budget ${budget:.0f}/day > $100 (diminishing returns)',
                'priority': 'P3',
                'action': 'Consider splitting into 2 campaigns or reducing to $75/day'
            })

        print(f"{name:<30} ${budget:>11.0f} ${spend_30d:>11.0f} {conversions:>12} ${cpa:>9.0f} {status}")

    print("-" * 120)
    print(f"{'TOTALS':<30} ${total_budget:>11.0f} ${total_spend:>11.0f} {total_conversions:>12} ${overall_cpl:>9.0f}")
    print(f"{'WASTED (to pause)':<30} ${wasted_daily:>11.0f} ${wasted_daily * 30:>11.0f} {'':>12} {'':>10} 💰 ${wasted_daily * 365:.0f}/yr savings")
    print()

    # === SECTION 5: CRITICAL ISSUES SUMMARY ===
    print("=" * 120)
    print("5. CRITICAL ISSUES & ACTION ITEMS")
    print("=" * 120)
    print()

    all_issues = creative_issues + targeting_issues + budget_issues
    all_issues.sort(key=lambda x: x['priority'])

    if all_issues:
        # Group by priority
        p0_issues = [i for i in all_issues if i['priority'] == 'P0']
        p1_issues = [i for i in all_issues if i['priority'] == 'P1']
        p2_issues = [i for i in all_issues if i['priority'] == 'P2']

        if p0_issues:
            print("🔴 P0 - CRITICAL (Fix This Week)")
            print("-" * 120)
            for issue in p0_issues:
                print(f"\n❌ {issue['name']}")
                print(f"   Issue: {issue['issue']}")
                print(f"   Action: {issue['action']}")
                if 'expected_impact' in issue:
                    print(f"   Impact: {issue['expected_impact']}")
                if 'expected_savings' in issue:
                    print(f"   Savings: {issue['expected_savings']}")
            print()

        if p1_issues:
            print("🟡 P1 - HIGH PRIORITY (Fix Within 2-3 Weeks)")
            print("-" * 120)
            for issue in p1_issues:
                print(f"\n⚠️  {issue['name']}")
                print(f"   Issue: {issue['issue']}")
                print(f"   Action: {issue['action']}")
                if 'expected_impact' in issue:
                    print(f"   Impact: {issue['expected_impact']}")
            print()

        if p2_issues:
            print("📋 P2 - MEDIUM PRIORITY (Fix Within 4-6 Weeks)")
            print("-" * 120)
            for issue in p2_issues:
                print(f"\n• {issue['name']}")
                print(f"   Issue: {issue['issue']}")
                print(f"   Action: {issue['action']}")
            print()
    else:
        print("✅ No critical issues found! All campaigns are healthy.\n")

    # === SECTION 6: BENCHMARKS COMPARISON ===
    print("=" * 120)
    print("6. PROGRAM PERFORMANCE VS. 2025-2026 BENCHMARKS")
    print("=" * 120)
    print()

    print("Your Program vs. B2B SaaS Benchmarks:")
    print()
    print(f"Metric                      Your Value     Median       Top Quartile   Status")
    print("-" * 120)
    print(f"CTR                         {overall_ctr*100:>7.2f}%        0.50-0.56%   0.60-0.80%+    {format_status(overall_ctr*100, 0.53, 0.70)}")
    print(f"CPC                         ${overall_cpc:>7.2f}        $5.00-7.85   <$5.00         {format_status(overall_cpc, 6.43, 5.00, lower_is_better=True)}")
    print(f"CPL                         ${overall_cpl:>7.0f}         $75-150      <$90           {format_status(overall_cpl, 112.50, 90.00, lower_is_better=True)}")
    print()

    # === SECTION 7: QUICK WINS ===
    print("=" * 120)
    print("7. QUICK WINS - IMPLEMENT THESE FIRST")
    print("=" * 120)
    print()

    # Generate actionable commands
    quick_wins = []

    # Pause wasteful campaigns
    for issue in p0_issues:
        if 'update-status' in issue.get('action', ''):
            quick_wins.append({
                'action': 'Pause wasteful campaign',
                'command': issue['action'],
                'impact': issue.get('expected_savings', 'Stop waste'),
                'time': '5 seconds'
            })

    # Fix targeting issues
    for issue in p0_issues:
        if 'copy-targeting' in issue.get('action', ''):
            quick_wins.append({
                'action': 'Fix restrictive AND logic',
                'command': issue['action'],
                'impact': issue.get('expected_impact', '2-3× more clicks'),
                'time': '10 seconds'
            })

    # Creative refreshes
    for issue in p1_issues:
        if 'days old' in issue.get('issue', ''):
            quick_wins.append({
                'action': f'Refresh creatives for {issue["name"][:20]}',
                'command': 'Create new creatives in Campaign Manager',
                'impact': '30-50% CTR improvement',
                'time': '30 minutes'
            })

    if quick_wins:
        for i, win in enumerate(quick_wins[:5], 1):  # Top 5 quick wins
            print(f"{i}. {win['action']}")
            print(f"   Command: {win['command']}")
            print(f"   Impact: {win['impact']}")
            print(f"   Time: {win['time']}")
            print()
    else:
        print("✅ No quick wins needed - program is well-optimized!\n")

    # === SECTION 8: RECOMMENDATIONS ===
    print("=" * 120)
    print("8. STRATEGIC RECOMMENDATIONS")
    print("=" * 120)
    print()

    recommendations = []

    # Check budget distribution
    if total_budget > 0:
        awareness_budget = 0  # Would need to categorize campaigns
        consideration_budget = 0
        decision_budget = 0

        # For now, provide general recommendations
        print("📊 Budget Allocation:")
        print(f"   Current total: ${total_budget:.0f}/day (${total_budget * 30:.0f}/month)")
        print(f"   Recommended split:")
        print(f"     - Awareness (20-30%): ${total_budget * 0.25:.0f}/day")
        print(f"     - Consideration (40-50%): ${total_budget * 0.45:.0f}/day")
        print(f"     - Decision (20-30%): ${total_budget * 0.25:.0f}/day")
        print()

    # Check for missing elements
    print("🎯 Strategic Gaps:")

    # CAPI check (would need additional verification)
    print("   - Implement CAPI for 20% lower CPA (if not already done)")

    # Thought leader ads check
    print("   - Launch Thought Leader Ads for 1.7× CTR, 40% lower CPL")

    # Video check
    print("   - Expand video content (target 28% of impressions for 5× engagement)")

    # Retargeting check
    print("   - Verify retargeting infrastructure (website visitors, pricing page, video viewers)")
    print()

    # === SECTION 9: OVERALL HEALTH SCORE ===
    print("=" * 120)
    print("9. OVERALL PROGRAM HEALTH")
    print("=" * 120)
    print()

    # Calculate aggregate health score
    total_health = sum(m['health'] for m in campaign_metrics) / len(campaign_metrics) if campaign_metrics else 0

    health_status = "🔴 Poor"
    if total_health >= 90:
        health_status = "🟢 Excellent - Top Quartile"
    elif total_health >= 75:
        health_status = "🟢 Good - Solid Program"
    elif total_health >= 60:
        health_status = "🟡 Fair - Improvement Needed"

    print(f"Program Health Score: {total_health:.0f}/100 - {health_status}")
    print()

    if total_health < 75:
        print("Improvement Priorities:")
        if overall_ctr < BENCHMARKS['ctr']['median']:
            print("  1. Improve CTR (refresh creatives, better hooks)")
        if overall_cpc > BENCHMARKS['cpc']['median']:
            print("  2. Reduce CPC (fix targeting, improve Quality Score)")
        if overall_cpl > BENCHMARKS['cpl']['median']:
            print("  3. Lower CPL (optimize conversion funnel)")
        if len(p0_issues) > 0:
            print(f"  4. Fix {len(p0_issues)} critical issues (see above)")
    else:
        print("✅ Program is performing well! Focus on scaling proven winners.")

    print()
    print("=" * 120)
    print(f"Audit complete. Next audit: {(datetime.now() + timedelta(days=30)).strftime('%B %d, %Y')}")
    print("For detailed framework, see: AUDIT_FRAMEWORK.md")
    print("=" * 120)

    return 0

if __name__ == '__main__':
    exit(main())
