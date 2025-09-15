#!/usr/bin/env python3
"""
Test script for Meeting Assistant functionality
"""

import asyncio
import time
from meeting_assistant import meeting_assistant, handle_meeting_command

def test_meeting_commands():
    """Test meeting command handling"""
    print("🧪 Testing Meeting Assistant Commands")
    print("=" * 50)
    
    # Test command recognition
    test_commands = [
        "Jarvis attend the meeting for me",
        "jarvis attend meeting",
        "Jarvis you can leave the meeting",
        "jarvis stop meeting",
        "meeting status"
    ]
    
    for cmd in test_commands:
        print(f"\n🎯 Testing: '{cmd}'")
        result = handle_meeting_command(cmd)
        if result:
            print(f"✅ Result: {result}")
        else:
            print("❌ Command not recognized")

def test_recording_flow():
    """Test the complete recording flow"""
    print("\n🎙️ Testing Recording Flow")
    print("=" * 50)
    
    try:
        # Start recording
        print("1. Starting recording...")
        result = meeting_assistant.start_recording()
        print(f"Result: {result}")
        
        # Wait a bit
        print("2. Recording for 5 seconds...")
        time.sleep(5)
        
        # Check status
        print("3. Checking status...")
        status = meeting_assistant.get_status()
        print(f"Status: {status}")
        
        # Stop recording
        print("4. Stopping recording and processing...")
        result = meeting_assistant.stop_recording()
        print(f"Result: {result}")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")

def test_ollama_connection():
    """Test Ollama connection"""
    print("\n🧠 Testing Ollama Connection")
    print("=" * 50)
    
    import requests
    
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            models = response.json()
            print("✅ Ollama is running!")
            print("Available models:")
            for model in models.get('models', []):
                print(f"  - {model.get('name', 'Unknown')}")
        else:
            print(f"❌ Ollama responded with status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama. Make sure it's running with 'ollama serve'")
    except Exception as e:
        print(f"❌ Error testing Ollama: {e}")

if __name__ == "__main__":
    print("🤖 Meeting Assistant Test Suite")
    print("=" * 50)
    
    # Test 1: Command recognition
    test_meeting_commands()
    
    # Test 2: Ollama connection
    test_ollama_connection()
    
    # Test 3: Ask user if they want to test recording
    print("\n" + "=" * 50)
    user_input = input("Do you want to test actual recording? (y/n): ").lower()
    
    if user_input == 'y':
        print("⚠️  Make sure you have a microphone connected!")
        input("Press Enter when ready to start recording test...")
        test_recording_flow()
    else:
        print("Skipping recording test.")
    
    print("\n✅ Test suite completed!")