#!/usr/bin/env python3
"""
Debug Whisper File Access - Find out exactly why it can't read your files
"""

import os
import whisper
import wave

def debug_whisper_file_access():
    """Debug why Whisper can't access your audio files"""
    print("🔍 DEBUGGING WHISPER FILE ACCESS")
    print("=" * 50)
    
    # Find your latest audio file
    audio_files = [f for f in os.listdir('.') if f.endswith('.wav') and ('meeting' in f or 'final' in f)]
    if not audio_files:
        print("❌ No audio files found")
        return
    
    latest_file = sorted(audio_files)[-1]
    print(f"📁 Testing with your file: {latest_file}")
    
    # Check file details
    print(f"📊 Current directory: {os.getcwd()}")
    print(f"📊 File exists: {os.path.exists(latest_file)}")
    print(f"📊 File size: {os.path.getsize(latest_file)} bytes")
    print(f"📊 Full path: {os.path.abspath(latest_file)}")
    
    # Check WAV file properties
    try:
        with wave.open(latest_file, 'rb') as wf:
            print(f"📊 WAV properties:")
            print(f"   Channels: {wf.getnchannels()}")
            print(f"   Sample rate: {wf.getframerate()}")
            print(f"   Sample width: {wf.getsampwidth()}")
            print(f"   Frames: {wf.getnframes()}")
            print(f"   Duration: {wf.getnframes() / wf.getframerate():.2f} seconds")
    except Exception as e:
        print(f"❌ WAV file error: {e}")
        return
    
    # Test Whisper with different approaches
    print("\n🔄 Testing Whisper approaches...")
    
    # Method 1: Direct filename
    print("Method 1: Direct filename")
    try:
        model = whisper.load_model("tiny")  # Use tiny for speed
        print(f"Trying to transcribe: {latest_file}")
        result = model.transcribe(latest_file, fp16=False)
        transcript = result["text"].strip()
        print(f"✅ SUCCESS! Transcript: {transcript}")
        return transcript
    except Exception as e:
        print(f"❌ Method 1 failed: {e}")
    
    # Method 2: Full absolute path
    print("\nMethod 2: Full absolute path")
    try:
        full_path = os.path.abspath(latest_file)
        print(f"Trying with full path: {full_path}")
        result = model.transcribe(full_path, fp16=False)
        transcript = result["text"].strip()
        print(f"✅ SUCCESS! Transcript: {transcript}")
        return transcript
    except Exception as e:
        print(f"❌ Method 2 failed: {e}")
    
    # Method 3: Copy to simple name
    print("\nMethod 3: Copy to simple name")
    try:
        import shutil
        simple_name = "test.wav"
        shutil.copy2(latest_file, simple_name)
        print(f"Copied to: {simple_name}")
        
        result = model.transcribe(simple_name, fp16=False)
        transcript = result["text"].strip()
        
        os.remove(simple_name)  # cleanup
        print(f"✅ SUCCESS! Transcript: {transcript}")
        return transcript
    except Exception as e:
        print(f"❌ Method 3 failed: {e}")
    
    # Method 4: Convert with FFmpeg first
    print("\nMethod 4: Convert with FFmpeg")
    try:
        import subprocess
        converted_file = "converted.wav"
        
        cmd = ['ffmpeg', '-i', latest_file, '-ar', '16000', '-ac', '1', '-y', converted_file]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("FFmpeg conversion successful")
            result = model.transcribe(converted_file, fp16=False)
            transcript = result["text"].strip()
            
            os.remove(converted_file)  # cleanup
            print(f"✅ SUCCESS! Transcript: {transcript}")
            return transcript
        else:
            print(f"FFmpeg failed: {result.stderr}")
    except Exception as e:
        print(f"❌ Method 4 failed: {e}")
    
    print("\n❌ ALL METHODS FAILED")
    print("💡 Possible solutions:")
    print("1. Check if FFmpeg is properly installed")
    print("2. Try running as administrator")
    print("3. Move audio file to C:\\temp\\ and try again")

if __name__ == "__main__":
    debug_whisper_file_access()