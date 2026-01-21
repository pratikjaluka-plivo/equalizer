#!/usr/bin/env python3
"""
Gmail Token Generator
=====================
Run this script ONCE after setting up gmail_credentials.json
to generate the gmail_token.json file.

Steps:
1. Go to https://console.cloud.google.com/
2. Create a new project (or select existing)
3. Enable Gmail API: APIs & Services > Library > Gmail API > Enable
4. Create OAuth credentials: APIs & Services > Credentials > Create > OAuth Client ID
   - Application type: Desktop app
   - Download the JSON file
5. Replace the contents of gmail_credentials.json with your downloaded JSON
6. Run this script: python3 generate_gmail_token.py
7. A browser window will open - sign in and authorize
8. gmail_token.json will be created automatically
"""

import os
import json

try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
except ImportError:
    print("Missing required packages. Install them with:")
    print("  pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    exit(1)

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
CREDENTIALS_FILE = 'gmail_credentials.json'
TOKEN_FILE = 'gmail_token.json'

def main():
    creds = None
    
    # Check if token already exists
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # If no valid credentials, run the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired token...")
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                print(f"ERROR: {CREDENTIALS_FILE} not found!")
                print("Please download OAuth credentials from Google Cloud Console")
                return
            
            # Check if credentials are still placeholder
            with open(CREDENTIALS_FILE) as f:
                cred_data = json.load(f)
                if "REPLACE_WITH" in str(cred_data):
                    print("ERROR: Please replace placeholder values in gmail_credentials.json")
                    print("Download your OAuth credentials from Google Cloud Console")
                    return
            
            print("Opening browser for authorization...")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
        print(f"Token saved to {TOKEN_FILE}")
    
    print("Gmail authentication successful!")
    print(f"Token file: {os.path.abspath(TOKEN_FILE)}")

if __name__ == '__main__':
    main()
