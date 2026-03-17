# LinkedIn Ads Audit Framework

**Comprehensive campaign health assessment based on 2025-2026 best practices**
**Last updated: February 4, 2026**

---

## Overview

This framework provides systematic campaign auditing beyond basic "are creatives serving?" checks. It evaluates performance against industry benchmarks, identifies strategic gaps, and provides actionable improvement recommendations based on proven B2B SaaS best practices.

**Audit Cadences:**
- **Weekly:** Performance spot-checks (15 minutes)
- **Monthly:** Full campaign health audit (60 minutes)
- **Quarterly:** Strategic program review (2-3 hours)

---

## 1. Performance Metrics Audit

### 1.1 Benchmark Comparison

**Compare your metrics against 2025-2026 B2B SaaS benchmarks:**

| Metric | Your Value | Benchmark (Median) | Top Quartile | Status |
|--------|-----------|-------------------|--------------|--------|
| **CTR** | _____% | 0.50-0.56% | 0.60-0.80%+ | 🔴/🟡/🟢 |
| **CPC** | $_____ | $5.00-$7.85 | <$5.00 | 🔴/🟡/🟢 |
| **CPM** | $_____ | $31-$38 | <$30 | 🔴/🟡/🟢 |
| **CPL (Lead Gen)** | $_____ | $75-$150 | <$90 | 🔴/🟡/🟢 |
| **CPL (Landing Page)** | $_____ | $100-$200 | <$125 | 🔴/🟡/🟢 |
| **Form Conv. Rate** | _____% | 6-10% | >10% | 🔴/🟡/🟢 |
| **Landing Page Conv.** | _____% | 3-5% | >6% | 🔴/🟡/🟢 |

**Status Indicators:**
- 🟢 **Green:** Top quartile performance (maintain current approach)
- 🟡 **Yellow:** Median range (opportunities for optimization)
- 🔴 **Red:** Below median (requires immediate attention)

### 1.2 Vertical-Specific Adjustments

**Adjust benchmarks based on your vertical:**

| Vertical | CTR Benchmark | CPC Benchmark | CPL Benchmark | Competition Level |
|----------|--------------|---------------|---------------|-------------------|
| **General SaaS** | 0.42% | $5-8 | $100-160 | Moderate |
| **HR-Tech** | 0.58% | $4-7 | $90-140 | Lower (favorable) |
| **FinTech** | 0.38% | $8-12 | ≥$180 | Highest (premium) |
| **DevOps/Infrastructure** | 0.45-0.52% | $6-10 | $110-170 | Moderate-High |

### 1.3 Performance Red Flags

**Immediate attention required if:**
- ❌ CTR < 0.40% (poor engagement, creative/targeting issues)
- ❌ CPC > $15 (inefficient targeting or low Quality Score)
- ❌ CPL > 2× your target (conversion funnel issues)
- ❌ Form conversion < 4% (poor offer or message-market mismatch)
- ❌ Zero conversions after $200+ spend (fundamental targeting problem)
- ❌ CPC increasing >20% week-over-week (ad fatigue or competition shift)

### 1.4 SQL Rate Analysis (Critical)

**Don't stop at lead volume - track quality:**

| Stage | Your Rate | Benchmark | Status |
|-------|-----------|-----------|--------|
| Lead → SQL | _____% | 15-25% | 🔴/🟡/🟢 |
| SQL → Opportunity | _____% | 30-40% | 🔴/🟡/🟢 |
| Opportunity → Close | _____% | 20-30% | 🔴/🟡/🟢 |
| **Blended Lead → Close** | _____% | 1-3% | 🔴/🟡/🟢 |

**If SQL rate is low (<15%):**
- Lead quality issue, not lead volume issue
- Check: Hyper-targeted creatives (persona filtering)
- Check: Lead Gen Form vs. Landing Page (LP filters better)
- Check: Offer alignment with buying stage
- Check: ICP targeting precision (too broad = low quality)

---

## 2. Creative Health Audit

### 2.1 Creative Age & Fatigue

**Track creative age and performance decay:**

| Creative ID | Launch Date | Days Live | Current CTR | Week 1 CTR | Decay % | Status |
|------------|-------------|-----------|-------------|------------|---------|--------|
| Creative A | 2026-01-21 | 14 days | 0.48% | 0.62% | -22.6% | 🟡 Refresh needed |
| Creative B | 2026-01-28 | 7 days | 0.65% | 0.65% | 0% | 🟢 Healthy |
| Creative C | 2025-12-15 | 51 days | 0.32% | 0.71% | -54.9% | 🔴 URGENT |

**Creative refresh protocol:**
- 🟢 **Days 1-7:** Monitor performance baseline
- 🟡 **Days 8-14:** Plan refresh, identify winning elements
- 🔴 **Days 15+:** Performance decay expected (30-50% CTR drop)
- ⚠️ **Days 21+:** Severe fatigue, pause immediately

**Action items:**
- Creatives 15+ days old → Schedule refresh within 7 days
- Creatives with >30% CTR decay → Pause and replace immediately
- Winning concepts (high CTR) → Refresh execution (new visual, same message)

### 2.2 Creative Diversity Check

**Minimum requirements per campaign:**

| Funnel Stage | Min Creatives | Format Mix | Current Count | Status |
|--------------|--------------|------------|---------------|--------|
| **Awareness** | 3-5 | 60% video, 40% image/carousel | _____ | 🔴/🟡/🟢 |
| **Consideration** | 4-6 | 50% carousel, 30% image, 20% video | _____ | 🔴/🟡/🟢 |
| **Decision** | 2-3 | 70% lead gen forms, 30% landing pages | _____ | 🔴/🟡/🟢 |

**Red flags:**
- ❌ Single creative only (no A/B testing, single point of failure)
- ❌ All static images (missing video engagement opportunity)
- ❌ No carousel format (missing storytelling capability)
- ❌ All same format (no format testing)

### 2.3 Creative Quality Checklist

**Evaluate each creative against best practices:**

**Hook Quality (First Line):**
- [ ] Calls out role, problem, or desired outcome
- [ ] Specific and concrete (not generic)
- [ ] Creates curiosity or urgency
- Example: "SRE teams drowning in noisy alerts?" ✅ vs. "Improve your DevOps" ❌

**Message Focus:**
- [ ] Focuses on pain + outcome (not features)
- [ ] Includes customer proof (specific numbers, names)
- [ ] Uses authentic language (not corporate jargon)
- Example: "Cut MTTR from 4 hours to 37 minutes" ✅ vs. "Automated workflows" ❌

**Visual Quality:**
- [ ] Native to LinkedIn (not repurposed banner ad)
- [ ] Product UI screenshot or founder/SME face
- [ ] Clear hierarchy and readable on mobile
- [ ] No stock photos (low trust)

**CTA Clarity:**
- [ ] Single clear CTA aligned to funnel stage
- [ ] Action verb (Grab, Download, Book, Start)
- [ ] Friction reduction (No credit card, 15-min setup)

**Persona Targeting:**
- [ ] Explicit persona callout in visual or text
- [ ] Role-specific value prop
- [ ] Filters wrong personas (self-qualifying)

---

## 3. Targeting Quality Audit

### 3.1 ICP Alignment Check

**Evaluate targeting precision against ICP:**

| Targeting Element | Current Setup | ICP Requirement | Alignment |
|------------------|---------------|-----------------|-----------|
| **Company Size** | _____ employees | _____ employees | 🔴/🟡/🟢 |
| **Industry** | _____ | _____ | 🔴/🟡/🟢 |
| **Geography** | _____ | _____ | 🔴/🟡/🟢 |
| **Job Functions** | _____ | _____ | 🔴/🟡/🟢 |
| **Seniority Levels** | _____ | _____ | 🔴/🟡/🟢 |
| **Skills** | _____ | _____ | 🔴/🟡/🟢 |

**Red flags:**
- ❌ Audience Expansion enabled (dilutes targeting)
- ❌ No exclusions set (wasting budget on wrong personas)
- ❌ Too broad company size (e.g., 1-10,000 employees)
- ❌ Generic job functions (e.g., "Business Development" for engineering tool)
- ❌ Title-only targeting (misses 60-80% of relevant audience)

### 3.2 AND/OR Logic Diagnosis

**Check for restrictive AND logic between title and skills:**

```bash
./linkedin analyze CAMPAIGN_ID
```

**Look for this red flag:**
```
⚠️ Titles and Skills are in DIFFERENT facet groups
Logic: (Title1 OR Title2) AND (Skill1 OR Skill2)
Effect: RESTRICTIVE - person needs BOTH
```

**Impact of restrictive AND logic:**
- Artificially narrows audience by 60-80%
- Misses VP Engineering without "DevOps" skill listed
- Misses Software Engineer with DevOps skill but "wrong" title
- Typical performance: 25-40% higher CPC, 50-70% lower volume

**Fix:** Use skills-based targeting (inclusive OR) like Chewy/Opsgenie_JT templates:
```bash
./linkedin copy-targeting --source 447062324 --target CAMPAIGN_ID
```

### 3.3 Audience Size Assessment

**Check audience size and penetration:**

| Campaign | Estimated Audience | Daily Impressions | Penetration Rate | Status |
|----------|-------------------|-------------------|------------------|--------|
| Campaign A | 50,000 | 15,000 | 30%/day | 🟢 Good reach |
| Campaign B | 8,000 | 6,000 | 75%/day | 🔴 Too small - burnout risk |
| Campaign C | 500,000 | 5,000 | 1%/day | 🟡 Underspending |

**Guidelines:**
- 🟢 **Optimal:** 20,000-100,000 audience size for ABM
- 🟡 **Caution:** <10,000 (burnout risk) or >200,000 (too broad)
- 🔴 **Problem:** <5,000 (definitely too narrow) or frequency >8/week

**Action items:**
- Too small audience → Add complementary skills/titles
- Too large audience → Add seniority filters, narrow functions
- High frequency (>8/week) → Expand audience or reduce budget

### 3.4 Critical Targeting Elements

**For SRE/DevOps tools (example), verify presence of:**

**Must-have skills (inclusive OR):**
- [ ] PagerDuty (55983) - competitive displacement
- [ ] Opsgenie (56845) - competitive displacement
- [ ] Incident Management (1952)
- [ ] DevOps (18442)
- [ ] Site Reliability Engineering (55383)
- [ ] Kubernetes (55158)
- [ ] Docker (1500290)
- [ ] AWS (10798)
- [ ] Terraform (55396)

**Seniority levels:**
- [ ] 4-8 (Associate through Director) - prevents too-junior

**Job functions:**
- [ ] Engineering
- [ ] IT
- [ ] (Exclude: HR, Finance, Sales unless multi-stakeholder)

**Exclusions:**
- [ ] Existing customers suppression list
- [ ] Unqualified company sizes
- [ ] Irrelevant geographies

---

## 4. Budget Efficiency Audit

### 4.1 Budget Distribution Analysis

**Current vs. recommended funnel allocation:**

| Funnel Stage | Current Budget | Current % | Recommended % | Delta | Action |
|--------------|---------------|-----------|---------------|-------|--------|
| **Awareness** | $_____ | ____% | 20-30% | _____ | ↑↓→ |
| **Consideration** | $_____ | ____% | 40-50% | _____ | ↑↓→ |
| **Decision** | $_____ | ____% | 20-30% | _____ | ↑↓→ |
| **Total** | $_____ | 100% | 100% | - | - |

**Red flags:**
- ❌ >50% budget in awareness (underinvesting in conversion)
- ❌ <30% budget in consideration (missing nurture stage)
- ❌ >40% budget in decision only (no top-of-funnel pipeline)
- ❌ No retargeting budget allocated (missing 40% of conversions)

### 4.2 Prospecting vs. Retargeting Split

**Current vs. recommended:**

| Type | Current Budget | Current % | Recommended % | Delta |
|------|---------------|-----------|---------------|-------|
| **Cold Prospecting** | $_____ | ____% | 60% | _____ |
| **Retargeting** | $_____ | ____% | 40% | _____ |

**From TripleDart case study ($904K annual spend):**
- 60% cold prospecting / demand gen
- 40% retargeting
- Result: Scaled from $10K/mo to $100K/mo with positive ROI

**If retargeting <30%:**
- Missing high-intent website visitors
- Leaving conversions on the table
- Lower overall program efficiency

### 4.3 Campaign-Level Budget Assessment

**Evaluate each campaign's budget efficiency:**

| Campaign | Daily Budget | 30-Day Spend | Conversions | CPA | CPA vs. Target | Status |
|----------|-------------|--------------|-------------|-----|----------------|--------|
| Campaign A | $50 | $1,500 | 12 | $125 | ✅ On target | 🟢 Keep |
| Campaign B | $75 | $2,250 | 3 | $750 | 🔴 6× over | 🔴 Pause |
| Campaign C | $25 | $750 | 0 | N/A | 🔴 No conv. | 🔴 Pause |

**Budget thresholds:**
- 🟢 **Minimum:** $15/day (below this = insufficient volume)
- 🟢 **Sweet spot:** $25-50/day for ABM campaigns
- 🟡 **High spend:** $75-100/day (only for top performers)
- 🔴 **Red flag:** >$100/day single campaign (diminishing returns)

**Pause criteria:**
- ❌ Zero clicks after $50+ spend
- ❌ Zero conversions after $200+ spend (3× normal CPL)
- ❌ CPA > 3× target after 2 weeks of optimization
- ❌ CPC > $40 consistently

### 4.4 Wasted Spend Identification

**Calculate total wasted spend:**

| Issue Type | Campaigns Affected | Daily Waste | Monthly Waste | Annual Impact |
|------------|-------------------|-------------|---------------|---------------|
| No creatives serving | _____ | $_____ | $_____ | $_____ |
| Zero conversions (>$200 spend) | _____ | $_____ | $_____ | $_____ |
| CPC >$40 | _____ | $_____ | $_____ | $_____ |
| Restrictive AND logic | _____ | $_____ | $_____ | $_____ |
| Ad fatigue (30+ days old) | _____ | $_____ | $_____ | $_____ |
| **TOTAL RECOVERABLE** | _____ | $_____ | $_____ | $_____ |

**Generate pause commands for wasteful campaigns:**
```bash
# Example output from audit
./linkedin update-status 447062324 --status PAUSED  # No creatives
./linkedin update-status 454052514 --status PAUSED  # Zero conversions
./linkedin update-status 454681874 --status PAUSED  # CPC >$40
```

---

## 5. Quality Score Indicators

### 5.1 Quality Score Proxy (CTR)

**LinkedIn Quality Score drives costs:**
- Campaigns with CTR >0.7% enjoy ~15% lower CPCs
- Algorithm rewards engagement over bid amount
- High-quality ads get preferential delivery

**Quality Score tiers:**

| CTR Range | Quality Tier | CPC Impact | Delivery Priority | Action |
|-----------|-------------|------------|------------------|--------|
| **>0.7%** | Excellent | -15% CPC | High | 🟢 Scale budget |
| **0.5-0.7%** | Good | Neutral | Normal | 🟢 Maintain |
| **0.4-0.5%** | Fair | +10% CPC | Lower | 🟡 Optimize |
| **<0.4%** | Poor | +25% CPC | Very Low | 🔴 Fix or pause |

**Impact of poor Quality Score:**
- Better to spend $100/day on high-CTR ad (0.7%) than $200/day on low-CTR ad (0.3%)
- Poor-performing ads hurt account-level Quality Score (affects all campaigns)
- Negative spiral: Low CTR → Higher CPC → Less spend → Even lower CTR

### 5.2 Engagement Signals

**Beyond CTR, track engagement quality:**

| Signal | Your Rate | Benchmark | Impact on Quality Score |
|--------|-----------|-----------|------------------------|
| **Likes** | _____ per 1K impr. | 5-10 | Moderate positive |
| **Comments** | _____ per 1K impr. | 1-3 | High positive |
| **Shares** | _____ per 1K impr. | 0.5-2 | Very high positive |
| **Follows** | _____ per 1K impr. | 2-5 | Moderate positive |

**Engagement boosters:**
- Thought Leader Ads (1.7× CTR, higher engagement)
- Questions in creative (drives comments)
- Controversial/hot takes (drives discussion)
- Customer testimonials (high trust = high engagement)

**Engagement killers:**
- Generic stock photos
- Corporate jargon
- Feature lists without benefits
- Hard sales pitches

---

## 6. Ad Fatigue Analysis

### 6.1 Frequency Monitoring

**Track frequency by campaign and audience:**

| Campaign | Audience | Frequency (7d) | Frequency (30d) | Status |
|----------|----------|----------------|-----------------|--------|
| Awareness | Cold ICP | 2.3 | 8.5 | 🟢 Healthy |
| Consideration | Website visitors | 4.1 | 14.2 | 🟡 Monitor |
| Retargeting | Pricing page | 7.8 | 28.3 | 🔴 Burnout risk |

**Frequency guidelines:**
- 🟢 **Awareness:** 2-3 impressions/user/week
- 🟢 **Consideration:** 3-5 impressions/user/week
- 🟡 **Retargeting:** 5-8 impressions/user/week
- 🔴 **Burnout:** >10 impressions/user/week (CTR declines sharply)

**If frequency >8/week:**
1. Set frequency caps in campaign settings
2. Rotate creative every 14 days
3. Expand audience size
4. Reduce daily budget

### 6.2 Performance Decay Tracking

**Week-over-week performance trends:**

| Campaign | Week 1 CTR | Week 2 CTR | Week 3 CTR | Week 4 CTR | Decay % | Action |
|----------|-----------|-----------|-----------|-----------|---------|--------|
| Campaign A | 0.65% | 0.62% | 0.58% | 0.48% | -26% | 🔴 Refresh NOW |
| Campaign B | 0.52% | 0.54% | 0.51% | 0.53% | +2% | 🟢 Healthy |
| Campaign C | 0.48% | 0.43% | 0.35% | 0.28% | -42% | 🔴 URGENT |

**Performance decay thresholds:**
- 🟢 <10% decay: Healthy (normal fluctuation)
- 🟡 10-20% decay: Monitor (plan refresh)
- 🟠 20-30% decay: Refresh needed within 7 days
- 🔴 >30% decay: Pause and replace immediately

### 6.3 Creative Lifespan Analysis

**Track average creative lifespan and retirement criteria:**

| Creative Format | Avg. Peak Days | Decline Begins | Retirement Day | Your Avg. |
|----------------|---------------|----------------|----------------|-----------|
| **Video** | 10-14 days | Day 12 | Day 18 | _____ |
| **Carousel** | 8-12 days | Day 10 | Day 16 | _____ |
| **Single Image** | 6-10 days | Day 8 | Day 14 | _____ |
| **Thought Leader** | 12-18 days | Day 14 | Day 21 | _____ |

**If your avg. is shorter than benchmarks:**
- Audience too small (burnout faster)
- Creative not engaging (fatigue faster)
- Frequency too high (overexposure)

---

## 7. Strategic Program Audit

### 7.1 Full-Funnel Coverage

**Verify presence of campaigns at each stage:**

| Funnel Stage | Campaign Count | Budget Allocated | Status |
|--------------|---------------|------------------|--------|
| **Awareness** | _____ | $_____ / ____% | 🔴/🟡/🟢 |
| **Consideration** | _____ | $_____ / ____% | 🔴/🟡/🟢 |
| **Decision** | _____ | $_____ / ____% | 🔴/🟡/🟢 |

**Red flags:**
- ❌ No awareness campaigns (no top-of-funnel pipeline)
- ❌ No consideration campaigns (missing nurture layer)
- ❌ Only decision campaigns (no audience priming)
- ❌ All campaigns are the same stage (not full-funnel)

**Campaign requirements by stage:**

**Awareness (minimum 2-3 campaigns):**
- Broad ICP targeting (job function + seniority)
- Educational content (problem/solution, benchmarks)
- Video and carousel formats
- No lead capture (content consumption goal)

**Consideration (minimum 3-4 campaigns):**
- Narrower targeting (engaged audiences, warm traffic)
- Case studies, comparison guides, webinars
- Lead gen forms for gated assets
- Email nurture integration

**Decision (minimum 2-3 campaigns):**
- High-intent retargeting (pricing page, demo page)
- Direct conversion offers (demo, trial, ROI calc)
- Tight audience (small, high-value)
- Lead gen forms or direct calendar booking

### 7.2 Retargeting Infrastructure

**Verify retargeting audience setup:**

| Audience Type | Status | Size | Campaign(s) Using | Budget |
|--------------|--------|------|-------------------|--------|
| **Website visitors (all)** | _____ | _____ | _____ | $_____ |
| **Pricing page visitors** | _____ | _____ | _____ | $_____ |
| **Demo page visitors** | _____ | _____ | _____ | $_____ |
| **Video viewers (50%+)** | _____ | _____ | _____ | $_____ |
| **Post engagers** | _____ | _____ | _____ | $_____ |
| **Form abandoners** | _____ | _____ | _____ | $_____ |

**Red flags:**
- ❌ No website visitor retargeting (missing 40% of conversions)
- ❌ No high-intent page retargeting (pricing, demo)
- ❌ No video viewer retargeting (engagement signal)
- ❌ No Insight Tag installed (can't build retargeting audiences)

**Quick wins:**
1. Install Insight Tag if missing (week 1 priority)
2. Create website visitor audience (minimum viable)
3. Launch retargeting campaign with objection-handling content
4. Expected: 3-5× better conversion rate than cold prospecting

### 7.3 Multichannel Integration

**Check for cross-platform coordination:**

| Integration | Status | Description |
|------------|--------|-------------|
| **LinkedIn → Google Display** | _____ | Retarget LinkedIn engagers on Display |
| **LinkedIn → Meta** | _____ | Retarget on Facebook/Instagram |
| **LinkedIn → Email** | _____ | Lead gen form → CRM → Email nurture |
| **Email → LinkedIn** | _____ | Email openers retargeted on LinkedIn |
| **CRM → LinkedIn** | _____ | Account lists synced for ABM |

**Why multichannel matters:**
- Multiple touchpoints increase conversion rates 3-5×
- Lower-cost channels (Display, Meta) amplify LinkedIn
- Email + LinkedIn combination = 40% higher close rates

### 7.4 Attribution & Tracking

**Verify attribution infrastructure:**

| Tracking Element | Status | Coverage | Quality |
|-----------------|--------|----------|---------|
| **Insight Tag** | _____ | ____% pages | 🔴/🟡/🟢 |
| **Conversion tracking** | _____ | _____ events | 🔴/🟡/🟢 |
| **UTM parameters** | _____ | ____% campaigns | 🔴/🟡/🟢 |
| **CAPI integration** | _____ | _____ | 🔴/🟡/🟢 |
| **Self-reported attribution** | _____ | _____ | 🔴/🟡/🟢 |
| **CRM sync** | _____ | _____ | 🔴/🟡/🟢 |

**CAPI (Conversions API) priority:**
- ⚠️ If not implemented → 20% higher CPA, 18-22% worse attribution
- 🎯 Q1 2026 priority: Set up CAPI infrastructure
- 💰 Expected impact: $3K-8K/month savings on $25K/month budget

**Self-reported attribution:**
- Add "How did you hear about us?" to all forms
- Compare self-reported vs. UTM vs. platform attribution
- LinkedIn often influences 2-3× more pipeline than last-touch shows

---

## 8. Advanced Optimization Opportunities

### 8.1 Thought Leader Ads Assessment

**Current usage vs. potential:**

| Metric | Current | Potential | Delta |
|--------|---------|-----------|-------|
| **% of budget in TL ads** | ____% | 20-30% | _____ |
| **TL ad CTR** | ____% | 1.7× standard | _____ |
| **TL ad CPL** | $_____ | 40% lower | _____ |

**If <10% budget in Thought Leader Ads:**
- Missing highest-performing format
- Opportunity: 1.7× CTR, 40% lower CPL
- Content needed: Founder insights, customer testimonials, SME expertise

**Thought Leader content ideas:**
- Founder sharing company learnings (behind-the-scenes)
- Customer praising your product (sponsored testimonial)
- Engineer sharing technical expertise (how-to, best practices)
- "3 mistakes we made scaling to 1,000 customers"

### 8.2 Competitive Displacement Targeting

**Are you targeting competitor tool users?**

| Competitor | Skill ID | In Targeting? | Estimated Audience | Opportunity |
|-----------|----------|---------------|-------------------|-------------|
| **PagerDuty** | 55983 | _____ | _____ | $_____ |
| **Opsgenie** | 56845 | _____ | _____ | $_____ |
| **xMatters** | 57616 | _____ | _____ | $_____ |
| **Datadog** | 10569 | _____ | _____ | $_____ |

**Why competitive displacement works:**
- Self-selecting audience (already using incident management tools)
- Higher intent than generic SRE targeting
- Lower CPA (more qualified prospects)

**If missing:**
```bash
./linkedin update-targeting CAMPAIGN_ID --add-skills "55983,56845,57616,10569"
```

### 8.3 Skills vs. Titles Strategy

**Current targeting approach:**

| Approach | Campaigns | % Budget | Typical Performance |
|----------|-----------|----------|---------------------|
| **Skills-only** | _____ | ____% | Best (inclusive OR) |
| **Titles-only** | _____ | ____% | Narrow (misses skills-listed users) |
| **Titles AND Skills (separate groups)** | _____ | ____% | Worst (restrictive AND) |
| **Titles + Skills (same group)** | _____ | ____% | Good (inclusive OR) |

**From incident.io validation (Jan 2026):**
- **Best performers:** Opsgenie_JT (101 conv @ $10.58 CPC), DeliveryHero (23 conv @ $5.81 CPC)
  - Strategy: Skills-only + seniorities + job functions
- **Underperformers:** CapitalOne (25 conv @ $16.32 CPC), PayPal (3 conv @ $17.37 CPC)
  - Strategy: Titles AND Skills (restrictive)

**If using titles AND skills in separate groups:**
1. Run targeting analysis: `./linkedin analyze CAMPAIGN_ID --recommend`
2. Copy proven template: `./linkedin copy-targeting --source 447062324 --target CAMPAIGN_ID`
3. Expected: 2-3× more clicks, 30-40% lower CPC

### 8.4 Video Expansion Opportunity

**Current video usage:**

| Metric | Current | 2026 Benchmark | Gap |
|--------|---------|---------------|-----|
| **% of impressions from video** | ____% | 28% | _____ |
| **Video completion rate** | ____% | 25-40% | _____ |
| **Video avg. duration** | ____ sec | <15 sec | _____ |

**If <20% impressions from video:**
- Missing 5× engagement vs. static
- Missing algorithm boost (LinkedIn favors video)
- Opportunity: Native LinkedIn video (<15 sec)

**Video content priorities:**
1. 10-second product UI walkthrough
2. 12-second customer testimonial clip
3. 15-second founder insight or hot take
4. Use captions (85% watch without sound)

---

## 9. Audit Scoring System

### 9.1 Overall Health Score

**Calculate your program health score (0-100):**

| Category | Weight | Your Score | Weighted Score |
|----------|--------|-----------|----------------|
| **Performance vs. Benchmarks** | 25% | _____ / 100 | _____ |
| **Creative Health** | 20% | _____ / 100 | _____ |
| **Targeting Quality** | 20% | _____ / 100 | _____ |
| **Budget Efficiency** | 15% | _____ / 100 | _____ |
| **Strategic Coverage** | 10% | _____ / 100 | _____ |
| **Advanced Optimization** | 10% | _____ / 100 | _____ |
| **TOTAL HEALTH SCORE** | 100% | - | _____ / 100 |

**Health score interpretation:**
- **90-100:** Excellent - Top quartile performance
- **75-89:** Good - Solid program with minor optimization opportunities
- **60-74:** Fair - Significant improvement opportunities
- **<60:** Poor - Requires immediate strategic overhaul

### 9.2 Category Scoring Details

**Performance vs. Benchmarks (25 points):**
- 5 pts: CTR at or above benchmark
- 5 pts: CPC at or below benchmark
- 5 pts: CPL at or below benchmark
- 5 pts: SQL rate >15%
- 5 pts: No campaigns with zero conversions after $200 spend

**Creative Health (20 points):**
- 5 pts: All creatives <14 days old
- 5 pts: 3+ creatives per campaign
- 5 pts: Format diversity (video, carousel, image)
- 5 pts: Creative quality checklist >80% pass rate

**Targeting Quality (20 points):**
- 5 pts: ICP alignment >90%
- 5 pts: No restrictive AND logic issues
- 5 pts: Audience sizes in optimal range (20K-100K)
- 5 pts: Critical targeting elements present

**Budget Efficiency (15 points):**
- 5 pts: Funnel budget distribution aligned (20/40/30)
- 5 pts: No campaigns <$15/day or >$100/day
- 5 pts: Wasted spend <10% of total budget

**Strategic Coverage (10 points):**
- 3 pts: Full-funnel coverage (awareness/consideration/decision)
- 3 pts: Retargeting infrastructure in place
- 4 pts: Attribution tracking complete (Insight Tag, CAPI, UTMs)

**Advanced Optimization (10 points):**
- 3 pts: Thought Leader Ads >10% of budget
- 3 pts: Competitive displacement targeting
- 2 pts: Video >20% of impressions
- 2 pts: Multichannel integration

---

## 10. Action Plan Generator

### 10.1 Priority Matrix

**Based on audit findings, prioritize actions:**

| Priority | Action Item | Impact | Effort | Expected Outcome | Deadline |
|----------|------------|--------|--------|------------------|----------|
| **P0 (Critical)** | _____ | High | _____ | _____ | Week 1 |
| **P0 (Critical)** | _____ | High | _____ | _____ | Week 1 |
| **P1 (High)** | _____ | High | _____ | _____ | Week 2-3 |
| **P1 (High)** | _____ | High | _____ | _____ | Week 2-3 |
| **P2 (Medium)** | _____ | Medium | _____ | _____ | Week 4-6 |
| **P3 (Low)** | _____ | Low | _____ | _____ | Quarter |

**Priority criteria:**
- **P0:** Broken fundamentals (no tracking, wasted spend, zero conversions)
- **P1:** High-impact optimizations (creative refresh, targeting fixes, CAPI)
- **P2:** Strategic improvements (full-funnel coverage, thought leader ads)
- **P3:** Nice-to-haves (video expansion, multichannel integration)

### 10.2 Quick Wins (Week 1)

**Implement these in the first week:**

1. **Pause wasteful campaigns** (zero clicks, no creatives, high CPC >$40)
   - Commands generated by audit script
   - Immediate budget recovery

2. **Refresh fatigued creatives** (>14 days old, >20% CTR decay)
   - Pause and replace immediately
   - Expected: 30-50% CTR improvement

3. **Fix restrictive AND logic** (titles AND skills in separate groups)
   ```bash
   ./linkedin analyze CAMPAIGN_ID --recommend
   ./linkedin copy-targeting --source 447062324 --target CAMPAIGN_ID
   ```
   - Expected: 2-3× more clicks, 30-40% lower CPC

4. **Set frequency caps** (if frequency >8/week)
   - Prevents audience burnout
   - Preserves creative lifespan

### 10.3 Month 1 Priorities

**Complete in the first 30 days:**

**Week 1: Stop the bleeding**
- Pause wasteful campaigns
- Refresh fatigued creatives
- Fix targeting issues (AND logic)

**Week 2: Foundation**
- Install/verify Insight Tag
- Set up conversion tracking
- Create retargeting audiences
- Implement UTM structure

**Week 3: Optimization**
- Launch retargeting campaigns
- Add competitive displacement skills
- Expand audience with complementary skills
- Test 2-3 new creative variants

**Week 4: Strategic**
- Evaluate funnel budget distribution
- Plan thought leader ad content
- Implement CAPI (start setup)
- Document baseline metrics for tracking

### 10.4 Quarter 1 Roadmap

**90-day strategic plan:**

**Month 1: Fundamentals**
- Fix broken campaigns
- Establish tracking infrastructure
- Launch retargeting
- Baseline metrics documentation

**Month 2: Optimization**
- Full creative refresh cycle (all campaigns)
- CAPI implementation complete
- Thought leader ads launch (3-5 posts)
- Multichannel integration (LinkedIn → Google/Meta)

**Month 3: Scale**
- Expand budget on top performers (20-30% increase)
- Fill funnel gaps (awareness/consideration/decision)
- Video content production (5-10 short videos)
- Self-reported attribution implementation

**Expected outcomes:**
- 20-40% reduction in CPA (from optimizations)
- 30-50% increase in lead volume (from expanded targeting)
- 15-25% improvement in SQL rate (from better targeting)
- 10-20% budget reallocation (pause wasteful, scale winners)

---

## 11. Monthly Audit Checklist

### 11.1 Data Collection (15 minutes)

**Run these commands and export data:**

```bash
# 1. Full campaign audit
./linkedin audit > audit_$(date +%Y%m%d).txt

# 2. 30-day performance summary
./linkedin performance --name "ABM" --days 30 > performance_30d_$(date +%Y%m%d).txt

# 3. Analyze targeting for top 3 campaigns
./linkedin analyze TOP_CAMPAIGN_1 --recommend > targeting_1.txt
./linkedin analyze TOP_CAMPAIGN_2 --recommend > targeting_2.txt
./linkedin analyze TOP_CAMPAIGN_3 --recommend > targeting_3.txt

# 4. List all campaigns for status overview
./linkedin list --limit 100 > campaigns_list_$(date +%Y%m%d).txt
```

### 11.2 Benchmark Comparison (10 minutes)

**Compare against benchmarks:**
- [ ] Overall CTR vs. 0.50-0.56%
- [ ] Overall CPC vs. $5-8
- [ ] Overall CPL vs. $75-150
- [ ] SQL rate vs. 15-25%
- [ ] Top performers vs. top quartile (CTR >0.6%, CPC <$5)

### 11.3 Creative Review (15 minutes)

**Check all creatives:**
- [ ] Identify creatives >14 days old (schedule refresh)
- [ ] Identify creatives with >20% CTR decay (pause immediately)
- [ ] Check creative diversity (3+ per campaign, format mix)
- [ ] Review creative quality checklist (hook, message, visual, CTA)

### 11.4 Targeting Review (10 minutes)

**Verify targeting health:**
- [ ] Run targeting analysis on all active campaigns
- [ ] Check for restrictive AND logic (titles AND skills separate)
- [ ] Verify critical skills present (PagerDuty, Opsgenie, DevOps, etc.)
- [ ] Check audience sizes (20K-100K optimal)
- [ ] Review frequency (target <8/week)

### 11.5 Budget Review (10 minutes)

**Evaluate budget efficiency:**
- [ ] Check funnel distribution (20% awareness, 40% consideration, 30% decision)
- [ ] Identify campaigns with zero conversions after $200 spend
- [ ] Calculate wasted spend (campaigns to pause)
- [ ] Review campaign-level budgets ($15-50/day optimal)

### 11.6 Action Items (5 minutes)

**Generate action plan:**
- [ ] List campaigns to pause (with commands)
- [ ] List creatives to refresh (with deadlines)
- [ ] List targeting fixes needed (with commands)
- [ ] List budget reallocation recommendations

### 11.7 Report Summary (5 minutes)

**Create executive summary:**
- Total spend last 30 days: $_____
- Total conversions: _____
- Overall CPA: $_____
- Wasted spend identified: $_____
- Expected savings from optimizations: $_____
- Top 3 action items with deadlines

**Total audit time: 60 minutes/month**

---

## 12. Quarterly Strategic Review

### 12.1 Program Performance (60 minutes)

**Quarter-over-quarter comparison:**

| Metric | Q4 2025 | Q1 2026 | Delta | Target Q2 2026 |
|--------|---------|---------|-------|----------------|
| **Total Spend** | $_____ | $_____ | ____% | $_____ |
| **Total Leads** | _____ | _____ | ____% | _____ |
| **Total SQLs** | _____ | _____ | ____% | _____ |
| **Total Pipeline** | $_____ | $_____ | ____% | $_____ |
| **Avg. CPA** | $_____ | $_____ | ____% | $_____ |
| **SQL Rate** | ____% | ____% | ____% | ____% |
| **Pipeline/Spend** | ____× | ____× | ____% | ____× |

**Strategic questions:**
1. Is LinkedIn generating positive ROI? (Pipeline > 3× Spend?)
2. Are we improving efficiency? (CPA declining QoQ?)
3. Are we scaling effectively? (Spend + conversions both growing?)
4. What's limiting growth? (Budget, creative, targeting, funnel gaps?)

### 12.2 Competitive Positioning (30 minutes)

**How do we compare to industry benchmarks?**

| Our Performance | Industry Median | Top Quartile | Gap to Top Quartile |
|-----------------|----------------|--------------|---------------------|
| CTR: ____% | 0.50-0.56% | 0.60-0.80%+ | ____% |
| CPC: $____ | $5-8 | <$5 | $____ |
| CPL: $____ | $75-150 | <$90 | $____ |

**If below median:**
- What's holding us back? (Creative, targeting, budget?)
- What can we learn from top performers?
- What experiments should we run?

**If above median:**
- What's working well? (Document for scaling)
- How can we reach top quartile?
- What new channels should we test?

### 12.3 Strategic Initiatives (60 minutes)

**Review major strategic shifts:**

**Q1 2026 initiatives:**
- [ ] CAPI implementation (complete/in-progress/not started)
- [ ] Thought leader ads launch (% of budget, performance)
- [ ] Video expansion (% of impressions, completion rates)
- [ ] Full-funnel coverage (awareness/consideration/decision)
- [ ] Retargeting infrastructure (audiences built, campaigns launched)

**Q2 2026 planning:**
- What new initiatives should we launch?
- What's working that we should double down on?
- What's not working that we should cut?
- What budget changes are needed?

### 12.4 Talent & Resources (30 minutes)

**Do we have the right resources?**

| Function | Current | Needed | Gap |
|----------|---------|--------|-----|
| **Campaign management** | _____ hrs/week | _____ hrs/week | _____ |
| **Creative production** | _____ hrs/week | _____ hrs/week | _____ |
| **Analytics/reporting** | _____ hrs/week | _____ hrs/week | _____ |
| **Strategy/optimization** | _____ hrs/week | _____ hrs/week | _____ |

**Agency/freelancer needs:**
- Video production (5-10 videos/quarter?)
- Creative design (refresh cycle every 14 days?)
- Copywriting (hooks, ad copy, landing pages?)

**Total quarterly review time: 3 hours**

---

## 13. Automation Opportunities

### 13.1 Automated Monitoring

**Set up alerts for these conditions:**

| Alert Type | Condition | Action | Frequency |
|------------|-----------|--------|-----------|
| **Creative fatigue** | CTR decline >20% WoW | Pause and refresh | Daily |
| **High CPC** | CPC >$15 for 3+ days | Investigate and fix | Daily |
| **Zero conversions** | No conversions after $200 spend | Pause campaign | Weekly |
| **Budget pacing** | Spend >110% of target | Reduce bids | Daily |
| **Frequency burnout** | Frequency >8/week | Expand audience or reduce budget | Weekly |

### 13.2 Automated Actions

**Rules to implement in Campaign Manager:**

1. **Pause poor performers:**
   - If CTR <0.35% for 7 days → Pause
   - If CPC >$25 for 3 days → Pause
   - If zero clicks after $50 spend → Pause

2. **Scale winners:**
   - If CTR >0.70% and CPA <target → Increase budget 20%
   - If Quality Score proxy (CTR) improves → Lower max bid 10%

3. **Creative rotation:**
   - If creative >14 days old → Set to rotate out
   - If creative CTR <campaign avg. -30% → Pause

### 13.3 Reporting Automation

**Automated weekly reports:**

**Monday morning dashboard (automated):**
- Last 7 days performance summary
- Top 3 performers and bottom 3 performers
- Wasted spend alerts (campaigns to pause)
- Creative refresh needed (>14 days old)
- Budget pacing (on track / overspend / underspend)

**Monthly deep-dive report (semi-automated):**
- Benchmark comparison (CTR, CPC, CPL vs. industry)
- Funnel analysis (awareness/consideration/decision)
- SQL rate and pipeline influence
- Strategic recommendations

---

## 14. Audit History Tracking

### 14.1 Longitudinal Tracking

**Track metrics over time to measure improvement:**

| Month | Health Score | CTR | CPC | CPL | SQL Rate | Wasted $ | Top Action |
|-------|-------------|-----|-----|-----|----------|----------|-----------|
| Jan 2026 | 68 | 0.45% | $9.20 | $142 | 12% | $1,200 | Fix AND logic |
| Feb 2026 | 74 | 0.52% | $7.85 | $128 | 16% | $800 | Refresh creatives |
| Mar 2026 | 81 | 0.58% | $6.50 | $110 | 19% | $400 | CAPI setup |
| Apr 2026 | _____ | ____% | $_____ | $_____ | ____% | $_____ | _____ |

**Review quarterly:**
- Are we trending in the right direction?
- What optimizations had the biggest impact?
- Where are we still struggling?
- What should we focus on next quarter?

### 14.2 Before/After Analysis

**Document major changes and their impact:**

| Change | Date | Before | After | Delta | Status |
|--------|------|--------|-------|-------|--------|
| Fixed AND logic (PayPal) | Jan 15 | $17.37 CPC | $11.20 CPC | -35% | ✅ Success |
| Added skills (Chewy) | Jan 18 | 24 skills | 35 skills | +40% reach | ✅ Success |
| CAPI implementation | Feb 1 | N/A | -18% CPA | -18% | ✅ Success |
| Thought leader ads | Feb 10 | 0% TL | 15% TL | +28% CTR | ✅ Success |

**Use this data to:**
- Justify continued investment
- Replicate successful optimizations across campaigns
- Avoid repeating failed experiments
- Build institutional knowledge

---

## 15. Summary & Quick Reference

### 15.1 Monthly Audit Quick Checklist

**Complete this in 60 minutes:**

- [ ] Run audit commands (15 min)
- [ ] Compare benchmarks (10 min)
- [ ] Review creatives (15 min)
- [ ] Check targeting (10 min)
- [ ] Review budgets (10 min)
- [ ] Generate action plan (5 min)
- [ ] Write summary (5 min)

### 15.2 Red Flags (Immediate Attention)

**Pause/fix these immediately:**
- ❌ CTR <0.40%
- ❌ CPC >$15
- ❌ Zero conversions after $200 spend
- ❌ Creatives >21 days old
- ❌ Frequency >10/week
- ❌ No creatives serving
- ❌ Restrictive AND logic (titles AND skills separate)

### 15.3 Green Flags (Maintain & Scale)

**Double down on these:**
- ✅ CTR >0.60%
- ✅ CPC <$6
- ✅ CPA at or below target
- ✅ SQL rate >20%
- ✅ Thought leader ads performing (1.7× CTR)
- ✅ Skills-based targeting (inclusive OR)
- ✅ Creative refresh cycle working (maintain CTR)

### 15.4 Key Takeaways

**Remember these principles:**

1. **Benchmark religiously:** CTR 0.50-0.56%, CPC $5-8, CPL $75-150
2. **Refresh creatives every 14 days:** Prevents 30-50% CTR decay
3. **Use skills-based targeting:** Inclusive OR, not restrictive AND
4. **Optimize for SQLs, not leads:** Quality > quantity
5. **Implement CAPI:** 20% lower CPA, 18-22% better attribution
6. **Thought leader ads = game-changer:** 1.7× CTR, 40% lower CPL
7. **Full-funnel required:** 20% awareness, 40% consideration, 30% decision
8. **Retargeting is essential:** 40% of budget, 3-5× better conversion rate
9. **Quality Score drives cost:** CTR >0.7% = 15% lower CPC
10. **Pause wasteful spend:** Zero conversions after $200 = fundamental problem

---

**Last Updated:** February 4, 2026
**Framework Version:** 1.0
**Maintained by:** incident.io Marketing Operating System
**Related Resources:** `BEST_PRACTICES_B2B_SAAS.md` (strategic guidance), `PLAYBOOK.md` (tactical execution), `audit_campaigns.py` (basic audit script)
