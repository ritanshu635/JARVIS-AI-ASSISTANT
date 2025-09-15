#!/usr/bin/env python3
"""
Test Whisper with the recorded audio file
"""

import whisper
import os

def test_whisper_with_file():
    """Test Whisper transcription with existing audio file"""
    print("🎤 Testing Whisper with recorded audio file")
    print("=" * 50)
    
    # Find the latest meeting file
    meeting_files = [f for f in os.listdir('.') if f.startswith('meeting_') and f.endswith('.wav')]
    
    if not meeting_files:
        print("❌ No meeting audio files found")
        return
    
    # Use the latest file
    latest_file = sorted(meeting_files)[-1]
    print(f"📁 Using file: {latest_file}")
    
    # Check if file exists and get size
    if os.path.exists(latest_file):
        file_size = os.path.getsize(latest_file)
        print(f"📊 File size: {file_size:,} bytes")
        
        if file_size < 1000:
            print("⚠️ File is very small - might be empty or corrupted")
        else:
            print("✅ File size looks good")
    else:
        print("❌ File doesn't exist")
        return
    
    # Load Whisper model
    print("\n🔄 Loading Whisper model...")
    try:
        model = whisper.load_model("base")
        print("✅ Whisper model loaded")
    except Exception as e:
        print(f"❌ Whisper model error: {e}")
        return
    
    # Try transcription
    print(f"\n🔄 Transcribing {latest_file}...")
    
    # Use absolute path
    abs_path = os.path.abspath(latest_file)
    print(f"📁 Full path: {abs_path}")
    print(f"📁 File exists check: {os.path.exists(abs_path)}")
    
    try:
        # Try copying to a simpler path first
        import shutil
        simple_path = "temp_audio.wav"
        shutil.copy2(abs_path, simple_path)
        print(f"📁 Copied to simple path: {simple_path}")
        
        result = model.transcribe(simple_path)
        transcript = result["text"].strip()
        
        print(f"✅ Transcription completed!")
        print(f"📝 Transcript length: {len(transcript)} characters")
        
        if transcript:
            print(f"📝 Transcript: '{transcript}'")
            
            # Save transcript
            transcript_file = latest_file.replace('.wav', '_transcript.txt')
            with open(transcript_file, 'w', encoding='utf-8') as f:
                f.write(transcript)
            print(f"💾 Transcript saved to: {transcript_file}")
            
        else:
            print("⚠️ No speech detected in audio")
            print("💡 This might mean:")
            print("   - Audio is too quiet")
            print("   - No speech in the recording")
            print("   - Audio format issue")
            
    except Exception as e:
        print(f"❌ Transcription error: {e}")
        print(f"Error type: {type(e).__name__}")

if __name__ == "__main__":
    test_whisper_with_file()