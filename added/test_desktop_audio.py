#!/usr/bin/env python3
"""
Test Desktop Audio Recording
This will record whatever is playing on your speakers (Google Meet, YouTube, etc.)
"""

from simple_meeting_recorder import SimpleMeetingRecorder
import time

def main():
    print("🎤 Desktop Audio Recording Test")
    print("=" * 50)
    print("📢 This will record DESKTOP AUDIO (whatever is playing on your speakers)")
    print("💡 Perfect for Google Meet, Zoom, YouTube, etc.")
    print()
    
    recorder = SimpleMeetingRecorder()
    
    print("📋 Instructions:")
    print("1. Open Google Meet, YouTube, or play any audio")
    print("2. Make sure audio is playing through your speakers")
    print("3. Press Enter to start recording")
    print("4. Let audio play for 15 seconds")
    print("5. Recording will stop automatically")
    print()
    
    input("👆 Press Enter when audio is playing...")
    
    # Start recording
    print("\n🎙️ Starting desktop audio recording...")
    result = recorder.start_recording()
    print(f"Result: {result}")
    
    if "✅" in result:
        print("\n🔴 Recording desktop audio for 15 seconds...")
        print("💡 Make sure Google Meet or other audio is playing!")
        
        for i in range(15, 0, -1):
            print(f"   {i} seconds remaining...")
            time.sleep(1)
        
        print("\n🛑 Stopping and processing...")
        result = recorder.stop_recording()
        print("\n" + "=" * 60)
        print("📋 PROCESSING RESULT:")
        print("=" * 60)
        print(result)
    else:
        print("❌ Failed to start recording")

if __name__ == "__main__":
    main()