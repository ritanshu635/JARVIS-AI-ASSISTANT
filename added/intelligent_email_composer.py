#!/usr/bin/env python3
"""
Intelligent Email Composer for JARVIS
Voice-controlled email composition with smart follow-up questions
Uses Whisper/SpeechRecognition for voice input, pyttsx3 for TTS, and Ollama for content generation
"""

import asyncio
import speech_recognition as sr
import smtplib
import ssl
import os
import json
import requests
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from engine.command import speak
from engine.ai_router import AIRouter
from typing import Dict, List, Optional

class IntelligentEmailComposer:
    """Voice-controlled intelligent email composer with smart follow-up questions"""
    
    def __init__(self):
        print("📧 Initializing Intelligent Email Composer...")
        speak("Initializing email composer system")
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Initialize AI router for content generation
        self.ai_router = AIRouter()
        
        # Email configuration
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = None
        self.sender_password = None
        
        # Email composition state
        self.current_email = {
            'recipient': '',
            'subject': '',
            'content': '',
            'additional_info': {}
        }
        
        # Subject-based question templates
        self.subject_questions = {
            'leave': [
                "Who should I address this leave application to? (manager, principal, HR, etc.)",
                "What type of leave is this? (sick leave, vacation, personal, etc.)",
                "From which date do you want the leave to start?",
                "Until which date do you need the leave?",
                "What is the reason for your leave?"
            ],
            'job': [
                "What position are you applying for?",
                "What company is this application for?",
                "How many years of experience do you have?",
                "What are your key skills for this role?",
                "When are you available to start?"
            ],
            'meeting': [
                "What is the purpose of this meeting?",
                "When would you like to schedule the meeting?",
                "How long should the meeting be?",
                "Who else should attend this meeting?",
                "Should this be in-person or virtual?"
            ],
            'complaint': [
                "What department or person is this complaint about?",
                "When did this issue occur?",
                "What exactly happened?",
                "What resolution are you seeking?",
                "Do you have any supporting documents or evidence?"
            ],
            'inquiry': [
                "What specific information are you looking for?",
                "Is this for personal or business purposes?",
                "When do you need this information by?",
                "Have you tried contacting them before about this?"
            ],
            'invitation': [
                "What type of event is this invitation for?",
                "When is the event scheduled?",
                "Where will the event take place?",
                "What should guests know or bring?",
                "How should they RSVP?"
            ],
            'thank': [
                "What are you thanking them for specifically?",
                "When did this happen?",
                "How did their help impact you?",
                "Would you like to mention any future collaboration?"
            ],
            'apology': [
                "What are you apologizing for?",
                "When did this incident occur?",
                "How will you prevent this in the future?",
                "What steps are you taking to make it right?"
            ]
        }
        
        print("✅ Email Composer initialized!")
        speak("Email composer ready. I can help you write professional emails with smart suggestions.")
    
    def setup_email_credentials(self):
        """Setup email credentials for sending"""
        try:
            print("📧 Setting up email credentials...")
            speak("I need your email credentials to send emails. Please provide your Gmail address and app password.")
            
            # Get email address
            speak("What is your Gmail address?")
            self.sender_email = input("Enter your Gmail address: ").strip()
            
            # Get app password
            speak("What is your Gmail app password? You can create one in your Google account security settings.")
            self.sender_password = input("Enter your Gmail app password: ").strip()
            
            print("✅ Email credentials configured!")
            speak("Email credentials configured successfully!")
            
        except Exception as e:
            print(f"❌ Error setting up email credentials: {e}")
            speak("Error setting up email credentials")
    
    def calibrate_microphone(self):
        """Calibrate microphone for ambient noise"""
        print("🎤 Calibrating microphone...")
        speak("Calibrating microphone. Please remain quiet for a moment.")
        
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        
        print("✅ Microphone calibrated!")
        speak("Microphone calibrated successfully.")
    
    def listen_for_speech(self, prompt_text="", timeout=10):
        """Listen for speech input with timeout"""
        try:
            if prompt_text:
                speak(prompt_text)
            
            print(f"🎤 Listening... (timeout: {timeout}s)")
            
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=15)
            
            try:
                # Use Google Speech Recognition
                text = self.recognizer.recognize_google(audio)
                print(f"🎤 Heard: {text}")
                return text.strip()
                
            except sr.UnknownValueError:
                speak("Sorry, I didn't understand that. Please try again.")
                return None
            except sr.RequestError as e:
                speak("Sorry, there was an error with speech recognition.")
                print(f"❌ Speech recognition error: {e}")
                return None
                
        except sr.WaitTimeoutError:
            speak("I didn't hear anything. Let's continue.")
            return None
        except Exception as e:
            print(f"❌ Speech listening error: {e}")
            return None
    
    def detect_email_subject_type(self, subject):
        """Detect the type of email based on subject"""
        subject_lower = subject.lower()
        
        # Define keywords for each email type
        keywords = {
            'leave': ['leave', 'vacation', 'sick', 'time off', 'absence', 'holiday'],
            'job': ['application', 'job', 'position', 'employment', 'career', 'resume', 'cv'],
            'meeting': ['meeting', 'appointment', 'schedule', 'conference', 'discussion'],
            'complaint': ['complaint', 'issue', 'problem', 'concern', 'dissatisfied'],
            'inquiry': ['inquiry', 'question', 'information', 'details', 'clarification'],
            'invitation': ['invitation', 'invite', 'event', 'party', 'celebration', 'gathering'],
            'thank': ['thank', 'thanks', 'grateful', 'appreciation', 'acknowledge'],
            'apology': ['apology', 'sorry', 'apologize', 'regret', 'mistake']
        }
        
        # Check for matches
        for email_type, type_keywords in keywords.items():
            if any(keyword in subject_lower for keyword in type_keywords):
                return email_type
        
        return 'general'  # Default type
    
    async def ask_follow_up_questions(self, email_type):
        """Ask intelligent follow-up questions based on email type"""
        questions = self.subject_questions.get(email_type, [])
        
        if not questions:
            # For general emails, ask basic questions
            questions = [
                "What is the main purpose of this email?",
                "Is there any specific information you want to include?",
                "What tone should this email have? (formal, casual, friendly, etc.)"
            ]
        
        speak(f"I'll ask you some questions to help write a better {email_type} email.")
        
        answers = {}
        
        for i, question in enumerate(questions, 1):
            speak(f"Question {i}: {question}")
            
            # Listen for answer
            answer = self.listen_for_speech("", timeout=15)
            
            if answer:
                answers[f"question_{i}"] = {
                    'question': question,
                    'answer': answer
                }
                speak("Got it.")
            else:
                speak("Skipping this question.")
        
        return answers
    
    async def generate_email_content(self, recipient, subject, email_type, additional_info):
        """Generate email content using Ollama AI"""
        try:
            speak("Generating your email content using AI. Please wait.")
            
            # Prepare context for AI
            context = f"""
Email Type: {email_type}
Recipient: {recipient}
Subject: {subject}

Additional Information:
"""
            
            for key, info in additional_info.items():
                context += f"- {info['question']}: {info['answer']}\n"
            
            # Create prompt for email generation
            prompt = f"""You are JARVIS, an AI assistant helping to write a professional email. 

Generate a well-structured, professional email with the following details:

{context}

Requirements:
1. Use proper email format with greeting and closing
2. Make it professional but friendly
3. Include all relevant information provided
4. Keep it concise and clear
5. Use appropriate tone for the email type
6. Include proper salutation based on recipient type

Generate only the email body content (no subject line, as that's already provided).
"""
            
            # Generate content using AI Router
            result = await self.ai_router.process_query(prompt, "content")
            
            if result['success']:
                content = result['response'].strip()
                speak("Email content generated successfully!")
                return content
            else:
                speak("Error generating email content. I'll create a basic template.")
                return self.generate_fallback_content(recipient, subject, email_type, additional_info)
                
        except Exception as e:
            print(f"❌ Error generating email content: {e}")
            speak("Error generating email content. Creating basic template.")
            return self.generate_fallback_content(recipient, subject, email_type, additional_info)
    
    def generate_fallback_content(self, recipient, subject, email_type, additional_info):
        """Generate basic email content as fallback"""
        
        # Basic greeting
        if any(title in recipient.lower() for title in ['manager', 'sir', 'madam', 'principal', 'hr']):
            greeting = f"Dear {recipient},"
        else:
            greeting = f"Hello {recipient},"
        
        # Basic content based on type
        if email_type == 'leave':
            content = f"""I am writing to request leave from work.

Please find the details below:
"""
            for info in additional_info.values():
                content += f"- {info['question']}: {info['answer']}\n"
            
            content += "\nI would appreciate your approval for this leave request.\n\nThank you for your consideration."
        
        elif email_type == 'job':
            content = f"""I am writing to express my interest in the position mentioned in the subject line.

Details:
"""
            for info in additional_info.values():
                content += f"- {info['question']}: {info['answer']}\n"
            
            content += "\nI look forward to hearing from you.\n\nThank you for your time and consideration."
        
        else:
            # General template
            content = f"""I hope this email finds you well.

"""
            for info in additional_info.values():
                content += f"{info['answer']}\n\n"
            
            content += "Thank you for your time."
        
        # Add closing
        closing = "\n\nBest regards,\n[Your Name]"
        
        return f"{greeting}\n\n{content}{closing}"
    
    def preview_email(self, recipient, subject, content):
        """Preview the generated email"""
        print("\n" + "="*60)
        print("📧 EMAIL PREVIEW")
        print("="*60)
        print(f"To: {recipient}")
        print(f"Subject: {subject}")
        print("-"*60)
        print(content)
        print("="*60)
        
        speak("Here's your email preview. I'll read the content for you.")
        
        # Read the email content
        speak(f"To: {recipient}")
        speak(f"Subject: {subject}")
        speak("Email content:")
        speak(content)
    
    def send_email(self, recipient, subject, content):
        """Send the email via SMTP"""
        try:
            if not self.sender_email or not self.sender_password:
                speak("Email credentials not configured. Please set them up first.")
                return False
            
            speak("Sending your email now.")
            
            # Create message
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = recipient
            message["Subject"] = subject
            
            # Add body to email
            message.attach(MIMEText(content, "plain"))
            
            # Create SMTP session
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Enable security
            server.login(self.sender_email, self.sender_password)
            
            # Send email
            text = message.as_string()
            server.sendmail(self.sender_email, recipient, text)
            server.quit()
            
            speak("Email sent successfully!")
            print("✅ Email sent successfully!")
            return True
            
        except Exception as e:
            error_msg = f"Error sending email: {str(e)}"
            print(f"❌ {error_msg}")
            speak("Sorry, there was an error sending the email.")
            return False
    
    def save_email_draft(self, recipient, subject, content):
        """Save email as draft"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"email_draft_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("="*60 + "\n")
                f.write("EMAIL DRAFT\n")
                f.write("="*60 + "\n")
                f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"To: {recipient}\n")
                f.write(f"Subject: {subject}\n")
                f.write("-"*60 + "\n")
                f.write(content)
                f.write("\n" + "="*60)
            
            speak(f"Email draft saved as {filename}")
            print(f"💾 Email draft saved as: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error saving draft: {e}")
            speak("Error saving email draft")
            return None
    
    async def compose_email_interactive(self):
        """Interactive email composition process"""
        try:
            speak("I will help you write an email sir. Let me ask you some questions.")
            
            # Step 1: Get recipient
            speak("Whom should I send this email to? Please provide the email address.")
            recipient = self.listen_for_speech("", timeout=15)
            
            if not recipient:
                speak("I need the recipient's email address to continue.")
                return
            
            self.current_email['recipient'] = recipient
            speak(f"Email will be sent to {recipient}")
            
            # Step 2: Get subject
            speak("What should be the subject of this email?")
            subject = self.listen_for_speech("", timeout=15)
            
            if not subject:
                speak("I need a subject for the email.")
                return
            
            self.current_email['subject'] = subject
            speak(f"Subject set as: {subject}")
            
            # Step 3: Detect email type and ask follow-up questions
            email_type = self.detect_email_subject_type(subject)
            print(f"🎯 Detected email type: {email_type}")
            
            if email_type != 'general':
                speak(f"I detected this is a {email_type} email. Let me ask some relevant questions.")
            
            # Ask follow-up questions
            additional_info = await self.ask_follow_up_questions(email_type)
            self.current_email['additional_info'] = additional_info
            
            # Step 4: Generate email content
            speak("Now I'll generate the email content based on your responses.")
            content = await self.generate_email_content(
                recipient, subject, email_type, additional_info
            )
            
            self.current_email['content'] = content
            
            # Step 5: Preview email
            self.preview_email(recipient, subject, content)
            
            # Step 6: Ask for confirmation
            speak("Are you satisfied with this email? Say yes to send, no to regenerate, or save to save as draft.")
            confirmation = self.listen_for_speech("", timeout=10)
            
            if confirmation:
                confirmation_lower = confirmation.lower()
                
                if 'yes' in confirmation_lower or 'send' in confirmation_lower:
                    # Send email
                    if self.send_email(recipient, subject, content):
                        speak("Your email has been sent successfully sir!")
                    else:
                        # Save as draft if sending fails
                        self.save_email_draft(recipient, subject, content)
                
                elif 'save' in confirmation_lower or 'draft' in confirmation_lower:
                    # Save as draft
                    self.save_email_draft(recipient, subject, content)
                
                elif 'no' in confirmation_lower or 'regenerate' in confirmation_lower:
                    speak("Let me regenerate the email content.")
                    # Regenerate content
                    new_content = await self.generate_email_content(
                        recipient, subject, email_type, additional_info
                    )
                    self.preview_email(recipient, subject, new_content)
                    self.save_email_draft(recipient, subject, new_content)
                
                else:
                    speak("I didn't understand. Saving as draft for now.")
                    self.save_email_draft(recipient, subject, content)
            else:
                speak("Saving email as draft.")
                self.save_email_draft(recipient, subject, content)
            
        except Exception as e:
            error_msg = f"Error in email composition: {str(e)}"
            print(f"❌ {error_msg}")
            speak("Sorry, I encountered an error while composing the email.")
    
    async def quick_email_test(self):
        """Quick test of email composition"""
        print("\n🧪 Quick Email Composition Test")
        print("=" * 40)
        
        # Test data
        test_recipient = "test@example.com"
        test_subject = "Leave Application"
        test_type = "leave"
        test_info = {
            'question_1': {
                'question': 'Who should I address this to?',
                'answer': 'Manager'
            },
            'question_2': {
                'question': 'What type of leave?',
                'answer': 'Sick leave'
            },
            'question_3': {
                'question': 'From which date?',
                'answer': 'Tomorrow'
            },
            'question_4': {
                'question': 'Until which date?',
                'answer': 'Day after tomorrow'
            },
            'question_5': {
                'question': 'Reason for leave?',
                'answer': 'Fever and need rest'
            }
        }
        
        print("📧 Generating test email...")
        content = await self.generate_email_content(test_recipient, test_subject, test_type, test_info)
        
        print("📋 Test email generated:")
        self.preview_email(test_recipient, test_subject, content)
        
        # Save test email
        self.save_email_draft(test_recipient, test_subject, content)

async def main():
    """Main function"""
    print("📧 JARVIS Intelligent Email Composer")
    print("=" * 40)
    
    # Initialize composer
    composer = IntelligentEmailComposer()
    
    # Menu
    print("\n📋 What would you like to do?")
    print("1. Compose email with voice (full interactive mode)")
    print("2. Setup email credentials")
    print("3. Test email generation")
    print("4. Calibrate microphone")
    print("5. Exit")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == '1':
        # Calibrate microphone first
        composer.calibrate_microphone()
        
        # Start interactive email composition
        await composer.compose_email_interactive()
    
    elif choice == '2':
        composer.setup_email_credentials()
    
    elif choice == '3':
        await composer.quick_email_test()
    
    elif choice == '4':
        composer.calibrate_microphone()
    
    elif choice == '5':
        speak("Goodbye!")
        print("👋 Goodbye!")
    
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Email Composer shutting down...")
    except Exception as e:
        print(f"❌ System error: {e}")
        import traceback
        traceback.print_exc()