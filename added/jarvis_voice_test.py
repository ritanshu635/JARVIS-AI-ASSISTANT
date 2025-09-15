#!/usr/bin/env python3
"""
JARVIS Voice Test - Direct voice interaction without web interface
"""
import asyncio
import time
import speech_recognition as sr
from engine.ai_router import AIRouter
from engine.voice_engine import VoiceEngine
from engine.android_controller import AndroidController
from engine.database_manager import initialize_default_data
from engine.command_processor import CommandProcessor
from engine.command import speak

class JarvisVoiceTest:
    def __init__(self):
        self.running = False
        self.initialize_components()
    
    def initialize_components(self):
        """Initialize all JARVIS components"""
        print("🚀 Initializing JARVIS Voice System...")
        
        try:
            # Database
            self.db_manager = initialize_default_data()
            print("✅ Database initialized")
            
            # AI Router
            self.ai_router = AIRouter()
            print("✅ AI Router initialized")
            
            # Voice Engine
            self.voice_engine = VoiceEngine()
            print("✅ Voice Engine initialized")
            
            # Android Controller
            self.android_controller = AndroidController(self.db_manager)
            print("✅ Android Controller initialized")
            
            # Command Processor
            self.command_processor = CommandProcessor(self.ai_router, self.db_manager)
            print("✅ Command Processor initialized")
            
            # Speech Recognition
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # Calibrate microphone
            print("🎤 Calibrating microphone...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("✅ Microphone calibrated")
            
            return True
            
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            return False
    
    def listen_for_speech(self, timeout=5):
        """Listen for speech input"""
        try:
            print("🎤 Listening... (speak now)")
            
            with self.microphone as source:
                # Listen for audio
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=5)
            
            print("🔄 Processing speech...")
            
            # Recognize speech
            text = self.recognizer.recognize_google(audio, language='en-US')
            print(f"🗣️ You said: '{text}'")
            
            return text.strip()
            
        except sr.WaitTimeoutError:
            print("⏰ No speech detected (timeout)")
            return None
        except sr.UnknownValueError:
            print("❓ Could not understand speech")
            return None
        except sr.RequestError as e:
            print(f"❌ Speech recognition error: {e}")
            return None
        except Exception as e:
            print(f"❌ Listen error: {e}")
            return None
    
    async def process_command(self, command):
        """Process voice command"""
        try:
            print(f"⚙️ Processing: '{command}'")
            
            # Use command processor
            result = await self.command_processor.process_command(command)
            
            if result['success']:
                response = result['response']
                print(f"🤖 JARVIS: {response}")
                
                # Speak the response
                speak(response)
                
                # Handle specific actions
                await self.handle_action(result)
                
                return True
            else:
                error_msg = result.get('response', 'Sorry, I could not process that command.')
                print(f"❌ Error: {error_msg}")
                speak(error_msg)
                return False
                
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            print(f"❌ Processing error: {e}")
            speak(error_msg)
            return False
    
    async def handle_action(self, result):
        """Handle specific actions from command processing"""
        action = result.get('action', '')
        
        try:
            if action == 'open_system_app':
                app_name = result.get('app_name', '')
                app_path = result.get('app_path', '')
                if app_path:
                    import subprocess
                    subprocess.Popen(app_path, shell=True)
                    print(f"📱 Opened {app_name}")
            
            elif action == 'open_website':
                url = result.get('url', '')
                if url:
                    import webbrowser
                    webbrowser.open(url)
                    print(f"🌐 Opened website: {url}")
            
            elif action == 'play_media':
                media_name = result.get('media_name', '')
                platform = result.get('platform', 'youtube')
                if media_name:
                    import webbrowser
                    search_url = f"https://www.youtube.com/results?search_query={media_name.replace(' ', '+')}"
                    webbrowser.open(search_url)
                    print(f"🎵 Searching YouTube for: {media_name}")
            
            elif action == 'make_call':
                contact = result.get('contact', {})
                if contact:
                    call_result = self.android_controller.make_call(
                        contact['mobile_no'], 
                        contact['name']
                    )
                    if call_result['success']:
                        print(f"📞 Calling {contact['name']} at {contact['mobile_no']}")
                    else:
                        print(f"❌ Call failed: {call_result['message']}")
                        speak(call_result['message'])
            
            elif action.startswith('whatsapp_'):
                contact = result.get('contact', {})
                message = result.get('message', '')
                action_type = action.replace('whatsapp_', '')
                
                if contact:
                    print(f"📱 WhatsApp {action_type} to {contact['name']}")
                    whatsapp_result = self.android_controller.whatsapp_automation(
                        contact['name'], 
                        message, 
                        action_type
                    )
                    if whatsapp_result['success']:
                        print(f"✅ {whatsapp_result['message']}")
                    else:
                        print(f"❌ WhatsApp failed: {whatsapp_result['message']}")
                        speak(whatsapp_result['message'])
            
            elif action == 'web_search':
                search_query = result.get('search_query', '')
                if search_query:
                    import webbrowser
                    search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
                    webbrowser.open(search_url)
                    print(f"🔍 Searching Google for: {search_query}")
            
            elif action in ['mute', 'unmute', 'volume_up', 'volume_down']:
                import pyautogui
                if action == 'mute':
                    pyautogui.press('volumemute')
                elif action == 'unmute':
                    pyautogui.press('volumemute')
                elif action == 'volume_up':
                    pyautogui.press('volumeup')
                elif action == 'volume_down':
                    pyautogui.press('volumedown')
                print(f"🔊 System {action.replace('_', ' ')}")
            
        except Exception as e:
            print(f"❌ Action handling error: {e}")
    
    def run_interactive_mode(self):
        """Run interactive voice mode"""
        print("\n" + "="*60)
        print("🎤 JARVIS VOICE INTERACTION MODE")
        print("="*60)
        print("💡 Say 'Hello JARVIS' to start")
        print("💡 Say 'stop jarvis' or 'quit' to exit")
        print("💡 Press Ctrl+C to force quit")
        print("-"*60)
        
        # Initial greeting
        greeting = "Hello! I am JARVIS, your voice assistant. I'm ready to help you. What can I do for you?"
        print(f"🤖 JARVIS: {greeting}")
        speak(greeting)
        
        self.running = True
        
        try:
            while self.running:
                print("\n🎧 Waiting for your command...")
                
                # Listen for speech
                command = self.listen_for_speech(timeout=10)
                
                if command:
                    # Check for exit commands
                    if any(exit_word in command.lower() for exit_word in ['stop jarvis', 'quit', 'exit', 'goodbye']):
                        farewell = "Goodbye! It was nice talking to you."
                        print(f"🤖 JARVIS: {farewell}")
                        speak(farewell)
                        break
                    
                    # Process the command
                    asyncio.run(self.process_command(command))
                else:
                    # No speech detected, continue listening
                    continue
                    
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user")
            speak("Goodbye!")
        except Exception as e:
            print(f"\n❌ Runtime error: {e}")
        finally:
            self.running = False
            print("🔚 JARVIS Voice Mode ended")
    
    def run_single_test(self):
        """Run a single voice command test"""
        print("\n" + "="*60)
        print("🧪 JARVIS SINGLE VOICE TEST")
        print("="*60)
        
        # Test TTS first
        test_message = "JARVIS voice system is ready. Please speak a command."
        print(f"🔊 Testing TTS: {test_message}")
        speak(test_message)
        
        # Listen for one command
        command = self.listen_for_speech(timeout=10)
        
        if command:
            # Process the command
            asyncio.run(self.process_command(command))
        else:
            print("❌ No command received")
            speak("I didn't hear any command. Please try again.")

def main():
    """Main function"""
    import sys
    
    # Create JARVIS instance
    jarvis = JarvisVoiceTest()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "single":
            jarvis.run_single_test()
        elif sys.argv[1] == "interactive":
            jarvis.run_interactive_mode()
        else:
            print("Usage: python jarvis_voice_test.py [single|interactive]")
    else:
        # Default to interactive mode
        jarvis.run_interactive_mode()

if __name__ == "__main__":
    main()