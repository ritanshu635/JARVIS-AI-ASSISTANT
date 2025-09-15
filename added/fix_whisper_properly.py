#!/usr/bin/env python3
"""
Fix Whisper Properly - Make it work with your audio files
"""

import os
import whisper
import wave
import subprocess
import shutil

def fix_whisper_file_access():
    """Fix Whisper file access issues"""
    print("🔧 Fixing Whisper File Access")
    print("=" * 50)
    
    # Find latest meeting audio file
    audio_files = [f for f in os.listdir('.') if f.startswith('meeting_') and f.endswith('.wav')]
    if not audio_files:
        print("❌ No meeting audio files found")
        return None
    
    latest_file = sorted(audio_files)[-1]
    print(f"📁 Testing with: {latest_file}")
    
    # Method 1: Try direct transcription
    print("\n🔄 Method 1: Direct transcription...")
    try:
        model = whisper.load_model("tiny")  # Use tiny for speed
        result = model.transcribe(latest_file, fp16=False)
        transcript = result["text"].strip()
        
        if transcript:
            print(f"✅ SUCCESS! Direct method worked!")
            print(f"📝 Transcript: {transcript}")
            return transcript
        else:
            print("⚠️ No speech detected")
            
    except Exception as e:
        print(f"❌ Direct method failed: {e}")
    
    # Method 2: Convert with FFmpeg first
    print("\n🔄 Method 2: Convert with FFmpeg...")
    try:
        converted_file = "converted_audio.wav"
        
        # Convert to standard PCM format
        cmd = [
            'ffmpeg', '-i', latest_file, 
            '-acodec', 'pcm_s16le', 
            '-ar', '16000', 
            '-ac', '1',  # mono
            '-y',  # overwrite
            converted_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ FFmpeg conversion successful")
            
            # Try transcribing converted file
            model = whisper.load_model("tiny")
            result = model.transcribe(converted_file, fp16=False)
            transcript = result["text"].strip()
            
            # Clean up
            if os.path.exists(converted_file):
                os.remove(converted_file)
            
            if transcript:
                print(f"✅ SUCCESS! FFmpeg method worked!")
                print(f"📝 Transcript: {transcript}")
                return transcript
            else:
                print("⚠️ No speech detected in converted file")
        else:
            print(f"❌ FFmpeg conversion failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ FFmpeg method failed: {e}")
    
    # Method 3: Copy to simple filename
    print("\n🔄 Method 3: Simple filename...")
    try:
        simple_file = "test_audio.wav"
        shutil.copy2(latest_file, simple_file)
        
        model = whisper.load_model("tiny")
        result = model.transcribe(simple_file, fp16=False)
        transcript = result["text"].strip()
        
        # Clean up
        if os.path.exists(simple_file):
            os.remove(simple_file)
        
        if transcript:
            print(f"✅ SUCCESS! Simple filename method worked!")
            print(f"📝 Transcript: {transcript}")
            return transcript
        else:
            print("⚠️ No speech detected")
            
    except Exception as e:
        print(f"❌ Simple filename method failed: {e}")
    
    print("\n❌ All methods failed")
    return None

if __name__ == "__main__":
    fix_whisper_file_access()