#!/usr/bin/env python3
"""
Quick test script for Tom's contact from CSV file
Tests all functionality with Tom's real contact
"""

import asyncio
from engine.database_manager import DatabaseManager
from engine.android_controller import AndroidController
from engine.system_controller import SystemController
from engine.command_processor import CommandProcessor
from engine.action_executor import ActionExecutor
from engine.ai_router import AIRouter
from engine.command import speak

async def test_tom_contact():
    """Test all functionality with Tom's contact"""
    
    print("🤖 Testing JARVIS with Tom's Contact")
    print("=" * 40)
    
    # Initialize components
    db_manager = DatabaseManager()
    android_controller = AndroidController(db_manager)
    system_controller = SystemController()
    ai_router = AIRouter()
    command_processor = CommandProcessor(ai_router, db_manager)
    action_executor = ActionExecutor()
    
    # Test 1: Check if Tom's contact is found
    print("1️⃣ Testing Contact Lookup")
    tom_contact = db_manager.get_contact("Tom")
    
    if tom_contact:
        print(f"✅ Found Tom: {tom_contact['name']} - {tom_contact['mobile_no']}")
        speak(f"Found Tom's contact with number {tom_contact['mobile_no']}")
    else:
        print("❌ Tom not found in contacts.csv")
        speak("Tom not found in contacts")
        return
    
    # Test 2: Check Android connection
    print("\n2️⃣ Testing Android Connection")
    connection_test = android_controller.test_connection()
    
    if connection_test['success']:
        print(f"✅ Android device connected")
        speak("Android device is connected")
    else:
        print(f"⚠️ Android device not connected: {connection_test['message']}")
        speak("Android device not connected, but we can still test other features")
    
    # Test 3: Voice commands with Tom
    print("\n3️⃣ Testing Voice Commands")
    
    test_commands = [
        "call Tom",
        "whatsapp Tom hello from JARVIS",
        "message Tom",
        "open notepad",
        "volume up",
        "search JARVIS AI on google",
        "play relaxing music on youtube"
    ]
    
    for i, command in enumerate(test_commands, 1):
        print(f"\n🧪 Test {i}: {command}")
        
        try:
            # Process command
            result = await command_processor.process_command(command)
            print(f"   🎯 Intent: {result['intent']}")
            print(f"   📝 Response: {result['response']}")
            
            # Execute action if needed
            if result['success'] and result.get('action'):
                print(f"   ⚡ Executing: {result['action']}")
                execution_result = await action_executor.execute_action(result)
                
                if execution_result['success']:
                    print(f"   ✅ Success: {execution_result['message']}")
                else:
                    print(f"   ❌ Failed: {execution_result['message']}")
            else:
                # Just speak the response
                speak(result['response'])
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Ask user if they want to continue
        if i < len(test_commands):
            cont = input("   Continue to next test? (y/n): ").lower().strip()
            if cont != 'y':
                break
    
    print("\n🎉 All tests completed!")
    speak("All tests completed successfully!")

def test_system_features():
    """Test system features without voice commands"""
    
    print("\n🖥️ Testing System Features")
    print("=" * 30)
    
    system_controller = SystemController()
    
    # Test volume control
    print("🔊 Testing volume control...")
    result = system_controller.control_volume('up')
    print(f"   Volume up: {result['message']}")
    speak(result['message'])
    
    # Test app opening
    print("📝 Testing app opening...")
    result = system_controller.open_application('notepad')
    print(f"   Open notepad: {result['message']}")
    speak(result['message'])
    
    # Wait a bit then close
    import time
    time.sleep(2)
    
    print("❌ Testing app closing...")
    result = system_controller.close_application('notepad')
    print(f"   Close notepad: {result['message']}")
    speak(result['message'])
    
    # Test web search
    print("🌐 Testing web search...")
    result = system_controller.search_web('JARVIS AI assistant')
    print(f"   Web search: {result['message']}")
    speak(result['message'])

async def interactive_test():
    """Interactive test mode"""
    
    print("\n🎙️ Interactive Test Mode")
    print("=" * 25)
    print("Try these commands:")
    print("📞 'call Tom' - Call Tom's number")
    print("📱 'whatsapp Tom hello' - Send WhatsApp to Tom")
    print("💬 'message Tom' - Send SMS to Tom")
    print("📝 'open notepad' - Open Notepad")
    print("🔊 'volume up' - Increase volume")
    print("🌐 'search cats on google' - Search Google")
    print("🎵 'play music on youtube' - Play YouTube")
    print("🗑️ 'open recycle bin' - Open Recycle Bin")
    print("❌ 'close chrome' - Close Chrome")
    print("🚪 'quit' - Exit")
    
    # Initialize components
    db_manager = DatabaseManager()
    ai_router = AIRouter()
    command_processor = CommandProcessor(ai_router, db_manager)
    action_executor = ActionExecutor()
    
    while True:
        try:
            command = input("\n🎤 Enter command: ").strip()
            
            if command.lower() in ['quit', 'exit', 'q']:
                speak("Goodbye!")
                break
            
            if not command:
                continue
            
            print(f"🔄 Processing: {command}")
            
            # Process command
            result = await command_processor.process_command(command)
            print(f"🎯 Intent: {result['intent']}")
            print(f"📝 Response: {result['response']}")
            
            # Execute action
            if result['success'] and result.get('action'):
                print(f"⚡ Executing: {result['action']}")
                execution_result = await action_executor.execute_action(result)
                
                if execution_result['success']:
                    print(f"✅ Success: {execution_result['message']}")
                else:
                    print(f"❌ Failed: {execution_result['message']}")
            else:
                speak(result['response'])
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            speak("Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

async def main():
    """Main function"""
    
    print("🤖 JARVIS Tom Contact Test")
    print("=" * 25)
    print("1. Test Tom's contact functionality")
    print("2. Test system features")
    print("3. Interactive test mode")
    print("4. Exit")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == '1':
        await test_tom_contact()
    elif choice == '2':
        test_system_features()
    elif choice == '3':
        await interactive_test()
    elif choice == '4':
        speak("Goodbye!")
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()