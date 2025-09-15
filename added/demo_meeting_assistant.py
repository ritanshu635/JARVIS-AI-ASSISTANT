#!/usr/bin/env python3
"""
Demo script for Meeting Assistant - Perfect for hackathon presentation
"""

import time
import os
import sys
from meeting_assistant import meeting_assistant

def print_banner(text):
    """Print a fancy banner"""
    print("\n" + "=" * 60)
    print(f"🤖 {text}")
    print("=" * 60)

def demo_meeting_assistant():
    """Run a complete demo of the meeting assistant"""
    
    print_banner("JARVIS MEETING ASSISTANT DEMO")
    print("🎯 This demo shows how Jarvis can attend meetings for you!")
    print("📝 It will record audio, transcribe with Whisper, and summarize with Ollama")
    
    input("\n👆 Press Enter to start the demo...")
    
    # Step 1: Start recording
    print_banner("STEP 1: Starting Meeting Recording")
    print("🎙️ Command: 'Jarvis, attend the meeting for me'")
    
    result = meeting_assistant.start_recording()
    print(f"✅ Jarvis Response: {result}")
    
    # Step 2: Simulate meeting content
    print_banner("STEP 2: Simulating Meeting Audio")
    print("🗣️ Now we simulate a meeting happening...")
    print("   (In real use, this would be your Google Meet/Zoom audio)")
    
    # Record for a short time
    for i in range(5, 0, -1):
        print(f"   Recording... {i} seconds remaining")
        time.sleep(1)
    
    # Step 3: Check status
    print_banner("STEP 3: Checking Recording Status")
    status = meeting_assistant.get_status()
    print(f"📊 Status: {status}")
    
    # Step 4: Stop and process
    print_banner("STEP 4: Processing Meeting")
    print("🛑 Command: 'Jarvis, you can leave the meeting'")
    print("⏳ Processing (transcription + summarization)...")
    
    result = meeting_assistant.stop_recording()
    print(f"✅ Result: {result}")
    
    # Step 5: Show files created
    print_banner("STEP 5: Generated Files")
    print("📁 Files created during this demo:")
    
    # List meeting files
    for file in os.listdir('.'):
        if file.startswith('meeting_') and (file.endswith('.txt') or file.endswith('.wav')):
            print(f"   📄 {file}")
    
    print_banner("DEMO COMPLETED!")
    print("🎉 That's how Jarvis saves you from boring meetings!")
    print("💡 Key Benefits:")
    print("   ✅ Never miss important points")
    print("   ✅ Get structured summaries")
    print("   ✅ Save time and focus on what matters")
    print("   ✅ All processing happens locally (privacy-first)")

def hackathon_pitch():
    """Print the hackathon pitch"""
    print_banner("HACKATHON PITCH")
    print("🏆 Why This Feature Wins:")
    print()
    print("1. 🎯 SOLVES REAL PROBLEMS")
    print("   - Meeting fatigue is universal")
    print("   - People hate sitting through long meetings")
    print("   - Important points often get missed")
    print()
    print("2. 🚀 CUTTING-EDGE TECHNOLOGY")
    print("   - OpenAI Whisper for transcription")
    print("   - Local LLM (Ollama) for summarization")
    print("   - Voice-activated interface")
    print("   - Real-time audio processing")
    print()
    print("3. 🔒 PRIVACY-FIRST APPROACH")
    print("   - All processing happens locally")
    print("   - No data sent to external servers")
    print("   - Complete control over meeting data")
    print()
    print("4. 🎤 NATURAL USER INTERFACE")
    print("   - Simple voice commands")
    print("   - Conversational interaction")
    print("   - No complex setup required")
    print()
    print("5. 📈 MARKET POTENTIAL")
    print("   - Remote work is here to stay")
    print("   - Meeting productivity is a huge pain point")
    print("   - Scalable to enterprise solutions")

if __name__ == "__main__":
    print("🤖 JARVIS MEETING ASSISTANT")
    print("Choose an option:")
    print("1. Run Demo")
    print("2. Show Hackathon Pitch")
    print("3. Both")
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    if choice == "1":
        demo_meeting_assistant()
    elif choice == "2":
        hackathon_pitch()
    elif choice == "3":
        hackathon_pitch()
        input("\n👆 Press Enter to continue to demo...")
        demo_meeting_assistant()
    else:
        print("Invalid choice. Running demo...")
        demo_meeting_assistant()