#!/usr/bin/env python3
"""
Voice-Controlled JARVIS - Listens to your voice commands and responds
"""

import asyncio
import speech_recognition as sr
import threading
import time
from engine.database_manager import DatabaseManager
from engine.android_controller import AndroidController
from engine.system_controller import SystemController
from engine.command_processor import CommandProcessor
from engine.action_executor import ActionExecutor
from engine.ai_router import AIRouter
from engine.command import speak

class VoiceJarvis:
    """Voice-controlled JARVIS that listens and responds to speech"""
    
    def __init__(self):
        print("🤖 Initializing Voice JARVIS...")
        speak("Initializing JARVIS voice system")
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Initialize JARVIS components
        self.db_manager = DatabaseManager()
        self.android_controller = AndroidController(self.db_manager)
        self.system_controller = SystemController()
        self.ai_router = AIRouter()
        self.command_processor = CommandProcessor(self.ai_router, self.db_manager)
        self.action_executor = ActionExecutor()
        
        # Voice settings
        self.listening = False
        self.wake_word = "jarvis"
        
        print("✅ Voice JARVIS initialized!")
        speak("JARVIS voice system ready. Say 'Hey JARVIS' to wake me up.")
    
    def calibrate_microphone(self):
        """Calibrate microphone for ambient noise"""
        print("🎤 Calibrating microphone for ambient noise...")
        speak("Calibrating microphone. Please remain quiet for a moment.")
        
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        
        print("✅ Microphone calibrated!")
        speak("Microphone calibrated successfully.")
    
    def listen_for_wake_word(self):
        """Listen for wake word 'Hey JARVIS' or 'JARVIS'"""
        print("👂 Listening for wake word...")
        
        while True:
            try:
                with self.microphone as source:
                    print("🔍 Listening for 'Hey JARVIS'...")
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                
                try:
                    # Recognize speech
                    text = self.recognizer.recognize_google(audio).lower()
                    print(f"🎤 Heard: {text}")
                    
                    # Check for wake word
                    if "jarvis" in text or "hey jarvis" in text:
                        print("🎯 Wake word detected!")
                        speak("Yes, I'm listening. What can I do for you?")
                        return True
                        
                except sr.UnknownValueError:
                    # Couldn't understand audio - continue listening
                    pass
                except sr.RequestError as e:
                    print(f"❌ Speech recognition error: {e}")
                    time.sleep(1)
                    
            except sr.WaitTimeoutError:
                # Timeout - continue listening
                pass
            except KeyboardInterrupt:
                print("\n👋 Stopping wake word detection...")
                return False
    
    def listen_for_command(self):
        """Listen for a command after wake word"""
        print("🎤 Listening for command...")
        
        try:
            with self.microphone as source:
                # Listen for command with longer timeout
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            try:
                # Recognize the command
                command = self.recognizer.recognize_google(audio)
                print(f"🎤 Command received: {command}")
                return command
                
            except sr.UnknownValueError:
                speak("Sorry, I didn't understand that. Please try again.")
                return None
            except sr.RequestError as e:
                speak("Sorry, there was an error with speech recognition.")
                print(f"❌ Speech recognition error: {e}")
                return None
                
        except sr.WaitTimeoutError:
            speak("I didn't hear anything. Say 'Hey JARVIS' to wake me up again.")
            return None
    
    async def process_voice_command(self, command):
        """Process the voice command"""
        try:
            print(f"🔄 Processing command: {command}")
            
            # Process the command
            result = await self.command_processor.process_command(command)
            
            print(f"🎯 Intent: {result['intent']}")
            print(f"📝 Response: {result['response']}")
            
            # Execute the action if needed
            if result['success'] and result.get('action'):
                print(f"⚡ Executing action: {result['action']}")
                execution_result = await self.action_executor.execute_action(result)
                
                if execution_result['success']:
                    print(f"✅ Action completed: {execution_result['message']}")
                else:
                    print(f"❌ Action failed: {execution_result['message']}")
                    speak(f"Sorry, {execution_result['message']}")
            else:
                # Just speak the response
                speak(result['response'])
            
            return result
            
        except Exception as e:
            error_msg = f"Error processing command: {str(e)}"
            print(f"❌ {error_msg}")
            speak("Sorry, I encountered an error processing that command")
            return {'success': False, 'message': error_msg}
    
    async def voice_loop(self):
        """Main voice interaction loop"""
        print("\n🎙️ JARVIS Voice Mode Active")
        print("=" * 30)
        print("Say 'Hey JARVIS' to wake me up")
        print("Then give your command")
        print("Say 'JARVIS stop' or 'JARVIS quit' to exit")
        print("Press Ctrl+C to force quit")
        
        while True:
            try:
                # Listen for wake word
                if self.listen_for_wake_word():
                    # Listen for command
                    command = self.listen_for_command()
                    
                    if command:
                        # Check for exit commands
                        if any(word in command.lower() for word in ['stop', 'quit', 'exit', 'goodbye']):
                            speak("Goodbye! JARVIS is shutting down.")
                            break
                        
                        # Process the command
                        await self.process_voice_command(command)
                    
                    # Brief pause before listening for wake word again
                    time.sleep(1)
                else:
                    break
                    
            except KeyboardInterrupt:
                print("\n👋 JARVIS shutting down...")
                speak("JARVIS shutting down. Goodbye!")
                break
            except Exception as e:
                print(f"❌ Voice loop error: {e}")
                speak("I encountered an error. Restarting voice recognition.")
                time.sleep(2)
    
    def test_voice_recognition(self):
        """Test voice recognition"""
        print("\n🧪 Testing Voice Recognition")
        print("=" * 30)
        
        speak("Voice recognition test. Please say something.")
        
        try:
            with self.microphone as source:
                print("🎤 Listening... (speak now)")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            try:
                text = self.recognizer.recognize_google(audio)
                print(f"✅ I heard: {text}")
                speak(f"I heard you say: {text}")
                return True
            except sr.UnknownValueError:
                print("❌ Could not understand audio")
                speak("I couldn't understand what you said")
                return False
            except sr.RequestError as e:
                print(f"❌ Speech recognition error: {e}")
                speak("There was an error with speech recognition")
                return False
                
        except sr.WaitTimeoutError:
            print("❌ No speech detected")
            speak("I didn't hear anything")
            return False
    
    def check_contacts(self):
        """Check available contacts"""
        print("\n📋 Checking Contacts")
        print("=" * 20)
        
        contacts = self.db_manager.get_all_contacts()
        
        if contacts:
            print(f"✅ Found {len(contacts)} contacts:")
            for contact in contacts:
                print(f"  - {contact['name']}: {contact['mobile_no']}")
            
            speak(f"I have {len(contacts)} contacts available")
            
            # Check specifically for Tom
            tom = self.db_manager.get_contact("Tom")
            if tom:
                print(f"🎯 Tom's number: {tom['mobile_no']}")
                speak(f"Tom's number is {tom['mobile_no']}")
        else:
            print("❌ No contacts found")
            speak("No contacts found")

async def main():
    """Main function"""
    print("🤖 JARVIS Voice Assistant")
    print("=" * 25)
    
    # Initialize Voice JARVIS
    jarvis = VoiceJarvis()
    
    # Menu
    print("\n📋 What would you like to do?")
    print("1. Start voice mode (listen to your commands)")
    print("2. Test voice recognition")
    print("3. Check contacts")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == '1':
        # Calibrate microphone first
        jarvis.calibrate_microphone()
        
        # Start voice mode
        await jarvis.voice_loop()
    
    elif choice == '2':
        jarvis.test_voice_recognition()
    
    elif choice == '3':
        jarvis.check_contacts()
    
    elif choice == '4':
        speak("Goodbye!")
        print("👋 Goodbye!")
    
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 JARVIS shutting down...")
    except Exception as e:
        print(f"❌ System error: {e}")
        import traceback
        traceback.print_exc()