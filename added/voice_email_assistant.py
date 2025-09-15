#!/usr/bin/env python3
"""
Voice Email Assistant for JARVIS
Integrates with existing JARVIS voice system to read and summarize emails
"""

import os
import json
import base64
import pickle
import requests
from datetime import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from engine.command import speak

class VoiceEmailAssistant:
    """Voice-activated email digest assistant"""
    
    def __init__(self):
        # Gmail API scope - read only
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
        self.gmail_service = None
        self.ollama_url = 'http://localhost:11434'
        self.ollama_model = 'llama3.2:3b'
        
        print("📧 Initializing Voice Email Assistant...")
        self.setup_gmail_api()
    
    def setup_gmail_api(self):
        """Setup Gmail API authentication"""
        try:
            creds = None
            
            # Check for existing token
            if os.path.exists('gmail_token.pickle'):
                with open('gmail_token.pickle', 'rb') as token:
                    creds = pickle.load(token)
            
            # If no valid credentials, authenticate
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file('gmail.json', self.SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save credentials for next run
                with open('gmail_token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
            
            # Build Gmail service
            self.gmail_service = build('gmail', 'v1', credentials=creds)
            print("✅ Gmail API ready")
            
        except Exception as e:
            print(f"❌ Gmail setup error: {e}")
            self.gmail_service = None
    
    def fetch_unread_emails(self, max_results=5):
        """Fetch top unread emails"""
        if not self.gmail_service:
            return []
        
        try:
            print(f"📬 Fetching top {max_results} unread emails...")
            
            # Get unread message IDs
            result = self.gmail_service.users().messages().list(
                userId='me', 
                q='is:unread', 
                maxResults=max_results
            ).execute()
            
            messages = result.get('messages', [])
            
            if not messages:
                return []
            
            email_list = []
            
            for i, msg in enumerate(messages, 1):
                print(f"📖 Reading email {i}/{len(messages)}...")
                
                # Get full message
                msg_data = self.gmail_service.users().messages().get(
                    userId='me', 
                    id=msg['id'], 
                    format='full'
                ).execute()
                
                # Extract email details
                email_data = self.extract_email_data(msg_data)
                if email_data:
                    email_list.append(email_data)
            
            print(f"✅ Successfully processed {len(email_list)} emails")
            return email_list
            
        except Exception as e:
            print(f"❌ Error fetching emails: {e}")
            return []
    
    def extract_email_data(self, msg_data):
        """Extract subject and body from email message"""
        try:
            payload = msg_data['payload']
            headers = payload.get('headers', [])
            
            # Get subject and sender
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
            
            # Extract body text
            body = self.get_email_body(payload)
            
            return {
                'subject': subject,
                'sender': sender,
                'body': body[:1000]  # Limit body length for processing
            }
            
        except Exception as e:
            print(f"❌ Error extracting email data: {e}")
            return None
    
    def get_email_body(self, payload):
        """Extract plain text body from email payload"""
        try:
            body = ""
            
            # Check if payload has body data
            if 'body' in payload and 'data' in payload['body']:
                body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
            
            # Check parts for multipart messages
            elif 'parts' in payload:
                for part in payload['parts']:
                    if part.get('mimeType') == 'text/plain' and 'data' in part.get('body', {}):
                        body += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                    elif 'parts' in part:
                        # Recursive for nested parts
                        body += self.get_email_body(part)
            
            return body.strip()
            
        except Exception as e:
            print(f"❌ Error extracting body: {e}")
            return ""
    
    def summarize_emails_with_ollama(self, emails):
        """Summarize emails using Ollama"""
        if not emails:
            return "No unread emails found."
        
        try:
            print("🧠 Generating summary with Ollama...")
            
            # Prepare email content for summarization
            email_content = ""
            for i, email in enumerate(emails, 1):
                email_content += f"\nEMAIL {i}:\n"
                email_content += f"From: {email['sender']}\n"
                email_content += f"Subject: {email['subject']}\n"
                email_content += f"Content: {email['body'][:300]}...\n"
                email_content += "-" * 50 + "\n"
            
            # Create summarization prompt
            prompt = f"""You are JARVIS, an AI assistant. Analyze these {len(emails)} unread emails and provide a concise voice-friendly summary.

{email_content}

Provide a brief summary that includes:
1. Total number of emails
2. Most urgent/important emails (if any)
3. Key senders or topics
4. Any action items or deadlines mentioned

Keep the summary conversational and suitable for voice output. Limit to 2-3 sentences per email maximum."""

            # Call Ollama API
            response = requests.post(
                f'{self.ollama_url}/api/generate',
                json={
                    'model': self.ollama_model,
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        'temperature': 0.7,
                        'max_tokens': 500
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                summary = result.get('response', '').strip()
                
                if summary:
                    print("✅ Summary generated successfully")
                    return summary
                else:
                    return self.generate_fallback_summary(emails)
            else:
                print(f"❌ Ollama API error: {response.status_code}")
                return self.generate_fallback_summary(emails)
                
        except Exception as e:
            print(f"❌ Ollama summarization error: {e}")
            return self.generate_fallback_summary(emails)
    
    def generate_fallback_summary(self, emails):
        """Generate a simple fallback summary without AI"""
        if not emails:
            return "No unread emails found."
        
        summary = f"You have {len(emails)} unread emails. "
        
        # List first few subjects
        for i, email in enumerate(emails[:3], 1):
            sender_name = email['sender'].split('<')[0].strip().replace('"', '')
            summary += f"Email {i}: {email['subject']} from {sender_name}. "
        
        if len(emails) > 3:
            summary += f"And {len(emails) - 3} more emails."
        
        return summary
    
    def process_voice_email_command(self):
        """Main function to process voice email command"""
        try:
            print("🎤 Processing voice email command...")
            speak("I'll check your emails for you sir.")
            
            # Fetch unread emails
            emails = self.fetch_unread_emails(5)
            
            if not emails:
                response = "You have no unread emails at the moment sir."
                speak(response)
                return response
            
            # Generate summary
            summary = self.summarize_emails_with_ollama(emails)
            
            # Clean summary for speech
            clean_summary = self.clean_text_for_speech(summary)
            
            # Speak the summary
            speak(clean_summary)
            
            # Save detailed summary to file
            self.save_email_digest(emails, summary)
            
            return clean_summary
            
        except Exception as e:
            error_msg = f"I encountered an error while checking your emails: {str(e)}"
            speak(error_msg)
            return error_msg
    
    def clean_text_for_speech(self, text):
        """Clean text for better speech output"""
        try:
            # Remove markdown formatting
            clean_text = text.replace("**", "")
            clean_text = clean_text.replace("*", "")
            clean_text = clean_text.replace("#", "")
            clean_text = clean_text.replace("- ", "")
            clean_text = clean_text.replace("  ", " ")
            
            # Replace common abbreviations for better speech
            clean_text = clean_text.replace("&", "and")
            clean_text = clean_text.replace("@", "at")
            clean_text = clean_text.replace("etc.", "etcetera")
            
            return clean_text.strip()
            
        except Exception as e:
            print(f"❌ Text cleaning error: {e}")
            return text
    
    def save_email_digest(self, emails, summary):
        """Save detailed email digest to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"voice_email_digest_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("JARVIS VOICE EMAIL DIGEST\n")
                f.write("=" * 60 + "\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Unread Emails: {len(emails)}\n\n")
                
                f.write("SUMMARY:\n")
                f.write("-" * 20 + "\n")
                f.write(summary + "\n\n")
                
                f.write("DETAILED EMAIL LIST:\n")
                f.write("-" * 30 + "\n")
                
                for i, email in enumerate(emails, 1):
                    f.write(f"\nEMAIL {i}:\n")
                    f.write(f"From: {email['sender']}\n")
                    f.write(f"Subject: {email['subject']}\n")
                    f.write(f"Preview: {email['body'][:200]}...\n")
                    f.write("-" * 40 + "\n")
            
            print(f"💾 Email digest saved to: {filename}")
            
        except Exception as e:
            print(f"❌ Error saving digest: {e}")

# Global instance for easy access
voice_email_assistant = VoiceEmailAssistant()

def handle_voice_email_command():
    """Handle voice email command - called from main JARVIS"""
    return voice_email_assistant.process_voice_email_command()

# Test function
if __name__ == "__main__":
    print("🧪 Testing Voice Email Assistant...")
    assistant = VoiceEmailAssistant()
    result = assistant.process_voice_email_command()
    print(f"Result: {result}")