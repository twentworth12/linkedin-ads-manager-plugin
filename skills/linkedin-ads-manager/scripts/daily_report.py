#!/usr/bin/env python3
"""
LinkedIn Daily Campaign Performance Report

Generates a fast (<30 sec) daily overview with:
- Yesterday's snapshot vs 7-day average
- MTD pacing and EOM projection
- Top campaigns by spend
- Alert detection (creative fatigue, targeting issues, budget pacing)

Uses a single account-level adAnalytics API call (not per-campaign).
"""

import sys
import os
import argparse
import requests
from datetime import datetime, timedelta, date
import calendar

# Add script directory to path for linkedin_api import
sys.path.insert(0, os.path.dirname(__file__))
from linkedin_api import LinkedInAdsClient


# Benchmarks from BEST_PRACTICES_B2B_SAAS.md
BENCHMARKS = {
    'ctr': 0.50,       # 0.50% CTR target
    'cpc': 8.00,       # $5-8 CPC range, flag above $8
    'cpc_critical': 15.00,  # Critical CPC threshold
    'cpl': 150.00,     # $75-150 CPL range
}


def fetch_analytics(client, start_date, end_date):
    """Fetch account-level analytics with DAILY granularity, pivoted by CAMPAIGN.

    Single API call returns all campaigns at once.
    """
    account_urn = f'urn%3Ali%3AsponsoredAccount%3A{client.account_id}'

    url = (
        f"{client.base_url}/adAnalytics?q=analytics"
        f"&pivot=CAMPAIGN"
        f"&timeGranularity=DAILY"
        f"&dateRange=(start:(year:{start_date.year},month:{start_date.month},day:{start_date.day}),"
        f"end:(year:{end_date.year},month:{end_date.month},day:{end_date.day}))"
        f"&accounts=List({account_urn})"
        f"&fields=impressions,clicks,costInUsd,externalWebsiteConversions,pivotValues,dateRange"
    )

    response = requests.get(url, headers=client._headers())

    if response.status_code != 200:
        raise Exception(f"Analytics query failed: {response.status_code} - {response.text}")

    return response.json().get('elements', [])


def fetch_campaigns(client):
    """Get all campaigns for name lookup and budget info."""
    campaigns = client.search_campaigns(paginate_all=True)
    camp_map = {}
    for c in campaigns:
        cid = str(c['id'])
        daily_budget = 0
        if 'dailyBudget' in c:
            daily_budget = float(c['dailyBudget'].get('amount', 0))
        camp_map[cid] = {
            'name': c.get('name', f'Campaign {cid}'),
            'status': c.get('status', 'UNKNOWN'),
            'daily_budget': daily_budget,
            'type': c.get('type', 'UNKNOWN'),
        }
    return camp_map


def parse_date_from_element(elem):
    """Extract date from analytics element."""
    dr = elem.get('dateRange', {}).get('start', {})
    if dr:
        return date(dr['year'], dr['month'], dr['day'])
    return None


def build_daily_data(elements, camp_map):
    """Organize raw API elements into per-campaign, per-day dicts.

    Returns:
        daily: {campaign_id: {date: {spend, impressions, clicks, conversions}}}
    """
    daily = {}

    for elem in elements:
        camp_urn = (elem.get('pivotValues') or [''])[0]
        camp_id = camp_urn.split(':')[-1] if camp_urn else None
        if not camp_id:
            continue

        d = parse_date_from_element(elem)
        if not d:
            continue

        if camp_id not in daily:
            daily[camp_id] = {}

        daily[camp_id][d] = {
            'spend': float(elem.get('costInUsd', 0)),
            'impressions': elem.get('impressions', 0),
            'clicks': elem.get('clicks', 0),
            'conversions': elem.get('externalWebsiteConversions', 0),
        }

    return daily


def calc_metrics(data):
    """Calculate derived metrics from raw data dict."""
    spend = data.get('spend', 0)
    impressions = data.get('impressions', 0)
    clicks = data.get('clicks', 0)
    conversions = data.get('conversions', 0)

    ctr = (clicks / impressions * 100) if impressions > 0 else 0
    cpc = (spend / clicks) if clicks > 0 else 0
    cpl = (spend / conversions) if conversions > 0 else 0

    return {
        'spend': spend,
        'impressions': impressions,
        'clicks': clicks,
        'conversions': conversions,
        'ctr': ctr,
        'cpc': cpc,
        'cpl': cpl,
    }


def sum_day_data(daily_data, target_date):
    """Sum metrics across all campaigns for a single date."""
    totals = {'spend': 0, 'impressions': 0, 'clicks': 0, 'conversions': 0}
    for camp_id, dates in daily_data.items():
        if target_date in dates:
            for k in totals:
                totals[k] += dates[target_date].get(k, 0)
    return totals


def sum_date_range(daily_data, start, end):
    """Sum metrics across all campaigns for a date range (inclusive)."""
    totals = {'spend': 0, 'impressions': 0, 'clicks': 0, 'conversions': 0}
    d = start
    while d <= end:
        day_totals = sum_day_data(daily_data, d)
        for k in totals:
            totals[k] += day_totals[k]
        d += timedelta(days=1)
    return totals


def avg_date_range(daily_data, start, end):
    """Average daily metrics across a date range."""
    totals = sum_date_range(daily_data, start, end)
    num_days = (end - start).days + 1
    if num_days <= 0:
        return totals
    return {k: v / num_days for k, v in totals.items()}


def campaign_sum_date_range(camp_dates, start, end):
    """Sum a single campaign's metrics over a date range."""
    totals = {'spend': 0, 'impressions': 0, 'clicks': 0, 'conversions': 0}
    d = start
    while d <= end:
        if d in camp_dates:
            for k in totals:
                totals[k] += camp_dates[d].get(k, 0)
        d += timedelta(days=1)
    return totals


def campaign_avg_date_range(camp_dates, start, end):
    """Average a single campaign's daily metrics over a date range."""
    totals = campaign_sum_date_range(camp_dates, start, end)
    num_days = (end - start).days + 1
    if num_days <= 0:
        return totals
    return {k: v / num_days for k, v in totals.items()}


def delta_str(current, previous):
    """Format a delta as +X% or -X%."""
    if previous == 0:
        if current == 0:
            return '—'
        return '+∞'
    pct = (current - previous) / previous * 100
    sign = '+' if pct >= 0 else ''
    return f'{sign}{pct:.0f}%'


def benchmark_indicator(value, benchmark, higher_is_better=True):
    """Return indicator vs benchmark."""
    if value == 0:
        return '—'
    if higher_is_better:
        if value >= benchmark:
            return '✅'
        elif value >= benchmark * 0.8:
            return '⚠️'
        else:
            return '❌'
    else:
        if value <= benchmark:
            return '✅'
        elif value <= benchmark * 1.2:
            return '⚠️'
        else:
            return '❌'


def detect_alerts(daily_data, camp_map, report_date):
    """Detect issues needing attention.

    Returns list of {campaign, issue, detail, severity, action}
    """
    alerts = []
    seven_end = report_date - timedelta(days=1)
    seven_start = report_date - timedelta(days=7)
    mtd_start = report_date.replace(day=1)

    for camp_id, camp_dates in daily_data.items():
        info = camp_map.get(camp_id, {})
        name = info.get('name', camp_id)
        status = info.get('status', '')

        if status != 'ACTIVE':
            continue

        # Yesterday's metrics for this campaign
        yesterday = report_date
        yday_data = camp_dates.get(yesterday, {})
        yday_metrics = calc_metrics(yday_data)

        # 7-day average
        avg_data = campaign_avg_date_range(camp_dates, seven_start, seven_end)
        avg_metrics = calc_metrics(avg_data)

        # MTD totals
        mtd_data = campaign_sum_date_range(camp_dates, mtd_start, report_date)
        mtd_metrics = calc_metrics(mtd_data)

        # Alert: CTR drop >20% vs 7-day avg (creative fatigue)
        if avg_metrics['ctr'] > 0 and yday_metrics['ctr'] > 0:
            ctr_change = (yday_metrics['ctr'] - avg_metrics['ctr']) / avg_metrics['ctr']
            if ctr_change < -0.20:
                alerts.append({
                    'campaign': name,
                    'issue': 'Creative fatigue',
                    'detail': f"CTR {yday_metrics['ctr']:.2f}% vs 7d avg {avg_metrics['ctr']:.2f}% ({ctr_change*100:.0f}%)",
                    'severity': 'P1',
                    'action': 'Refresh creatives (14-day cycle recommended)',
                })

        # Alert: CPC >$15 or >2x 7-day avg (targeting issue)
        if yday_metrics['cpc'] > BENCHMARKS['cpc_critical']:
            alerts.append({
                'campaign': name,
                'issue': 'CPC critical',
                'detail': f"CPC ${yday_metrics['cpc']:.2f} exceeds ${BENCHMARKS['cpc_critical']:.0f} threshold",
                'severity': 'P0',
                'action': 'Review targeting — audience may be too narrow or competitive',
            })
        elif avg_metrics['cpc'] > 0 and yday_metrics['cpc'] > avg_metrics['cpc'] * 2:
            alerts.append({
                'campaign': name,
                'issue': 'CPC spike',
                'detail': f"CPC ${yday_metrics['cpc']:.2f} is 2x+ the 7d avg ${avg_metrics['cpc']:.2f}",
                'severity': 'P1',
                'action': 'Check for audience saturation or bid competition',
            })

        # Alert: Zero conversions with >$200 MTD spend
        if mtd_metrics['conversions'] == 0 and mtd_metrics['spend'] > 200:
            alerts.append({
                'campaign': name,
                'issue': 'No conversions',
                'detail': f"${mtd_metrics['spend']:.0f} MTD spend, 0 conversions",
                'severity': 'P0',
                'action': 'Review landing page, conversion tracking, or pause campaign',
            })

        # Alert: Budget pacing
        daily_budget = info.get('daily_budget', 0)
        if daily_budget > 0 and yday_metrics['spend'] > 0:
            pacing = yday_metrics['spend'] / daily_budget * 100
            if pacing < 80:
                alerts.append({
                    'campaign': name,
                    'issue': 'Underpacing',
                    'detail': f"Spent ${yday_metrics['spend']:.2f} of ${daily_budget:.0f} budget ({pacing:.0f}%)",
                    'severity': 'P2',
                    'action': 'Check if audience is too small or bid is too low',
                })
            elif pacing > 120:
                alerts.append({
                    'campaign': name,
                    'issue': 'Overpacing',
                    'detail': f"Spent ${yday_metrics['spend']:.2f} of ${daily_budget:.0f} budget ({pacing:.0f}%)",
                    'severity': 'P2',
                    'action': 'Review daily budget cap — may need increase or bid adjustment',
                })

    # Sort by severity
    severity_order = {'P0': 0, 'P1': 1, 'P2': 2}
    alerts.sort(key=lambda a: severity_order.get(a['severity'], 9))

    return alerts


def generate_report(daily_data, camp_map, report_date, month_budget=None):
    """Generate markdown report."""
    lines = []

    # Header
    lines.append(f'# LinkedIn Campaign Daily Report — {report_date.strftime("%A, %B %d, %Y")}')
    lines.append('')

    # Date ranges
    seven_end = report_date - timedelta(days=1)
    seven_start = report_date - timedelta(days=7)
    mtd_start = report_date.replace(day=1)
    days_in_month = calendar.monthrange(report_date.year, report_date.month)[1]
    days_elapsed = (report_date - mtd_start).days + 1

    # --- Section 1: Yesterday's Snapshot ---
    lines.append('## Yesterday\'s Snapshot')
    lines.append('')

    yday_totals = sum_day_data(daily_data, report_date)
    yday = calc_metrics(yday_totals)

    avg_totals = avg_date_range(daily_data, seven_start, seven_end)
    avg7 = calc_metrics(avg_totals)

    lines.append('| Metric | Yesterday | 7d Avg | Delta | Benchmark |')
    lines.append('|--------|-----------|--------|-------|-----------|')

    lines.append(f'| Spend | ${yday["spend"]:,.2f} | ${avg7["spend"]:,.2f} | {delta_str(yday["spend"], avg7["spend"])} | — |')
    lines.append(f'| Impressions | {yday["impressions"]:,} | {avg7["impressions"]:,.0f} | {delta_str(yday["impressions"], avg7["impressions"])} | — |')
    lines.append(f'| Clicks | {yday["clicks"]:,} | {avg7["clicks"]:,.0f} | {delta_str(yday["clicks"], avg7["clicks"])} | — |')
    lines.append(f'| Conversions | {yday["conversions"]:,} | {avg7["conversions"]:,.0f} | {delta_str(yday["conversions"], avg7["conversions"])} | — |')
    lines.append(f'| CTR | {yday["ctr"]:.2f}% | {avg7["ctr"]:.2f}% | {delta_str(yday["ctr"], avg7["ctr"])} | {benchmark_indicator(yday["ctr"], BENCHMARKS["ctr"])} {BENCHMARKS["ctr"]:.2f}% |')
    lines.append(f'| CPC | ${yday["cpc"]:.2f} | ${avg7["cpc"]:.2f} | {delta_str(yday["cpc"], avg7["cpc"])} | {benchmark_indicator(yday["cpc"], BENCHMARKS["cpc"], higher_is_better=False)} <${BENCHMARKS["cpc"]:.0f} |')

    if yday['conversions'] > 0 or avg7['conversions'] > 0:
        lines.append(f'| CPL | ${yday["cpl"]:.2f} | ${avg7["cpl"]:.2f} | {delta_str(yday["cpl"], avg7["cpl"])} | {benchmark_indicator(yday["cpl"], BENCHMARKS["cpl"], higher_is_better=False)} <${BENCHMARKS["cpl"]:.0f} |')

    lines.append('')

    # --- Section 2: MTD Pacing ---
    lines.append('## MTD Pacing')
    lines.append('')

    mtd_totals = sum_date_range(daily_data, mtd_start, report_date)
    mtd = calc_metrics(mtd_totals)

    # Calculate monthly budget from active campaign daily budgets if not provided
    if month_budget is None:
        total_daily = sum(
            info['daily_budget']
            for info in camp_map.values()
            if info.get('status') == 'ACTIVE' and info.get('daily_budget', 0) > 0
        )
        month_budget = total_daily * days_in_month

    projected_eom = (mtd['spend'] / days_elapsed * days_in_month) if days_elapsed > 0 else 0
    pacing_pct = (mtd['spend'] / month_budget * 100) if month_budget > 0 else 0
    expected_pacing = (days_elapsed / days_in_month * 100)
    on_track = '✅ On track' if abs(pacing_pct - expected_pacing) < 15 else ('⚠️ Underpacing' if pacing_pct < expected_pacing else '⚠️ Overpacing')

    lines.append(f'| Metric | Value |')
    lines.append(f'|--------|-------|')
    lines.append(f'| MTD Spend | ${mtd["spend"]:,.2f} |')
    lines.append(f'| Monthly Budget | ${month_budget:,.0f} |')
    lines.append(f'| Days Elapsed | {days_elapsed} / {days_in_month} |')
    lines.append(f'| Budget Used | {pacing_pct:.1f}% (expected: {expected_pacing:.1f}%) |')
    lines.append(f'| Projected EOM | ${projected_eom:,.0f} |')
    lines.append(f'| Status | {on_track} |')
    lines.append('')

    mtd_avg_daily = mtd['spend'] / days_elapsed if days_elapsed > 0 else 0
    lines.append(f'MTD averages: ${mtd_avg_daily:,.0f}/day spend, {mtd["clicks"]/days_elapsed:.0f} clicks/day, {mtd["conversions"]/days_elapsed:.1f} conversions/day')
    lines.append('')

    # --- Section 3: Top 5 Campaigns by Spend ---
    lines.append('## Top 5 Campaigns by Yesterday\'s Spend')
    lines.append('')

    # Calculate per-campaign yesterday spend
    camp_yesterday = []
    for camp_id, camp_dates in daily_data.items():
        info = camp_map.get(camp_id, {})
        if info.get('status') != 'ACTIVE':
            continue

        yday_data = camp_dates.get(report_date, {})
        if not yday_data or yday_data.get('spend', 0) == 0:
            continue

        yday_m = calc_metrics(yday_data)

        # 7d avg for trend
        avg_data = campaign_avg_date_range(camp_dates, seven_start, seven_end)
        avg_m = calc_metrics(avg_data)

        spend_trend = delta_str(yday_m['spend'], avg_m['spend'])

        camp_yesterday.append({
            'id': camp_id,
            'name': info.get('name', camp_id),
            'spend': yday_m['spend'],
            'clicks': yday_m['clicks'],
            'conversions': yday_m['conversions'],
            'ctr': yday_m['ctr'],
            'cpc': yday_m['cpc'],
            'trend': spend_trend,
        })

    camp_yesterday.sort(key=lambda x: x['spend'], reverse=True)

    lines.append('| Campaign | Spend | Clicks | Conv | CTR | CPC | vs 7d |')
    lines.append('|----------|-------|--------|------|-----|-----|-------|')

    for c in camp_yesterday[:5]:
        name_short = c['name'][:35]
        lines.append(
            f'| {name_short} | ${c["spend"]:.2f} | {c["clicks"]} | {c["conversions"]} '
            f'| {c["ctr"]:.2f}% | ${c["cpc"]:.2f} | {c["trend"]} |'
        )

    if len(camp_yesterday) > 5:
        remaining_spend = sum(c['spend'] for c in camp_yesterday[5:])
        lines.append(f'| *({len(camp_yesterday)-5} more campaigns)* | *${remaining_spend:.2f}* | | | | | |')

    lines.append('')

    # --- Section 4: Alerts ---
    alerts = detect_alerts(daily_data, camp_map, report_date)

    lines.append('## Attention Needed')
    lines.append('')

    if not alerts:
        lines.append('No issues detected. All campaigns performing within thresholds.')
    else:
        lines.append(f'{len(alerts)} issue(s) detected:')
        lines.append('')

        for a in alerts:
            severity_icon = {'P0': '🔴', 'P1': '🟡', 'P2': '🔵'}.get(a['severity'], '⚪')
            lines.append(f'**{severity_icon} {a["severity"]} — {a["campaign"]}**: {a["issue"]}')
            lines.append(f'  - {a["detail"]}')
            lines.append(f'  - Action: {a["action"]}')
            lines.append('')

    # --- Section 5: Recommendations ---
    lines.append('## Recommendations')
    lines.append('')

    recs = []

    p0_alerts = [a for a in alerts if a['severity'] == 'P0']
    p1_alerts = [a for a in alerts if a['severity'] == 'P1']

    if p0_alerts:
        for a in p0_alerts:
            recs.append(f'1. **[P0]** {a["campaign"]}: {a["action"]}')

    if p1_alerts:
        for a in p1_alerts:
            recs.append(f'1. **[P1]** {a["campaign"]}: {a["action"]}')

    # General recommendations based on aggregate metrics
    if yday['ctr'] < BENCHMARKS['ctr'] * 0.8 and yday['impressions'] > 100:
        recs.append(f'1. **[Aggregate]** Overall CTR ({yday["ctr"]:.2f}%) is below benchmark ({BENCHMARKS["ctr"]:.2f}%). Consider refreshing creatives across campaigns.')

    if yday['cpc'] > BENCHMARKS['cpc'] and yday['clicks'] > 0:
        recs.append(f'1. **[Aggregate]** Overall CPC (${yday["cpc"]:.2f}) exceeds ${BENCHMARKS["cpc"]:.0f} target. Review audience overlap and bid strategy.')

    if not recs:
        recs.append('No immediate actions needed. Performance is within acceptable ranges.')

    lines.extend(recs)
    lines.append('')

    # Footer
    lines.append('---')
    active_count = sum(1 for c in camp_map.values() if c.get('status') == 'ACTIVE')
    lines.append(f'*Generated {datetime.now().strftime("%Y-%m-%d %H:%M")} | {active_count} active campaigns | Account {report_date.strftime("%B %Y")}*')

    return '\n'.join(lines)


def main(report_date_str=None, month_budget=None):
    """Main entry point.

    Args:
        report_date_str: Date string YYYY-MM-DD (default: yesterday)
        month_budget: Monthly budget override (default: auto-calculate from daily budgets)
    """
    # Determine report date
    if report_date_str:
        report_date = datetime.strptime(report_date_str, '%Y-%m-%d').date()
    else:
        report_date = date.today() - timedelta(days=1)

    print(f'Generating daily report for {report_date}...', file=sys.stderr)

    # Initialize client
    client = LinkedInAdsClient()

    # Determine data range: 1st of month or 30 days ago, whichever is earlier
    mtd_start = report_date.replace(day=1)
    thirty_ago = report_date - timedelta(days=30)
    fetch_start = min(mtd_start, thirty_ago)

    # Need data through report_date (inclusive), API end is exclusive so +1
    fetch_end = report_date + timedelta(days=1)

    print(f'Fetching analytics {fetch_start} to {report_date}...', file=sys.stderr)

    # Single API call for all data
    elements = fetch_analytics(client, fetch_start, fetch_end)
    print(f'  → {len(elements)} data points returned', file=sys.stderr)

    # Get campaign metadata
    print('Fetching campaign metadata...', file=sys.stderr)
    camp_map = fetch_campaigns(client)
    print(f'  → {len(camp_map)} campaigns found', file=sys.stderr)

    # Build daily data structure
    daily_data = build_daily_data(elements, camp_map)

    # Generate report
    report = generate_report(daily_data, camp_map, report_date, month_budget)

    # Output to stdout
    print(report)

    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='LinkedIn Daily Campaign Performance Report')
    parser.add_argument('--date', help='Report date YYYY-MM-DD (default: yesterday)')
    parser.add_argument('--month-budget', type=float, help='Monthly budget override (default: auto from daily budgets)')

    args = parser.parse_args()
    sys.exit(main(args.date, args.month_budget))
