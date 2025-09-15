#!/usr/bin/env python3
"""
Quick Meeting Test - Test the meeting recording manually
"""

from voice_meeting_assistant import VoiceMeetingAssistant
import time

def main():
    print("🎤 Quick Meeting Recording Test")
    print("=" * 50)
    
    assistant = VoiceMeetingAssistant()
    
    print("📋 This will test meeting recording:")
    print("1. Start recording desktop audio")
    print("2. Record for 10 seconds")
    print("3. Stop and process with Whisper + Ollama")
    print()
    
    # Test manual recording
    print("🎙️ Starting meeting recording...")
    result = assistant.manual_start_recording()
    print(f"Start result: {result}")
    
    if "✅" in result:
        print("\n🔴 Recording for 10 seconds...")
        print("💡 Play some audio now (YouTube, music, etc.)")
        
        for i in range(10, 0, -1):
            print(f"   {i} seconds remaining...")
            time.sleep(1)
        
        print("\n🛑 Stopping recording and processing...")
        result = assistant.manual_stop_recording()
        print(f"Stop result: {result}")
    else:
        print("❌ Failed to start recording")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    main()