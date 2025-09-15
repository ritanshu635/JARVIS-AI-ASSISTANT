#!/usr/bin/env python3
"""
Real Contact Integration Test for JARVIS
Tests calling, messaging, and WhatsApp with actual phone contacts
"""

import asyncio
import os
import sys
from engine.database_manager import DatabaseManager
from engine.android_controller import AndroidController
from engine.command_processor import CommandProcessor
from engine.ai_router import AIRouter
from engine.command import speak

async def test_real_contact_integration():
    """Test JARVIS with real contacts from your phone"""
    
    print("🤖 JARVIS Real Contact Integration Test")
    print("=" * 50)
    
    # Initialize components
    db_manager = DatabaseManager()
    android_controller = AndroidController(db_manager)
    ai_router = AIRouter()
    command_processor = CommandProcessor(ai_router, db_manager)
    
    # Check ADB connection
    print("📱 Checking Android device connection...")
    connection_test = android_controller.test_connection()
    
    if not connection_test['success']:
        print("❌ Android device not connected!")
        print("Please connect your phone and enable USB debugging")
        return False
    
    print(f"✅ {connection_test['message']}")
    
    # Check contacts in database
    contacts = db_manager.get_all_contacts()
    print(f"📋 Found {len(contacts)} contacts in database")
    
    if len(contacts) == 0:
        print("❌ No contacts found!")
        print("Please run 'python sync_contacts.py' first to import your contacts")
        return False
    
    # Show available contacts
    print("\n📞 Available contacts:")
    for i, contact in enumerate(contacts[:10]):  # Show first 10
        print(f"  {i+1:2d}. {contact['name']}: {contact['mobile_no']}")
    
    if len(contacts) > 10:
        print(f"  ... and {len(contacts) - 10} more contacts")
    
    # Interactive testing
    print("\n🧪 Interactive Contact Testing")
    print("Commands you can try:")
    print("  - 'call [contact_name]'")
    print("  - 'message [contact_name]'") 
    print("  - 'whatsapp [contact_name]'")
    print("  - 'whatsapp [contact_name] hello there'")
    print("  - 'whatsapp call [contact_name]'")
    print("  - 'whatsapp video call [contact_name]'")
    print("  - 'list contacts'")
    print("  - 'quit' to exit")
    
    while True:
        try:
            # Get user command
            command = input("\n🎤 Enter command: ").strip()
            
            if command.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if command.lower() == 'list contacts':
                print(f"\n📋 All {len(contacts)} contacts:")
                for i, contact in enumerate(contacts):
                    email_info = f" ({contact['email']})" if contact['email'] else ""
                    print(f"  {i+1:3d}. {contact['name']}: {contact['mobile_no']}{email_info}")
                continue
            
            if not command:
                continue
            
            print(f"\n🔄 Processing: {command}")
            
            # Process command
            result = await command_processor.process_command(command)
            
            print(f"📝 Response: {result['response']}")
            print(f"🎯 Intent: {result['intent']}")
            print(f"✅ Success: {result['success']}")
            
            # Execute the action if successful
            if result['success'] and result.get('action'):
                await execute_contact_action(result, android_controller, db_manager)
            
        except KeyboardInterrupt:
            print("\n\n👋 Test interrupted by user")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

async def execute_contact_action(result: dict, android_controller: AndroidController, db_manager: DatabaseManager):
    """Execute the actual contact action"""
    
    action = result.get('action')
    
    try:
        if action == 'make_call':
            contact = result.get('contact')
            if contact:
                print(f"📞 Making call to {contact['name']} ({contact['mobile_no']})")
                speak(f"Calling {contact['name']}")
                
                call_result = android_controller.make_call(
                    contact['mobile_no'], 
                    contact['name']
                )
                
                print(f"📞 Call result: {call_result['message']}")
                if call_result['success']:
                    speak(call_result['message'])
                else:
                    speak(f"Failed to call {contact['name']}")
        
        elif action.startswith('whatsapp_'):
            contact = result.get('contact')
            message = result.get('message', '')
            
            if contact:
                whatsapp_type = action.replace('whatsapp_', '')
                print(f"📱 WhatsApp {whatsapp_type} to {contact['name']}")
                
                whatsapp_result = android_controller.whatsapp_automation(
                    contact['name'],
                    message,
                    whatsapp_type
                )
                
                print(f"📱 WhatsApp result: {whatsapp_result['message']}")
                if whatsapp_result['success']:
                    speak(whatsapp_result['message'])
                else:
                    speak(f"Failed to WhatsApp {contact['name']}")
        
        elif action == 'get_message_content':
            contact = result.get('contact')
            if contact:
                print(f"💬 Getting message content for {contact['name']}")
                message = input(f"📝 Enter message for {contact['name']}: ").strip()
                
                if message:
                    print(f"📱 Sending SMS to {contact['name']}: {message}")
                    speak(f"Sending message to {contact['name']}")
                    
                    sms_result = android_controller.send_sms(
                        contact['mobile_no'],
                        message,
                        contact['name']
                    )
                    
                    print(f"📱 SMS result: {sms_result['message']}")
                    if sms_result['success']:
                        speak(sms_result['message'])
                    else:
                        speak(f"Failed to send message to {contact['name']}")
        
        else:
            print(f"ℹ️ Action '{action}' doesn't require execution")
    
    except Exception as e:
        print(f"❌ Action execution error: {e}")
        speak("Sorry, I encountered an error executing that action")

def test_specific_contact():
    """Test with a specific contact name"""
    
    print("\n🎯 Specific Contact Test")
    
    db_manager = DatabaseManager()
    android_controller = AndroidController(db_manager)
    
    # Get contact name from user
    contact_name = input("Enter contact name to test: ").strip()
    
    if not contact_name:
        print("❌ No contact name provided")
        return
    
    # Search for contact
    contact = db_manager.get_contact(contact_name)
    
    if not contact:
        print(f"❌ Contact '{contact_name}' not found")
        
        # Show similar contacts
        all_contacts = db_manager.get_all_contacts()
        similar = [c for c in all_contacts if contact_name.lower() in c['name'].lower()]
        
        if similar:
            print("🔍 Similar contacts found:")
            for c in similar[:5]:
                print(f"  - {c['name']}: {c['mobile_no']}")
        
        return
    
    print(f"✅ Found contact: {contact['name']} - {contact['mobile_no']}")
    
    # Test different actions
    actions = [
        ('call', 'Make a call'),
        ('sms', 'Send SMS'),
        ('whatsapp_message', 'WhatsApp message'),
        ('whatsapp_call', 'WhatsApp call'),
        ('whatsapp_video_call', 'WhatsApp video call')
    ]
    
    print(f"\n📋 Available actions for {contact['name']}:")
    for i, (action, description) in enumerate(actions):
        print(f"  {i+1}. {description}")
    
    choice = input("\nSelect action (1-5): ").strip()
    
    try:
        choice_idx = int(choice) - 1
        if 0 <= choice_idx < len(actions):
            action, description = actions[choice_idx]
            
            print(f"\n🚀 Executing: {description}")
            
            if action == 'call':
                result = android_controller.make_call(contact['mobile_no'], contact['name'])
            elif action == 'sms':
                message = input("Enter SMS message: ").strip()
                result = android_controller.send_sms(contact['mobile_no'], message, contact['name'])
            elif action.startswith('whatsapp_'):
                whatsapp_type = action.replace('whatsapp_', '')
                message = ""
                if whatsapp_type == 'message':
                    message = input("Enter WhatsApp message: ").strip()
                result = android_controller.whatsapp_automation(contact['name'], message, whatsapp_type)
            
            print(f"📊 Result: {result['message']}")
            print(f"✅ Success: {result['success']}")
            
            if result['success']:
                speak(result['message'])
            
        else:
            print("❌ Invalid choice")
    
    except ValueError:
        print("❌ Invalid input")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🤖 JARVIS Real Contact Test Suite")
    print("=" * 40)
    
    print("1. Interactive contact testing")
    print("2. Specific contact test")
    print("3. Exit")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == '1':
        asyncio.run(test_real_contact_integration())
    elif choice == '2':
        test_specific_contact()
    elif choice == '3':
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")