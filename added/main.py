import os
import eel
import threading
import asyncio
import json
import sqlite3
import subprocess
import time
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Import engine modules
from engine.ai_router import AIRouter
from engine.voice_engine import VoiceEngine
from engine.android_controller import AndroidController
from engine.database_manager import DatabaseManager, initialize_default_data
from engine.features import playAssistantSound
from engine.command import speak

# Import meeting assistant
from voice_meeting_assistant import voice_meeting_assistant, start_voice_meeting_assistant, stop_voice_meeting_assistant, get_meeting_assistant_status

# Load environment variables
load_dotenv()

# Global variables
state = 'Ready'
ai_router = None
voice_engine = None
android_controller = None
db_manager = None

def initialize_components():
    """Initialize all JARVIS components"""
    global ai_router, voice_engine, android_controller, db_manager
    
    try:
        # Initialize Database Manager first
        db_manager = initialize_default_data()
        print("✅ Database Manager initialized")
        
        # Initialize AI Router
        ai_router = AIRouter()
        print("✅ AI Router initialized")
        
        # Initialize Voice Engine
        voice_engine = VoiceEngine()
        print("✅ Voice Engine initialized")
        
        # Initialize Android Controller
        android_controller = AndroidController(db_manager)
        print("✅ Android Controller initialized")
        
        # Start voice meeting assistant
        meeting_result = start_voice_meeting_assistant()
        print(f"🎤 Voice Meeting Assistant: {meeting_result}")
        
        return True
    except Exception as e:
        print(f"❌ Error initializing components: {e}")
        return False

def setup_eel_functions():
    """Setup all Eel exposed functions for frontend communication"""
    
    @eel.expose
    def test_connection():
        """Test backend connection"""
        return {"status": "connected", "message": "JARVIS backend is running"}
    
    @eel.expose
    def process_command(command):
        """Process user command and return response"""
        try:
            print(f"📝 Processing command: {command}")
            
            # Use asyncio to run the async AI processing
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # First classify the intent
                intent_result = loop.run_until_complete(ai_router.classify_intent(command))
                intent = intent_result.get('intent', 'general')
                
                print(f"🎯 Classified as: {intent}")
                
                # Handle specific intents
                if intent.startswith('open '):
                    app_name = intent.replace('open ', '').strip()
                    return handle_open_command(app_name)
                elif intent.startswith('call '):
                    contact_name = intent.replace('call ', '').strip()
                    return handle_call_command(contact_name)
                elif intent.startswith('message ') or intent.startswith('text '):
                    contact_name = intent.replace('message ', '').replace('text ', '').strip()
                    return handle_message_command(contact_name, command)
                elif intent.startswith('play '):
                    media = intent.replace('play ', '').strip()
                    return handle_media_command(media)
                elif intent.startswith('search '):
                    query = intent.replace('search ', '').strip()
                    return handle_search_command(query)
                elif 'time' in intent.lower():
                    return handle_time_command()
                elif 'date' in intent.lower():
                    return handle_date_command()
                elif any(phrase in command.lower() for phrase in ['attend the meeting', 'meeting status', 'leave the meeting']):
                    return handle_meeting_command(command)
                else:
                    # General AI query
                    result = loop.run_until_complete(ai_router.process_query(command, "general"))
                    
                    if result['success']:
                        response = result['response']
                        
                        # Save to chat history
                        if db_manager:
                            db_manager.save_chat_message(
                                command, 
                                response, 
                                intent, 
                                result.get('processing_time'), 
                                result.get('ai_model')
                            )
                        
                        return response
                    else:
                        return "I'm sorry, I couldn't process your request at the moment."
            
            finally:
                loop.close()
                
        except Exception as e:
            print(f"❌ Command processing error: {e}")
            return f"I encountered an error: {str(e)}"
    
    @eel.expose
    def get_ai_status():
        """Get AI service status"""
        if ai_router:
            return ai_router.get_service_status()
        return {"ollama": False, "groq": False, "cohere": False}
    
    @eel.expose
    def speak_text(text):
        """Convert text to speech"""
        try:
            if voice_engine:
                voice_engine.speak(text)
                return True
            else:
                # Fallback TTS
                speak(text)
                return True
        except Exception as e:
            print(f"❌ Speech error: {e}")
            return False
    
    @eel.expose
    def start_voice_input():
        """Start voice input and return recognized text"""
        try:
            if voice_engine:
                # Start listening for 5 seconds
                if voice_engine.start_listening(5):
                    # This is a simplified version - in reality we'd need proper threading
                    return {"text": "", "success": False, "message": "Voice input feature coming soon"}
                else:
                    return {"text": "", "success": False, "message": "Could not start voice input"}
            return {"text": "", "success": False, "message": "Voice engine not available"}
        except Exception as e:
            print(f"❌ Voice input error: {e}")
            return {"text": "", "success": False, "message": str(e)}
    
    @eel.expose
    def get_chat_history():
        """Get recent chat history"""
        try:
            if db_manager:
                history = db_manager.get_chat_history(20)
                formatted_history = []
                
                for msg in history:
                    if isinstance(msg, dict) and 'user_input' in msg:
                        # Add user message
                        formatted_history.append({
                            'sender': 'user',
                            'message': msg.get('user_input', ''),
                            'timestamp': str(msg.get('timestamp', ''))
                        })
                        # Add assistant response
                        formatted_history.append({
                            'sender': 'assistant',
                            'message': msg.get('response', ''),
                            'timestamp': str(msg.get('timestamp', ''))
                        })
                
                return formatted_history
            return []
        except Exception as e:
            print(f"❌ Chat history error: {e}")
            return []
    
    @eel.expose
    def update_settings(settings):
        """Update user settings"""
        try:
            if db_manager:
                for key, value in settings.items():
                    db_manager.set_preference(key, value)
            
            # Update voice settings if available
            if voice_engine and 'voiceRate' in settings:
                voice_engine.set_voice_properties(rate=settings['voiceRate'])
            
            print(f"✅ Settings updated: {settings}")
            return True
        except Exception as e:
            print(f"❌ Settings update error: {e}")
            return False
    
    @eel.expose
    def start_meeting_assistant():
        """Start voice-activated meeting assistant"""
        try:
            result = start_voice_meeting_assistant()
            return {"success": True, "message": result}
        except Exception as e:
            return {"success": False, "message": f"Error: {e}"}
    
    @eel.expose
    def stop_meeting_assistant():
        """Stop voice-activated meeting assistant"""
        try:
            result = stop_voice_meeting_assistant()
            return {"success": True, "message": result}
        except Exception as e:
            return {"success": False, "message": f"Error: {e}"}
    
    @eel.expose
    def get_meeting_status():
        """Get meeting assistant status"""
        try:
            status = get_meeting_assistant_status()
            return {"success": True, "status": status}
        except Exception as e:
            return {"success": False, "message": f"Error: {e}"}

def handle_open_command(app_name):
    """Handle application opening commands"""
    try:
        if db_manager:
            # Check if it's a system command
            app_path = db_manager.get_system_command(app_name)
            if app_path:
                subprocess.Popen(app_path, shell=True)
                return f"Opening {app_name}..."
            
            # Check if it's a web command
            url = db_manager.get_web_command(app_name)
            if url:
                import webbrowser
                webbrowser.open(url)
                return f"Opening {app_name} in browser..."
        
        # Try common applications
        common_apps = {
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'paint': 'mspaint.exe',
            'chrome': 'chrome.exe',
            'edge': 'msedge.exe',
            'explorer': 'explorer.exe'
        }
        
        if app_name.lower() in common_apps:
            subprocess.Popen(common_apps[app_name.lower()], shell=True)
            return f"Opening {app_name}..."
        
        return f"I couldn't find {app_name}. Please make sure it's installed."
        
    except Exception as e:
        print(f"❌ Open command error: {e}")
        return f"Error opening {app_name}: {str(e)}"

def handle_call_command(contact_name):
    """Handle phone call commands"""
    try:
        if android_controller:
            contact = db_manager.get_contact(contact_name) if db_manager else None
            if contact:
                result = android_controller.make_call(contact['mobile_no'])
                if result:
                    return f"Calling {contact['name']}..."
                else:
                    return f"Failed to call {contact['name']}. Please check your phone connection."
            else:
                return f"Contact {contact_name} not found. Please add them to your contacts first."
        else:
            return "Phone functionality requires Android device connection via ADB."
    except Exception as e:
        print(f"❌ Call command error: {e}")
        return f"Error making call: {str(e)}"

def handle_message_command(contact_name, full_command):
    """Handle SMS/message commands"""
    try:
        if android_controller:
            return f"Message functionality for {contact_name} is coming soon. Please use the full command with message content."
        else:
            return "Messaging functionality requires Android device connection via ADB."
    except Exception as e:
        print(f"❌ Message command error: {e}")
        return f"Error sending message: {str(e)}"

def handle_media_command(media):
    """Handle media playbook commands"""
    try:
        import webbrowser
        
        if 'youtube' in media.lower() or 'video' in media.lower():
            search_query = media.replace('youtube', '').replace('video', '').strip()
            if search_query:
                url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"
                webbrowser.open(url)
                return f"Searching YouTube for: {search_query}"
            else:
                webbrowser.open("https://www.youtube.com")
                return "Opening YouTube..."
        
        elif 'spotify' in media.lower() or 'music' in media.lower():
            webbrowser.open("https://open.spotify.com")
            return "Opening Spotify..."
        
        else:
            # General media search on YouTube
            url = f"https://www.youtube.com/results?search_query={media.replace(' ', '+')}"
            webbrowser.open(url)
            return f"Searching for: {media}"
            
    except Exception as e:
        print(f"❌ Media command error: {e}")
        return f"Error playing media: {str(e)}"

def handle_search_command(query):
    """Handle web search commands"""
    try:
        import webbrowser
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(search_url)
        return f"Searching Google for: {query}"
    except Exception as e:
        print(f"❌ Search command error: {e}")
        return f"Error performing search: {str(e)}"

def handle_time_command():
    """Handle time queries"""
    current_time = datetime.now().strftime("%I:%M %p")
    return f"The current time is {current_time}."

def handle_date_command():
    """Handle date queries"""
    current_date = datetime.now().strftime("%A, %B %d, %Y")
    return f"Today is {current_date}."

def handle_meeting_command(command):
    """Handle meeting-related commands"""
    try:
        command_lower = command.lower()
        
        if "attend the meeting" in command_lower:
            result = voice_meeting_assistant.manual_start_recording()
            return f"Meeting Assistant: {result}"
        
        elif "leave the meeting" in command_lower or "stop meeting" in command_lower:
            result = voice_meeting_assistant.manual_stop_recording()
            return f"Meeting Assistant: {result}"
        
        elif "meeting status" in command_lower:
            status = voice_meeting_assistant.get_status()
            return f"Meeting Status: {status}"
        
        else:
            return "Meeting command not recognized. Try 'attend the meeting' or 'leave the meeting'."
            
    except Exception as e:
        print(f"❌ Meeting command error: {e}")
        return f"Error processing meeting command: {str(e)}"

def start():
    """Main application entry point"""
    print("🚀 Starting Unified JARVIS Assistant...")
    
    # Initialize Eel
    eel.init("www")
    
    # Initialize all components
    if not initialize_components():
        print("❌ Failed to initialize components. Exiting...")
        return
    
    # Setup Eel exposed functions
    setup_eel_functions()
    
    # Play startup sound
    playAssistantSound()
    
    print("✅ JARVIS is ready!")
    print("🌐 Opening web interface...")
    
    # Start the web interface
    try:
        # Try to open in Edge app mode first
        subprocess.Popen(['msedge.exe', '--app=http://localhost:8000/index.html'], 
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        try:
            # Fallback to Chrome app mode
            subprocess.Popen(['chrome.exe', '--app=http://localhost:8000/index.html'], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            print("⚠️ Could not start in app mode, will open in default browser")
    
    # Start Eel server
    eel.start('index.html', mode=None, host='localhost', port=8000, block=True)

if __name__ == "__main__":
    start()