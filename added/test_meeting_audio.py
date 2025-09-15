#!/usr/bin/env python3
"""
Test script to verify meeting audio capture
Tests both microphone and system audio (Google Meet)
"""

import time
from system_audio_capture import SystemAudioCapture
from datetime import datetime

def test_meeting_audio_capture():
    """Test if we can capture both mic and system audio"""
    print("🎤 Testing Meeting Audio Capture")
    print("=" * 50)
    
    print("This test will help us verify if we can capture:")
    print("✅ Your voice (microphone)")
    print("✅ Google Meet participants (system audio)")
    print()
    
    # Test 1: Check available devices
    print("📋 STEP 1: Checking Audio Devices")
    print("-" * 30)
    
    try:
        capture = SystemAudioCapture()
        print("✅ Audio system initialized successfully")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Test 2: Record a sample
    print("\n📋 STEP 2: Recording Test Sample")
    print("-" * 30)
    print("Instructions:")
    print("1. Join a Google Meet (or play a YouTube video)")
    print("2. We'll record for 10 seconds")
    print("3. During recording:")
    print("   - Say something (test your mic)")
    print("   - Let meeting audio play (test system audio)")
    
    input("\n👆 Press Enter when you're ready to start recording...")
    
    # Start recording
    success, message = capture.start_recording()
    if not success:
        print(f"❌ Failed to start recording: {message}")
        return
    
    print("🔴 RECORDING NOW - 10 seconds...")
    print("🗣️ Say something now!")
    print("🔊 Make sure meeting/video audio is playing!")
    
    for i in range(10, 0, -1):
        print(f"   {i} seconds remaining...")
        time.sleep(1)
    
    # Stop recording
    audio_data, stop_message = capture.stop_recording()
    print(f"⏹️ {stop_message}")
    
    if audio_data is None:
        print("❌ No audio captured. Check your microphone permissions.")
        return
    
    # Save the test file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"meeting_test_{timestamp}.wav"
    
    save_success, save_message = capture.save_audio(audio_data, filename)
    if save_success:
        print(f"✅ Test audio saved as: {filename}")
        
        # Analyze the audio
        import numpy as np
        duration = len(audio_data) / capture.rate
        max_amplitude = np.max(np.abs(audio_data))
        
        print(f"\n📊 Audio Analysis:")
        print(f"   Duration: {duration:.2f} seconds")
        print(f"   Max amplitude: {max_amplitude:.4f}")
        print(f"   Channels: {audio_data.shape[1] if len(audio_data.shape) > 1 else 1}")
        
        # Check if we got good audio
        if max_amplitude > 0.01:
            print("✅ Good audio levels detected!")
            print("🎯 Your setup should work well for meeting recording")
        else:
            print("⚠️ Low audio levels detected")
            print("💡 Try speaking louder or check microphone settings")
        
        # Test with Whisper
        print(f"\n📋 STEP 3: Testing Whisper Transcription")
        print("-" * 30)
        test_whisper = input("Test transcription with Whisper? (y/n): ").lower()
        
        if test_whisper == 'y':
            print("🔄 Transcribing with Whisper...")
            try:
                import whisper
                model = whisper.load_model("base")
                result = model.transcribe(filename)
                transcript = result["text"].strip()
                
                if transcript:
                    print(f"✅ Transcription successful!")
                    print(f"📝 Transcript: '{transcript}'")
                    
                    if len(transcript) > 10:
                        print("🎉 Great! Your audio setup is working perfectly!")
                    else:
                        print("⚠️ Short transcript. Try speaking more clearly during recording.")
                else:
                    print("⚠️ No speech detected in audio")
                    
            except Exception as e:
                print(f"❌ Transcription error: {e}")
    
    else:
        print(f"❌ Failed to save audio: {save_message}")

def check_microphone_permissions():
    """Check if microphone permissions are set up correctly"""
    print("\n🔒 Checking Microphone Permissions")
    print("-" * 30)
    print("If recording fails, check these Windows settings:")
    print("1. Settings > Privacy & Security > Microphone")
    print("2. Allow apps to access your microphone: ON")
    print("3. Allow desktop apps to access microphone: ON")
    print("4. Make sure Python/Command Prompt has permission")

if __name__ == "__main__":
    print("🤖 Meeting Audio Test for Jarvis")
    print("=" * 50)
    
    check_microphone_permissions()
    
    print("\n" + "=" * 50)
    user_input = input("Ready to test your meeting audio setup? (y/n): ").lower()
    
    if user_input == 'y':
        test_meeting_audio_capture()
    else:
        print("Test skipped. Run this script when you're ready to test!")
    
    print("\n✅ Test completed!")
    print("\n💡 Tips for best results:")
    print("   - Use built-in laptop mic (it's fine!)")
    print("   - Make sure Stereo Mix is enabled for system audio")
    print("   - Test in a quiet environment")
    print("   - Speak clearly during meetings")