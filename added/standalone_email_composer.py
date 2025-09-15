#!/usr/bin/env python3
"""
Standalone Intelligent Email Composer for JARVIS
Complete voice-controlled email composition system
Independent script that doesn't require existing JARVIS files
"""

import asyncio
import speech_recognition as sr
import pyttsx3
import smtplib
import ssl
import os
import json
import requests
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional

class StandaloneEmailComposer:
    """Complete standalone email composer with voice control and AI"""
    
    def __init__(self):
        print("📧 Initializing Standalone Email Composer...")
        self.speak("Initializing JARVIS email composer system")
        
        # Initialize TTS engine
        self.tts_engine = pyttsx3.init('sapi5')
        self.setup_tts()
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Ollama configuration
        self.ollama_url = 'http://localhost:11434'
        self.ollama_model = 'llama3.2:3b'  # You can change this to your preferred model
        
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
                "Who should I address this leave application to? Say manager, principal, HR, or a specific name.",
                "What type of leave is this? Say sick leave, vacation, personal leave, or emergency leave.",
                "From which date do you want the leave to start? You can say tomorrow, next Monday, or a specific date.",
                "Until which date do you need the leave? Say the end date or number of days.",
                "What is the reason for your leave? Please provide details."
            ],
            'job': [
                "What position are you applying for? Please state the job title.",
                "What company is this application for? Say the company name.",
                "How many years of experience do you have in this field?",
                "What are your key skills for this role? List your main qualifications.",
                "When are you available to start? Say immediately, two weeks notice, or a specific date."
            ],
            'meeting': [
                "What is the purpose of this meeting? Describe the main agenda.",
                "When would you like to schedule the meeting? Provide date and time preferences.",
                "How long should the meeting be? Say 30 minutes, 1 hour, etc.",
                "Who else should attend this meeting? List the participants.",
                "Should this be in-person or virtual? Say in-person, online, or Teams meeting."
            ],
            'complaint': [
                "What department or person is this complaint about? Be specific.",
                "When did this issue occur? Provide the date or time frame.",
                "What exactly happened? Describe the problem in detail.",
                "What resolution are you seeking? Say what you want them to do.",
                "Do you have any supporting documents or evidence? Say yes or no and describe."
            ],
            'inquiry': [
                "What specific information are you looking for? Be detailed about your question.",
                "Is this for personal or business purposes? Specify the context.",
                "When do you need this information by? Provide a deadline if any.",
                "Have you tried contacting them before about this? Say yes or no and when."
            ],
            'invitation': [
                "What type of event is this invitation for? Say party, meeting, wedding, etc.",
                "When is the event scheduled? Provide date and time.",
                "Where will the event take place? Give the location or address.",
                "What should guests know or bring? Any special instructions.",
                "How should they RSVP? Provide contact method and deadline."
            ],
            'thank': [
                "What are you thanking them for specifically? Describe their help or action.",
                "When did this happen? Provide the timeframe.",
                "How did their help impact you? Explain the positive outcome.",
                "Would you like to mention any future collaboration? Say yes or no."
            ],
            'apology': [
                "What are you apologizing for? Describe the issue or mistake.",
                "When did this incident occur? Provide the date or timeframe.",
                "How will you prevent this in the future? Explain your plan.",
                "What steps are you taking to make it right? Describe your corrective actions."
            ]
        }
        
        print("✅ Standalone Email Composer initialized!")
        self.speak("Email composer ready sir. I can help you write professional emails with smart suggestions.")
    
    def setup_tts(self):
        """Setup text-to-speech engine"""
        try:
            voices = self.tts_engine.getProperty('voices')
            if voices and len(voices) > 0:
                # Try to use a male voice (David) if available
                for voice in voices:
                    if 'david' in voice.name.lower() or 'male' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
                else:
                    self.tts_engine.setProperty('voice', voices[0].id)
            
            self.tts_engine.setProperty('rate', 174)  # Speech rate
            self.tts_engine.setProperty('volume', 1.0)  # Max volume
            
        except Exception as e:
            print(f"⚠️ TTS setup warning: {e}")
    
    def speak(self, text):
        """Text-to-speech function"""
        try:
            text = str(text).strip()
            if not text:
                return
                
            print(f"🔊 JARVIS: {text}")
            
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            
        except Exception as e:
            print(f"❌ TTS error: {e}")
            print(f"🔊 Fallback: {text}")
    
    def setup_email_credentials(self):
        """Setup email credentials for sending"""
        try:
            print("📧 Setting up email credentials...")
            self.speak("I need your email credentials to send emails sir. Please provide your Gmail address and app password.")
            
            # Get email address
            self.speak("What is your Gmail address?")
            self.sender_email = input("Enter your Gmail address: ").strip()
            
            # Get app password
            self.speak("What is your Gmail app password? You can create one in your Google account security settings.")
            print("📝 Note: This should be an App Password, not your regular Gmail password")
            print("📝 To create: Google Account → Security → 2-Step Verification → App passwords")
            self.sender_password = input("Enter your Gmail app password: ").strip()
            
            print("✅ Email credentials configured!")
            self.speak("Email credentials configured successfully sir!")
            
        except Exception as e:
            print(f"❌ Error setting up email credentials: {e}")
            self.speak("Error setting up email credentials")
    
    def calibrate_microphone(self):
        """Calibrate microphone for ambient noise"""
        print("🎤 Calibrating microphone...")
        self.speak("Calibrating microphone sir. Please remain quiet for a moment.")
        
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
            
            print("✅ Microphone calibrated!")
            self.speak("Microphone calibrated successfully sir.")
        except Exception as e:
            print(f"⚠️ Microphone calibration warning: {e}")
            self.speak("Microphone calibration completed.")
    
    def listen_for_speech(self, prompt_text="", timeout=15):
        """Listen for speech input with timeout"""
        try:
            if prompt_text:
                self.speak(prompt_text)
            
            print(f"🎤 Listening... (timeout: {timeout}s)")
            
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=20)
            
            try:
                # Use Google Speech Recognition
                text = self.recognizer.recognize_google(audio)
                print(f"🎤 You said: {text}")
                return text.strip()
                
            except sr.UnknownValueError:
                self.speak("Sorry sir, I didn't understand that. Please try again.")
                return None
            except sr.RequestError as e:
                self.speak("Sorry sir, there was an error with speech recognition.")
                print(f"❌ Speech recognition error: {e}")
                return None
                
        except sr.WaitTimeoutError:
            self.speak("I didn't hear anything sir. Let's continue.")
            return None
        except Exception as e:
            print(f"❌ Speech listening error: {e}")
            return None
    
    def detect_email_subject_type(self, subject):
        """Detect the type of email based on subject"""
        subject_lower = subject.lower()
        
        # Define keywords for each email type
        keywords = {
            'leave': ['leave', 'vacation', 'sick', 'time off', 'absence', 'holiday', 'day off'],
            'job': ['application', 'job', 'position', 'employment', 'career', 'resume', 'cv', 'hiring'],
            'meeting': ['meeting', 'appointment', 'schedule', 'conference', 'discussion', 'call'],
            'complaint': ['complaint', 'issue', 'problem', 'concern', 'dissatisfied', 'unhappy'],
            'inquiry': ['inquiry', 'question', 'information', 'details', 'clarification', 'help'],
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
                "What tone should this email have? Say formal, casual, or friendly."
            ]
        
        self.speak(f"I'll ask you some questions to help write a better {email_type} email sir.")
        
        answers = {}
        
        for i, question in enumerate(questions, 1):
            self.speak(f"Question {i}: {question}")
            
            # Listen for answer
            answer = self.listen_for_speech("", timeout=20)
            
            if answer:
                answers[f"question_{i}"] = {
                    'question': question,
                    'answer': answer
                }
                self.speak("Got it sir.")
            else:
                self.speak("Skipping this question sir.")
        
        return answers
    
    def test_ollama_connection(self):
        """Test if Ollama is available"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    async def generate_email_content_with_ollama(self, recipient, subject, email_type, additional_info):
        """Generate email content using Ollama AI"""
        try:
            if not self.test_ollama_connection():
                print("⚠️ Ollama not available, using template generation")
                return self.generate_fallback_content(recipient, subject, email_type, additional_info)
            
            self.speak("Generating your email content using AI sir. Please wait.")
            
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
7. Sign off with "Best regards," and leave space for name

Generate only the email body content (no subject line, as that's already provided).
Make it sound professional and courteous.
"""
            
            # Call Ollama API
            response = requests.post(
                f'{self.ollama_url}/api/generate',
                json={
                    'model': self.ollama_model,
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        'temperature': 0.7,
                        'max_tokens': 1000
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('response', '').strip()
                
                if content:
                    self.speak("Email content generated successfully sir!")
                    return content
                else:
                    return self.generate_fallback_content(recipient, subject, email_type, additional_info)
            else:
                print(f"❌ Ollama API error: {response.status_code}")
                return self.generate_fallback_content(recipient, subject, email_type, additional_info)
                
        except Exception as e:
            print(f"❌ Error generating email content: {e}")
            self.speak("Error generating email content sir. Creating basic template.")
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
                content += f"- {info['question'].split('?')[0]}: {info['answer']}\n"
            
            content += "\nI would appreciate your approval for this leave request.\n\nThank you for your consideration."
        
        elif email_type == 'job':
            content = f"""I am writing to express my interest in the position mentioned in the subject line.

Details:
"""
            for info in additional_info.values():
                content += f"- {info['question'].split('?')[0]}: {info['answer']}\n"
            
            content += "\nI look forward to hearing from you.\n\nThank you for your time and consideration."
        
        elif email_type == 'meeting':
            content = f"""I would like to schedule a meeting with you.

Meeting Details:
"""
            for info in additional_info.values():
                content += f"- {info['question'].split('?')[0]}: {info['answer']}\n"
            
            content += "\nPlease let me know if this works for you.\n\nThank you."
        
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
        
        self.speak("Here's your email preview sir. I'll read the content for you.")
        
        # Read the email content
        self.speak(f"To: {recipient}")
        self.speak(f"Subject: {subject}")
        self.speak("Email content:")
        
        # Read content in chunks for better speech
        sentences = content.split('. ')
        for sentence in sentences:
            if sentence.strip():
                self.speak(sentence.strip())
                time.sleep(0.5)  # Brief pause between sentences
    
    def send_email(self, recipient, subject, content):
        """Send the email via SMTP"""
        try:
            if not self.sender_email or not self.sender_password:
                self.speak("Email credentials not configured sir. Please set them up first.")
                return False
            
            self.speak("Sending your email now sir.")
            
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
            
            self.speak("Email sent successfully sir!")
            print("✅ Email sent successfully!")
            return True
            
        except Exception as e:
            error_msg = f"Error sending email: {str(e)}"
            print(f"❌ {error_msg}")
            self.speak("Sorry sir, there was an error sending the email.")
            return False
    
    def save_email_draft(self, recipient, subject, content):
        """Save email as draft"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"email_draft_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("="*60 + "\n")
                f.write("JARVIS EMAIL DRAFT\n")
                f.write("="*60 + "\n")
                f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"To: {recipient}\n")
                f.write(f"Subject: {subject}\n")
                f.write("-"*60 + "\n")
                f.write(content)
                f.write("\n" + "="*60)
            
            self.speak(f"Email draft saved as {filename} sir.")
            print(f"💾 Email draft saved as: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error saving draft: {e}")
            self.speak("Error saving email draft sir.")
            return None
    
    async def compose_email_interactive(self):
        """Interactive email composition process"""
        try:
            self.speak("I will help you write an email sir. Let me ask you some questions.")
            
            # Step 1: Get recipient
            self.speak("Whom should I send this email to sir? Please provide the email address.")
            recipient = self.listen_for_speech("", timeout=20)
            
            if not recipient:
                self.speak("I need the recipient's email address to continue sir.")
                return
            
            self.current_email['recipient'] = recipient
            self.speak(f"Email will be sent to {recipient}")
            
            # Step 2: Get subject
            self.speak("What should be the subject of this email sir?")
            subject = self.listen_for_speech("", timeout=20)
            
            if not subject:
                self.speak("I need a subject for the email sir.")
                return
            
            self.current_email['subject'] = subject
            self.speak(f"Subject set as: {subject}")
            
            # Step 3: Detect email type and ask follow-up questions
            email_type = self.detect_email_subject_type(subject)
            print(f"🎯 Detected email type: {email_type}")
            
            if email_type != 'general':
                self.speak(f"I detected this is a {email_type} email sir. Let me ask some relevant questions.")
            else:
                self.speak("I'll ask some general questions to help write your email sir.")
            
            # Ask follow-up questions
            additional_info = await self.ask_follow_up_questions(email_type)
            self.current_email['additional_info'] = additional_info
            
            # Step 4: Generate email content
            self.speak("Now I'll generate the email content based on your responses sir.")
            content = await self.generate_email_content_with_ollama(
                recipient, subject, email_type, additional_info
            )
            
            self.current_email['content'] = content
            
            # Step 5: Preview email
            self.preview_email(recipient, subject, content)
            
            # Step 6: Ask for confirmation
            self.speak("Are you satisfied with this email sir? Say yes to send, no to regenerate, or save to save as draft.")
            confirmation = self.listen_for_speech("", timeout=15)
            
            if confirmation:
                confirmation_lower = confirmation.lower()
                
                if 'yes' in confirmation_lower or 'send' in confirmation_lower:
                    # Send email
                    if self.send_email(recipient, subject, content):
                        self.speak("Your email has been sent successfully sir!")
                    else:
                        # Save as draft if sending fails
                        self.save_email_draft(recipient, subject, content)
                
                elif 'save' in confirmation_lower or 'draft' in confirmation_lower:
                    # Save as draft
                    self.save_email_draft(recipient, subject, content)
                
                elif 'no' in confirmation_lower or 'regenerate' in confirmation_lower:
                    self.speak("Let me regenerate the email content sir.")
                    # Regenerate content
                    new_content = await self.generate_email_content_with_ollama(
                        recipient, subject, email_type, additional_info
                    )
                    self.preview_email(recipient, subject, new_content)
                    self.save_email_draft(recipient, subject, new_content)
                
                else:
                    self.speak("I didn't understand sir. Saving as draft for now.")
                    self.save_email_draft(recipient, subject, content)
            else:
                self.speak("Saving email as draft sir.")
                self.save_email_draft(recipient, subject, content)
            
        except Exception as e:
            error_msg = f"Error in email composition: {str(e)}"
            print(f"❌ {error_msg}")
            self.speak("Sorry sir, I encountered an error while composing the email.")
    
    def listen_for_wake_word(self):
        """Listen for wake word 'JARVIS'"""
        print("👂 Listening for wake word 'JARVIS'...")
        
        while True:
            try:
                with self.microphone as source:
                    print("🔍 Say 'JARVIS' to wake me up...")
                    audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=3)
                
                try:
                    text = self.recognizer.recognize_google(audio).lower()
                    print(f"🎤 Heard: {text}")
                    
                    if "jarvis" in text:
                        print("🎯 Wake word detected!")
                        self.speak("Yes sir, I'm listening. How can I help you with your email?")
                        return True
                        
                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    print(f"❌ Speech recognition error: {e}")
                    time.sleep(1)
                    
            except sr.WaitTimeoutError:
                pass
            except KeyboardInterrupt:
                print("\n👋 Stopping wake word detection...")
                return False
    
    async def voice_mode(self):
        """Voice-activated email composition mode"""
        print("\n🎙️ JARVIS Email Composer - Voice Mode")
        print("=" * 45)
        print("Say 'JARVIS' to wake me up")
        print("Then I'll help you compose an email")
        print("Press Ctrl+C to exit")
        
        while True:
            try:
                if self.listen_for_wake_word():
                    await self.compose_email_interactive()
                    
                    self.speak("Is there anything else I can help you with sir? Say JARVIS to compose another email, or press Ctrl+C to exit.")
                    time.sleep(2)
                else:
                    break
                    
            except KeyboardInterrupt:
                print("\n👋 Email Composer shutting down...")
                self.speak("Email composer shutting down. Goodbye sir!")
                break
            except Exception as e:
                print(f"❌ Voice mode error: {e}")
                self.speak("I encountered an error sir. Restarting voice recognition.")
                time.sleep(2)
    
    async def quick_test(self):
        """Quick test of email generation"""
        print("\n🧪 Quick Email Generation Test")
        print("=" * 35)
        
        # Test data
        test_recipient = "manager@company.com"
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
        self.speak("Generating test email sir.")
        
        content = await self.generate_email_content_with_ollama(
            test_recipient, test_subject, test_type, test_info
        )
        
        print("📋 Test email generated:")
        self.preview_email(test_recipient, test_subject, content)
        
        # Save test email
        self.save_email_draft(test_recipient, test_subject, content)
        
        self.speak("Test completed sir. Email draft has been saved.")

async def main():
    """Main function"""
    print("📧 JARVIS Standalone Email Composer")
    print("=" * 40)
    print("🤖 Complete voice-controlled email system")
    print("🧠 AI-powered content generation")
    print("🎤 Speech recognition and TTS")
    
    # Initialize composer
    composer = StandaloneEmailComposer()
    
    # Check Ollama connection
    if composer.test_ollama_connection():
        print("✅ Ollama AI connected")
        composer.speak("AI system ready sir.")
    else:
        print("⚠️ Ollama not available - will use template generation")
        composer.speak("AI system not available sir, but I can still help with basic templates.")
    
    # Menu
    print("\n📋 What would you like to do sir?")
    print("1. Voice mode (say 'JARVIS' to compose emails)")
    print("2. Interactive mode (compose email now)")
    print("3. Setup email credentials")
    print("4. Test email generation")
    print("5. Calibrate microphone")
    print("6. Exit")
    
    choice = input("\nEnter your choice (1-6): ").strip()
    
    if choice == '1':
        # Calibrate microphone first
        composer.calibrate_microphone()
        
        # Start voice mode
        await composer.voice_mode()
    
    elif choice == '2':
        # Calibrate microphone first
        composer.calibrate_microphone()
        
        # Start interactive email composition
        await composer.compose_email_interactive()
    
    elif choice == '3':
        composer.setup_email_credentials()
    
    elif choice == '4':
        await composer.quick_test()
    
    elif choice == '5':
        composer.calibrate_microphone()
    
    elif choice == '6':
        composer.speak("Goodbye sir!")
        print("👋 Goodbye!")
    
    else:
        print("❌ Invalid choice")
        composer.speak("Invalid choice sir.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Email Composer shutting down...")
    except Exception as e:
        print(f"❌ System error: {e}")
        import traceback
        traceback.print_exc()