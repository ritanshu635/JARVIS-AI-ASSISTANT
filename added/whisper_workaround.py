#!/usr/bin/env python3
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
            
            # Ensure it's float32 (Whisper requirement)
            audio_float = audio_float.astype(np.float32)
            
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
