#!/usr/bin/env python3
"""
Test Whisper with simple filename
"""

import whisper
import os

def test_simple_whisper():
    """Test Whisper with simple.wav"""
    print("🧪 Testing Whisper with simple.wav")
    print("=" * 40)
    
    if not os.path.exists("simple.wav"):
        print("❌ simple.wav not found")
        return
    
    try:
        print("📥 Loading Whisper model...")
        model = whisper.load_model("tiny")
        
        print("🔄 Transcribing simple.wav...")
        result = model.transcribe("simple.wav", fp16=False)
        transcript = result["text"].strip()
        
        if transcript:
            print(f"✅ SUCCESS!")
            print(f"📝 Transcript: {transcript}")
            
            # Save transcript
            with open("simple_transcript.txt", "w", encoding="utf-8") as f:
                f.write(transcript)
            print("💾 Saved to: simple_transcript.txt")
            
        else:
            print("⚠️ No speech detected")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_simple_whisper()