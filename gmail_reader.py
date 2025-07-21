import os.path
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define your SCOPES
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']  # You can update the scope as needed

def check_latest_email(service):
    from base64 import urlsafe_b64decode

    # Get the latest message
    results = service.users().messages().list(userId='me', maxResults=1).execute()
    messages = results.get('messages', [])
    
    if not messages:
        return "No new messages found."

    msg = service.users().messages().get(userId='me', id=messages[0]['id'], format='full').execute()
    
    headers = msg['payload']['headers']
    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
    sender = next((h['value'] for h in headers if h['name'] == 'From'), 'No Sender')

    body = ''
    if 'parts' in msg['payload']:
        for part in msg['payload']['parts']:
            if part['mimeType'] == 'text/plain':
                body = urlsafe_b64decode(part['body']['data']).decode('utf-8')
                break
    else:
        body = urlsafe_b64decode(msg['payload']['body']['data']).decode('utf-8')

    return f"From: {sender}\nSubject: {subject}\nBody: {body[:500]}"


def get_gmail_service():
    creds = None

    # ✅ Check if token.json exists
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # ✅ If no valid creds, generate using local server (this should only run locally)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # ⚠️ Only run this locally to generate token.json
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)

        # ✅ Save the token for future use
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # ✅ Return Gmail service
    service = build('gmail', 'v1', credentials=creds)
    return service
