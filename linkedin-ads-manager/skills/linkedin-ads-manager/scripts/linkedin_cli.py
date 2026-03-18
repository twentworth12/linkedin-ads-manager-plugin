#!/usr/bin/env python3
"""
LinkedIn Ads Manager CLI
Usage: ./linkedin [command] [options]

Campaign Management:
  list              List campaigns with filters
  get               Get campaign details
  clone             Clone campaign (with optional creatives)
  update-status     Update campaign status (pause/activate)
  update-budget     Update campaign budget
  pause-all         Pause all active campaigns (with state file for resume)
  resume-all        Resume previously paused campaigns from state file

Targeting:
  analyze           Analyze campaign targeting
  update-targeting  Update targeting (company, titles, skills)
  copy-targeting    Copy targeting between campaigns
  recommend-skills  Get recommended SRE/DevOps skills

Search:
  find-org          Search for organization by name
  find-skill        Search for skills
  find-title        Search for job titles

Analytics:
  performance       Get campaign performance metrics
  daily             Daily performance report (yesterday snapshot, MTD pacing, alerts)
  audit             Audit ABM campaigns and recommend which to pause
  campaign-group    Get all campaigns in a campaign group (breakdown by type)
"""

import argparse
import json
import sys
from linkedin_api import LinkedInAdsClient, add_project_dir_arg, load_env

class LinkedInCLI:
    def __init__(self):
        self.client = LinkedInAdsClient()

    def list_campaigns(self, args):
        """List campaigns with optional filters"""
        print(f"Fetching campaigns from account {self.client.account_id}...\n")

        campaigns = self.client.search_campaigns(
            name_contains=args.name,
            status=args.status.split(',') if args.status else None
        )

        print(f"✓ Found {len(campaigns)} campaigns\n")

        for i, campaign in enumerate(campaigns[:args.limit], 1):
            camp_id = campaign['id']
            if isinstance(camp_id, int):
                camp_id = str(camp_id)

            print(f"{i}. {campaign['name']}")
            print(f"   ID: {camp_id}")
            print(f"   Status: {campaign['status']}")
            print(f"   Type: {campaign['type']}")

            if 'dailyBudget' in campaign:
                print(f"   Budget: ${campaign['dailyBudget']['amount']}/day")
            elif 'totalBudget' in campaign:
                print(f"   Budget: ${campaign['totalBudget']['amount']} total")

            print()

        if len(campaigns) > args.limit:
            print(f"... and {len(campaigns) - args.limit} more campaigns")

    def get_campaign(self, args):
        """Get detailed campaign information"""
        campaign = self.client.get_campaign(args.campaign_id)

        print(f"Campaign: {campaign['name']}")
        print(f"ID: {campaign['id']}")
        print(f"Status: {campaign['status']}")
        print(f"Type: {campaign['type']}")

        if 'dailyBudget' in campaign:
            print(f"Daily Budget: ${campaign['dailyBudget']['amount']}")
        if 'totalBudget' in campaign:
            print(f"Total Budget: ${campaign['totalBudget']['amount']}")

        print(f"\nTargeting:")
        targeting = campaign.get('targetingCriteria', {})

        if args.json:
            print(json.dumps(targeting, indent=2))
        else:
            self._print_targeting_summary(targeting)

    def clone_campaign(self, args):
        """Clone a campaign"""
        print(f"Cloning campaign {args.source}...\n")

        # Search for source
        if args.source.isdigit():
            source = self.client.get_campaign(args.source)
        else:
            campaigns = self.client.search_campaigns(name_contains=args.source)
            if not campaigns:
                print(f"❌ Campaign not found: {args.source}")
                return 1
            if len(campaigns) > 1:
                print(f"❌ Multiple campaigns found. Please use campaign ID instead.")
                for c in campaigns:
                    print(f"  {c['id']}: {c['name']}")
                return 1
            source = campaigns[0]

        print(f"✓ Source: {source['name']} (ID: {source['id']})")

        # Clone
        modifications = {}
        if args.budget:
            modifications['dailyBudget'] = {
                'amount': str(args.budget),
                'currencyCode': 'USD'
            }
        if args.status:
            modifications['status'] = args.status

        result = self.client.clone_campaign(
            source_campaign_id=source['id'],
            new_name=args.name,
            modifications=modifications
        )

        campaign_id = result.get('id', 'created')
        if isinstance(campaign_id, int):
            campaign_id = str(campaign_id)

        print(f"\n✅ Campaign cloned!")
        print(f"  Name: {args.name}")
        print(f"  ID: {campaign_id}")

        # Clone creatives if requested
        if args.clone_creatives:
            print(f"\nCloning creatives...")
            self._clone_campaign_creatives(source['id'], campaign_id)

        print(f"\n🔗 View: https://www.linkedin.com/campaignmanager/accounts/{self.client.account_id}/campaigns/{campaign_id}")

    def _clone_campaign_creatives(self, source_id, target_id):
        """Clone all creatives from source to target campaign"""
        import requests

        # Get source creatives
        url = f"{self.client.base_url}/adAccounts/{self.client.account_id}/creatives?q=criteria&campaigns=List(urn%3Ali%3AsponsoredCampaign%3A{source_id})"
        headers = self.client._headers()
        headers['X-RestLi-Method'] = 'FINDER'

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"  ❌ Failed to get creatives: {response.status_code}")
            return

        creatives = response.json().get('elements', [])
        print(f"  Found {len(creatives)} creatives to clone")

        # Clone each creative
        for creative in creatives:
            create_url = f"{self.client.base_url}/adAccounts/{self.client.account_id}/creatives"

            payload = {
                'campaign': f'urn:li:sponsoredCampaign:{target_id}',
                'content': creative['content'],
                'intendedStatus': 'DRAFT',
                'name': creative.get('name', '').replace(str(source_id), str(target_id))
            }

            create_response = requests.post(create_url, headers=self.client._headers(), json=payload)

            if create_response.status_code in [200, 201]:
                print(f"  ✓ Cloned: {creative.get('name')}")
            else:
                print(f"  ❌ Failed to clone creative: {create_response.status_code}")

    def analyze_targeting(self, args):
        """Analyze campaign targeting"""
        # Support both campaign ID and name
        if args.campaign_id.isdigit():
            campaign = self.client.get_campaign(args.campaign_id)
        else:
            # Search by name
            campaigns = self.client.search_campaigns(name_contains=args.campaign_id)
            if not campaigns:
                print(f"❌ No campaign found matching '{args.campaign_id}'")
                print(f"\nTip: Use './linkedin list' to see all campaigns")
                return
            if len(campaigns) > 1:
                print(f"⚠️  Found {len(campaigns)} campaigns matching '{args.campaign_id}':")
                for i, c in enumerate(campaigns[:5], 1):
                    print(f"  {i}. {c['name']} (ID: {c['id']})")
                print(f"\nPlease use campaign ID to specify which one:")
                print(f"  ./linkedin analyze {campaigns[0]['id']}")
                return
            campaign = campaigns[0]

        print(f"Campaign: {campaign['name']}")
        print(f"ID: {campaign['id']}")
        print(f"Status: {campaign['status']}\n")

        targeting = campaign.get('targetingCriteria', {})
        self._analyze_targeting_detail(targeting, args.recommend)

    def _analyze_targeting_detail(self, targeting, show_recommendations=False):
        """Detailed targeting analysis"""
        include = targeting.get('include', {}).get('and', [])

        # Extract what's being targeted
        titles = []
        skills = []
        employers = []
        seniorities = []
        functions = []

        for facet_group in include:
            for facet_urn, values in facet_group.get('or', {}).items():
                facet_name = facet_urn.split(':')[-1]

                if facet_name == 'titles':
                    titles = [int(urn.split(':')[-1]) for urn in values]
                elif facet_name == 'skills':
                    skills = [int(urn.split(':')[-1]) for urn in values]
                elif facet_name == 'employers':
                    employers = values
                elif facet_name == 'seniorities':
                    seniorities = values
                elif facet_name == 'jobFunctions':
                    functions = values

        # Print summary
        print("Targeting Summary:")
        print("=" * 80)

        if titles:
            print(f"✓ {len(titles)} Job Titles")
            decoded = self._decode_titles(titles[:10])
            for tid, name in decoded.items():
                print(f"  {tid:6} | {name}")
            if len(titles) > 10:
                print(f"  ... and {len(titles) - 10} more titles")

        if skills:
            print(f"\n✓ {len(skills)} Skills")
            decoded_skills = self._decode_skills(skills[:10])
            for sid, name in decoded_skills.items():
                print(f"  {sid:6} | {name}")
            if len(skills) > 10:
                print(f"  ... and {len(skills) - 10} more skills")

        if seniorities:
            print(f"\n✓ {len(seniorities)} Seniority Levels")
            for seniority in seniorities:
                print(f"  {seniority}")

        if functions:
            print(f"\n✓ {len(functions)} Job Functions")
            for function in functions:
                print(f"  {function}")

        if employers:
            print(f"\n✓ {len(employers)} Companies")
            for employer in employers:
                print(f"  {employer}")

        # Recommendations
        if show_recommendations:
            self._print_targeting_recommendations(titles, skills)

    def _decode_titles(self, title_ids):
        """Decode title IDs to names"""
        searches = [
            "Site Reliability Engineer", "DevOps Engineer", "Platform Engineer",
            "Infrastructure Engineer", "Cloud Engineer", "Engineering Manager",
            "Director of Engineering", "VP Engineering", "CTO"
        ]

        decoded = {}
        for search in searches:
            results = self._search_title(search)
            for result in results:
                if result['id'] in title_ids and result['id'] not in decoded:
                    decoded[result['id']] = result['name']

        return decoded

    def _decode_skills(self, skill_ids):
        """Decode skill IDs to names"""
        searches = [
            "DevOps", "Site Reliability", "Incident Management", "PagerDuty",
            "Kubernetes", "Docker", "AWS", "Terraform", "Monitoring",
            "Grafana", "Datadog", "Splunk", "Incident Response"
        ]

        decoded = {}
        for search in searches:
            results = self._search_skill(search)
            for result in results:
                if result['id'] in skill_ids and result['id'] not in decoded:
                    decoded[result['id']] = result['name']

        return decoded

    def _search_title(self, query):
        """Search for job titles"""
        import requests

        url = f"{self.client.base_url}/adTargetingEntities?q=typeahead&facet=urn%3Ali%3AadTargetingFacet%3Atitles&query={query.replace(' ', '%20')}&queryVersion=QUERY_USES_URNS"
        response = requests.get(url, headers=self.client._headers())

        if response.status_code != 200:
            return []

        results = []
        for elem in response.json().get('elements', []):
            urn = elem.get('urn', '')
            title_id = int(urn.split(':')[-1]) if ':' in urn else None
            if title_id:
                results.append({'id': title_id, 'name': elem.get('name', '')})

        return results

    def _search_skill(self, query):
        """Search for skills"""
        import requests

        url = f"{self.client.base_url}/adTargetingEntities?q=typeahead&facet=urn%3Ali%3AadTargetingFacet%3Askills&query={query.replace(' ', '%20')}&queryVersion=QUERY_USES_URNS"
        response = requests.get(url, headers=self.client._headers())

        if response.status_code != 200:
            return []

        results = []
        for elem in response.json().get('elements', []):
            urn = elem.get('urn', '')
            skill_id = int(urn.split(':')[-1]) if ':' in urn else None
            if skill_id:
                results.append({'id': skill_id, 'name': elem.get('name', '')})

        return results

    def _print_targeting_summary(self, targeting):
        """Print human-readable targeting summary"""
        include = targeting.get('include', {}).get('and', [])

        for facet_group in include:
            for facet_urn, values in facet_group.get('or', {}).items():
                facet_name = facet_urn.split(':')[-1]
                print(f"  {facet_name}: {len(values)} values")

    def _print_targeting_recommendations(self, current_titles, current_skills):
        """Print targeting recommendations"""
        critical_titles = {
            25764: "DevOps Engineer",
            6483: "Platform Engineer",
            30006: "Cloud Engineer",
            2922: "Infrastructure Engineer",
            2083: "Reliability Engineer",
            22848: "Site Reliability Engineer",
            25890: "Senior Site Reliability Engineer"
        }

        critical_skills = {
            1952: "Incident Management",
            18442: "DevOps",
            55383: "Site Reliability Engineering",
            55983: "PagerDuty",
            4008: "Incident Response"
        }

        missing_titles = {tid: name for tid, name in critical_titles.items() if tid not in current_titles}
        missing_skills = {sid: name for sid, name in critical_skills.items() if sid not in current_skills}

        if missing_titles or missing_skills:
            print("\n" + "=" * 80)
            print("RECOMMENDATIONS")
            print("=" * 80)

        if missing_titles:
            print(f"\n❌ Missing Critical Titles:")
            for tid, name in sorted(missing_titles.items(), key=lambda x: x[1]):
                print(f"  {tid:6} | {name}")

        if missing_skills:
            print(f"\n❌ Missing Critical Skills:")
            for sid, name in sorted(missing_skills.items(), key=lambda x: x[1]):
                print(f"  {sid:6} | {name}")

    def update_targeting(self, args):
        """Update campaign targeting"""
        print(f"Updating campaign {args.campaign_id}...\n")

        # Get current campaign
        campaign = self.client.get_campaign(args.campaign_id)
        targeting = campaign.get('targetingCriteria', {})

        changes_made = []

        # Find and update based on args
        if args.add_organization:
            result = self._add_organization(targeting, args.add_organization, args.org_name)
            if result:
                changes_made.append(f"Company: {result}")

        if args.add_titles:
            added = self._add_titles(targeting, args.add_titles)
            if added:
                changes_made.append(f"Titles: {len(added)} added")

        if args.add_skills:
            added = self._add_skills(targeting, args.add_skills)
            if added:
                changes_made.append(f"Skills: {len(added)} added")

        if not changes_made:
            print("⚠️  No changes to make")
            return 0

        # Update campaign
        print(f"\nApplying changes to campaign...")
        try:
            result = self.client.update_campaign(args.campaign_id, updates={'targetingCriteria': targeting})

            print(f"\n✅ Targeting updated successfully!")
            print(f"Changes made:")
            for change in changes_made:
                print(f"  • {change}")

            # Verify update
            updated_campaign = self.client.get_campaign(args.campaign_id)
            print(f"\n✓ Verified campaign updated")

        except Exception as e:
            print(f"\n❌ Update failed: {e}")
            return 1

    def _add_organization(self, targeting, org_urn, org_name=None):
        """Add or replace organization in targeting

        Returns: organization name if changed
        """
        include_and = targeting.get('include', {}).get('and', [])

        if not org_urn.startswith('urn:li:organization:'):
            org_urn = f'urn:li:organization:{org_urn}'

        # Find employers facet
        for facet in include_and:
            if 'urn:li:adTargetingFacet:employers' in facet.get('or', {}):
                old_orgs = facet['or']['urn:li:adTargetingFacet:employers']

                if org_urn in old_orgs:
                    print(f"  Already targeting: {org_urn}")
                    return None

                print(f"  Changing from: {old_orgs[0]}")
                print(f"  Changing to: {org_urn}")
                if org_name:
                    print(f"  Name: {org_name}")

                facet['or']['urn:li:adTargetingFacet:employers'] = [org_urn]
                return org_name or org_urn

        # If no employers facet exists, create one
        print("  Creating employer targeting")
        include_and.append({
            'or': {
                'urn:li:adTargetingFacet:employers': [org_urn]
            }
        })
        return org_name or org_urn

    def _add_titles(self, targeting, title_ids):
        """Add job titles to targeting

        Returns: list of title IDs that were added
        """
        include_and = targeting.setdefault('include', {}).setdefault('and', [])

        added = []

        # Find titles facet
        for facet in include_and:
            if 'urn:li:adTargetingFacet:titles' in facet.get('or', {}):
                current = facet['or']['urn:li:adTargetingFacet:titles']
                current_ids = [urn.split(':')[-1] for urn in current]

                # Add new titles
                for tid in title_ids.split(','):
                    tid = tid.strip()
                    if tid not in current_ids:
                        current.append(f'urn:li:title:{tid}')
                        print(f"  ✓ Added title: {tid}")
                        added.append(tid)
                    else:
                        print(f"  - Already has title: {tid}")

                return added

        # Create titles facet
        print("  Creating new title targeting")
        title_urns = [f'urn:li:title:{tid.strip()}' for tid in title_ids.split(',')]
        include_and.append({
            'or': {
                'urn:li:adTargetingFacet:titles': title_urns
            }
        })
        added = [tid.strip() for tid in title_ids.split(',')]
        return added

    def _add_skills(self, targeting, skill_ids):
        """Add skills to targeting

        Returns: list of skill IDs that were added
        """
        include_and = targeting.setdefault('include', {}).setdefault('and', [])

        added = []

        # Find skills facet
        for facet in include_and:
            if 'urn:li:adTargetingFacet:skills' in facet.get('or', {}):
                current = facet['or']['urn:li:adTargetingFacet:skills']
                current_ids = [urn.split(':')[-1] for urn in current]

                # Add new skills
                for sid in skill_ids.split(','):
                    sid = sid.strip()
                    if sid not in current_ids:
                        current.append(f'urn:li:skill:{sid}')
                        print(f"  ✓ Added skill: {sid}")
                        added.append(sid)
                    else:
                        print(f"  - Already has skill: {sid}")

                print(f"\nTotal: {len(added)} skills added, {len(skill_ids.split(',')) - len(added)} already present")
                return added

        # Create skills facet
        print("  Creating new skills targeting")
        skill_urns = [f'urn:li:skill:{sid.strip()}' for sid in skill_ids.split(',')]
        include_and.append({
            'or': {
                'urn:li:adTargetingFacet:skills': skill_urns
            }
        })
        added = [sid.strip() for sid in skill_ids.split(',')]
        print(f"Created skills facet with {len(added)} skills")
        return added

    def copy_targeting(self, args):
        """Copy targeting from one campaign to another"""
        print(f"Copying targeting from {args.source} to {args.target}...\n")

        source = self.client.get_campaign(args.source)
        target = self.client.get_campaign(args.target)

        source_targeting = source.get('targetingCriteria', {})

        print(f"Source: {source['name']}")
        print(f"Target: {target['name']}\n")

        # Update target campaign
        updates = {'targetingCriteria': source_targeting}
        result = self.client.update_campaign(args.target, updates)

        print(f"✅ Targeting copied successfully!")
        self._print_targeting_summary(source_targeting)

    def update_status(self, args):
        """Update campaign status (pause/activate)"""
        campaign = self.client.get_campaign(args.campaign_id)

        print(f"Campaign: {campaign['name']}")
        print(f"Current status: {campaign['status']}")
        print(f"New status: {args.status}\n")

        updates = {'status': args.status}
        result = self.client.update_campaign(args.campaign_id, updates)

        print(f"✅ Campaign status updated to {args.status}!")

    def pause_all(self, args):
        """Pause all active campaigns and save state for resume"""
        import os
        from datetime import datetime

        print(f"Fetching ACTIVE campaigns from account {self.client.account_id}...\n")

        campaigns = self.client.search_campaigns(
            name_contains=args.name if hasattr(args, 'name') and args.name else None,
            status=['ACTIVE']
        )

        if not campaigns:
            print("No active campaigns found.")
            return 0

        # Calculate total daily budget
        total_daily = 0
        for c in campaigns:
            if 'dailyBudget' in c:
                total_daily += float(c['dailyBudget'].get('amount', 0))

        print(f"Found {len(campaigns)} active campaign(s) (${total_daily:.0f}/day total):\n")
        for c in campaigns:
            budget = f"${float(c['dailyBudget']['amount']):.0f}/day" if 'dailyBudget' in c else "no budget"
            print(f"  • {c['name']} (ID: {c['id']}) — {budget}")

        if args.dry_run:
            print(f"\n🔍 DRY RUN — no changes made. Would pause {len(campaigns)} campaigns.")
            return 0

        # Save state file before pausing
        state_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.pause_state.json')
        state = {
            'paused_at': datetime.now().isoformat(),
            'campaigns': [{'id': str(c['id']), 'name': c['name']} for c in campaigns]
        }
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)

        # Pause each campaign
        print()
        failed = []
        for c in campaigns:
            try:
                self.client.update_campaign(c['id'], {'status': 'PAUSED'})
                print(f"  ✅ Paused {c['name']}")
            except Exception as e:
                print(f"  ❌ Failed to pause {c['name']}: {e}")
                failed.append(c['name'])

        paused_count = len(campaigns) - len(failed)
        print(f"\n✅ Paused {paused_count}/{len(campaigns)} campaigns (${total_daily:.0f}/day saved)")
        print(f"State saved to {state_file} — use 'resume-all' to reactivate.")

        if failed:
            print(f"\n⚠️  Failed to pause: {', '.join(failed)}")
            return 1

        return 0

    def resume_all(self, args):
        """Resume previously paused campaigns from state file"""
        import os

        state_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.pause_state.json')

        if not os.path.exists(state_file):
            print("❌ No .pause_state.json found. Nothing to resume.")
            print("   (State file is created by 'pause-all' command)")
            return 1

        with open(state_file, 'r') as f:
            state = json.load(f)

        campaigns = state.get('campaigns', [])
        paused_at = state.get('paused_at', 'unknown')

        if not campaigns:
            print("State file exists but contains no campaigns.")
            os.remove(state_file)
            return 0

        print(f"Found {len(campaigns)} campaign(s) paused at {paused_at}:\n")
        for c in campaigns:
            print(f"  • {c['name']} (ID: {c['id']})")

        if args.dry_run:
            print(f"\n🔍 DRY RUN — no changes made. Would resume {len(campaigns)} campaigns.")
            return 0

        # Resume each campaign
        print()
        failed = []
        for c in campaigns:
            try:
                self.client.update_campaign(c['id'], {'status': 'ACTIVE'})
                print(f"  ✅ Resumed {c['name']}")
            except Exception as e:
                print(f"  ❌ Failed to resume {c['name']}: {e}")
                failed.append(c['name'])

        resumed_count = len(campaigns) - len(failed)
        print(f"\n✅ Resumed {resumed_count}/{len(campaigns)} campaigns")

        if failed:
            print(f"\n⚠️  Failed to resume: {', '.join(failed)}")
            print("State file preserved — fix issues and retry.")
            return 1

        # Clean up state file on full success
        os.remove(state_file)
        print("State file cleaned up.")
        return 0

    def update_budget(self, args):
        """Update campaign budget"""
        campaign = self.client.get_campaign(args.campaign_id)

        print(f"Campaign: {campaign['name']}")

        if 'dailyBudget' in campaign:
            print(f"Current daily budget: ${campaign['dailyBudget']['amount']}")

        print(f"New daily budget: ${args.budget}\n")

        updates = {
            'dailyBudget': {
                'amount': str(args.budget),
                'currencyCode': 'USD'
            }
        }

        result = self.client.update_campaign(args.campaign_id, updates)

        print(f"✅ Budget updated to ${args.budget}/day!")

    def performance(self, args):
        """Get campaign performance analytics"""
        import requests
        from datetime import datetime, timedelta

        # Default to last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=args.days)

        # Get campaigns to analyze
        if args.campaign_id:
            campaign_ids = [args.campaign_id]
        elif args.name:
            campaigns = self.client.search_campaigns(name_contains=args.name)
            campaign_ids = [c['id'] for c in campaigns]
        else:
            print("❌ Must provide --campaign-id or --name")
            return 1

        # Build campaign URNs for API
        campaign_urns = ','.join([f'urn%3Ali%3AsponsoredCampaign%3A{cid}' for cid in campaign_ids])

        # Query analytics
        url = f"{self.client.base_url}/adAnalytics?q=analytics&pivot=CAMPAIGN&timeGranularity=ALL&dateRange=(start:(year:{start_date.year},month:{start_date.month},day:{start_date.day}),end:(year:{end_date.year},month:{end_date.month},day:{end_date.day}))&campaigns=List({campaign_urns})&fields=impressions,clicks,costInUsd,externalWebsiteConversions,landingPageClicks,pivotValues"

        response = requests.get(url, headers=self.client._headers())

        if response.status_code != 200:
            print(f"❌ Analytics query failed: {response.status_code}")
            print(response.text)
            return 1

        data = response.json()

        print(f"Campaign Performance (Last {args.days} days)")
        print("=" * 90)
        print(f"{'Campaign ID':<15} {'Spend':>10} {'Impr':>8} {'Clicks':>7} {'CTR':>6} {'Conv':>5} {'CPC':>8}")
        print("-" * 90)

        total_spend = 0
        total_clicks = 0
        total_impr = 0
        total_conv = 0

        for elem in data.get('elements', []):
            camp_urn = elem.get('pivotValues', [''])[0]
            camp_id = camp_urn.split(':')[-1] if camp_urn else 'Unknown'

            impressions = elem.get('impressions', 0)
            clicks = elem.get('clicks', 0)
            spend = float(elem.get('costInUsd', 0))
            conversions = elem.get('externalWebsiteConversions', 0)

            ctr = (clicks / impressions * 100) if impressions > 0 else 0
            cpc = (spend / clicks) if clicks > 0 else 0

            print(f"{camp_id:<15} ${spend:>9.2f} {impressions:>8,} {clicks:>7} {ctr:>5.2f}% {conversions:>5} ${cpc:>7.2f}")

            total_spend += spend
            total_clicks += clicks
            total_impr += impressions
            total_conv += conversions

        if len(data.get('elements', [])) > 1:
            avg_ctr = (total_clicks / total_impr * 100) if total_impr > 0 else 0
            avg_cpc = (total_spend / total_clicks) if total_clicks > 0 else 0
            print("-" * 90)
            print(f"{'TOTAL':<15} ${total_spend:>9.2f} {total_impr:>8,} {total_clicks:>7} {avg_ctr:>5.2f}% {total_conv:>5} ${avg_cpc:>7.2f}")

    def campaign_group(self, args):
        """Get campaigns in a campaign group with optional performance"""
        print(f"Fetching campaigns in group {args.group_id}...\n")

        # Get all campaigns
        all_campaigns = self.client.search_campaigns(paginate_all=True)

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

                type_total_budget = 0
                active_count = 0

                for c in campaigns:
                    camp_id = str(c['id'])
                    budget = 0
                    budget_str = ''

                    if 'dailyBudget' in c:
                        budget = float(c['dailyBudget']['amount']) if c['dailyBudget']['amount'] else 0
                        budget_str = f"${budget}/day"
                        if c['status'] == 'ACTIVE':
                            type_total_budget += budget
                            active_count += 1
                    elif 'totalBudget' in c:
                        budget_str = f"${c['totalBudget']['amount']} total"

                    print(f"  {c['name'][:65]}")
                    print(f"    ID: {camp_id} | Status: {c['status']} | Budget: {budget_str}")

                if active_count > 0:
                    print(f"\n  → Active daily budget for {camp_type}: ${type_total_budget}/day ({active_count} campaigns)")
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

    def audit(self, args):
        """Audit ABM campaigns and recommend which to pause"""
        import requests

        print("Fetching all ABM campaigns...\n")
        all_campaigns = self.client.search_campaigns()

        abm_campaigns = [c for c in all_campaigns if 'abm' in c.get('name', '').lower()]
        active_abm = [c for c in abm_campaigns if c.get('status') == 'ACTIVE']

        print(f"Found {len(active_abm)} ACTIVE ABM campaigns\n")

        # Get performance for all active campaigns
        from datetime import datetime, timedelta

        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        campaign_urns = ','.join([f'urn%3Ali%3AsponsoredCampaign%3A{c["id"]}' for c in active_abm])

        url = f"{self.client.base_url}/adAnalytics?q=analytics&pivot=CAMPAIGN&timeGranularity=ALL&dateRange=(start:(year:{start_date.year},month:{start_date.month},day:{start_date.day}),end:(year:{end_date.year},month:{end_date.month},day:{end_date.day}))&campaigns=List({campaign_urns})&fields=impressions,clicks,costInUsd,externalWebsiteConversions,pivotValues"

        response = requests.get(url, headers=self.client._headers())

        if response.status_code != 200:
            print(f"❌ Analytics failed: {response.status_code}")
            return 1

        data = response.json()

        # Build campaign name map
        camp_map = {str(c['id']): c['name'] for c in active_abm}

        print("ABM CAMPAIGN AUDIT (Last 30 Days)")
        print("=" * 100)
        print(f"{'Campaign':<30} {'Spend':>10} {'Clicks':>7} {'Conv':>5} {'CPC':>8} {'Status'}")
        print("-" * 100)

        results = []

        for elem in data.get('elements', []):
            camp_urn = elem.get('pivotValues', [''])[0]
            camp_id = camp_urn.split(':')[-1]
            camp_name = camp_map.get(camp_id, f'Campaign {camp_id}')

            clicks = elem.get('clicks', 0)
            spend = float(elem.get('costInUsd', 0))
            conversions = elem.get('externalWebsiteConversions', 0)
            cpc = (spend / clicks) if clicks > 0 else 0

            if clicks == 0 and spend > 10:
                status = '❌ PAUSE'
            elif cpc > 40:
                status = '❌ HIGH CPC'
            elif conversions >= 5:
                status = '✅ GOOD'
            elif conversions > 0:
                status = '📊 OK'
            else:
                status = '⚠️  REVIEW'

            results.append({
                'id': camp_id,
                'name': camp_name,
                'spend': spend,
                'clicks': clicks,
                'conversions': conversions,
                'cpc': cpc,
                'status': status
            })

        results.sort(key=lambda x: x['spend'], reverse=True)

        for r in results:
            print(f"{r['name']:<30} ${r['spend']:>9.2f} {r['clicks']:>7} {r['conversions']:>5} ${r['cpc']:>7.2f} {r['status']}")

        # Recommendations
        pause_list = [r for r in results if '❌' in r['status']]

        if pause_list:
            print(f"\n💡 RECOMMENDATIONS:")
            print(f"\n❌ Pause these {len(pause_list)} campaigns:")
            for r in pause_list:
                print(f"  ./linkedin update-status {r['id']} --status PAUSED  # {r['name']}")

            wasted = sum(r['spend'] for r in pause_list)
            print(f"\n💰 Potential savings: ${wasted:.2f}/month")
        else:
            print(f"\n✅ All campaigns performing acceptably - keep running!")

    def audit_v2(self, args):
        """Run comprehensive audit based on 2025-2026 best practices"""
        import subprocess
        import os

        script_path = os.path.join(
            os.path.dirname(__file__),
            'audit_campaigns_v2.py'
        )

        # Run the enhanced audit script
        result = subprocess.run(['python3', script_path], capture_output=False)
        return result.returncode

    def daily(self, args):
        """Run daily performance report"""
        import daily_report
        return daily_report.main(args.date, args.month_budget)

    def find_organization(self, args):
        """Search for organization"""
        import requests

        print(f"Searching for: {args.name}\n")

        url = f"{self.client.base_url}/adTargetingEntities?q=typeahead&facet=urn%3Ali%3AadTargetingFacet%3Aemployers&query={args.name.replace(' ', '%20')}&queryVersion=QUERY_USES_URNS"

        response = requests.get(url, headers=self.client._headers())

        if response.status_code != 200:
            print(f"❌ Search failed: {response.status_code}")
            return 1

        results = response.json().get('elements', [])

        if not results:
            print(f"❌ No organizations found")
            return 1

        print(f"✓ Found {len(results)} organizations:\n")

        for i, org in enumerate(results, 1):
            urn = org.get('urn', '')
            name = org.get('name', '')
            org_id = urn.split(':')[-1] if ':' in urn else ''

            print(f"{i}. {name}")
            print(f"   URN: {urn}")
            print(f"   ID: {org_id}")
            print()

    def find_skill(self, args):
        """Search for skills"""
        import requests

        print(f"Searching for skill: {args.name}\n")

        url = f"{self.client.base_url}/adTargetingEntities?q=typeahead&facet=urn%3Ali%3AadTargetingFacet%3Askills&query={args.name.replace(' ', '%20')}&queryVersion=QUERY_USES_URNS"

        response = requests.get(url, headers=self.client._headers())

        if response.status_code != 200:
            print(f"❌ Search failed: {response.status_code}")
            return 1

        results = response.json().get('elements', [])

        if not results:
            print(f"❌ No skills found")
            return 1

        print(f"✓ Found {len(results)} skills:\n")

        for i, skill in enumerate(results[:args.limit], 1):
            urn = skill.get('urn', '')
            name = skill.get('name', '')
            skill_id = urn.split(':')[-1] if ':' in urn else ''

            print(f"{i}. {name}")
            print(f"   URN: {urn}")
            print(f"   ID: {skill_id}")
            print()

        if len(results) > args.limit:
            print(f"... and {len(results) - args.limit} more results")

    def find_title(self, args):
        """Search for job titles"""
        import requests

        print(f"Searching for title: {args.name}\n")

        url = f"{self.client.base_url}/adTargetingEntities?q=typeahead&facet=urn%3Ali%3AadTargetingFacet%3Atitles&query={args.name.replace(' ', '%20')}&queryVersion=QUERY_USES_URNS"

        response = requests.get(url, headers=self.client._headers())

        if response.status_code != 200:
            print(f"❌ Search failed: {response.status_code}")
            return 1

        results = response.json().get('elements', [])

        if not results:
            print(f"❌ No titles found")
            return 1

        print(f"✓ Found {len(results)} titles:\n")

        for i, title in enumerate(results[:args.limit], 1):
            urn = title.get('urn', '')
            name = title.get('name', '')
            title_id = urn.split(':')[-1] if ':' in urn else ''

            print(f"{i}. {name}")
            print(f"   URN: {urn}")
            print(f"   ID: {title_id}")
            print()

        if len(results) > args.limit:
            print(f"... and {len(results) - args.limit} more results")

    def recommend_skills(self, args):
        """Recommend skills for SRE/DevOps targeting"""
        import requests

        print("Searching for recommended SRE/DevOps skills...\n")

        # Critical skill categories
        searches = {
            'Container/Orchestration': ['Kubernetes', 'Docker'],
            'Cloud Platforms': ['Amazon Web Services', 'Google Cloud Platform', 'Microsoft Azure'],
            'Infrastructure as Code': ['Terraform', 'Ansible'],
            'CI/CD': ['CI/CD', 'Jenkins', 'GitLab'],
            'Monitoring': ['Prometheus', 'New Relic'],
            'Incident Tools': ['PagerDuty', 'Opsgenie', 'xMatters', 'ServiceNow']
        }

        recommendations = {}

        for category, terms in searches.items():
            category_skills = {}

            for term in terms:
                url = f"{self.client.base_url}/adTargetingEntities?q=typeahead&facet=urn%3Ali%3AadTargetingFacet%3Askills&query={term.replace(' ', '%20')}&queryVersion=QUERY_USES_URNS"

                response = requests.get(url, headers=self.client._headers())

                if response.status_code == 200:
                    for elem in response.json().get('elements', [])[:3]:
                        urn = elem.get('urn', '')
                        name = elem.get('name', '')
                        skill_id = int(urn.split(':')[-1]) if ':' in urn else None

                        if skill_id and skill_id not in category_skills:
                            category_skills[skill_id] = name

            if category_skills:
                recommendations[category] = category_skills

        # Print recommendations
        print("RECOMMENDED SKILLS FOR SRE/DEVOPS TARGETING")
        print("=" * 80)

        priority_ids = []

        for category, skills in recommendations.items():
            print(f"\n{category}:")
            for skill_id, name in sorted(skills.items(), key=lambda x: x[1]):
                priority = "⭐⭐⭐" if skill_id in [55158, 1500290, 10798, 55396] else "⭐⭐" if skill_id in [55175, 10475, 55002] else "⭐"
                print(f"  {skill_id:6} | {name} {priority}")

                # Build priority list
                if skill_id in [55158, 1500290, 10798, 55175, 10475, 55396, 55002, 55466, 55644, 55106]:
                    priority_ids.append(str(skill_id))

        # Generate command
        if priority_ids:
            print(f"\n\nTOP 10 PRIORITY SKILLS:")
            print("-" * 80)
            cmd = f'python3 linkedin_cli.py update-targeting CAMPAIGN_ID --add-skills "{",".join(priority_ids)}"'
            print(cmd)

        # If analyzing specific campaign, check what's missing
        if args.campaign_id:
            print(f"\n\nANALYZING CAMPAIGN {args.campaign_id}...")
            campaign = self.client.get_campaign(args.campaign_id)
            targeting = campaign.get('targetingCriteria', {})

            # Get current skills
            current_skills = []
            for facet_group in targeting.get('include', {}).get('and', []):
                if 'urn:li:adTargetingFacet:skills' in facet_group.get('or', {}):
                    skill_urns = facet_group['or']['urn:li:adTargetingFacet:skills']
                    current_skills = [int(urn.split(':')[-1]) for urn in skill_urns]
                    break

            # Find missing
            all_recommended = []
            for category_skills in recommendations.values():
                all_recommended.extend(category_skills.keys())

            missing = [sid for sid in all_recommended if sid not in current_skills]

            if missing:
                print(f"\n❌ MISSING FROM CAMPAIGN:")
                for sid in missing:
                    for category_skills in recommendations.values():
                        if sid in category_skills:
                            print(f"  {sid:6} | {category_skills[sid]}")
                            break

                missing_ids = ','.join([str(sid) for sid in missing])
                print(f"\n💡 ADD MISSING SKILLS:")
                print(f'python3 linkedin_cli.py update-targeting {args.campaign_id} --add-skills "{missing_ids}"')
            else:
                print(f"\n✓ Campaign already has all recommended skills!")


def main():
    parser = argparse.ArgumentParser(description='LinkedIn Ads Manager CLI')
    add_project_dir_arg(parser)
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # List command
    list_parser = subparsers.add_parser('list', help='List campaigns')
    list_parser.add_argument('--name', help='Filter by name (substring match)')
    list_parser.add_argument('--status', help='Filter by status (comma-separated: ACTIVE,PAUSED)')
    list_parser.add_argument('--limit', type=int, default=20, help='Max results to show')

    # Get command
    get_parser = subparsers.add_parser('get', help='Get campaign details')
    get_parser.add_argument('campaign_id', help='Campaign ID')
    get_parser.add_argument('--json', action='store_true', help='Output raw JSON')

    # Clone command
    clone_parser = subparsers.add_parser('clone', help='Clone campaign')
    clone_parser.add_argument('--source', required=True, help='Source campaign ID or name')
    clone_parser.add_argument('--name', required=True, help='New campaign name')
    clone_parser.add_argument('--budget', type=float, help='Override daily budget')
    clone_parser.add_argument('--status', default='DRAFT', help='Campaign status')
    clone_parser.add_argument('--clone-creatives', action='store_true', help='Also clone creatives')

    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze targeting')
    analyze_parser.add_argument('campaign_id', help='Campaign ID')
    analyze_parser.add_argument('--recommend', action='store_true', help='Show recommendations')

    # Update targeting command
    update_parser = subparsers.add_parser('update-targeting', help='Update campaign targeting')
    update_parser.add_argument('campaign_id', help='Campaign ID')
    update_parser.add_argument('--add-organization', help='Set organization (URN or ID)')
    update_parser.add_argument('--org-name', help='Organization name (for display)')
    update_parser.add_argument('--add-titles', help='Add job titles (comma-separated IDs)')
    update_parser.add_argument('--add-skills', help='Add skills (comma-separated IDs)')

    # Copy targeting command
    copy_parser = subparsers.add_parser('copy-targeting', help='Copy targeting between campaigns')
    copy_parser.add_argument('--source', required=True, help='Source campaign ID')
    copy_parser.add_argument('--target', required=True, help='Target campaign ID')

    # Find organization command
    find_parser = subparsers.add_parser('find-org', help='Search for organization')
    find_parser.add_argument('name', help='Organization name to search')

    # Find skill command
    skill_parser = subparsers.add_parser('find-skill', help='Search for skills')
    skill_parser.add_argument('name', help='Skill name to search')
    skill_parser.add_argument('--limit', type=int, default=10, help='Max results')

    # Find title command
    title_parser = subparsers.add_parser('find-title', help='Search for job titles')
    title_parser.add_argument('name', help='Job title to search')
    title_parser.add_argument('--limit', type=int, default=10, help='Max results')

    # Recommend skills command
    recommend_parser = subparsers.add_parser('recommend-skills', help='Get recommended SRE/DevOps skills')
    recommend_parser.add_argument('--campaign-id', help='Analyze specific campaign and show missing skills')

    # Update status command
    status_parser = subparsers.add_parser('update-status', help='Update campaign status (pause/activate)')
    status_parser.add_argument('campaign_id', help='Campaign ID')
    status_parser.add_argument('--status', required=True, choices=['ACTIVE', 'PAUSED', 'DRAFT'], help='New status')

    # Update budget command
    budget_parser = subparsers.add_parser('update-budget', help='Update campaign budget')
    budget_parser.add_argument('campaign_id', help='Campaign ID')
    budget_parser.add_argument('--budget', type=float, required=True, help='New daily budget (USD)')

    # Performance command
    perf_parser = subparsers.add_parser('performance', help='Get campaign performance analytics')
    perf_parser.add_argument('--campaign-id', help='Specific campaign ID')
    perf_parser.add_argument('--name', help='Search campaigns by name')
    perf_parser.add_argument('--days', type=int, default=30, help='Days of history (default: 30)')

    # Daily report command
    daily_parser = subparsers.add_parser('daily', help='Daily performance report (snapshot, MTD pacing, alerts)')
    daily_parser.add_argument('--date', help='Report date YYYY-MM-DD (default: yesterday)')
    daily_parser.add_argument('--month-budget', type=float, help='Monthly budget override (default: auto from daily budgets)')

    # Audit command
    audit_parser = subparsers.add_parser('audit', help='Audit ABM campaigns and recommend which to pause')

    # Audit V2 command (comprehensive best practices audit)
    audit_v2_parser = subparsers.add_parser('audit-v2', help='Comprehensive audit with benchmarks, creative health, targeting quality')

    # Pause all command
    pause_parser = subparsers.add_parser('pause-all', help='Pause all active campaigns (saves state for resume)')
    pause_parser.add_argument('--name', help='Filter by name (only pause matching campaigns)')
    pause_parser.add_argument('--dry-run', action='store_true', help='Preview without making changes')

    # Resume all command
    resume_parser = subparsers.add_parser('resume-all', help='Resume previously paused campaigns from state file')
    resume_parser.add_argument('--dry-run', action='store_true', help='Preview without making changes')

    # Campaign group command
    group_parser = subparsers.add_parser('campaign-group', help='Get campaigns in a campaign group')
    group_parser.add_argument('--group-id', required=True, help='Campaign group ID')
    group_parser.add_argument('--by-type', action='store_true', help='Group by ad type')
    group_parser.add_argument('--active-only', action='store_true', help='Show only active campaigns')
    group_parser.add_argument('--performance', action='store_true', help='Include performance metrics')

    args = parser.parse_args()
    load_env(args)

    if not args.command:
        parser.print_help()
        return 1

    # Run command
    cli = LinkedInCLI()

    commands = {
        'list': cli.list_campaigns,
        'get': cli.get_campaign,
        'clone': cli.clone_campaign,
        'analyze': cli.analyze_targeting,
        'update-targeting': cli.update_targeting,
        'update-status': cli.update_status,
        'update-budget': cli.update_budget,
        'copy-targeting': cli.copy_targeting,
        'find-org': cli.find_organization,
        'find-skill': cli.find_skill,
        'find-title': cli.find_title,
        'recommend-skills': cli.recommend_skills,
        'performance': cli.performance,
        'daily': cli.daily,
        'audit': cli.audit,
        'audit-v2': cli.audit_v2,
        'campaign-group': cli.campaign_group,
        'pause-all': cli.pause_all,
        'resume-all': cli.resume_all
    }

    try:
        return commands[args.command](args) or 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
