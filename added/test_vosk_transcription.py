#!/usr/bin/env python3
"""
Test Vosk transcription with existing audio file
"""

import os
import json
import wave
import numpy as np
from vosk import Model, KaldiRecognizer

def test_vosk_transcription():
    """Test Vosk transcription with existing file"""
    print("🧪 Testing Vosk Transcription")
    print("=" * 40)
    
    # Use the latest audio file
    audio_file = "working_vosk_20250909_024707.wav"
    
    if not os.path.exists(audio_file):
        print(f"❌ File not found: {audio_file}")
        return
    
    # Setup Vosk model
    model_path = "vosk-model-en-us-0.22-lgraph"
    if not os.path.exists(model_path):
        print("❌ Vosk model not found")
        return
    
    print("✅ Loading Vosk model...")
    model = Model(model_path)
    
    # Convert audio first
    print("🔄 Converting audio...")
    converted_file = convert_audio_for_vosk(audio_file)
    
    if converted_file:
        print(f"✅ Using converted file: {converted_file}")
        transcribe_file = converted_file
    else:
        print("⚠️ Using original file")
        transcribe_file = audio_file
    
    # Transcribe
    print("🗣️ Transcribing...")
    try:
        wf = wave.open(transcribe_file, "rb")
        
        print(f"📊 Audio: {wf.getnchannels()} channels, {wf.getframerate()} Hz")
        
        rec = KaldiRecognizer(model, wf.getframerate())
        rec.SetWords(True)
        
        transcript_parts = []
        
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                if result.get('text'):
                    transcript_parts.append(result['text'])
                    print(f"📝 Partial: {result['text']}")
        
        # Get final result
        final_result = json.loads(rec.FinalResult())
        if final_result.get('text'):
            transcript_parts.append(final_result['text'])
            print(f"📝 Final: {final_result['text']}")
        
        wf.close()
        
        # Combine results
        full_transcript = ' '.join(transcript_parts).strip()
        
        if full_transcript:
            print(f"\n✅ SUCCESS!")
            print(f"📝 Full transcript: {full_transcript}")
            
            # Save transcript
            with open("vosk_test_transcript.txt", "w", encoding="utf-8") as f:
                f.write(full_transcript)
            print("💾 Saved to: vosk_test_transcript.txt")
            
        else:
            print("⚠️ No speech detected")
        
        # Clean up
        if converted_file and converted_file != audio_file:
            os.remove(converted_file)
            
    except Exception as e:
        print(f"❌ Transcription error: {e}")

def convert_audio_for_vosk(audio_file):
    """Convert audio for Vosk"""
    try:
        print("🔄 Converting with Python...")
        
        # Read original WAV file
        with wave.open(audio_file, 'rb') as wf:
            frames = wf.readframes(wf.getnframes())
            sample_rate = wf.getframerate()
            channels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
        
        if sampwidth != 2:
            print(f"⚠️ Unsupported sample width: {sampwidth}")
            return None
        
        # Convert to numpy array
        audio_data = np.frombuffer(frames, dtype=np.int16)
        
        # Convert stereo to mono if needed
        if channels == 2:
            audio_data = audio_data.reshape(-1, 2).mean(axis=1).astype(np.int16)
            print("✅ Converted stereo to mono")
        
        # Resample to 16kHz if needed
        if sample_rate != 16000:
            target_length = int(len(audio_data) * 16000 / sample_rate)
            audio_data = np.interp(
                np.linspace(0, len(audio_data), target_length),
                np.arange(len(audio_data)),
                audio_data
            ).astype(np.int16)
            print(f"✅ Resampled from {sample_rate}Hz to 16000Hz")
        
        # Save converted audio
        converted_file = "vosk_converted.wav"
        with wave.open(converted_file, 'wb') as wf:
            wf.setnchannels(1)  # mono
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(16000)  # 16kHz
            wf.writeframes(audio_data.tobytes())
        
        print(f"✅ Converted audio saved: {converted_file}")
        return converted_file
        
    except Exception as e:
        print(f"❌ Conversion error: {e}")
        return None

if __name__ == "__main__":
    test_vosk_transcription()