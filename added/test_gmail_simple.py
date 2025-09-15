#!/usr/bin/env python3
"""
Simple Gmail Test - bypasses verification issues
"""

import os
import json
import base64
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

def test_gmail_connection():
    """Test Gmail API connection with minimal scope"""
    
    # Use minimal scope for testing
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    creds = None
    
    # Check if we have saved credentials
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Use your gmail.json file
            flow = InstalledAppFlow.from_client_secrets_file('gmail.json', SCOPES)
            
            # Try different port to avoid conflicts
            try:
                creds = flow.run_local_server(port=8080, prompt='consent')
            except Exception as e:
                print(f"Local server failed: {e}")
                print("Trying manual flow...")
                creds = flow.run_console()
        
        # Save credentials for next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    try:
        # Build Gmail service
        service = build('gmail', 'v1', credentials=creds)
        
        # Test: Get user profile (minimal request)
        profile = service.users().getProfile(userId='me').execute()
        print(f"✅ Gmail API connected successfully!")
        print(f"Email: {profile.get('emailAddress')}")
        print(f"Total messages: {profile.get('messagesTotal')}")
        
        # Test: Get first 3 messages (not just unread)
        print("\n📧 Testing message retrieval...")
        result = service.users().messages().list(userId='me', maxResults=3).execute()
        messages = result.get('messages', [])
        
        print(f"Found {len(messages)} messages")
        
        for i, msg in enumerate(messages, 1):
            msg_data = service.users().messages().get(userId='me', id=msg['id'], format='metadata').execute()
            headers = msg_data['payload'].get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            print(f"{i}. {subject[:50]}...")
        
        return service
        
    except Exception as e:
        print(f"❌ Error connecting to Gmail: {e}")
        return None

if __name__ == "__main__":
    print("🔧 Testing Gmail API connection...")
    service = test_gmail_connection()
    
    if service:
        print("\n✅ Gmail API is working! You can now run the full email digest.")
    else:
        print("\n❌ Gmail API connection failed. Check the steps above.")