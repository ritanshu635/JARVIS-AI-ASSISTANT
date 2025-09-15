#!/usr/bin/env python3
"""
Fix Whisper File Access Issues
Multiple approaches to make audio files readable by Whisper
"""

import os
import shutil
import wave
import tempfile
import whisper

def fix_method_1_copy_to_temp():
    """Method 1: Copy file to temp directory"""
    print("🔧 Method 1: Copy to temp directory")
    print("-" * 40)
    
    # Find latest audio file
    audio_files = [f for f in os.listdir('.') if f.startswith('meeting_') and f.endswith('.wav')]
    if not audio_files:
        print("❌ No audio files found")
        return False
    
    latest_file = sorted(audio_files)[-1]
    print(f"📁 Using: {latest_file}")
    
    try:
        # Create temp file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Copy audio file to temp location
        shutil.copy2(latest_file, temp_path)
        print(f"📋 Copied to: {temp_path}")
        
        # Test with Whisper
        model = whisper.load_model("tiny")
        result = model.transcribe(temp_path, fp16=False)
        transcript = result["text"].strip()
        
        # Clean up temp file
        os.unlink(temp_path)
        
        if transcript:
            print(f"✅ Success! Transcript: {transcript}")
            return transcript
        else:
            print("⚠️ No speech detected")
            return ""
            
    except Exception as e:
        print(f"❌ Method 1 failed: {e}")
        return False

def fix_method_2_recreate_wav():
    """Method 2: Recreate WAV file with proper headers"""
    print("\n🔧 Method 2: Recreate WAV file")
    print("-" * 40)
    
    # Find latest audio file
    audio_files = [f for f in os.listdir('.') if f.startswith('meeting_') and f.endswith('.wav')]
    if not audio_files:
        print("❌ No audio files found")
        return False
    
    latest_file = sorted(audio_files)[-1]
    print(f"📁 Using: {latest_file}")
    
    try:
        # Read original audio data
        with wave.open(latest_file, 'rb') as original:
            frames = original.readframes(original.getnframes())
            params = original.getparams()
        
        # Create new file with clean name
        new_filename = "clean_audio.wav"
        
        # Write new WAV file
        with wave.open(new_filename, 'wb') as new_file:
            new_file.setparams(params)
            new_file.writeframes(frames)
        
        print(f"📋 Created clean file: {new_filename}")
        
        # Test with Whisper
        model = whisper.load_model("tiny")
        result = model.transcribe(new_filename, fp16=False)
        transcript = result["text"].strip()
        
        if transcript:
            print(f"✅ Success! Transcript: {transcript}")
            
            # Save transcript
            with open("clean_audio_transcript.txt", 'w', encoding='utf-8') as f:
                f.write(transcript)
            print("💾 Transcript saved to: clean_audio_transcript.txt")
            
            return transcript
        else:
            print("⚠️ No speech detected")
            return ""
            
    except Exception as e:
        print(f"❌ Method 2 failed: {e}")
        return False

def fix_method_3_convert_to_mp3():
    """Method 3: Convert to MP3 format"""
    print("\n🔧 Method 3: Convert to MP3")
    print("-" * 40)
    
    try:
        # This requires pydub and ffmpeg
        from pydub import AudioSegment
        
        # Find latest audio file
        audio_files = [f for f in os.listdir('.') if f.startswith('meeting_') and f.endswith('.wav')]
        if not audio_files:
            print("❌ No audio files found")
            return False
        
        latest_file = sorted(audio_files)[-1]
        print(f"📁 Using: {latest_file}")
        
        # Convert WAV to MP3
        audio = AudioSegment.from_wav(latest_file)
        mp3_filename = "meeting_audio.mp3"
        audio.export(mp3_filename, format="mp3")
        print(f"📋 Converted to: {mp3_filename}")
        
        # Test with Whisper
        model = whisper.load_model("tiny")
        result = model.transcribe(mp3_filename, fp16=False)
        transcript = result["text"].strip()
        
        if transcript:
            print(f"✅ Success! Transcript: {transcript}")
            return transcript
        else:
            print("⚠️ No speech detected")
            return ""
            
    except ImportError:
        print("⚠️ pydub not installed. Install with: pip install pydub")
        return False
    except Exception as e:
        print(f"❌ Method 3 failed: {e}")
        return False

def fix_method_4_simple_filename():
    """Method 4: Use simple filename without special characters"""
    print("\n🔧 Method 4: Simple filename")
    print("-" * 40)
    
    # Find latest audio file
    audio_files = [f for f in os.listdir('.') if f.startswith('meeting_') and f.endswith('.wav')]
    if not audio_files:
        print("❌ No audio files found")
        return False
    
    latest_file = sorted(audio_files)[-1]
    print(f"📁 Using: {latest_file}")
    
    try:
        # Copy to simple filename
        simple_name = "test.wav"
        shutil.copy2(latest_file, simple_name)
        print(f"📋 Copied to: {simple_name}")
        
        # Test with Whisper
        model = whisper.load_model("tiny")
        result = model.transcribe(simple_name, fp16=False)
        transcript = result["text"].strip()
        
        if transcript:
            print(f"✅ Success! Transcript: {transcript}")
            return transcript
        else:
            print("⚠️ No speech detected")
            return ""
            
    except Exception as e:
        print(f"❌ Method 4 failed: {e}")
        return False

def main():
    """Try all methods to fix Whisper access"""
    print("🔧 Fixing Whisper File Access Issues")
    print("=" * 60)
    
    methods = [
        fix_method_1_copy_to_temp,
        fix_method_2_recreate_wav,
        fix_method_4_simple_filename,
        fix_method_3_convert_to_mp3
    ]
    
    for method in methods:
        result = method()
        if result:
            print(f"\n🎉 SUCCESS! Method worked!")
            print(f"📝 Transcript: {result}")
            break
        print()
    else:
        print("\n❌ All methods failed")
        print("💡 Possible solutions:")
        print("   1. Run as administrator")
        print("   2. Install ffmpeg: https://ffmpeg.org/download.html")
        print("   3. Try different Whisper version: pip install --upgrade openai-whisper")

if __name__ == "__main__":
    main()