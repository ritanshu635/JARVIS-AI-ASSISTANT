#!/usr/bin/env python3
"""
Test the working meeting assistant with proper Stereo Mix
"""

from simple_meeting_recorder import SimpleMeetingRecorder
import time

def test_meeting_flow():
    """Test the complete meeting flow"""
    print("🎤 Testing Complete Meeting Flow")
    print("=" * 40)
    
    recorder = SimpleMeetingRecorder()
    
    print("📋 Instructions:")
    print("1. Join a Google Meet or play some audio")
    print("2. We'll record for 10 seconds")
    print("3. Then transcribe and summarize with AI")
    
    input("\n👆 Press Enter when you're ready (make sure audio is playing)...")
    
    # Start recording
    print("\n🎙️ Starting meeting recording...")
    result = recorder.start_recording()
    print(result)
    
    if "✅" not in result:
        print("❌ Recording failed to start")
        return
    
    # Record for 10 seconds
    print("\n🔴 Recording for 10 seconds...")
    for i in range(10, 0, -1):
        print(f"   {i} seconds remaining...")
        time.sleep(1)
    
    # Stop and process
    print("\n🛑 Stopping and processing meeting...")
    result = recorder.stop_recording()
    
    print("\n" + "=" * 60)
    print("📋 MEETING PROCESSING RESULT:")
    print("=" * 60)
    print(result)

if __name__ == "__main__":
    test_meeting_flow()