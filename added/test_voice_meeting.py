#!/usr/bin/env python3
"""
Test Voice Meeting Assistant
Quick test to verify the voice-activated meeting recording works
"""

import time
from voice_meeting_assistant import VoiceMeetingAssistant

def test_voice_meeting_flow():
    """Test the complete voice meeting flow"""
    print("🎤 Testing Voice-Activated Meeting Assistant")
    print("=" * 60)
    
    assistant = VoiceMeetingAssistant()
    
    print("📋 This test will:")
    print("1. Start voice command listening")
    print("2. Wait for you to say voice commands")
    print("3. Process meeting recording when triggered")
    print()
    print("🗣️ Voice Commands to try:")
    print("   • 'Jarvis attend the meeting for me'")
    print("   • 'OK you can leave the meeting Jarvis'")
    print("   • 'meeting status'")
    print()
    
    # Start voice listening
    print("🎙️ Starting voice command listening...")
    result = assistant.start_voice_listening()
    print(f"Result: {result}")
    
    print("\n" + "=" * 60)
    print("🎤 VOICE COMMANDS ARE NOW ACTIVE!")
    print("🗣️ Try saying: 'Jarvis attend the meeting for me'")
    print("💡 Make sure your Google Meet is playing audio")
    print("⏹️ Press Ctrl+C to stop the test")
    print("=" * 60)
    
    try:
        # Keep running until interrupted
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping voice meeting assistant...")
        assistant.stop_voice_listening()
        print("✅ Test completed!")

def test_manual_commands():
    """Test manual meeting commands (without voice)"""
    print("🧪 Testing Manual Meeting Commands")
    print("=" * 50)
    
    assistant = VoiceMeetingAssistant()
    
    print("\nCommands:")
    print("'start' - Start meeting recording")
    print("'stop' - Stop meeting recording")
    print("'status' - Check status")
    print("'quit' - Exit")
    
    while True:
        cmd = input("\nEnter command: ").lower().strip()
        
        if cmd == 'start':
            result = assistant.manual_start_recording()
            print(f"Result: {result}")
        elif cmd == 'stop':
            result = assistant.manual_stop_recording()
            print(f"Result: {result}")
        elif cmd == 'status':
            result = assistant.get_status()
            print(f"Status: {result}")
        elif cmd == 'quit':
            break
        else:
            print("Unknown command")

if __name__ == "__main__":
    print("🤖 Voice Meeting Assistant Test Suite")
    print("=" * 60)
    
    test_choice = input("Choose test:\n1. Voice commands (full test)\n2. Manual commands (quick test)\nEnter 1 or 2: ").strip()
    
    if test_choice == "1":
        print("\n🎤 Starting VOICE COMMAND test...")
        print("⚠️ Make sure your microphone is working!")
        input("Press Enter when ready...")
        test_voice_meeting_flow()
    elif test_choice == "2":
        print("\n🧪 Starting MANUAL COMMAND test...")
        test_manual_commands()
    else:
        print("Invalid choice. Exiting.")