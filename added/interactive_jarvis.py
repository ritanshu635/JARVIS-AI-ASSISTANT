#!/usr/bin/env python3
"""
Interactive JARVIS - Type commands or use voice
Waits for YOUR input and then executes what YOU tell it to do
"""

import asyncio
import os
from engine.database_manager import DatabaseManager
from engine.android_controller import AndroidController
from engine.system_controller import SystemController
from engine.command_processor import CommandProcessor
from engine.action_executor import ActionExecutor
from engine.ai_router import AIRouter
from engine.command import speak

class InteractiveJarvis:
    """Interactive JARVIS that waits for your commands"""
    
    def __init__(self):
        print("🤖 Initializing Interactive JARVIS...")
        speak("JARVIS interactive system starting up")
        
        # Initialize JARVIS components
        self.db_manager = DatabaseManager()
        self.android_controller = AndroidController(self.db_manager)
        self.system_controller = SystemController()
        self.ai_router = AIRouter()
        self.command_processor = CommandProcessor(self.ai_router, self.db_manager)
        self.action_executor = ActionExecutor()
        
        print("✅ Interactive JARVIS ready!")
        speak("JARVIS is ready for your commands")
    
    def show_available_commands(self):
        """Show available commands"""
        print("\n📋 Available Commands:")
        print("=" * 25)
        
        # Check contacts first
        contacts = self.db_manager.get_all_contacts()
        if contacts:
            print("📞 Phone Commands:")
            for contact in contacts:
                print(f"  - 'call {contact['name']}'")
                print(f"  - 'message {contact['name']}'")
                print(f"  - 'whatsapp {contact['name']} your message here'")
        
        print("\n🖥️ System Commands:")
        print("  - 'open notepad' / 'open calculator' / 'open chrome'")
        print("  - 'close notepad' / 'close chrome'")
        print("  - 'volume up' / 'volume down' / 'mute' / 'unmute'")
        print("  - 'open recycle bin' / 'empty recycle bin'")
        print("  - 'minimize all windows'")
        
        print("\n🌐 Web Commands:")
        print("  - 'search cats on google'")
        print("  - 'play music on youtube'")
        print("  - 'open youtube' / 'open facebook'")
        
        print("\n💬 General Commands:")
        print("  - 'hello jarvis'")
        print("  - 'what time is it'")
        print("  - 'what's the weather'")
        print("  - Ask any question")
        
        print("\n🚪 Exit Commands:")
        print("  - 'quit' / 'exit' / 'goodbye'")
    
    async def process_command(self, command):
        """Process a single command"""
        try:
            print(f"\n🔄 Processing: {command}")
            speak("Processing your command")
            
            # Process the command
            result = await self.command_processor.process_command(command)
            
            print(f"🎯 Intent: {result['intent']}")
            print(f"📝 Response: {result['response']}")
            
            # Execute the action if needed
            if result['success'] and result.get('action'):
                print(f"⚡ Executing: {result['action']}")
                
                execution_result = await self.action_executor.execute_action(result)
                
                if execution_result['success']:
                    print(f"✅ Completed: {execution_result['message']}")
                else:
                    print(f"❌ Failed: {execution_result['message']}")
                    speak(f"Sorry, {execution_result['message']}")
            else:
                # Just speak the response for non-action commands
                speak(result['response'])
            
            return result
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"❌ {error_msg}")
            speak("Sorry, I encountered an error")
            return {'success': False, 'message': error_msg}
    
    async def interactive_mode(self):
        """Main interactive loop - waits for YOUR commands"""
        print("\n🎙️ JARVIS Interactive Mode")
        print("=" * 30)
        print("Type your commands and press Enter")
        print("JARVIS will wait for YOUR input and do what YOU tell it")
        
        # Show contacts
        contacts = self.db_manager.get_all_contacts()
        if contacts:
            print(f"\n📞 Available contacts:")
            for contact in contacts:
                print(f"  - {contact['name']}: {contact['mobile_no']}")
        
        print(f"\nType 'help' to see all commands")
        print(f"Type 'quit' to exit")
        
        while True:
            try:
                # Wait for YOUR input
                command = input("\n🎤 JARVIS> ").strip()
                
                if not command:
                    continue
                
                # Check for exit commands
                if command.lower() in ['quit', 'exit', 'goodbye', 'stop']:
                    speak("Goodbye! Have a great day!")
                    print("👋 JARVIS shutting down...")
                    break
                
                # Show help
                elif command.lower() in ['help', 'commands']:
                    self.show_available_commands()
                    continue
                
                # Process the command
                await self.process_command(command)
                
            except KeyboardInterrupt:
                print("\n\n👋 JARVIS shutting down...")
                speak("Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                speak("I encountered an error")
    
    def quick_test(self):
        """Quick functionality test"""
        print("\n🧪 Quick Functionality Test")
        print("=" * 30)
        
        # Test 1: Check contacts
        print("1️⃣ Testing contacts...")
        contacts = self.db_manager.get_all_contacts()
        
        if contacts:
            print(f"✅ Found {len(contacts)} contacts")
            for contact in contacts:
                print(f"  - {contact['name']}: {contact['mobile_no']}")
            speak(f"Found {len(contacts)} contacts")
        else:
            print("❌ No contacts found")
            speak("No contacts found")
        
        # Test 2: Check Android connection
        print("\n2️⃣ Testing Android connection...")
        connection = self.android_controller.test_connection()
        
        if connection['success']:
            print("✅ Android device connected")
            speak("Android device is connected")
        else:
            print("⚠️ Android device not connected")
            speak("Android device not connected")
        
        # Test 3: Test system control
        print("\n3️⃣ Testing system control...")
        try:
            # Test opening notepad
            result = self.system_controller.open_application('notepad')
            print(f"Notepad test: {result['message']}")
            speak(result['message'])
            
            # Wait and close
            import time
            time.sleep(2)
            
            close_result = self.system_controller.close_application('notepad')
            print(f"Close test: {close_result['message']}")
            speak(close_result['message'])
            
        except Exception as e:
            print(f"System test error: {e}")
        
        print("\n✅ Quick test completed!")
        speak("Quick test completed")

async def main():
    """Main function"""
    print("🤖 JARVIS Interactive Assistant")
    print("=" * 30)
    print("This JARVIS waits for YOUR commands!")
    
    # Initialize JARVIS
    jarvis = InteractiveJarvis()
    
    # Menu
    print("\n📋 What would you like to do?")
    print("1. Start interactive mode (type commands)")
    print("2. Quick functionality test")
    print("3. Show available commands")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == '1':
        await jarvis.interactive_mode()
    
    elif choice == '2':
        jarvis.quick_test()
        
        # Ask if user wants to continue to interactive mode
        cont = input("\nStart interactive mode? (y/n): ").lower().strip()
        if cont == 'y':
            await jarvis.interactive_mode()
    
    elif choice == '3':
        jarvis.show_available_commands()
        
        # Ask if user wants to start interactive mode
        start = input("\nStart interactive mode? (y/n): ").lower().strip()
        if start == 'y':
            await jarvis.interactive_mode()
    
    elif choice == '4':
        speak("Goodbye!")
        print("👋 Goodbye!")
    
    else:
        print("❌ Invalid choice")
        speak("Invalid choice")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 JARVIS shutting down...")
    except Exception as e:
        print(f"❌ System error: {e}")
        import traceback
        traceback.print_exc()