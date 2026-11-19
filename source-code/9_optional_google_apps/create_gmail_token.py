"""Run once to authorize read-only Gmail access and save a token.

Needs client_secret.json, the OAuth client file you download from the Google
Cloud Console. See README.md in this directory for the steps. The script opens
a browser window where you approve access, then writes the token to
~/.gmail_token.json for summarize_gmail.py to use.
"""

import os
import pathlib
import sys

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CLIENT_SECRET = pathlib.Path("client_secret.json")
TOKEN_PATH = pathlib.Path.home() / ".gmail_token.json"

if not CLIENT_SECRET.exists():
    sys.exit(f"Missing {CLIENT_SECRET}. Download it from the Google Cloud Console.")

flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, scopes=SCOPES)
creds = flow.run_local_server(port=0)

TOKEN_PATH.write_text(creds.to_json())
os.chmod(TOKEN_PATH, 0o600)
print(f"Saved token to {TOKEN_PATH}")
