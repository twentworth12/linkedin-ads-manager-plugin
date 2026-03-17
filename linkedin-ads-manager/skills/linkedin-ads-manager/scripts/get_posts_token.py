#!/usr/bin/env python3
"""
LinkedIn OAuth 2.0 Token Generator - Community Management API
Exchanges client credentials for an access token with w_organization_social scope
"""

import requests
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# You'll paste your credentials here
CLIENT_ID = input("Paste your LinkedIn Client ID: ").strip()
CLIENT_SECRET = input("Paste your LinkedIn Client Secret: ").strip()

REDIRECT_URI = "http://localhost:8080/callback"
SCOPES = "w_organization_social"

print("\n" + "="*60)
print("LinkedIn OAuth 2.0 Token Generator")
print("Community Management API (Posting)")
print("="*60)

# Step 1: Authorization URL
auth_url = (
    f"https://www.linkedin.com/oauth/v2/authorization"
    f"?response_type=code"
    f"&client_id={CLIENT_ID}"
    f"&redirect_uri={REDIRECT_URI}"
    f"&scope={SCOPES}"
)

print("\n📱 Step 1: Authorize the application")
print("Opening browser for LinkedIn authorization...")
print("(If browser doesn't open, copy this URL manually)")
print(f"\n{auth_url}\n")

webbrowser.open(auth_url)

# Step 2: Capture authorization code
print("⏳ Waiting for authorization...")

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)

        if 'code' in query:
            self.server.auth_code = query['code'][0]
            self.send_response(200)
            self.end_headers()
            html = """
                <html>
                <body style="font-family: sans-serif; text-align: center; padding: 50px;">
                    <h1>✅ Authorization Successful!</h1>
                    <p>You can close this window and return to your terminal.</p>
                </body>
                </html>
            """
            self.wfile.write(html.encode('utf-8'))
        elif 'error' in query:
            self.server.auth_code = None
            self.send_response(400)
            self.end_headers()
            error = query.get('error_description', ['Unknown error'])[0]
            html = f"""
                <html>
                <body style="font-family: sans-serif; text-align: center; padding: 50px;">
                    <h1>❌ Authorization Failed</h1>
                    <p>{error}</p>
                </body>
                </html>
            """
            self.wfile.write(html.encode())

    def log_message(self, format, *args):
        pass  # Suppress request logs

server = HTTPServer(('localhost', 8080), CallbackHandler)
server.handle_request()

if not hasattr(server, 'auth_code') or not server.auth_code:
    print("\n❌ Authorization failed or was cancelled")
    exit(1)

auth_code = server.auth_code
print("✓ Authorization code received")

# Step 3: Exchange for access token
print("\n🔄 Step 2: Exchanging authorization code for access token...")

token_url = "https://www.linkedin.com/oauth/v2/accessToken"
token_data = {
    'grant_type': 'authorization_code',
    'code': auth_code,
    'redirect_uri': REDIRECT_URI,
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET
}

response = requests.post(token_url, data=token_data)

if response.status_code != 200:
    print(f"\n❌ Token exchange failed:")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text}")
    exit(1)

token_response = response.json()
access_token = token_response['access_token']
expires_in = token_response['expires_in']

print("✓ Access token received")

# Display results
print("\n" + "="*60)
print("✅ SUCCESS! Your LinkedIn Posts Token:")
print("="*60)
print(f"\n{access_token}\n")
print(f"Expires in: {expires_in} seconds ({expires_in // 86400} days)")
print("="*60)

# Offer to save to credentials file
print("\n💾 Save to credentials file?")
save = input("Update .credentials file with this token? (y/n): ").strip().lower()

if save == 'y':
    from pathlib import Path
    creds_file = Path(__file__).parent / '.credentials'

    # Read existing credentials
    existing_lines = []
    if creds_file.exists():
        with open(creds_file, 'r') as f:
            existing_lines = f.readlines()

    # Update or add LINKEDIN_POSTS_TOKEN
    updated = False
    new_lines = []
    for line in existing_lines:
        if line.startswith('LINKEDIN_POSTS_TOKEN='):
            new_lines.append(f'LINKEDIN_POSTS_TOKEN={access_token}\n')
            updated = True
        else:
            new_lines.append(line)

    if not updated:
        new_lines.append(f'\nLINKEDIN_POSTS_TOKEN={access_token}\n')

    with open(creds_file, 'w') as f:
        f.writelines(new_lines)

    print(f"\n✅ Credentials updated in: {creds_file}")
else:
    print("\nSkipped saving. Copy the token above and add to .credentials file manually:")
    print(f"LINKEDIN_POSTS_TOKEN={access_token}")

print("\n")
