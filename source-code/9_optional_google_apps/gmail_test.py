import base64
import re
from bs4 import BeautifulSoup # For parsing HTML emails
import datetime
import os
from google import genai

# --- Gmail Automation ---

def summarize_recent_emails(gmail_service, query, max_results=5):
    """Fetches and summarizes recent emails matching a query using Gemini."""
    print(f"\n--- Summarizing Emails (Query: {query}) ---")
    try:
        # 1. List messages matching the query
        results = gmail_service.users().messages().list(
            userId='me', q=query, maxResults=max_results
        ).execute()
        messages = results.get('messages', [])

        if not messages:
            print("No messages found matching the query.")
            return

        email_contents = []
        print(f"Found {len(messages)} emails. Fetching content...")
        for msg_info in messages:
            msg_id = msg_info['id']
            # 2. Get individual message content
            msg = gmail_service.users().messages().get(
                userId='me', id=msg_id, format='full' # Use 'full' or 'metadata'/'minimal'
            ).execute()

            # 3. Extract relevant text (handle different MIME types)
            snippet = msg.get('snippet', '') # Gmail's own summary
            payload = msg.get('payload', {})
            headers = payload.get('headers', [])
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown Sender')

            body_text = f"Subject: {subject}\nFrom: {sender}\nSnippet: {snippet}\n"

            # Try to get plain text part
            plain_text_body = ""
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                        plain_text_body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
                    # Fallback for HTML within multipart
                    elif part['mimeType'] == 'text/html' and 'data' in part['body']:
                         html_content = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                         soup = BeautifulSoup(html_content, 'html.parser')
                         plain_text_body = soup.get_text() # Basic HTML parsing
                         # Keep the loop going in case a text/plain part exists later
            elif payload.get('mimeType') == 'text/plain' and 'body' in payload and 'data' in payload['body']:
                 plain_text_body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')

            body_text += "\nFull Body (extracted):\n" + (plain_text_body[:1000] if plain_text_body else "[Body not easily extracted]") + "...\n" # Truncate for prompt
            email_contents.append(f"--- Email ID: {msg_id} ---\n{body_text}\n")

        # 4. Combine content and prompt Gemini for summary
        full_context = "\n".join(email_contents)
        prompt = f"""Please summarize the key points from the following emails matching the query '{query}':\n\n{full_context}"""

        client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )

        print("\n--- Gemini Summary ---")
        if response.text: print(response.text.strip())
        else: print(f"Blocked or empty response.")

    except Exception as e:
        print(f"An error occurred summarizing emails: {e}")
    
# Authentication setup (OAuth 2.0 flow) is required to get 'creds'
# Build service objects:
from googleapiclient.discovery import build
gmail_service = build('gmail', 'v1', credentials=creds)
# calendar_service = build('calendar', 'v3', credentials=creds)
# docs_service = build('docs', 'v1', credentials=creds)
# drive_service = build('drive', 'v3', credentials=creds)
