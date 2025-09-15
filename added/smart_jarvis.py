#!/usr/bin/env python3
"""
Smart JARVIS - AI-Powered Voice Assistant
Understands ANY command you give it and responds intelligently
Uses your phone's WhatsApp, calls, SMS via ADB
"""

import asyncio
import speech_recognition as sr
import threading
import time
import re
from engine.database_manager import DatabaseManager
from engine.android_controller import AndroidController
from engine.system_controller import SystemController
from engine.ai_router import AIRouter
from engine.command import speak

class SmartJarvis:
    """AI-powered JARVIS that understands any command"""
    
    def __init__(self):
        print("🤖 Initializing Smart JARVIS AI...")
        speak("Initializing JARVIS artificial intelligence system")
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Initialize JARVIS components
        self.db_manager = DatabaseManager()
        self.android_controller = AndroidController(self.db_manager)
        self.system_controller = SystemController()
        self.ai_router = AIRouter()
        
        # AI conversation context
        self.conversation_context = []
        
        print("✅ Smart JARVIS AI ready!")
        speak("JARVIS AI system online. I can understand any command you give me.")
    
    def calibrate_microphone(self):
        """Calibrate microphone"""
        print("🎤 Calibrating microphone...")
        speak("Calibrating microphone for optimal voice recognition")
        
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        
        print("✅ Microphone calibrated!")
        speak("Microphone calibrated. I'm ready to listen.")
    
    def listen_continuously(self):
        """Listen for wake word or direct commands"""
        print("👂 Listening for commands...")
        
        while True:
            try:
                with self.microphone as source:
                    print("🔍 Listening... (say 'Hey JARVIS' or give direct command)")
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                
                try:
                    text = self.recognizer.recognize_google(audio).lower()
                    print(f"🎤 Heard: {text}")
                    
                    # Check for wake word or direct command
                    if "jarvis" in text or self.is_command(text):
                        print("🎯 Command detected!")
                        
                        if "jarvis" in text:
                            # Remove wake word and process remaining
                            command = re.sub(r'\b(hey\s+)?jarvis\b', '', text).strip()
                            if command:
                                return command
                            else:
                                speak("Yes, I'm listening. What can I do for you?")
                                return self.listen_for_command()
                        else:
                            return text
                        
                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    print(f"❌ Speech recognition error: {e}")
                    time.sleep(1)
                    
            except sr.WaitTimeoutError:
                pass
            except KeyboardInterrupt:
                return None
    
    def is_command(self, text):
        """Check if text looks like a command"""
        command_indicators = [
            'call', 'message', 'whatsapp', 'open', 'close', 'play', 'search',
            'volume', 'mute', 'shutdown', 'restart', 'minimize', 'maximize',
            'what', 'how', 'when', 'where', 'why', 'tell me', 'show me'
        ]
        
        return any(indicator in text.lower() for indicator in command_indicators)
    
    def listen_for_command(self):
        """Listen for a specific command"""
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            command = self.recognizer.recognize_google(audio)
            print(f"🎤 Command: {command}")
            return command
            
        except sr.UnknownValueError:
            speak("I didn't catch that. Could you repeat?")
            return None
        except sr.RequestError:
            speak("Speech recognition error occurred")
            return None
        except sr.WaitTimeoutError:
            speak("I didn't hear anything")
            return None
    
    async def understand_and_execute(self, command):
        """Use AI to understand any command and execute it"""
        try:
            print(f"🧠 Analyzing command: {command}")
            speak("Let me understand what you want me to do")
            
            # Add to conversation context
            self.conversation_context.append(f"User: {command}")
            
            # Use AI to analyze the command
            analysis_prompt = f"""
            Analyze this user command and determine what action to take: "{command}"
            
            Available actions:
            1. PHONE_CALL - if user wants to call someone
            2. SEND_SMS - if user wants to send text message
            3. WHATSAPP_MESSAGE - if user wants to send WhatsApp message
            4. WHATSAPP_CALL - if user wants to make WhatsApp call
            5. OPEN_APP - if user wants to open an application
            6. CLOSE_APP - if user wants to close an application
            7. SYSTEM_CONTROL - if user wants to control volume, brightness, etc.
            8. WEB_SEARCH - if user wants to search something online
            9. PLAY_MEDIA - if user wants to play music/video
            10. GENERAL_QUESTION - if user is asking a question or having conversation
            
            Available contacts: Tom (7420817379)
            
            Respond in this format:
            ACTION: [action_type]
            TARGET: [person/app/query]
            MESSAGE: [message if applicable]
            DETAILS: [any additional details]
            """
            
            ai_result = await self.ai_router.process_query(analysis_prompt, "general")
            
            if ai_result['success']:
                analysis = ai_result['response']
                print(f"🧠 AI Analysis: {analysis}")
                
                # Parse AI response
                action_info = self.parse_ai_analysis(analysis, command)
                
                # Execute the action
                await self.execute_parsed_action(action_info, command)
            else:
                # Fallback to direct execution
                await self.fallback_execution(command)
                
        except Exception as e:
            print(f"❌ Error understanding command: {e}")
            speak("I'm having trouble understanding that command. Could you try rephrasing it?")
    
    def parse_ai_analysis(self, analysis, original_command):
        """Parse AI analysis into actionable information"""
        action_info = {
            'action': 'GENERAL_QUESTION',
            'target': '',
            'message': '',
            'details': original_command
        }
        
        try:
            lines = analysis.split('\n')
            for line in lines:
                if line.startswith('ACTION:'):
                    action_info['action'] = line.split(':', 1)[1].strip()
                elif line.startswith('TARGET:'):
                    action_info['target'] = line.split(':', 1)[1].strip()
                elif line.startswith('MESSAGE:'):
                    action_info['message'] = line.split(':', 1)[1].strip()
                elif line.startswith('DETAILS:'):
                    action_info['details'] = line.split(':', 1)[1].strip()
        except:
            pass
        
        return action_info
    
    async def execute_parsed_action(self, action_info, original_command):
        """Execute the parsed action"""
        action = action_info['action']
        target = action_info['target']
        message = action_info['message']
        
        try:
            if action == 'PHONE_CALL':
                await self.handle_phone_call(target)
            
            elif action == 'SEND_SMS':
                await self.handle_sms(target, message)
            
            elif action == 'WHATSAPP_MESSAGE':
                await self.handle_whatsapp_message(target, message)
            
            elif action == 'WHATSAPP_CALL':
                await self.handle_whatsapp_call(target)
            
            elif action == 'OPEN_APP':
                await self.handle_open_app(target)
            
            elif action == 'CLOSE_APP':
                await self.handle_close_app(target)
            
            elif action == 'SYSTEM_CONTROL':
                await self.handle_system_control(original_command)
            
            elif action == 'WEB_SEARCH':
                await self.handle_web_search(target)
            
            elif action == 'PLAY_MEDIA':
                await self.handle_play_media(target)
            
            else:  # GENERAL_QUESTION
                await self.handle_general_question(original_command)
                
        except Exception as e:
            print(f"❌ Execution error: {e}")
            speak("I encountered an error while executing that command")
    
    async def handle_phone_call(self, contact_name):
        """Handle phone call"""
        contact = self.db_manager.get_contact(contact_name)
        if contact:
            speak(f"Calling {contact['name']}")
            result = self.android_controller.make_call(contact['mobile_no'], contact['name'])
            speak(result['message'])
        else:
            speak(f"I couldn't find {contact_name} in your contacts")
    
    async def handle_sms(self, contact_name, message):
        """Handle SMS"""
        contact = self.db_manager.get_contact(contact_name)
        if contact:
            if not message:
                speak(f"What message would you like to send to {contact['name']}?")
                message = self.listen_for_command()
            
            if message:
                speak(f"Sending message to {contact['name']}")
                result = self.android_controller.send_sms(contact['mobile_no'], message, contact['name'])
                speak(result['message'])
        else:
            speak(f"I couldn't find {contact_name} in your contacts")
    
    async def handle_whatsapp_message(self, contact_name, message):
        """Handle WhatsApp message"""
        contact = self.db_manager.get_contact(contact_name)
        if contact:
            if not message:
                speak(f"What WhatsApp message would you like to send to {contact['name']}?")
                message = self.listen_for_command()
            
            if message:
                speak(f"Sending WhatsApp message to {contact['name']}")
                result = self.android_controller.whatsapp_automation(contact['name'], message, 'message')
                speak(result['message'])
        else:
            speak(f"I couldn't find {contact_name} in your contacts")
    
    async def handle_whatsapp_call(self, contact_name):
        """Handle WhatsApp call"""
        contact = self.db_manager.get_contact(contact_name)
        if contact:
            speak(f"Starting WhatsApp call with {contact['name']}")
            result = self.android_controller.whatsapp_automation(contact['name'], '', 'call')
            speak(result['message'])
        else:
            speak(f"I couldn't find {contact_name} in your contacts")
    
    async def handle_open_app(self, app_name):
        """Handle opening application"""
        speak(f"Opening {app_name}")
        result = self.system_controller.open_application(app_name)
        speak(result['message'])
    
    async def handle_close_app(self, app_name):
        """Handle closing application"""
        speak(f"Closing {app_name}")
        result = self.system_controller.close_application(app_name)
        speak(result['message'])
    
    async def handle_system_control(self, command):
        """Handle system control commands"""
        if 'volume up' in command.lower():
            result = self.system_controller.control_volume('up')
        elif 'volume down' in command.lower():
            result = self.system_controller.control_volume('down')
        elif 'mute' in command.lower():
            result = self.system_controller.control_volume('mute')
        elif 'unmute' in command.lower():
            result = self.system_controller.control_volume('unmute')
        elif 'shutdown' in command.lower():
            result = self.system_controller.system_power('shutdown')
        elif 'restart' in command.lower():
            result = self.system_controller.system_power('restart')
        elif 'minimize' in command.lower():
            result = self.system_controller.window_management('minimize_all')
        else:
            result = {'success': False, 'message': 'System command not recognized'}
        
        speak(result['message'])
    
    async def handle_web_search(self, query):
        """Handle web search"""
        speak(f"Searching for {query}")
        result = self.system_controller.search_web(query)
        speak(result['message'])
    
    async def handle_play_media(self, query):
        """Handle media playback"""
        speak(f"Playing {query} on YouTube")
        result = self.system_controller.play_youtube(query)
        speak(result['message'])
    
    async def handle_general_question(self, question):
        """Handle general questions using AI"""
        try:
            ai_result = await self.ai_router.process_query(question, "general")
            
            if ai_result['success']:
                response = ai_result['response']
                print(f"🤖 JARVIS: {response}")
                speak(response)
                
                # Add to conversation context
                self.conversation_context.append(f"JARVIS: {response}")
            else:
                speak("I'm not sure how to answer that question right now")
                
        except Exception as e:
            speak("I'm having trouble processing that question")
    
    async def fallback_execution(self, command):
        """Fallback execution for simple pattern matching"""
        command_lower = command.lower()
        
        # Simple pattern matching for common commands
        if 'call' in command_lower and 'tom' in command_lower:
            await self.handle_phone_call('Tom')
        elif 'message' in command_lower and 'tom' in command_lower:
            await self.handle_sms('Tom', '')
        elif 'whatsapp' in command_lower and 'tom' in command_lower:
            await self.handle_whatsapp_message('Tom', '')
        elif 'open' in command_lower:
            app_name = command_lower.replace('open', '').strip()
            await self.handle_open_app(app_name)
        elif 'close' in command_lower:
            app_name = command_lower.replace('close', '').strip()
            await self.handle_close_app(app_name)
        else:
            await self.handle_general_question(command)
    
    async def voice_loop(self):
        """Main voice interaction loop"""
        print("\n🎙️ Smart JARVIS AI Voice Mode")
        print("=" * 35)
        print("I can understand ANY command you give me!")
        print("Just speak naturally - no need for specific phrases")
        print("Say 'JARVIS stop' to exit")
        
        # Show available contacts
        contacts = self.db_manager.get_all_contacts()
        if contacts:
            print(f"\n📞 I know these contacts:")
            for contact in contacts:
                print(f"  - {contact['name']}: {contact['mobile_no']}")
        
        while True:
            try:
                command = self.listen_continuously()
                
                if command is None:
                    break
                
                if any(word in command.lower() for word in ['stop', 'quit', 'exit', 'goodbye']):
                    speak("Goodbye! JARVIS AI shutting down.")
                    break
                
                # Process any command with AI
                await self.understand_and_execute(command)
                
                # Brief pause
                time.sleep(1)
                
            except KeyboardInterrupt:
                print("\n👋 JARVIS AI shutting down...")
                speak("JARVIS AI shutting down. Goodbye!")
                break
            except Exception as e:
                print(f"❌ Voice loop error: {e}")
                speak("I encountered an error. Let me restart my listening system.")
                time.sleep(2)

async def main():
    """Main function"""
    print("🤖 Smart JARVIS AI Assistant")
    print("=" * 30)
    print("I understand ANY command you give me!")
    
    # Initialize Smart JARVIS
    jarvis = SmartJarvis()
    
    # Menu
    print("\n📋 What would you like to do?")
    print("1. Start AI voice mode (I'll understand anything you say)")
    print("2. Test my understanding with typed commands")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == '1':
        jarvis.calibrate_microphone()
        await jarvis.voice_loop()
    
    elif choice == '2':
        print("\n⌨️ Type any command and I'll understand it:")
        while True:
            command = input("\n🎤 You: ").strip()
            if command.lower() in ['quit', 'exit']:
                break
            await jarvis.understand_and_execute(command)
    
    elif choice == '3':
        speak("Goodbye!")
        print("👋 Goodbye!")
    
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 JARVIS AI shutting down...")
    except Exception as e:
        print(f"❌ System error: {e}")
        import traceback
        traceback.print_exc()