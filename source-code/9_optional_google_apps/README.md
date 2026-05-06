# Using Gemini with Google Apps

## Get credentials to access Google apps

Getting the creds object is the crucial step for authorizing your Python script to access Google Workspace data (like Gmail, Calendar, etc.) on behalf of a user (which is likely yourself for your solo work). This uses the OAuth 2.0 protocol.

Here is the Google Cloud Console URI:

    https://cloud.google.com/cloud-console/welcome

Create a credential for viewing GMail data and save to a file **~/.gmail_cred**

Here's the standard process, particularly relevant for scripts you run locally (like the examples for your book):

Enable the API: Go to the Google Cloud Console (console.cloud.google.com). Select or create a project. Navigate to "APIs & Services" > "Library" and search for the specific APIs you need (e.g., "Gmail API", "Google Calendar API", "Google Drive API", "Google Docs API"). Enable each one you intend to use.

Create OAuth 2.0 Credentials:

Go to "APIs & Services" > "Credentials".
Click "+ CREATE CREDENTIALS" and choose "OAuth client ID".
If prompted, configure the "OAuth consent screen" first. For testing/personal use, you can often select "External" user type and fill in the required app name, user support email, and developer contact info. You might need to add your Google account email as a "Test user" while the app is in testing status.
For "Application type", choose "Desktop app" (this is suitable for scripts run locally).
Give it a name (e.g., "My Book Script Client").
Click "Create".
Download Credentials File: After creation, a pop-up will show your "Client ID" and "Client Secret". More importantly, click the "DOWNLOAD JSON" button. Save this file and rename it to credentials.json. Place this file in the same directory as your Python script, or somewhere secure where your script can access it. Treat this file like a password - keep it secure!
