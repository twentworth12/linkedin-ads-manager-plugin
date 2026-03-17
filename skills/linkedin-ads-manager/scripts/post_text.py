#!/usr/bin/env python3
"""
Post simple text to incident.io LinkedIn page
Usage: python post_text.py --file /path/to/post.txt
       python post_text.py --text "Post text"
"""

import argparse
import requests
from linkedin_api import LinkedInAdsClient
from pathlib import Path

INCIDENT_IO_ORG = "urn:li:organization:75156029"

def create_text_post(client, text):
    """Create a simple text post"""
    print(f"📝 Creating organic text post...")
    print(f"   Text length: {len(text)} characters")
    print(f"   First 100 chars: {text[:100]}...")
    print()

    if not client.posts_token:
        raise Exception("LINKEDIN_POSTS_TOKEN required")

    url = f"{client.base_url}/posts"

    payload = {
        "author": INCIDENT_IO_ORG,
        "commentary": text,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": []
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False
    }

    headers = client._headers(use_posts_token=True)

    response = requests.post(url, headers=headers, json=payload)

    print(f"Status: {response.status_code}")
    if response.status_code not in [200, 201]:
        print(f"❌ Error: {response.text}")
        return None

    post_id = response.headers.get('x-restli-id')
    if not post_id and response.text:
        data = response.json()
        post_id = data.get('id')

    print(f"✅ Post created: {post_id}")
    return post_id

def main():
    parser = argparse.ArgumentParser(description='Post text to incident.io LinkedIn page')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--file', help='Path to text file with post content')
    group.add_argument('--text', help='Post text directly')

    args = parser.parse_args()

    # Get text from file or argument
    if args.file:
        post_text = Path(args.file).read_text()
    else:
        post_text = args.text

    try:
        client = LinkedInAdsClient()
        post_id = create_text_post(client, post_text)

        if post_id:
            print(f"\n🔗 View post:")
            print(f"   https://www.linkedin.com/feed/update/{post_id}")
            print(f"   https://www.linkedin.com/company/incidentio/posts/")
            return 0
        else:
            return 1

    except Exception as e:
        print(f"\n❌ Failed: {e}")
        return 1

if __name__ == '__main__':
    exit(main())
