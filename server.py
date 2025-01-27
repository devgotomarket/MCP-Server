from mcp.server.fastmcp import FastMCP
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64
import os
import pickle
import logging
import time
import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gmail_mcp_server")

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
mcp = FastMCP("gmail_mcp_server")

def get_gmail_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)

@mcp.tool()
def send_email(to: str, subject: str, body: str) -> dict:
    try:
        service = get_gmail_service()
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        result = service.users().messages().send(
            userId='me',
            body={'raw': raw}
        ).execute()
        
        return {"result": f"Email sent successfully (Message ID: {result['id']})"}
        
    except Exception as e:
        return {"error": str(e)}
    
def get_calendar_service():
    CALENDAR_SCOPES = ['https://www.googleapis.com/auth/calendar']
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', CALENDAR_SCOPES)
    creds = flow.run_local_server(port=0)
    return build('calendar', 'v3', credentials=creds)
@mcp.tool()
def list_events(max_results: int = 3) -> dict:
    try:
        calendar = get_calendar_service()
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        
        events_result = calendar.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        if not events:
            return {"result": "No upcoming events found"}
            
        output = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            output.append(f"Event: {event['summary']}\nTime: {start}\n---")
            
        return {"result": "\n".join(output)}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def create_event(summary: str, start_time: str, end_time: str, description: str = "") -> dict:
    try:
        calendar = get_calendar_service()
        event = {
            'summary': summary,
            'description': description,
            'start': {'dateTime': start_time, 'timeZone': 'UTC'},
            'end': {'dateTime': end_time, 'timeZone': 'UTC'}
        }
        
        event = calendar.events().insert(calendarId='primary', body=event).execute()
        return {"result": f"Event created: {event.get('htmlLink')}"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def search_emails(query: str, max_results: int = 10) -> dict:
    try:
        service = get_gmail_service()
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=max_results
        ).execute()
        
        messages = []
        for msg in results.get('messages', []):
            email = service.users().messages().get(userId='me', id=msg['id']).execute()
            headers = email['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            messages.append(f"ID: {msg['id']}\nFrom: {sender}\nSubject: {subject}\n---")
            
        return {"result": "\n".join(messages) if messages else "No emails found"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_email_content(email_id: str) -> dict:
   try:
       service = get_gmail_service()
       email = service.users().messages().get(userId='me', id=email_id).execute()
       
       headers = email['payload']['headers']
       subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
       sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
       
       if 'parts' in email['payload']:
           content = email['payload']['parts'][0]['body'].get('data', '')
       else:
           content = email['payload']['body'].get('data', '')
           
       decoded_content = base64.urlsafe_b64decode(content).decode() if content else 'No content'
       
       return {
           "result": f"From: {sender}\nSubject: {subject}\n\nContent:\n{decoded_content}"
       }
   except Exception as e:
       return {"error": str(e)}

@mcp.resource("gmail://inbox") 
def get_emails() -> str:
    """Get recent emails from inbox"""
    try:
        service = get_gmail_service()
        results = service.users().messages().list(
            userId='me', 
            maxResults=10
        ).execute()
        
        messages = []
        for msg in results.get('messages', []):
            email = service.users().messages().get(
                userId='me',
                id=msg['id']
            ).execute()
            headers = email['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            messages.append(f"From: {sender}\nSubject: {subject}\n---")
            
        return "\n".join(messages) if messages else "No messages found"
        
    except Exception as e:
        logger.error(f"Get emails failed: {e}")
        return str(e)

if __name__ == "__main__":
    mcp.run()