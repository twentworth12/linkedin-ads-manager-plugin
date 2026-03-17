#!/usr/bin/env python3
"""
Post video to incident.io LinkedIn page
Usage: python post_video.py --video /path/to/video.mp4 --text "Post text"

IMPORTANT FIX (January 2026):
- Video finalization was failing with 400 errors due to missing ETag
- Fix: Capture ETag from upload response headers and include in uploadedPartIds
- This allows LinkedIn to properly associate the uploaded bytes with the video URN
- Without this, posts would succeed in API but videos wouldn't appear
"""

import argparse
import requests
import json
import time
from pathlib import Path
from linkedin_api import LinkedInAdsClient

INCIDENT_IO_ORG = "urn:li:organization:75156029"

def upload_video(client, video_path, title):
    """Upload video and return video URN"""
    print(f"📤 Step 1: Initializing video upload for {title}...")

    if not client.posts_token:
        raise Exception("LINKEDIN_POSTS_TOKEN not set in .credentials - required for uploading videos")

    # Get file size
    file_size = video_path.stat().st_size
    print(f"  Video size: {file_size / 1024 / 1024:.1f} MB")

    # Step 1: Register upload
    url = f"{client.base_url}/videos?action=initializeUpload"

    payload = {
        "initializeUploadRequest": {
            "owner": INCIDENT_IO_ORG,
            "fileSizeBytes": file_size,
            "uploadCaptions": False,
            "uploadThumbnail": False
        }
    }

    headers = client._headers(use_posts_token=True)
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code not in [200, 201]:
        raise Exception(f"Initialize video upload failed: {response.status_code} - {response.text}")

    data = response.json()
    video_urn = data['value']['video']
    upload_instructions = data['value']['uploadInstructions']
    upload_token = upload_instructions[0].get('uploadToken', '')

    print(f"✓ Upload initialized: {video_urn}")
    print(f"  Upload token: {upload_token[:20] if upload_token else 'none'}...")

    # Step 2: Upload video in chunks
    print(f"📤 Step 2: Uploading video...")

    with open(video_path, 'rb') as f:
        video_data = f.read()

    # Upload to the URL provided by LinkedIn
    upload_url = upload_instructions[0]['uploadUrl']

    # Use headers from upload instructions if provided
    upload_headers = {'Content-Type': 'application/octet-stream'}

    upload_response = requests.put(
        upload_url,
        data=video_data,
        headers=upload_headers
    )

    if upload_response.status_code not in [200, 201]:
        raise Exception(f"Video upload failed: {upload_response.status_code} - {upload_response.text}")

    print(f"✓ Video uploaded successfully (status: {upload_response.status_code})")

    # Get ETag from upload response
    etag = upload_response.headers.get('ETag', '').strip('"')
    print(f"  ETag: {etag}")

    # Step 3: Finalize upload
    print(f"📤 Step 3: Finalizing upload...")

    finalize_url = f"{client.base_url}/videos?action=finalizeUpload"
    finalize_payload = {
        "finalizeUploadRequest": {
            "video": video_urn,
            "uploadToken": upload_token,
            "uploadedPartIds": [etag] if etag else []
        }
    }

    print(f"  Finalize payload: {finalize_payload}")

    finalize_response = requests.post(finalize_url, headers=headers, json=finalize_payload)

    print(f"  Finalize status: {finalize_response.status_code}")
    if finalize_response.status_code not in [200, 201]:
        print(f"  Finalize error: {finalize_response.text}")
        raise Exception(f"Finalize upload failed: {finalize_response.status_code} - {finalize_response.text}")
    else:
        print(f"✓ Upload finalized successfully")

    # Wait for processing
    print(f"⏳ Waiting for video to process...")
    time.sleep(10)  # Give it more time

    return video_urn

def create_video_post(client, video_urn, text):
    """Create a post with the uploaded video"""
    print(f"📝 Step 4: Creating post...")

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
        "content": {
            "media": {
                "title": "incident.io product video",
                "id": video_urn
            }
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False
    }

    headers = client._headers(use_posts_token=True)
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code not in [200, 201]:
        raise Exception(f"Create post failed: {response.status_code} - {response.text}")

    # Get post ID
    post_id = response.headers.get('x-restli-id')
    if not post_id and response.text:
        data = response.json()
        post_id = data.get('id')

    print(f"✓ Post created: {post_id}")

    return post_id

def main():
    parser = argparse.ArgumentParser(description='Post video to incident.io LinkedIn page')
    parser.add_argument('--video', required=True, help='Path to video file')
    parser.add_argument('--text', required=True, help='Post text/commentary')

    args = parser.parse_args()

    # Validate video exists
    video_path = Path(args.video)
    if not video_path.exists():
        print(f"❌ Video not found: {args.video}")
        return 1

    print(f"🚀 Posting video to incident.io LinkedIn page\n")
    print(f"  Video: {video_path.name}")
    print(f"  Text: {args.text[:80]}...")
    print()

    try:
        # Initialize client
        client = LinkedInAdsClient()

        # Upload video
        video_urn = upload_video(client, video_path, video_path.stem)

        # Create post
        post_id = create_video_post(client, video_urn, args.text)

        print(f"\n✅ Successfully posted to LinkedIn!")
        print(f"  Post ID: {post_id}")
        print(f"  Organization: incident.io")
        print(f"\n📱 View on LinkedIn:")
        print(f"  https://www.linkedin.com/feed/update/{post_id}")

        return 0

    except Exception as e:
        print(f"\n❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    exit(main())
