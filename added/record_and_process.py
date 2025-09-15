#!/usr/bin/env python3
"""
Record Desktop Audio and Process with Whisper + Ollama
Complete test of the meeting assistant pipeline
"""

from simple_meeting_recorder import SimpleMeetingRecorder
import time
import os

def main():
    print("🎤 Complete Meeting Assistant Test")
    print("=" * 60)
    print("📢 This will:")
    print("1. Record desktop audio (Google Meet, YouTube, etc.)")
    print("2. Convert audio to text with Whisper")
    print("3. Summarize text with Ollama")
    print("4. Show you the complete results")
    print()
    
    recorder = SimpleMeetingRecorder()
    
    print("📋 Instructions:")
    print("• Open Google Meet, YouTube, or any audio/video")
    print("• Make sure audio is playing through speakers")
    print("• Speak some words or play content with speech")
    print("• Recording will capture desktop audio (not your mic)")
    print()
    
    input("👆 Press Enter when audio with SPEECH is playing...")
    
    # Start recording
    print("\n🎙️ Starting desktop audio recording...")
    result = recorder.start_recording()
    print(f"Start result: {result}")
    
    if "✅" in result:
        print("\n🔴 Recording desktop audio for 20 seconds...")
        print("💡 Make sure there's SPEECH playing (not just music)")
        print("🗣️ You can also speak near your speakers")
        
        for i in range(20, 0, -1):
            if i % 5 == 0:
                print(f"   {i} seconds remaining... (make sure speech is playing)")
            time.sleep(1)
        
        print("\n🛑 Stopping and processing with Whisper + Ollama...")
        result = recorder.stop_recording()
        
        print("\n" + "=" * 60)
        print("📋 COMPLETE PROCESSING RESULT:")
        print("=" * 60)
        print(result)
        
        # Check if files were created
        print("\n📁 Generated files:")
        for file in os.listdir('.'):
            if file.startswith('meeting_') and (file.endswith('.txt') or file.endswith('.wav')):
                print(f"   {file}")
        
    else:
        print("❌ Failed to start recording")
        print("💡 Make sure Stereo Mix is enabled in Windows Sound settings")

if __name__ == "__main__":
    main()