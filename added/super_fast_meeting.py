#!/usr/bin/env python3
"""
Super Fast Meeting Assistant - Uses tiny Whisper model for speed
"""

from simple_meeting_recorder import SimpleMeetingRecorder
import time
import os
import wave
import numpy as np
import requests

def quick_meeting_test():
    """Quick meeting test with fast processing"""
    print("⚡ SUPER FAST MEETING ASSISTANT")
    print("=" * 50)
    
    # Initialize recorder
    recorder = SimpleMeetingRecorder()
    
    print("📢 Recording desktop audio for 10 seconds...")
    print("💡 Make sure audio with SPEECH is playing!")
    input("👆 Press Enter when ready...")
    
    # Start recording
    result = recorder.start_recording()
    if "✅" not in result:
        print(f"❌ Failed to start: {result}")
        return
    
    print("🔴 Recording...")
    
    # Record for 10 seconds
    for i in range(10, 0, -1):
        if i % 2 == 0:
            print(f"   {i} seconds...")
        time.sleep(1)
    
    # Stop recording
    print("\n🛑 Stopping...")
    recorder.is_recording = False
    
    if recorder.stream:
        recorder.stream.stop_stream()
        recorder.stream.close()
    
    if hasattr(recorder, 'recording_thread'):
        recorder.recording_thread.join(timeout=3)
    
    if not recorder.audio_frames:
        print("❌ No audio recorded")
        return
    
    # Check audio quality
    audio_data = np.frombuffer(b''.join(recorder.audio_frames), dtype=np.int16)
    max_amplitude = np.max(np.abs(audio_data))
    print(f"📊 Audio quality: {max_amplitude}")
    
    if max_amplitude < 100:
        print("⚠️ Very quiet audio")
        return
    
    # Quick transcription
    print("\n⚡ Quick transcription...")
    transcript = quick_transcribe(recorder.audio_frames, recorder.channels, recorder.rate)
    
    if transcript:
        print(f"✅ Transcript: {transcript}")
        
        # Quick summary
        print("\n🧠 Quick summary...")
        summary = quick_summary(transcript)
        
        print("\n" + "=" * 50)
        print("🎉 RESULTS:")
        print("=" * 50)
        print(f"📝 TRANSCRIPT:\n{transcript}")
        print(f"\n📋 SUMMARY:\n{summary}")
        print("=" * 50)
        print("✅ SUCCESS!")
        
    else:
        print("❌ No speech detected")

def quick_transcribe(audio_frames, channels, rate):
    """Quick transcription with tiny model"""
    try:
        import whisper
        
        # Convert to numpy
        audio_data = np.frombuffer(b''.join(audio_frames), dtype=np.int16)
        audio_float = audio_data.astype(np.float32) / 32768.0
        
        # Convert to mono if stereo
        if channels == 2:
            audio_float = audio_float.reshape(-1, 2).mean(axis=1)
        
        # Resample to 16kHz
        if rate != 16000:
            target_length = int(len(audio_float) * 16000 / rate)
            audio_float = np.interp(
                np.linspace(0, len(audio_float), target_length),
                np.arange(len(audio_float)),
                audio_float
            )
        
        # Use tiny model for speed
        model = whisper.load_model("tiny")
        result = model.transcribe(audio_float, fp16=False, language='en')
        
        return result["text"].strip()
        
    except Exception as e:
        print(f"❌ Transcription error: {e}")
        return None

def quick_summary(transcript):
    """Quick summary with Ollama"""
    try:
        prompt = f"Summarize this audio transcript in 2-3 bullet points:\n\n{transcript}"
        
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'llama3.2:3b',
                'prompt': prompt,
                'stream': False
            },
            timeout=20
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('response', 'Summary failed')
        else:
            return f"Ollama error: {response.status_code}"
            
    except Exception as e:
        return f"Summary error: {e}"

if __name__ == "__main__":
    quick_meeting_test()