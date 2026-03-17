# LinkedIn Ads Manager - Troubleshooting Guide

**Common errors and solutions**
**Last updated: February 4, 2026**

---

## Creative Upload Errors (Fixed February 2026)

### Error 1: Missing Required Parameter
**Error message:**
```
usage: upload_image_creative.py [-h] --image IMAGE --campaign-id CAMPAIGN_ID
                                --commentary COMMENTARY [--name NAME]
upload_image_creative.py: error: the following arguments are required: --commentary
```

**Cause:** Script requires `--commentary` parameter (not `--title`)

**Solution:**
```bash
# ❌ Wrong
python3 upload_image_creative.py --campaign-id 123 --image foo.jpg --title "Ad text"

# ✅ Correct
python3 upload_image_creative.py --campaign-id 123 --image foo.jpg --commentary "Ad text"
```

---

### Error 2: 404 "Could not find entity" on Post Creation
**Error message:**
```
❌ Failed: Create post failed: 404 - {"code":"NOT_FOUND","message":"Could not find entity","status":404}
```

**Cause:** Post creation payload included `targetEntities` array in distribution that caused LinkedIn API to fail

**Original problematic code:**
```python
"distribution": {
    "feedDistribution": "NONE",
    "targetEntities": [{
        "geoLocations": ["urn:li:geo:103644278"],
        "seniorities": ["urn:li:seniority:3"]
    }],
    "thirdPartyDistributionChannels": []
}
```

**Fix applied:** Simplified distribution to minimal required fields
```python
"distribution": {
    "feedDistribution": "NONE"
}
```

**Why it works:** DSC (Direct Sponsored Content) posts don't need targeting in the post itself - targeting happens at the campaign level. The `targetEntities` array was unnecessary and caused the API to fail validation.

**File fixed:** `upload_image_creative.py` lines 78-79

---

### Error 3: 422 "field is required but not found" (distribution)
**Error message:**
```
Status: 422
Error: {"message":"ERROR :: /distribution :: field is required but not found and has no default value\n","status":422}
```

**Cause:** Completely omitted `distribution` field in initial debugging attempts

**Solution:** Distribution field is REQUIRED for all LinkedIn posts, even DSC posts. Use minimal:
```python
"distribution": {
    "feedDistribution": "NONE"
}
```

---

### Error 4: 422 "reference value ... is of type post. Allowed URN types are share, ugcPost"
**Error message:**
```
Creative error: {"message":"ERROR :: /content/reference :: reference value urn:li:post:urn:li:share:7424893150759907328 is of type post. Allowed URN types are adInMailContent, share, ugcPost\n","status":422}
```

**Cause:** Double-URN prefix issue - the post creation returns a full URN like `urn:li:share:7424893150759907328`, but the code was adding `urn:li:post:` prefix, creating `urn:li:post:urn:li:share:...`

**Original problematic code:**
```python
post_id = response.headers.get('x-restli-id')
# Later...
'reference': f'urn:li:post:{post_id}'  # ❌ Wrong - double URN
```

**Fix applied:**
```python
post_urn = response.headers.get('x-restli-id')  # Already full URN
# Later...
'reference': post_urn  # ✅ Correct - use URN directly
```

**File fixed:** `upload_image_creative.py` lines 102-109 and line 121

---

## Campaign Cloning Best Practices

### Issue: Cloning Creatives Creates Irrelevant Ads
**Problem:** When cloning ABM_Chewy to create ABM_RocketMortgage with `--clone-creatives`, the new campaign gets 20 creatives that may reference Chewy or use generic messaging not tailored to Rocket Mortgage.

**Impact:**
- Lower CTR (generic vs. company-specific messaging)
- Poor Quality Score (irrelevant creative)
- Wasted time managing cloned creatives that need deletion
- Missed opportunity for hyper-targeted messaging

**Best Practice:**
```bash
# ✅ Clone targeting only (recommended)
./linkedin clone --source ABM_Chewy --name ABM_RocketMortgage
./linkedin update-targeting NEW_ID --add-organization ORG_ID

# Then add company-specific creative
python3 upload_image_creative.py --campaign-id NEW_ID --image custom.jpg --commentary "Company-specific message"

# ❌ Avoid cloning creatives (except for bulk testing)
./linkedin clone --source ABM_Chewy --name ABM_RocketMortgage --clone-creatives
```

**When to clone creatives:**
- Bulk testing with identical creative across multiple campaigns
- Rapid iteration testing (same creative, different audiences)
- **Rarely recommended** for production ABM campaigns

**Documentation updated:**
- `skill.md` - Agent instructions updated
- `PLAYBOOK.md` - Playbook 1 updated
- `README.md` - Best practice warning added

---

## API and Integration Issues

### Issue: LinkedIn API Rate Limits
**Symptoms:** Requests failing intermittently, 429 errors

**Solution:**
- Built-in retry logic in `linkedin_api.py`
- Pagination automatically handles large result sets
- If persistent, check LinkedIn Ad Account status

---

### Issue: Campaign Not Found (Pagination)
**Problem:** Campaign exists but not returned by list/search commands

**Cause:** LinkedIn API returns max 100 results per page

**Solution:**
```bash
# Search by name (automatically paginates)
./linkedin list --name "PartialName"

# Increase limit
./linkedin list --limit 100
```

---

### Issue: Terraform Schedule Reshuffling
**Problem:** When updating Opsgenie or LinkedIn schedules via Terraform, entire rotation order changes unexpectedly

**This was an Opsgenie issue - not applicable to LinkedIn Ads Manager**

Documented here for reference from competitive intelligence research.

---

## Command Execution Issues

### Issue: "./linkedin command not found"
**Error:**
```bash
./linkedin list
zsh: no such file or directory: ./linkedin
```

**Cause:** Running from wrong directory

**Solution:**
```bash
# Must run from repository root
cd /Users/tomwentworth/incidentio
./linkedin list

# ❌ Don't run from other directories
cd /Users/tomwentworth/incidentio/.claude/skills/linkedin-ads-manager
./linkedin list  # This will fail
```

---

### Issue: Python Module Import Errors
**Error:**
```python
ModuleNotFoundError: No module named 'linkedin_api'
```

**Cause:** Running Python scripts directly instead of using wrapper

**Solution:**
```bash
# ❌ Wrong - import paths break
python3 .claude/skills/linkedin-ads-manager/clone_campaign.py

# ✅ Correct - use wrapper
./linkedin clone --source ABM_Chewy --name ABM_NewCo
```

---

## Summary of Fixes (February 4, 2026)

| Issue | File Fixed | Change Made | Impact |
|-------|-----------|-------------|--------|
| `targetEntities` 404 error | `upload_image_creative.py` | Simplified distribution payload | Creative uploads now work |
| Double URN prefix | `upload_image_creative.py` | Use post URN directly without prefix | Creative creation succeeds |
| Creative cloning by default | `skill.md`, `PLAYBOOK.md`, `README.md` | Removed --clone-creatives from examples | Better ABM campaign quality |
| Payload structure order | `upload_image_creative.py` | Moved adContext to end | Better API compatibility |
| Post URN extraction | `upload_image_creative.py` | Renamed post_id → post_urn, added clarity | Clearer code, fewer bugs |

---

## Testing Checklist (After Script Changes)

When modifying API scripts, test these scenarios:

**Creative upload test:**
```bash
# Test with real image
python3 upload_image_creative.py \
  --campaign-id 481740984 \
  --image /path/to/test.jpg \
  --commentary "Test ad copy" \
  --name "Test Creative"

# Expected: 201 status on post creation, 201 on creative creation
```

**Campaign clone test:**
```bash
# Test without creatives
./linkedin clone --source ABM_Chewy --name Test_Campaign

# Expected: Campaign created in DRAFT, no creatives cloned
```

**Targeting update test:**
```bash
# Test organization targeting
./linkedin update-targeting TEST_ID --add-organization 80506627

# Expected: 204 success, organization updated
```

---

**Maintained by:** incident.io Marketing Operating System
**Last Major Update:** February 4, 2026 (Creative upload API fixes)
