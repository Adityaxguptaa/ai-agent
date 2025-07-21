from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os.path
import base64
import re

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def extract_email_body(payload):
    # Recursive decode function to handle multipart emails
    if payload.get('parts'):
        for part in payload['parts']:
            if part.get("mimeType") == "text/plain":
                data = part['body'].get('data')
                if data:
                    decoded = base64.urlsafe_b64decode(data).decode("utf-8")
                    return decoded
            elif part.get('parts'):
                return extract_email_body(part)
    else:
        data = payload['body'].get('data')
        if data:
            decoded = base64.urlsafe_b64decode(data).decode("utf-8")
            return decoded
    return "No readable content found."

def check_latest_email(service):
    response = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=1).execute()
    messages = response.get('messages', [])
    if not messages:
        return None, None
    msg_id = messages[0]['id']
    msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    headers = msg['payload'].get('headers', [])

    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
    sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
    body = extract_email_body(msg['payload'])

    content = f"📧 *From:* {sender}\n📌 *Subject:* {subject}\n\n📝 *Message:*\n{body}"
    return msg_id, content
