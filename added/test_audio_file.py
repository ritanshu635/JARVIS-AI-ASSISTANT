#!/usr/bin/env python3
"""
Test if we can read the audio file
"""

import os
import wave
import whisper

def test_audio_file():
    audio_file = "meeting_20250909_013050.wav"
    
    print(f"🔍 Testing audio file: {audio_file}")
    print("=" * 50)
    
    # Check if file exists
    if os.path.exists(audio_file):
        print("✅ File exists")
        
        # Get file size
        size = os.path.getsize(audio_file)
        print(f"📁 File size: {size} bytes")
        
        # Try to read with wave
        try:
            with wave.open(audio_file, 'rb') as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                duration = frames / rate
                print(f"🎵 Audio info: {duration:.1f} seconds, {rate} Hz")
                print("✅ Wave file is readable")
        except Exception as e:
            print(f"❌ Wave error: {e}")
        
        # Try with Whisper
        try:
            print("🗣️ Testing with Whisper...")
            model = whisper.load_model("base")
            result = model.transcribe(audio_file)
            transcript = result["text"].strip()
            print(f"✅ Whisper transcription successful!")
            print(f"📝 Transcript: {transcript}")
            return transcript
        except Exception as e:
            print(f"❌ Whisper error: {e}")
            return None
    else:
        print("❌ File does not exist")
        return None

if __name__ == "__main__":
    test_audio_file()