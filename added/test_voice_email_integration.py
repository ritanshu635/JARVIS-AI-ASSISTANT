#!/usr/bin/env python3
"""
Test Voice Email Integration with JARVIS
"""

import asyncio
import speech_recognition as sr
from engine.command import speak
from voice_email_assistant import handle_voice_email_command

class SimpleVoiceEmailTest:
    """Simple test for voice email integration"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Calibrate microphone
        print("🎤 Calibrating microphone...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        print("✅ Microphone ready")
    
    def listen_for_command(self):
        """Listen for voice command"""
        try:
            print("👂 Listening for command...")
            speak("I'm listening for your command")
            
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=8)
            
            command = self.recognizer.recognize_google(audio)
            print(f"🎤 You said: {command}")
            return command.lower()
            
        except sr.UnknownValueError:
            print("❌ Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"❌ Speech recognition error: {e}")
            return None
        except sr.WaitTimeoutError:
            print("⏰ Listening timeout")
            return None
    
    def process_command(self, command):
        """Process the voice command"""
        if not command:
            return
        
        # Check for email reading commands
        email_triggers = [
            "jarvis read my emails",
            "jarvis read my emails for me", 
            "jarvis check my emails",
            "read my emails",
            "check my emails"
        ]
        
        if any(trigger in command for trigger in email_triggers):
            print("🎯 Email reading command detected!")
            speak("I'll read your emails for you sir")
            
            try:
                result = handle_voice_email_command()
                print(f"✅ Email reading completed successfully")
                return True
            except Exception as e:
                print(f"❌ Error: {e}")
                speak("I encountered an error while reading your emails")
                return False
        else:
            print(f"ℹ️ Command not recognized as email reading: {command}")
            speak("I didn't recognize that as an email command. Try saying 'Jarvis read my emails for me'")
            return False
    
    def run_test(self):
        """Run the voice email test"""
        print("🚀 Starting Voice Email Integration Test")
        print("=" * 50)
        
        speak("Voice email assistant ready. Say 'Jarvis read my emails for me' to test.")
        
        while True:
            try:
                command = self.listen_for_command()
                
                if command:
                    if "exit" in command or "quit" in command or "stop" in command:
                        speak("Goodbye!")
                        break
                    
                    success = self.process_command(command)
                    
                    if success:
                        speak("Email reading test completed successfully!")
                    
                    print("\n" + "=" * 50)
                    speak("Say another command or 'exit' to quit")
                
            except KeyboardInterrupt:
                print("\n👋 Test interrupted by user")
                speak("Test stopped")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                speak("An unexpected error occurred")

if __name__ == "__main__":
    print("🧪 Voice Email Integration Test")
    print("This will test the voice email reading functionality")
    print("Say: 'Jarvis read my emails for me' to test")
    print("Say: 'exit' to quit")
    print()
    
    tester = SimpleVoiceEmailTest()
    tester.run_test()