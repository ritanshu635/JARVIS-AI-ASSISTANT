#!/usr/bin/env python3
"""
JARVIS Complete Test - Full voice interaction with actual action execution
"""
import asyncio
import time
import subprocess
import webbrowser
import speech_recognition as sr
from engine.ai_router import AIRouter
from engine.voice_engine import VoiceEngine
from engine.android_controller import AndroidController
from engine.database_manager import initialize_default_data
from engine.command_processor import CommandProcessor
from engine.command import speak

class JarvisCompleteTest:
    def __init__(self):
        self.running = False
        self.initialize_components()
    
    def initialize_components(self):
        """Initialize all JARVIS components"""
        print("🚀 Initializing JARVIS Complete System...")
        
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
    
    async def process_and_execute_command(self, command):
        """Process voice command and execute the action"""
        try:
            print(f"⚙️ Processing: '{command}'")
            
            # Use command processor
            result = await self.command_processor.process_command(command)
            
            if result['success']:
                response = result['response']
                print(f"🤖 JARVIS: {response}")
                
                # Speak the response
                speak(response)
                
                # Execute the actual action
                await self.execute_action(result)
                
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
    
    async def execute_action(self, result):
        """Execute the actual action based on command processing result"""
        action = result.get('action', '')
        
        try:
            print(f"🎯 Executing action: {action}")
            
            if action == 'open_system_app':
                app_name = result.get('app_name', '')
                app_path = result.get('app_path', '')
                
                if app_path:
                    subprocess.Popen(app_path, shell=True)
                    print(f"📱 Opened {app_name} from database")
                else:
                    # Try common applications
                    common_apps = {
                        'notepad': 'notepad.exe',
                        'calculator': 'calc.exe',
                        'paint': 'mspaint.exe',
                        'chrome': 'chrome.exe',
                        'edge': 'msedge.exe',
                        'explorer': 'explorer.exe',
                        'cmd': 'cmd.exe',
                        'powershell': 'powershell.exe'
                    }
                    
                    if app_name.lower() in common_apps:
                        subprocess.Popen(common_apps[app_name.lower()], shell=True)
                        print(f"📱 Opened {app_name}")
                        speak(f"{app_name} is now open")
                    else:
                        try:
                            subprocess.Popen(app_name, shell=True)
                            print(f"📱 Opened {app_name}")
                            speak(f"{app_name} is now open")
                        except:
                            print(f"❌ Could not open {app_name}")
                            speak(f"Sorry, I could not find {app_name}")
            
            elif action == 'open_website':
                url = result.get('url', '')
                app_name = result.get('app_name', '')
                if url:
                    webbrowser.open(url)
                    print(f"🌐 Opened website: {url}")
                    speak(f"{app_name} is now open in your browser")
            
            elif action == 'open_generic':
                app_name = result.get('app_name', '')
                if app_name:
                    try:
                        subprocess.Popen(app_name, shell=True)
                        print(f"📱 Opened {app_name}")
                        speak(f"{app_name} is now open")
                    except:
                        print(f"❌ Could not open {app_name}")
                        speak(f"Sorry, I could not find {app_name}")
            
            elif action == 'play_media':
                media_name = result.get('media_name', '')
                platform = result.get('platform', 'youtube')
                if media_name:
                    search_url = f"https://www.youtube.com/results?search_query={media_name.replace(' ', '+')}"
                    webbrowser.open(search_url)
                    print(f"🎵 Searching YouTube for: {media_name}")
                    speak(f"Playing {media_name} on YouTube")
            
            elif action == 'make_call':
                contact = result.get('contact', {})
                if contact:
                    call_result = self.android_controller.make_call(
                        contact['mobile_no'], 
                        contact['name']
                    )
                    if call_result['success']:
                        print(f"📞 Calling {contact['name']} at {contact['mobile_no']}")
                        speak(f"Calling {contact['name']} now")
                    else:
                        print(f"❌ Call failed: {call_result['message']}")
                        speak("Sorry, the call failed. Please check your phone connection.")
            
            elif action == 'whatsapp_message':
                contact = result.get('contact', {})
                if contact:
                    speak("What message would you like to send?")
                    print("🎤 Listening for message content...")
                    message = self.listen_for_speech(timeout=10)
                    
                    if message:
                        whatsapp_result = self.android_controller.whatsapp_automation(
                            contact['name'], message, 'message'
                        )
                        if whatsapp_result['success']:
                            print(f"📱 Sent WhatsApp message to {contact['name']}: {message}")
                            speak(f"WhatsApp message sent to {contact['name']}")
                        else:
                            print(f"❌ WhatsApp failed: {whatsapp_result['message']}")
                            speak("Sorry, WhatsApp message failed")
                    else:
                        speak("I didn't hear the message content")
            
            elif action == 'whatsapp_call':
                contact = result.get('contact', {})
                if contact:
                    whatsapp_result = self.android_controller.whatsapp_automation(
                        contact['name'], '', 'call'
                    )
                    if whatsapp_result['success']:
                        print(f"📱 WhatsApp calling {contact['name']}")
                        speak(f"Starting WhatsApp call with {contact['name']}")
                    else:
                        print(f"❌ WhatsApp call failed: {whatsapp_result['message']}")
                        speak("Sorry, WhatsApp call failed")
            
            elif action == 'web_search':
                search_query = result.get('search_query', '')
                search_engine = result.get('search_engine', 'google')
                if search_query:
                    if search_engine == 'youtube':
                        search_url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"
                    else:
                        search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
                    
                    webbrowser.open(search_url)
                    print(f"🔍 Searching {search_engine} for: {search_query}")
                    speak(f"Searching {search_engine} for {search_query}")
            
            elif action in ['mute', 'unmute', 'volume_up', 'volume_down', 'minimize_all', 'shutdown', 'restart']:
                try:
                    import pyautogui
                    if action == 'mute':
                        pyautogui.press('volumemute')
                        speak("System muted")
                    elif action == 'unmute':
                        pyautogui.press('volumemute')
                        speak("System unmuted")
                    elif action == 'volume_up':
                        pyautogui.press('volumeup')
                        speak("Volume increased")
                    elif action == 'volume_down':
                        pyautogui.press('volumedown')
                        speak("Volume decreased")
                    elif action == 'minimize_all':
                        pyautogui.hotkey('win', 'd')
                        speak("All windows minimized")
                    elif action == 'shutdown':
                        speak("Shutting down the system in 10 seconds. Say cancel to stop.")
                        print("🎤 Listening for cancel command...")
                        cancel_command = self.listen_for_speech(timeout=5)
                        if cancel_command and 'cancel' in cancel_command.lower():
                            speak("Shutdown cancelled")
                        else:
                            subprocess.run("shutdown /s /t 5", shell=True)
                    elif action == 'restart':
                        speak("Restarting the system in 10 seconds. Say cancel to stop.")
                        print("🎤 Listening for cancel command...")
                        cancel_command = self.listen_for_speech(timeout=5)
                        if cancel_command and 'cancel' in cancel_command.lower():
                            speak("Restart cancelled")
                        else:
                            subprocess.run("shutdown /r /t 5", shell=True)
                    
                    print(f"🔊 System {action.replace('_', ' ')}")
                except Exception as e:
                    print(f"❌ System control error: {e}")
                    speak("System control failed")
            
            elif action == 'greeting_response':
                # Greeting already handled by response
                pass
            
            elif action == 'time_date_info':
                # Time/date already handled by response
                pass
            
            elif action == 'ai_response':
                # AI response already handled
                pass
            
            elif action == 'content_generated':
                # Content generation already handled
                pass
            
            else:
                print(f"⚠️ Unknown action: {action}")
            
        except Exception as e:
            print(f"❌ Action execution error: {e}")
            speak("Sorry, I encountered an error while executing that command")
    
    def run_interactive_mode(self):
        """Run interactive voice mode with full action execution"""
        print("\n" + "="*60)
        print("🎤 JARVIS COMPLETE VOICE INTERACTION MODE")
        print("="*60)
        print("💡 Say commands and I'll execute them!")
        print("💡 Try: 'Open notepad', 'Call Tom', 'Play music', 'What time is it'")
        print("💡 Say 'stop jarvis' or 'quit' to exit")
        print("💡 Press Ctrl+C to force quit")
        print("-"*60)
        
        # Initial greeting
        greeting = "Hello! I am JARVIS, your complete voice assistant. I'm ready to help you and execute your commands. What can I do for you?"
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
                        farewell = "Goodbye! It was nice helping you today."
                        print(f"🤖 JARVIS: {farewell}")
                        speak(farewell)
                        break
                    
                    # Process and execute the command
                    asyncio.run(self.process_and_execute_command(command))
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
            print("🔚 JARVIS Complete Mode ended")

def main():
    """Main function"""
    # Create JARVIS instance
    jarvis = JarvisCompleteTest()
    
    # Run interactive mode
    jarvis.run_interactive_mode()

if __name__ == "__main__":
    main()