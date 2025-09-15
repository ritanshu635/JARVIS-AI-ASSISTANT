#!/usr/bin/env python3
"""
Start JARVIS Web Interface on localhost
"""
import os
import eel
import threading
import asyncio
import subprocess
from engine.ai_router import AIRouter
from engine.voice_engine import VoiceEngine
from engine.android_controller import AndroidController
from engine.database_manager import initialize_default_data
from engine.command_processor import CommandProcessor
from engine.command import speak
from engine.features import playAssistantSound

# Global variables
ai_router = None
voice_engine = None
android_controller = None
db_manager = None
command_processor = None

def initialize_components():
    """Initialize all JARVIS components"""
    global ai_router, voice_engine, android_controller, db_manager, command_processor
    
    try:
        print("🚀 Initializing JARVIS components...")
        
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
        
        # Initialize Command Processor
        command_processor = CommandProcessor(ai_router, db_manager)
        print("✅ Command Processor initialized")
        
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
            
            # Use asyncio to run the async command processing
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(command_processor.process_command(command))
                
                if result['success']:
                    response = result['response']
                    
                    # Handle specific actions
                    handle_command_action(result)
                    
                    return response
                else:
                    return result.get('response', "I'm sorry, I couldn't process your request.")
            
            finally:
                loop.close()
                
        except Exception as e:
            print(f"❌ Command processing error: {e}")
            return f"I encountered an error: {str(e)}"
    
    def handle_command_action(result):
        """Handle command actions"""
        action = result.get('action', '')
        
        try:
            if action == 'open_system_app':
                app_path = result.get('app_path', '')
                if app_path:
                    subprocess.Popen(app_path, shell=True)
            
            elif action == 'open_website':
                url = result.get('url', '')
                if url:
                    import webbrowser
                    webbrowser.open(url)
            
            elif action == 'play_media':
                media_name = result.get('media_name', '')
                if media_name:
                    import webbrowser
                    search_url = f"https://www.youtube.com/results?search_query={media_name.replace(' ', '+')}"
                    webbrowser.open(search_url)
            
            elif action == 'make_call':
                contact = result.get('contact', {})
                if contact:
                    android_controller.make_call(contact['mobile_no'], contact['name'])
            
            elif action.startswith('whatsapp_'):
                contact = result.get('contact', {})
                message = result.get('message', '')
                action_type = action.replace('whatsapp_', '')
                if contact:
                    android_controller.whatsapp_automation(contact['name'], message, action_type)
            
            elif action == 'web_search':
                search_query = result.get('search_query', '')
                if search_query:
                    import webbrowser
                    search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
                    webbrowser.open(search_url)
            
        except Exception as e:
            print(f"❌ Action handling error: {e}")
    
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
            speak(text)
            return True
        except Exception as e:
            print(f"❌ Speech error: {e}")
            return False
    
    @eel.expose
    def start_voice_input():
        """Start voice input and return recognized text"""
        try:
            # This would need proper implementation with threading
            return {"text": "", "success": False, "message": "Voice input via web interface coming soon"}
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

def start_web_interface():
    """Start the web interface on localhost"""
    print("🌐 Starting JARVIS Web Interface...")
    
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
    
    print("✅ JARVIS Web Interface is ready!")
    print("🌐 Open your browser and go to: http://localhost:8080")
    print("💡 The interface will automatically open in a few seconds...")
    
    # Wait a moment then try to open browser
    def open_browser():
        import time
        time.sleep(2)
        try:
            import webbrowser
            webbrowser.open("http://localhost:8080")
        except:
            pass
    
    # Start browser opening in background
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    # Start Eel server
    try:
        eel.start('index.html', mode=None, host='localhost', port=8080, block=True)
    except Exception as e:
        print(f"❌ Web interface error: {e}")
        print("💡 You can manually open: http://localhost:8080")

if __name__ == "__main__":
    start_web_interface()