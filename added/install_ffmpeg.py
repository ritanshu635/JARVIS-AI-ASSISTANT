#!/usr/bin/env python3
"""
Install FFmpeg for Whisper
Check if FFmpeg is available and provide installation instructions
"""

import subprocess
import os
import sys

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    print("🔍 Checking FFmpeg installation...")
    
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ FFmpeg is installed!")
            version_line = result.stdout.split('\n')[0]
            print(f"📋 Version: {version_line}")
            return True
        else:
            print("❌ FFmpeg command failed")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg not found in PATH")
        return False
    except Exception as e:
        print(f"❌ FFmpeg check error: {e}")
        return False

def install_ffmpeg_windows():
    """Install FFmpeg on Windows"""
    print("\n🔧 Installing FFmpeg for Windows...")
    print("=" * 50)
    
    print("📋 Option 1: Using winget (Windows Package Manager)")
    print("Run this command in PowerShell as Administrator:")
    print("   winget install ffmpeg")
    print()
    
    print("📋 Option 2: Using Chocolatey")
    print("If you have Chocolatey installed:")
    print("   choco install ffmpeg")
    print()
    
    print("📋 Option 3: Manual Installation")
    print("1. Download from: https://ffmpeg.org/download.html#build-windows")
    print("2. Extract to C:\\ffmpeg")
    print("3. Add C:\\ffmpeg\\bin to your PATH environment variable")
    print()
    
    print("📋 Option 4: Try automatic installation with pip")
    try:
        print("Attempting to install ffmpeg-python...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'ffmpeg-python'], 
                      check=True)
        print("✅ ffmpeg-python installed")
    except Exception as e:
        print(f"❌ Failed to install ffmpeg-python: {e}")

def test_whisper_without_ffmpeg():
    """Test Whisper with a workaround that doesn't need FFmpeg"""
    print("\n🧪 Testing Whisper workaround...")
    print("=" * 50)
    
    try:
        import whisper
        import torch
        import numpy as np
        
        # Load model
        model = whisper.load_model("tiny")
        print("✅ Whisper model loaded")
        
        # Create dummy audio data for testing
        # This bypasses file reading issues
        sample_rate = 16000
        duration = 1  # 1 second
        dummy_audio = np.zeros(sample_rate * duration, dtype=np.float32)
        
        # Test transcription with dummy data
        result = model.transcribe(dummy_audio)
        print("✅ Whisper transcription works (with dummy data)")
        
        return True
        
    except Exception as e:
        print(f"❌ Whisper test failed: {e}")
        return False

def create_whisper_workaround():
    """Create a workaround for Whisper file reading"""
    print("\n🔧 Creating Whisper workaround...")
    print("=" * 50)
    
    workaround_code = '''#!/usr/bin/env python3
"""
Whisper Workaround - Read audio manually and pass to Whisper
"""

import whisper
import wave
import numpy as np

def transcribe_wav_file(filename):
    """Transcribe WAV file by reading audio data manually"""
    try:
        # Read WAV file manually
        with wave.open(filename, 'rb') as wf:
            frames = wf.getnframes()
            sample_rate = wf.getframerate()
            channels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            
            # Read audio data
            audio_data = wf.readframes(frames)
            
            # Convert to numpy array
            if sampwidth == 2:  # 16-bit
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
            else:
                raise ValueError(f"Unsupported sample width: {sampwidth}")
            
            # Convert to float32 and normalize
            audio_float = audio_array.astype(np.float32) / 32768.0
            
            # If stereo, convert to mono
            if channels == 2:
                audio_float = audio_float.reshape(-1, 2).mean(axis=1)
            
            # Resample to 16kHz if needed (Whisper expects 16kHz)
            if sample_rate != 16000:
                # Simple resampling (not perfect but works)
                target_length = int(len(audio_float) * 16000 / sample_rate)
                audio_float = np.interp(
                    np.linspace(0, len(audio_float), target_length),
                    np.arange(len(audio_float)),
                    audio_float
                )
            
            print(f"📊 Audio: {len(audio_float)} samples, {len(audio_float)/16000:.2f} seconds")
            
            # Load Whisper model
            model = whisper.load_model("tiny")
            
            # Transcribe
            result = model.transcribe(audio_float)
            return result["text"].strip()
            
    except Exception as e:
        print(f"❌ Transcription error: {e}")
        return None

if __name__ == "__main__":
    import os
    
    # Find latest meeting file
    audio_files = [f for f in os.listdir('.') if f.startswith('meeting_') and f.endswith('.wav')]
    if audio_files:
        latest_file = sorted(audio_files)[-1]
        print(f"🎵 Transcribing: {latest_file}")
        
        transcript = transcribe_wav_file(latest_file)
        if transcript:
            print(f"✅ Transcript: {transcript}")
            
            # Save transcript
            transcript_file = latest_file.replace('.wav', '_transcript.txt')
            with open(transcript_file, 'w', encoding='utf-8') as f:
                f.write(transcript)
            print(f"💾 Saved: {transcript_file}")
        else:
            print("❌ Transcription failed")
    else:
        print("❌ No meeting audio files found")
'''
    
    # Save workaround script
    with open('whisper_workaround.py', 'w', encoding='utf-8') as f:
        f.write(workaround_code)
    
    print("✅ Created: whisper_workaround.py")
    print("💡 This script reads WAV files manually and passes audio data to Whisper")
    print("🚀 Try running: python whisper_workaround.py")

def main():
    """Main function"""
    print("🔧 FFmpeg and Whisper Setup")
    print("=" * 60)
    
    # Check FFmpeg
    ffmpeg_ok = check_ffmpeg()
    
    if not ffmpeg_ok:
        install_ffmpeg_windows()
    
    # Test Whisper
    whisper_ok = test_whisper_without_ffmpeg()
    
    # Create workaround
    create_whisper_workaround()
    
    print("\n" + "=" * 60)
    print("📋 SUMMARY")
    print("=" * 60)
    print(f"FFmpeg installed: {'✅' if ffmpeg_ok else '❌'}")
    print(f"Whisper working: {'✅' if whisper_ok else '❌'}")
    print("Workaround created: ✅")
    
    if not ffmpeg_ok:
        print("\n💡 Next steps:")
        print("1. Install FFmpeg using one of the methods above")
        print("2. Restart your terminal/PowerShell")
        print("3. Try running: python whisper_workaround.py")
    else:
        print("\n🚀 Try the workaround: python whisper_workaround.py")

if __name__ == "__main__":
    main()