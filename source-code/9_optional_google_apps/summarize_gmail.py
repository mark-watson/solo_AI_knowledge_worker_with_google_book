"""Summarize recent Gmail messages with Gemini.

Requires an OAuth 2.0 credential stored at ~/.gmail_cred. See README.md in
this directory for the Google Cloud Console steps that create it.
"""

import base64
import os
import pickle

from bs4 import BeautifulSoup
from google import genai
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Google ships new Flash models several times a year. See the model naming
# note in python_auth_setup.md when this model ID stops working.
MODEL_ID = "gemini-3.8-flash"

CREDENTIALS_PATH = os.path.expanduser("~/.gmail_cred")


def load_credentials():
    """Load the saved OAuth 2.0 credentials, refreshing them if needed."""
    with open(CREDENTIALS_PATH, "rb") as f:
        creds = pickle.load(f)
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise RuntimeError(
                f"Credentials in {CREDENTIALS_PATH} are not usable. "
                "Delete the file and create a new credential."
            )
    return creds


def extract_body(payload):
    """Return the text of a Gmail message payload, preferring text/plain."""
    if payload.get("mimeType") == "text/plain" and "data" in payload.get("body", {}):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8")

    for part in payload.get("parts", []):
        text = extract_body(part)
        if text:
            return text

    if payload.get("mimeType") == "text/html" and "data" in payload.get("body", {}):
        html = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8")
        return BeautifulSoup(html, "html.parser").get_text()

    return ""


def summarize_recent_emails(gmail_service, query, max_results=5):
    """Fetch and summarize recent emails matching a query using Gemini."""
    print(f"\n--- Summarizing Emails (Query: {query}) ---")

    results = gmail_service.users().messages().list(
        userId="me", q=query, maxResults=max_results
    ).execute()
    messages = results.get("messages", [])

    if not messages:
        print("No messages found matching the query.")
        return

    email_contents = []
    print(f"Found {len(messages)} emails. Fetching content...")
    for msg_info in messages:
        msg_id = msg_info["id"]
        msg = gmail_service.users().messages().get(
            userId="me", id=msg_id, format="full"
        ).execute()

        payload = msg.get("payload", {})
        headers = payload.get("headers", [])
        subject = next(
            (h["value"] for h in headers if h["name"].lower() == "subject"),
            "No Subject",
        )
        sender = next(
            (h["value"] for h in headers if h["name"].lower() == "from"),
            "Unknown Sender",
        )

        body = extract_body(payload)[:1000]
        email_contents.append(
            f"--- Email ID: {msg_id} ---\n"
            f"Subject: {subject}\nFrom: {sender}\n"
            f"Snippet: {msg.get('snippet', '')}\n\n{body}\n"
        )

    full_context = "\n".join(email_contents)
    prompt = (
        "Please summarize the key points from the following emails matching "
        f"the query '{query}':\n\n{full_context}"
    )

    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
    )

    print("\n--- Gemini Summary ---")
    if response.text:
        print(response.text.strip())
    else:
        print("Blocked or empty response.")


if __name__ == "__main__":
    # Build service objects from the stored OAuth 2.0 credential.
    gmail_service = build("gmail", "v1", credentials=load_credentials())
    # calendar_service = build('calendar', 'v3', credentials=creds)
    # docs_service = build('docs', 'v1', credentials=creds)
    # drive_service = build('drive', 'v3', credentials=creds)

    summarize_recent_emails(gmail_service, "newer_than:7d", max_results=5)
