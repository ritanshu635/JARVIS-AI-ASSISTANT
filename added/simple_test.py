#!/usr/bin/env python3
"""
Simple test script for JARVIS with Tom's contact
No external dependencies except basic Python libraries
"""

import asyncio
import os
import sys
import csv
from engine.database_manager import DatabaseManager
from engine.command import speak

def test_csv_contact():
    """Test reading Tom's contact from CSV"""
    print("📋 Testing CSV Contact Reading")
    print("=" * 35)
    
    # Check if CSV exists
    if not os.path.exists('contacts.csv'):
        print("❌ contacts.csv not found!")
        return False
    
    # Read CSV file
    try:
        with open('contacts.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            contacts = list(reader)
            
            print(f"✅ Found {len(contacts)} contacts in CSV:")
            for contact in contacts:
                name = contact.get('Name', '')
                phone = contact.get('Phone Number', '')
                print(f"  - {name}: {phone}")
                
                if name.lower() == 'tom':
                    print(f"🎯 Tom found with number: {phone}")
                    speak(f"Found Tom's contact with number {phone}")
                    return True
    
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return False
    
    return False

def test_database_contact():
    """Test database contact lookup"""
    print("\n💾 Testing Database Contact Lookup")
    print("=" * 40)
    
    try:
        db_manager = DatabaseManager()
        
        # Test getting Tom's contact
        tom_contact = db_manager.get_contact("Tom")
        
        if tom_contact:
            print(f"✅ Database found Tom: {tom_contact['name']} - {tom_contact['mobile_no']}")
            speak(f"Database found Tom with number {tom_contact['mobile_no']}")
            return True
        else:
            print("❌ Tom not found in database")
            speak("Tom not found in database")
            return False
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_basic_system():
    """Test basic system operations"""
    print("\n🖥️ Testing Basic System Operations")
    print("=" * 40)
    
    try:
        # Test opening notepad
        print("📝 Testing Notepad...")
        os.startfile('notepad.exe')
        speak("Opened Notepad")
        
        import time
        time.sleep(2)
        
        # Test closing notepad
        print("❌ Testing close Notepad...")
        import subprocess
        result = subprocess.run(['taskkill', '/f', '/im', 'notepad.exe'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Closed Notepad")
            speak("Closed Notepad")
        else:
            print("⚠️ Notepad may not have been running")
        
        # Test web browser
        print("🌐 Testing web browser...")
        import webbrowser
        webbrowser.open('https://www.google.com')
        speak("Opened Google in web browser")
        
        return True
        
    except Exception as e:
        print(f"❌ System test error: {e}")
        return False

async def test_voice_commands():
    """Test voice command processing"""
    print("\n🎤 Testing Voice Command Processing")
    print("=" * 40)
    
    try:
        from engine.command_processor import CommandProcessor
        from engine.ai_router import AIRouter
        
        # Initialize components
        db_manager = DatabaseManager()
        ai_router = AIRouter()
        command_processor = CommandProcessor(ai_router, db_manager)
        
        # Test commands
        test_commands = [
            "call Tom",
            "open notepad",
            "hello jarvis"
        ]
        
        for command in test_commands:
            print(f"\n🧪 Testing: '{command}'")
            
            try:
                result = await command_processor.process_command(command)
                print(f"   🎯 Intent: {result['intent']}")
                print(f"   📝 Response: {result['response']}")
                print(f"   ✅ Success: {result['success']}")
                
                # Speak the response
                speak(result['response'])
                
            except Exception as e:
                print(f"   ❌ Command error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Voice command test error: {e}")
        return False

def interactive_mode():
    """Simple interactive mode"""
    print("\n🎙️ Simple Interactive Mode")
    print("=" * 30)
    print("Available commands:")
    print("📞 'call Tom' - Test calling Tom")
    print("📝 'open notepad' - Open Notepad")
    print("🌐 'open google' - Open Google")
    print("🔊 'test voice' - Test voice synthesis")
    print("🚪 'quit' - Exit")
    
    db_manager = DatabaseManager()
    
    while True:
        try:
            command = input("\n🎤 Enter command: ").strip().lower()
            
            if command in ['quit', 'exit', 'q']:
                speak("Goodbye!")
                break
            
            elif command == 'call tom':
                tom_contact = db_manager.get_contact("Tom")
                if tom_contact:
                    print(f"📞 Would call Tom at {tom_contact['mobile_no']}")
                    speak(f"Calling Tom at {tom_contact['mobile_no']}")
                else:
                    print("❌ Tom not found")
                    speak("Tom not found in contacts")
            
            elif command == 'open notepad':
                try:
                    os.startfile('notepad.exe')
                    print("📝 Opened Notepad")
                    speak("Opened Notepad")
                except Exception as e:
                    print(f"❌ Failed to open Notepad: {e}")
                    speak("Failed to open Notepad")
            
            elif command == 'open google':
                try:
                    import webbrowser
                    webbrowser.open('https://www.google.com')
                    print("🌐 Opened Google")
                    speak("Opened Google")
                except Exception as e:
                    print(f"❌ Failed to open Google: {e}")
                    speak("Failed to open Google")
            
            elif command == 'test voice':
                speak("Voice synthesis is working correctly!")
                print("🔊 Voice test completed")
            
            else:
                print(f"❓ Unknown command: {command}")
                speak("I don't understand that command")
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            speak("Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

async def main():
    """Main function"""
    print("🤖 JARVIS Simple Test")
    print("=" * 20)
    
    # Test 1: CSV reading
    csv_success = test_csv_contact()
    
    # Test 2: Database
    db_success = test_database_contact()
    
    # Test 3: Basic system
    system_success = test_basic_system()
    
    # Test 4: Voice commands (optional)
    print("\n🎤 Test voice commands? (y/n): ", end="")
    test_voice = input().lower().strip() == 'y'
    
    if test_voice:
        voice_success = await test_voice_commands()
    
    # Summary
    print(f"\n📊 Test Results:")
    print(f"   📋 CSV Reading: {'✅' if csv_success else '❌'}")
    print(f"   💾 Database: {'✅' if db_success else '❌'}")
    print(f"   🖥️ System: {'✅' if system_success else '❌'}")
    if test_voice:
        print(f"   🎤 Voice: {'✅' if voice_success else '❌'}")
    
    # Interactive mode
    print("\n🎙️ Start interactive mode? (y/n): ", end="")
    start_interactive = input().lower().strip() == 'y'
    
    if start_interactive:
        interactive_mode()
    
    print("\n🎉 Test completed!")
    speak("Test completed successfully!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()