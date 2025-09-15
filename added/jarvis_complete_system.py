#!/usr/bin/env python3
"""
Complete JARVIS System with All Functionality
- Real contacts from CSV
- Voice responses (TTS)
- System control (volume, brightness, apps)
- Web automation (Chrome, YouTube)
- File management (recycle bin)
- Phone integration (calls, SMS, WhatsApp)
"""

import asyncio
import os
import sys
from engine.database_manager import DatabaseManager
from engine.android_controller import AndroidController
from engine.system_controller import SystemController
from engine.command_processor import CommandProcessor
from engine.action_executor import ActionExecutor
from engine.ai_router import AIRouter
from engine.command import speak

class JarvisCompleteSystem:
    """Complete JARVIS system with all functionality"""
    
    def __init__(self):
        print("🤖 Initializing JARVIS Complete System...")
        
        # Initialize all components
        self.db_manager = DatabaseManager()
        self.android_controller = AndroidController(self.db_manager)
        self.system_controller = SystemController()
        self.ai_router = AIRouter()
        self.command_processor = CommandProcessor(self.ai_router, self.db_manager)
        self.action_executor = ActionExecutor()
        
        print("✅ JARVIS system initialized successfully!")
    
    def check_system_status(self):
        """Check system status and capabilities"""
        print("\n🔍 System Status Check")
        print("=" * 30)
        
        # Check contacts
        contacts = self.db_manager.get_all_contacts()
        print(f"📋 Contacts available: {len(contacts)}")
        
        if contacts:
            print("📞 Available contacts:")
            for contact in contacts:
                print(f"  - {contact['name']}: {contact['mobile_no']}")
        
        # Check Android connection
        connection_test = self.android_controller.test_connection()
        if connection_test['success']:
            print(f"📱 Android device: ✅ Connected")
            device_info = self.android_controller.get_device_info()
            if device_info['connected']:
                print(f"   📱 Device: {device_info.get('model', 'Unknown')}")
                print(f"   🤖 Android: {device_info.get('android_version', 'Unknown')}")
        else:
            print(f"📱 Android device: ❌ Not connected")
        
        # Check CSV file
        if os.path.exists('contacts.csv'):
            print("📄 contacts.csv: ✅ Found")
        else:
            print("📄 contacts.csv: ❌ Not found")
        
        print("\n🚀 JARVIS is ready for commands!")
    
    async def process_voice_command(self, command: str):
        """Process a voice command with full functionality"""
        try:
            print(f"\n🎤 Command: {command}")
            
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
    
    async def interactive_mode(self):
        """Interactive command mode"""
        print("\n🎙️ JARVIS Interactive Mode")
        print("=" * 30)
        print("Available commands:")
        print("📞 Phone: 'call Tom', 'message Tom', 'whatsapp Tom hello'")
        print("🖥️ System: 'open notepad', 'close chrome', 'volume up', 'mute'")
        print("🌐 Web: 'search cats on google', 'play music on youtube'")
        print("🗑️ Files: 'open recycle bin', 'empty recycle bin'")
        print("⚡ Power: 'shutdown', 'restart', 'minimize all windows'")
        print("❓ General: Ask any question or request")
        print("🚪 Exit: 'quit', 'exit', or 'goodbye'")
        
        while True:
            try:
                command = input("\n🎤 JARVIS> ").strip()
                
                if command.lower() in ['quit', 'exit', 'goodbye', 'q']:
                    speak("Goodbye! Have a great day!")
                    break
                
                if not command:
                    continue
                
                # Process the command
                await self.process_voice_command(command)
                
            except KeyboardInterrupt:
                print("\n\n👋 JARVIS shutting down...")
                speak("Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def test_all_functionality(self):
        """Test all JARVIS functionality"""
        print("\n🧪 Testing All JARVIS Functionality")
        print("=" * 40)
        
        # Test 1: Contact lookup
        print("\n1️⃣ Testing Contact Lookup")
        tom_contact = self.db_manager.get_contact("Tom")
        if tom_contact:
            print(f"✅ Found Tom: {tom_contact['name']} - {tom_contact['mobile_no']}")
            speak(f"Found contact Tom with number {tom_contact['mobile_no']}")
        else:
            print("❌ Tom not found in contacts")
            speak("Tom not found in contacts")
        
        # Test 2: System control
        print("\n2️⃣ Testing System Control")
        volume_result = self.system_controller.control_volume('up')
        print(f"Volume control: {volume_result['message']}")
        speak(volume_result['message'])
        
        # Test 3: App opening
        print("\n3️⃣ Testing App Control")
        app_result = self.system_controller.open_application('notepad')
        print(f"App opening: {app_result['message']}")
        speak(app_result['message'])
        
        # Test 4: Web functionality
        print("\n4️⃣ Testing Web Functionality")
        web_result = self.system_controller.search_web('JARVIS AI assistant', 'google')
        print(f"Web search: {web_result['message']}")
        speak(web_result['message'])
        
        print("\n✅ All functionality tests completed!")
        speak("All functionality tests completed successfully!")

async def main():
    """Main function"""
    print("🤖 JARVIS Complete System")
    print("=" * 25)
    
    # Initialize JARVIS
    jarvis = JarvisCompleteSystem()
    
    # Check system status
    jarvis.check_system_status()
    
    # Menu
    print("\n📋 What would you like to do?")
    print("1. Interactive command mode")
    print("2. Test all functionality")
    print("3. Quick contact test")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == '1':
        await jarvis.interactive_mode()
    
    elif choice == '2':
        jarvis.test_all_functionality()
    
    elif choice == '3':
        # Quick test with Tom
        print("\n🎯 Quick Contact Test with Tom")
        
        test_commands = [
            "call Tom",
            "whatsapp Tom hello from JARVIS",
            "message Tom"
        ]
        
        for cmd in test_commands:
            print(f"\n🧪 Testing: {cmd}")
            await jarvis.process_voice_command(cmd)
            
            # Ask user if they want to continue
            cont = input("Continue to next test? (y/n): ").lower().strip()
            if cont != 'y':
                break
    
    elif choice == '4':
        speak("Goodbye!")
        print("👋 Goodbye!")
    
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 JARVIS shutting down...")
    except Exception as e:
        print(f"\n❌ System error: {e}")
        import traceback
        traceback.print_exc()