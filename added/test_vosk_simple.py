#!/usr/bin/env python3
"""
Simple Vosk Test - Just test if Vosk can read your audio files
"""

import os
import json
import wave
from vosk import Model, KaldiRecognizer

def test_vosk():
    """Simple test of Vosk with existing audio files"""
    print("🧪 Testing Vosk with your audio files")
    print("=" * 50)
    
    # Find audio files
    audio_files = [f for f in os.listdir('.') if f.endswith('.wav') and 'meeting' in f]
    if not audio_files:
        print("❌ No audio files found")
        return
    
    latest_file = sorted(audio_files)[-1]
    print(f"📁 Testing with: {latest_file}")
    
    # Try to use Vosk without downloading model first
    try:
        print("🔄 Testing Vosk...")
        
        # This will fail if no model, but let's see the error
        model = Model("vosk-model-en-us-0.22")
        
        wf = wave.open(latest_file, "rb")
        rec = KaldiRecognizer(model, wf.getframerate())
        
        transcript_parts = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                if result.get('text'):
                    transcript_parts.append(result['text'])
        
        final_result = json.loads(rec.FinalResult())
        if final_result.get('text'):
            transcript_parts.append(final_result['text'])
        
        transcript = ' '.join(transcript_parts)
        print(f"✅ SUCCESS: {transcript}")
        
    except Exception as e:
        print(f"❌ Vosk error: {e}")
        
        if "does not exist" in str(e):
            print("\n💡 Need to download Vosk model first")
            print("Run this to download:")
            print("wget https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip")
            print("unzip vosk-model-en-us-0.22.zip")

if __name__ == "__main__":
    test_vosk()