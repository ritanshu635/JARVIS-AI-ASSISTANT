#!/usr/bin/env python3
"""
Diagnose Audio File Issues
Check what's wrong with the audio files that Whisper can't read
"""

import os
import wave
import struct

def diagnose_audio_file(filename):
    """Diagnose issues with audio file"""
    print(f"🔍 Diagnosing: {filename}")
    print("=" * 50)
    
    # Check if file exists
    if not os.path.exists(filename):
        print("❌ File does not exist")
        return False
    
    # Check file size
    size = os.path.getsize(filename)
    print(f"📁 File size: {size} bytes")
    
    if size == 0:
        print("❌ File is empty")
        return False
    
    # Try to read with wave module
    try:
        with wave.open(filename, 'rb') as wf:
            frames = wf.getnframes()
            channels = wf.getnchannels()
            rate = wf.getframerate()
            sampwidth = wf.getsampwidth()
            duration = frames / rate if rate > 0 else 0
            
            print(f"🎵 Audio properties:")
            print(f"   Channels: {channels}")
            print(f"   Sample rate: {rate} Hz")
            print(f"   Sample width: {sampwidth} bytes")
            print(f"   Frames: {frames}")
            print(f"   Duration: {duration:.2f} seconds")
            
            # Check if audio has actual data
            if frames > 0:
                # Read some audio data
                wf.rewind()
                audio_data = wf.readframes(min(1024, frames))
                
                if audio_data:
                    # Convert to integers and check amplitude
                    if sampwidth == 2:  # 16-bit
                        samples = struct.unpack(f'<{len(audio_data)//2}h', audio_data)
                        max_amp = max(abs(s) for s in samples) if samples else 0
                        print(f"📊 Max amplitude: {max_amp}")
                        
                        if max_amp > 100:
                            print("✅ Audio has good signal levels")
                            return True
                        else:
                            print("⚠️ Audio signal is very weak")
                            return True  # Still valid, just quiet
                    else:
                        print("✅ Audio data present")
                        return True
                else:
                    print("❌ No audio data in file")
                    return False
            else:
                print("❌ No audio frames in file")
                return False
                
    except Exception as e:
        print(f"❌ Wave file error: {e}")
        return False

def main():
    """Check all meeting audio files"""
    print("🔍 Audio File Diagnosis")
    print("=" * 60)
    
    # Find all meeting audio files
    audio_files = [f for f in os.listdir('.') if f.startswith('meeting_') and f.endswith('.wav')]
    
    if not audio_files:
        print("❌ No meeting audio files found")
        return
    
    print(f"📁 Found {len(audio_files)} audio files")
    print()
    
    valid_files = []
    for audio_file in sorted(audio_files):
        if diagnose_audio_file(audio_file):
            valid_files.append(audio_file)
        print()
    
    print("=" * 60)
    print("📋 DIAGNOSIS SUMMARY")
    print("=" * 60)
    print(f"Total files: {len(audio_files)}")
    print(f"Valid files: {len(valid_files)}")
    
    if valid_files:
        print("\n✅ Valid audio files:")
        for f in valid_files:
            print(f"   {f}")
        
        # Test the latest valid file with a simple approach
        latest_valid = valid_files[-1]
        print(f"\n🧪 Testing Whisper with: {latest_valid}")
        test_whisper_simple(latest_valid)
    else:
        print("\n❌ No valid audio files found")

def test_whisper_simple(filename):
    """Test Whisper with a simple approach"""
    try:
        import whisper
        
        print("📥 Loading Whisper model...")
        model = whisper.load_model("tiny")  # Use tiny model for faster testing
        
        print(f"🔄 Transcribing {filename}...")
        
        # Try with just the filename (no path manipulation)
        result = model.transcribe(filename, fp16=False)  # Disable FP16
        transcript = result["text"].strip()
        
        if transcript:
            print(f"✅ Transcription successful!")
            print(f"📝 Transcript: {transcript}")
            
            # Save transcript
            transcript_file = filename.replace('.wav', '_transcript.txt')
            with open(transcript_file, 'w', encoding='utf-8') as f:
                f.write(transcript)
            print(f"💾 Saved: {transcript_file}")
            
        else:
            print("⚠️ No speech detected in audio")
            
    except Exception as e:
        print(f"❌ Whisper test failed: {e}")

if __name__ == "__main__":
    main()