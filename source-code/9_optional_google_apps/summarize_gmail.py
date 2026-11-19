"""Summarize recent Gmail messages with Gemini.

Run create_gmail_token.py once first. It saves an OAuth token at
~/.gmail_token.json. See README.md in this directory for the setup steps.
"""

import base64
import pathlib
import sys

from bs4 import BeautifulSoup
from google import genai
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Google ships new models several times a year. See the model naming note in
# python_auth_setup.md when this model ID stops working.
MODEL_ID = "gemini-4-hydrogen"

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
TOKEN_PATH = pathlib.Path.home() / ".gmail_token.json"


def load_credentials():
    """Load the saved OAuth token, refreshing it if it has expired."""
    if not TOKEN_PATH.exists():
        sys.exit(f"No token at {TOKEN_PATH}. Run create_gmail_token.py first.")
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            TOKEN_PATH.write_text(creds.to_json())
        else:
            sys.exit(f"The token in {TOKEN_PATH} is not usable. Run create_gmail_token.py again.")
    return creds


def decode(data):
    return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")


def extract_body(payload):
    """Return the text of a Gmail message payload, preferring text/plain."""
    if payload.get("mimeType") == "text/plain" and "data" in payload.get("body", {}):
        return decode(payload["body"]["data"])

    for part in payload.get("parts", []):
        text = extract_body(part)
        if text:
            return text

    if payload.get("mimeType") == "text/html" and "data" in payload.get("body", {}):
        return BeautifulSoup(decode(payload["body"]["data"]), "html.parser").get_text()

    return ""


def header(headers, name, default):
    return next((h["value"] for h in headers if h["name"].lower() == name), default)


def summarize_recent_emails(gmail_service, query, max_results=5):
    """Fetch recent emails that match a Gmail search query and summarize them."""
    print(f"\n--- Summarizing Emails (Query: {query}) ---")

    results = gmail_service.users().messages().list(
        userId="me", q=query, maxResults=max_results
    ).execute()
    messages = results.get("messages", [])
    if not messages:
        print("No messages found matching the query.")
        return

    print(f"Found {len(messages)} emails. Fetching content...")
    email_contents = []
    for msg_info in messages:
        msg = gmail_service.users().messages().get(
            userId="me", id=msg_info["id"], format="full"
        ).execute()
        payload = msg.get("payload", {})
        headers = payload.get("headers", [])
        email_contents.append(
            f"--- Email ---\n"
            f"Subject: {header(headers, 'subject', 'No Subject')}\n"
            f"From: {header(headers, 'from', 'Unknown Sender')}\n\n"
            f"{extract_body(payload)[:2000]}\n"
        )

    prompt = (
        "Summarize the key points of the following emails. For each email give "
        "one line with the sender and the main point, then list any action items "
        "for me at the end.\n\n" + "\n".join(email_contents)
    )

    client = genai.Client()
    response = client.models.generate_content(model=MODEL_ID, contents=prompt)

    print("\n--- Gemini Summary ---")
    print(response.text.strip() if response.text else "Blocked or empty response.")


if __name__ == "__main__":
    gmail_service = build("gmail", "v1", credentials=load_credentials())
    summarize_recent_emails(gmail_service, "newer_than:7d", max_results=5)
