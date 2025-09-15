#!/usr/bin/env python3
"""
Email Digest Assistant for JARVIS
Reads top 10 unread emails and provides ChatGPT summary
"""

import os
import json
import base64
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import openai
from datetime import datetime

class EmailDigestAssistant:
    def __init__(self):
        # Gmail API scope - read only
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
        self.service = None
        self.openai_client = None
        
        print("🤖 Initializing Email Digest Assistant...")
        self.setup_gmail_api()
        self.setup_openai()
    
    def setup_gmail_api(self):
        """Setup Gmail API authentication"""
        try:
            print("📧 Setting up Gmail API...")
            
            creds = None
            # Check if we have saved credentials
            if os.path.exists('gmail_token.pickle'):
                with open('gmail_token.pickle', 'rb') as token:
                    creds = pickle.load(token)
            
            # If no valid credentials, authenticate
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    print("🔄 Refreshing Gmail credentials...")
                    creds.refresh(Request())
                else:
                    print("🔐 First time Gmail authentication required...")
                    print("📱 Browser will open for Gmail login...")
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'gmail.json', self.SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save credentials for next time
                with open('gmail_token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
                    print("✅ Gmail credentials saved for future use")
            
            # Build Gmail service
            self.service = build('gmail', 'v1', credentials=creds)
            print("✅ Gmail API ready")
            
        except Exception as e:
            print(f"❌ Gmail API setup error: {e}")
            self.service = None
    
    def setup_openai(self):
        """Setup OpenAI API"""
        try:
            print("🧠 Setting up ChatGPT API...")
            
            # You'll need to add your OpenAI API key here
            # Get it from: https://platform.openai.com/api-keys
            api_key = input("Enter your OpenAI API key (or press Enter to skip): ").strip()
            
            if api_key:
                self.openai_client = openai.OpenAI(api_key=api_key)
                print("✅ ChatGPT API ready")
            else:
                print("⚠️ No OpenAI API key provided - will use local summarization")
                self.openai_client = None
                
        except Exception as e:
            print(f"❌ OpenAI setup error: {e}")
            self.openai_client = None
    
    def fetch_unread_emails(self, max_emails=5):
        """Fetch top unread emails"""
        if not self.service:
            return []
        
        try:
            print(f"📬 Fetching top {max_emails} unread emails...")
            
            # Search for unread emails
            results = self.service.users().messages().list(
                userId='me', 
                q='is:unread',
                maxResults=max_emails
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                print("📭 No unread emails found")
                return []
            
            print(f"📧 Found {len(messages)} unread emails")
            
            emails = []
            for i, message in enumerate(messages, 1):
                print(f"📖 Reading email {i}/{len(messages)}...")
                
                # Get full message details
                msg = self.service.users().messages().get(
                    userId='me', 
                    id=message['id'],
                    format='full'
                ).execute()
                
                # Extract email data
                email_data = self.extract_email_data(msg)
                if email_data:
                    emails.append(email_data)
            
            print(f"✅ Successfully processed {len(emails)} emails")
            return emails
            
        except Exception as e:
            print(f"❌ Error fetching emails: {e}")
            return []
    
    def extract_email_data(self, message):
        """Extract subject, sender, and body from email message"""
        try:
            payload = message['payload']
            headers = payload.get('headers', [])
            
            # Extract headers
            subject = ""
            sender = ""
            date = ""
            
            for header in headers:
                name = header.get('name', '').lower()
                value = header.get('value', '')
                
                if name == 'subject':
                    subject = value
                elif name == 'from':
                    sender = value
                elif name == 'date':
                    date = value
            
            # Extract body text
            body = self.extract_body_text(payload)
            
            return {
                'subject': subject,
                'sender': sender,
                'date': date,
                'body': body[:1000],  # Limit body length
                'snippet': message.get('snippet', '')
            }
            
        except Exception as e:
            print(f"⚠️ Error extracting email data: {e}")
            return None
    
    def extract_body_text(self, payload):
        """Extract plain text from email body"""
        try:
            body = ""
            
            # Check if payload has body data
            if 'body' in payload and 'data' in payload['body']:
                body = base64.urlsafe_b64decode(
                    payload['body']['data']
                ).decode('utf-8', errors='ignore')
            
            # Check for multipart content
            elif 'parts' in payload:
                for part in payload['parts']:
                    if part.get('mimeType') == 'text/plain':
                        if 'data' in part.get('body', {}):
                            part_body = base64.urlsafe_b64decode(
                                part['body']['data']
                            ).decode('utf-8', errors='ignore')
                            body += part_body
                    elif 'parts' in part:
                        # Recursive for nested parts
                        body += self.extract_body_text(part)
            
            return body.strip()
            
        except Exception as e:
            print(f"⚠️ Error extracting body: {e}")
            return ""
    
    def summarize_emails_with_chatgpt(self, emails):
        """Summarize emails using ChatGPT"""
        if not self.openai_client or not emails:
            return self.summarize_emails_local(emails)
        
        try:
            print("🧠 Generating summary with ChatGPT...")
            
            # Prepare email content for ChatGPT
            email_content = ""
            for i, email in enumerate(emails, 1):
                email_content += f"""
EMAIL {i}:
Subject: {email['subject']}
From: {email['sender']}
Content: {email['body'][:500]}...

"""
            
            # ChatGPT prompt
            prompt = f"""You are an AI assistant that summarizes emails. Please analyze these {len(emails)} unread emails and provide:

1. **URGENT EMAILS** (if any): Emails that need immediate attention
2. **ACTION REQUIRED**: Emails that need responses or actions
3. **INFORMATIONAL**: Important updates or information
4. **SUMMARY**: Brief overview of all emails

Here are the emails:
{email_content}

Please provide a clear, organized summary that helps prioritize what needs attention."""

            # Call ChatGPT API
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful email assistant that creates concise, actionable email summaries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content
            print("✅ ChatGPT summary generated")
            return summary
            
        except Exception as e:
            print(f"❌ ChatGPT error: {e}")
            print("🔄 Falling back to local summarization...")
            return self.summarize_emails_local(emails)
    
    def summarize_emails_local(self, emails):
        """Local email summarization (fallback)"""
        if not emails:
            return "No unread emails found."
        
        print("📝 Generating local summary...")
        
        summary = f"📧 EMAIL DIGEST - {len(emails)} Unread Emails\n"
        summary += "=" * 50 + "\n\n"
        
        urgent_keywords = ['urgent', 'asap', 'immediate', 'deadline', 'important']
        action_keywords = ['please', 'request', 'need', 'action', 'respond', 'reply']
        
        urgent_emails = []
        action_emails = []
        info_emails = []
        
        for email in emails:
            subject_lower = email['subject'].lower()
            body_lower = email['body'].lower()
            
            is_urgent = any(keyword in subject_lower or keyword in body_lower for keyword in urgent_keywords)
            needs_action = any(keyword in subject_lower or keyword in body_lower for keyword in action_keywords)
            
            if is_urgent:
                urgent_emails.append(email)
            elif needs_action:
                action_emails.append(email)
            else:
                info_emails.append(email)
        
        # Build summary
        if urgent_emails:
            summary += "🚨 URGENT EMAILS:\n"
            for email in urgent_emails:
                summary += f"• {email['subject']} (from {email['sender']})\n"
            summary += "\n"
        
        if action_emails:
            summary += "📋 ACTION REQUIRED:\n"
            for email in action_emails:
                summary += f"• {email['subject']} (from {email['sender']})\n"
            summary += "\n"
        
        if info_emails:
            summary += "📰 INFORMATIONAL:\n"
            for email in info_emails:
                summary += f"• {email['subject']} (from {email['sender']})\n"
            summary += "\n"
        
        summary += f"📊 TOTAL: {len(emails)} unread emails processed"
        
        return summary
    
    def run_email_digest(self):
        """Main function to run email digest"""
        print("🚀 Starting Email Digest...")
        print("=" * 60)
        
        # Fetch unread emails
        emails = self.fetch_unread_emails(max_emails=5)
        
        if not emails:
            print("📭 No unread emails to process")
            return
        
        # Generate summary
        summary = self.summarize_emails_with_chatgpt(emails)
        
        # Display results
        print("\n" + "=" * 60)
        print("📋 EMAIL DIGEST SUMMARY")
        print("=" * 60)
        print(summary)
        print("=" * 60)
        
        # Save summary to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"email_digest_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Email Digest - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            f.write(summary)
            f.write("\n\n" + "=" * 60 + "\n")
            f.write("Detailed Emails:\n\n")
            
            for i, email in enumerate(emails, 1):
                f.write(f"EMAIL {i}:\n")
                f.write(f"Subject: {email['subject']}\n")
                f.write(f"From: {email['sender']}\n")
                f.write(f"Date: {email['date']}\n")
                f.write(f"Content: {email['body']}\n")
                f.write("-" * 40 + "\n\n")
        
        print(f"💾 Detailed digest saved to: {filename}")
        print("✅ Email Digest Complete!")

def main():
    """Main function"""
    print("📧 JARVIS Email Digest Assistant")
    print("=" * 60)
    print("📋 This will read your top 5 unread emails and provide a summary")
    print()
    
    # Create assistant
    assistant = EmailDigestAssistant()
    
    if not assistant.service:
        print("❌ Gmail API not available. Please check your gmail.json file.")
        return
    
    # Run digest
    assistant.run_email_digest()

if __name__ == "__main__":
    main()