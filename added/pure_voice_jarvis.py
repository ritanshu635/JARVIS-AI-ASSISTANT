#!/usr/bin/env python3
"""
Pure Voice JARVIS - Just like the original 3 folders
Starts listening immediately, no menus, pure voice control
Does ANYTHING you tell it to do
"""

import asyncio
import speech_recognition as sr
import threading
import time
import re
import os
import subprocess
import webbrowser
import pyautogui
from engine.database_manager import DatabaseManager
from engine.android_controller import AndroidController
from engine.ai_router import AIRouter
from engine.command import speak

class PureVoiceJarvis:
    """Pure voice JARVIS - no menus, just voice control"""
    
    def __init__(self):
        print("🤖 JARVIS Starting...")
        
        # Initialize components silently
        self.db_manager = DatabaseManager()
        self.android_controller = AndroidController(self.db_manager)
        self.ai_router = AIRouter()
        
        # Speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Calibrate microphone
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        
        print("✅ JARVIS Online")
        speak("JARVIS online and ready for commands")
    
    def listen_continuously(self):
        """Listen for any voice command"""
        while True:
            try:
                with self.microphone as source:
                    print("👂 Listening...")
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=8)
                
                try:
                    command = self.recognizer.recognize_google(audio)
                    print(f"🎤 You said: {command}")
                    return command
                    
                except sr.UnknownValueError:
                    pass  # Couldn't understand, keep listening
                except sr.RequestError:
                    print("❌ Speech recognition error")
                    time.sleep(1)
                    
            except sr.WaitTimeoutError:
                pass  # Timeout, keep listening
            except KeyboardInterrupt:
                return "quit"
    
    async def execute_any_command(self, command):
        """Execute ANY command using AI and direct actions"""
        try:
            command_lower = command.lower()
            
            # Exit commands
            if any(word in command_lower for word in ['quit', 'exit', 'stop jarvis', 'goodbye']):
                speak("Goodbye!")
                return False
            
            print(f"🔄 Executing: {command}")
            
            # Phone commands - direct execution
            if self.handle_phone_commands(command_lower):
                return True
            
            # System commands - direct execution  
            if self.handle_system_commands(command_lower):
                return True
            
            # Web commands - direct execution
            if self.handle_web_commands(command_lower):
                return True
            
            # App commands - direct execution
            if self.handle_app_commands(command_lower):
                return True
            
            # AI for everything else
            await self.handle_with_ai(command)
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            speak("I encountered an error")
            return True
    
    def handle_phone_commands(self, command):
        """Handle phone-related commands directly"""
        
        # Call commands
        if 'call' in command:
            contact_name = self.extract_contact_name(command, 'call')
            if contact_name:
                contact = self.db_manager.get_contact(contact_name)
                if contact:
                    speak(f"Calling {contact['name']}")
                    result = self.android_controller.make_call(contact['mobile_no'], contact['name'])
                    speak(result['message'])
                    return True
                else:
                    speak(f"Contact {contact_name} not found")
                    return True
        
        # WhatsApp commands
        elif 'whatsapp' in command:
            contact_name = self.extract_contact_name(command, 'whatsapp')
            message = self.extract_message(command)
            
            if contact_name:
                contact = self.db_manager.get_contact(contact_name)
                if contact:
                    if 'call' in command:
                        speak(f"Starting WhatsApp call with {contact['name']}")
                        result = self.android_controller.whatsapp_automation(contact['name'], '', 'call')
                    else:
                        speak(f"Sending WhatsApp to {contact['name']}")
                        result = self.android_controller.whatsapp_automation(contact['name'], message, 'message')
                    speak(result['message'])
                    return True
                else:
                    speak(f"Contact {contact_name} not found")
                    return True
        
        # SMS commands
        elif 'message' in command or 'text' in command:
            contact_name = self.extract_contact_name(command, 'message')
            message = self.extract_message(command)
            
            if contact_name:
                contact = self.db_manager.get_contact(contact_name)
                if contact:
                    speak(f"Sending message to {contact['name']}")
                    result = self.android_controller.send_sms(contact['mobile_no'], message, contact['name'])
                    speak(result['message'])
                    return True
                else:
                    speak(f"Contact {contact_name} not found")
                    return True
        
        return False
    
    def handle_system_commands(self, command):
        """Handle system commands directly"""
        
        # Volume control
        if 'volume up' in command or 'increase volume' in command:
            self.control_volume('up')
            return True
        elif 'volume down' in command or 'decrease volume' in command:
            self.control_volume('down')
            return True
        elif 'mute' in command and 'unmute' not in command:
            self.control_volume('mute')
            return True
        elif 'unmute' in command:
            self.control_volume('unmute')
            return True
        
        # Brightness control
        elif 'brightness up' in command or 'increase brightness' in command:
            self.control_brightness('up')
            return True
        elif 'brightness down' in command or 'decrease brightness' in command or 'reduce brightness' in command:
            self.control_brightness('down')
            return True
        
        # Power commands
        elif 'shutdown' in command:
            speak("Shutting down computer")
            os.system('shutdown /s /t 5')
            return True
        elif 'restart' in command:
            speak("Restarting computer")
            os.system('shutdown /r /t 5')
            return True
        
        # Window management
        elif 'minimize all' in command or 'minimize windows' in command:
            speak("Minimizing all windows")
            pyautogui.hotkey('win', 'd')
            return True
        elif 'maximize' in command:
            speak("Maximizing window")
            pyautogui.hotkey('win', 'up')
            return True
        
        return False
    
    def handle_web_commands(self, command):
        """Handle web commands directly"""
        
        # Search commands
        if 'search' in command:
            query = command.replace('search', '').replace('for', '').replace('on google', '').replace('on youtube', '').strip()
            
            if 'youtube' in command:
                speak(f"Searching YouTube for {query}")
                webbrowser.open(f'https://www.youtube.com/results?search_query={query}')
            else:
                speak(f"Searching Google for {query}")
                webbrowser.open(f'https://www.google.com/search?q={query}')
            return True
        
        # Play commands
        elif 'play' in command and ('youtube' in command or 'music' in command or 'video' in command):
            query = command.replace('play', '').replace('on youtube', '').replace('music', '').replace('video', '').strip()
            speak(f"Playing {query} on YouTube")
            
            try:
                import pywhatkit as kit
                kit.playonyt(query)
            except:
                webbrowser.open(f'https://www.youtube.com/results?search_query={query}')
            return True
        
        return False
    
    def handle_app_commands(self, command):
        """Handle application commands directly"""
        
        # Open commands
        if 'open' in command:
            app_name = command.replace('open', '').strip()
            
            # Common apps
            apps = {
                'notepad': 'notepad.exe',
                'calculator': 'calc.exe',
                'paint': 'mspaint.exe',
                'chrome': 'chrome.exe',
                'firefox': 'firefox.exe',
                'edge': 'msedge.exe',
                'explorer': 'explorer.exe',
                'file explorer': 'explorer.exe',
                'task manager': 'taskmgr.exe',
                'control panel': 'control.exe',
                'recycle bin': 'explorer.exe shell:RecycleBinFolder'
            }
            
            app_lower = app_name.lower()
            if app_lower in apps:
                speak(f"Opening {app_name}")
                if app_lower == 'recycle bin':
                    os.system('explorer.exe shell:RecycleBinFolder')
                else:
                    try:
                        os.startfile(apps[app_lower])
                    except:
                        os.system(f'start "" "{apps[app_lower]}"')
                return True
            else:
                # Try generic open
                speak(f"Opening {app_name}")
                try:
                    os.system(f'start "" "{app_name}"')
                except:
                    speak(f"Could not open {app_name}")
                return True
        
        # Close commands
        elif 'close' in command:
            app_name = command.replace('close', '').strip()
            
            processes = {
                'chrome': 'chrome.exe',
                'firefox': 'firefox.exe',
                'edge': 'msedge.exe',
                'notepad': 'notepad.exe',
                'calculator': 'calc.exe',
                'paint': 'mspaint.exe'
            }
            
            app_lower = app_name.lower()
            process_name = processes.get(app_lower, f'{app_name}.exe')
            
            speak(f"Closing {app_name}")
            result = subprocess.run(['taskkill', '/f', '/im', process_name], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                speak(f"Closed {app_name}")
            else:
                speak(f"{app_name} was not running")
            return True
        
        return False
    
    def control_volume(self, action):
        """Control system volume"""
        try:
            if action == 'up':
                for _ in range(5):
                    pyautogui.press('volumeup')
                speak("Volume increased")
            elif action == 'down':
                for _ in range(5):
                    pyautogui.press('volumedown')
                speak("Volume decreased")
            elif action == 'mute':
                pyautogui.press('volumemute')
                speak("Volume muted")
            elif action == 'unmute':
                pyautogui.press('volumemute')
                speak("Volume unmuted")
        except Exception as e:
            speak("Volume control failed")
    
    def control_brightness(self, action):
        """Control screen brightness"""
        try:
            if action == 'up':
                # Use PowerShell to increase brightness
                subprocess.run(['powershell', '-Command', 
                              "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,100)"], 
                              capture_output=True)
                speak("Brightness increased")
            elif action == 'down':
                subprocess.run(['powershell', '-Command', 
                              "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,30)"], 
                              capture_output=True)
                speak("Brightness decreased")
        except Exception as e:
            speak("Brightness control not available")
    
    def extract_contact_name(self, command, action_word):
        """Extract contact name from command"""
        # Remove action word and common words
        words_to_remove = [action_word, 'to', 'a', 'the', 'please', 'can', 'you']
        words = command.split()
        
        filtered_words = []
        for word in words:
            if word.lower() not in words_to_remove:
                filtered_words.append(word)
        
        # Look for known contacts
        contacts = self.db_manager.get_all_contacts()
        for contact in contacts:
            contact_name_lower = contact['name'].lower()
            for word in filtered_words:
                if word.lower() in contact_name_lower or contact_name_lower in word.lower():
                    return contact['name']
        
        # Return first remaining word as potential contact name
        return filtered_words[0] if filtered_words else None
    
    def extract_message(self, command):
        """Extract message from command"""
        # Look for message indicators
        message_indicators = ['saying', 'tell him', 'tell her', 'message', 'text']
        
        for indicator in message_indicators:
            if indicator in command:
                parts = command.split(indicator, 1)
                if len(parts) > 1:
                    return parts[1].strip()
        
        return "Hello from JARVIS"  # Default message
    
    async def handle_with_ai(self, command):
        """Use AI for complex commands"""
        try:
            speak("Let me think about that")
            
            ai_result = await self.ai_router.process_query(command, "general")
            
            if ai_result['success']:
                response = ai_result['response']
                speak(response)
            else:
                speak("I'm not sure how to help with that")
                
        except Exception as e:
            speak("I couldn't process that request")
    
    async def start_listening(self):
        """Main listening loop - starts immediately"""
        print("\n🎙️ JARVIS Voice Control Active")
        print("Just speak your commands naturally...")
        
        # Show available contacts
        contacts = self.db_manager.get_all_contacts()
        if contacts:
            print(f"📞 Available contacts: {', '.join([c['name'] for c in contacts])}")
        
        while True:
            try:
                command = self.listen_continuously()
                
                if command and command != "quit":
                    should_continue = await self.execute_any_command(command)
                    if not should_continue:
                        break
                elif command == "quit":
                    speak("JARVIS shutting down")
                    break
                    
            except KeyboardInterrupt:
                print("\n👋 JARVIS shutting down...")
                speak("JARVIS shutting down")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(1)

# Start JARVIS immediately - no menus!
async def main():
    jarvis = PureVoiceJarvis()
    await jarvis.start_listening()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()