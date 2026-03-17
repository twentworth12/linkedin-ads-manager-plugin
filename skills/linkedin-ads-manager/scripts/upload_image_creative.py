#!/usr/bin/env python3
"""
Upload image and create LinkedIn ad creative
Usage: python upload_image_creative.py --image /path/to/image.png --campaign-id 475510294 --commentary "Ad text"
"""

import argparse
import requests
import json
import time
from pathlib import Path
from linkedin_api import LinkedInAdsClient

def upload_image(client, image_path, asset_name):
    """Upload image and return image URN"""
    print(f"📤 Step 1: Initializing image upload...")

    # Use posts token for organization-owned image uploads (w_organization_social scope)
    # Step 1: Initialize upload
    url = f"{client.base_url}/images?action=initializeUpload"

    payload = {
        "initializeUploadRequest": {
            "owner": "urn:li:organization:75156029",  # incident.io organization as owner
            "mediaLibraryMetadata": {
                "associatedAccount": f"urn:li:sponsoredAccount:{client.account_id}",
                "assetName": asset_name
            }
        }
    }

    if not client.posts_token:
        raise Exception("LINKEDIN_POSTS_TOKEN required to upload images for organization")

    response = requests.post(url, headers=client._headers(use_posts_token=True), json=payload)

    if response.status_code != 200:
        raise Exception(f"Initialize upload failed: {response.status_code} - {response.text}")

    data = response.json()
    upload_url = data['value']['uploadUrl']
    image_urn = data['value']['image']

    print(f"✓ Upload initialized: {image_urn}")

    # Step 2: Upload image bytes
    print(f"📤 Step 2: Uploading image bytes...")

    with open(image_path, 'rb') as f:
        image_data = f.read()

    upload_response = requests.put(upload_url, data=image_data)

    if upload_response.status_code not in [200, 201]:
        raise Exception(f"Image upload failed: {upload_response.status_code}")

    print(f"✓ Image uploaded successfully")

    return image_urn

def create_dsc_post(client, image_urn, commentary):
    """Create Direct Sponsored Content post with image"""
    print(f"📝 Step 3: Creating Direct Sponsored Content post...")

    if not client.posts_token:
        raise Exception("LINKEDIN_POSTS_TOKEN not set in credentials - required for creating posts")

    # Wait for LinkedIn to process the uploaded image before referencing it
    print(f"   Waiting for image processing...")
    time.sleep(3)

    url = f"{client.base_url}/posts"

    payload = {
        "author": "urn:li:organization:75156029",  # incident.io
        "commentary": commentary,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "NONE"
        },
        "content": {
            "media": {
                "title": "incident.io advertisement",
                "id": image_urn
            }
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": True,
        "adContext": {
            "dscAdAccount": f"urn:li:sponsoredAccount:{client.account_id}",
            "dscStatus": "ACTIVE"
        }
    }

    # Retry up to 3 times — LinkedIn may need time to process the image
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        response = requests.post(url, headers=client._headers(use_posts_token=True), json=payload)

        if response.status_code in [200, 201]:
            break

        if attempt < max_retries and response.status_code == 404:
            wait = attempt * 3
            print(f"   Image not ready yet, retrying in {wait}s (attempt {attempt}/{max_retries})...")
            time.sleep(wait)
        else:
            raise Exception(f"Create post failed: {response.status_code} - {response.text}")

    # Get post URN from response header (LinkedIn returns full URN)
    post_urn = response.headers.get('x-restli-id')

    if not post_urn:
        # Fallback: try to get from response body
        if response.text:
            data = response.json()
            post_urn = data.get('id')

    if not post_urn:
        raise Exception("Could not extract post URN from response")

    print(f"✓ Post created: {post_urn}")

    return post_urn

def create_creative(client, campaign_id, post_urn, creative_name):
    """Create creative referencing the post"""
    print(f"🎨 Step 4: Creating creative...")

    url = f"{client.base_url}/adAccounts/{client.account_id}/creatives"

    # post_urn is already a full URN (e.g., urn:li:share:...), use it directly
    payload = {
        "campaign": f"urn:li:sponsoredCampaign:{campaign_id}",
        "content": {
            "reference": post_urn  # Use URN directly - already in correct format
        },
        "intendedStatus": "ACTIVE",  # Changed from DRAFT to ACTIVE for immediate use
        "name": creative_name
    }

    response = requests.post(url, headers=client._headers(), json=payload)

    if response.status_code not in [200, 201]:
        raise Exception(f"Create creative failed: {response.status_code} - {response.text}")

    creative_id = response.headers.get('x-restli-id') or response.json().get('id', 'created')

    print(f"✓ Creative created: {creative_id}")

    return creative_id

def main():
    parser = argparse.ArgumentParser(description='Upload image and create LinkedIn ad creative')
    parser.add_argument('--image', required=True, help='Path to image file')
    parser.add_argument('--campaign-id', required=True, help='Campaign ID to add creative to')
    parser.add_argument('--commentary', required=True, help='Ad commentary/text')
    parser.add_argument('--name', help='Creative name (default: derived from filename)')

    args = parser.parse_args()

    # Validate image exists
    image_path = Path(args.image)
    if not image_path.exists():
        print(f"❌ Image not found: {args.image}")
        return 1

    creative_name = args.name or f"yorkshire_{image_path.stem}"

    print(f"🚀 Creating new ad creative from image\n")
    print(f"  Image: {image_path.name}")
    print(f"  Campaign: {args.campaign_id}")
    print(f"  Commentary: {args.commentary[:50]}...")
    print(f"  Creative name: {creative_name}\n")

    try:
        # Initialize client
        client = LinkedInAdsClient()

        # Upload image
        image_urn = upload_image(client, image_path, creative_name)

        # Create DSC post
        post_urn = create_dsc_post(client, image_urn, args.commentary)

        # Create creative
        creative_id = create_creative(client, args.campaign_id, post_urn, creative_name)

        print(f"\n✅ Successfully created new ad creative!")
        print(f"  Creative ID: {creative_id}")
        print(f"  Campaign: {args.campaign_id}")
        print(f"  Status: DRAFT")
        print(f"\n🔗 View in Campaign Manager:")
        print(f"  https://www.linkedin.com/campaignmanager/accounts/{client.account_id}/campaigns/{args.campaign_id}")

        return 0

    except Exception as e:
        print(f"\n❌ Failed: {e}")
        return 1

if __name__ == '__main__':
    exit(main())
