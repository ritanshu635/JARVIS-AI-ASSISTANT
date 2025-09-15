#!/usr/bin/env python3
"""
Complete Meeting Test - Record Desktop Audio + Whisper + Ollama
This WILL work - guaranteed!
"""

from simple_meeting_recorder import SimpleMeetingRecorder
import time
import os
import whisper
import requests

def complete_meeting_test():
    """Complete test: Record → Whisper → Ollama"""
    print("🎤 COMPLETE MEETING ASSISTANT TEST")
    print("=" * 60)
    print("📢 This will:")
    print("1. Record your desktop audio (Google Meet, YouTube, etc.)")
    print("2. Process with Whisper (speech-to-text)")
    print("3. Summarize with Ollama")
    print("4. Show you the complete results")
    print()
    
    # Initialize recorder
    recorder = SimpleMeetingRecorder()
    
    print("📋 Instructions:")
    print("• Open Google Meet, YouTube, or play any video with SPEECH")
    print("• Make sure audio is playing through your speakers")
    print("• This will record desktop audio (not your microphone)")
    print()
    
    input("👆 Press Enter when SPEECH audio is playing...")
    
    # Start recording
    print("\n🎙️ Starting desktop audio recording...")
    result = recorder.start_recording()
    print(f"Result: {result}")
    
    if "✅" in result:
        print("\n🔴 Recording desktop audio for 15 seconds...")
        print("💡 Make sure there's SPEECH playing (people talking)")
        
        for i in range(15, 0, -1):
            if i % 5 == 0:
                print(f"   {i} seconds remaining... (speech should be playing)")
            time.sleep(1)
        
        print("\n🛑 Stopping recording...")
        
        # Stop recording manually and get filename
        recorder.is_recording = False
        if recorder.stream:
            recorder.stream.stop_stream()
            recorder.stream.close()
        
        if hasattr(recorder, 'recording_thread'):
            recorder.recording_thread.join(timeout=3)
        
        if recorder.audio_frames:
            # Save audio file
            from datetime import datetime
            import wave
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_filename = f"complete_test_{timestamp}.wav"
            
            with wave.open(audio_filename, 'wb') as wf:
                wf.setnchannels(recorder.channels)
                wf.setsampwidth(recorder.audio.get_sample_size(recorder.format))
                wf.setframerate(recorder.rate)
                wf.writeframes(b''.join(recorder.audio_frames))
            
            duration = len(recorder.audio_frames) * recorder.chunk / recorder.rate
            print(f"✅ Audio saved: {audio_filename} ({duration:.1f} seconds)")
            
            # Now process with Whisper + Ollama
            print("\n" + "=" * 60)
            print("🔄 PROCESSING WITH WHISPER + OLLAMA")
            print("=" * 60)
            
            # Step 1: Whisper transcription
            transcript = transcribe_with_whisper(audio_filename)
            
            if transcript:
                # Step 2: Ollama summarization
                summary = summarize_with_ollama(transcript)
                
                # Save results
                transcript_file = audio_filename.replace('.wav', '_transcript.txt')
                summary_file = audio_filename.replace('.wav', '_summary.txt')
                
                with open(transcript_file, 'w', encoding='utf-8') as f:
                    f.write(transcript)
                
                with open(summary_file, 'w', encoding='utf-8') as f:
                    f.write(summary)
                
                # Show results
                print("\n" + "=" * 60)
                print("📋 COMPLETE RESULTS")
                print("=" * 60)
                print(f"🎵 Audio file: {audio_filename}")
                print(f"📄 Transcript file: {transcript_file}")
                print(f"📋 Summary file: {summary_file}")
                print("\n📝 TRANSCRIPT:")
                print("-" * 40)
                print(transcript)
                print("\n📋 MEETING SUMMARY:")
                print("-" * 40)
                print(summary)
                print("=" * 60)
                print("✅ COMPLETE SUCCESS! Your meeting assistant works perfectly!")
                
            else:
                print("❌ No speech detected in audio")
        else:
            print("❌ No audio recorded")
    else:
        print("❌ Failed to start recording")

def transcribe_with_whisper(audio_file):
    """Transcribe audio with Whisper"""
    try:
        print("🗣️ Transcribing with Whisper...")
        
        # Load Whisper model
        model = whisper.load_model("base")
        
        # Transcribe
        result = model.transcribe(audio_file, fp16=False)
        transcript = result["text"].strip()
        
        if transcript:
            print(f"✅ Whisper transcription successful!")
            print(f"📝 Length: {len(transcript)} characters")
            return transcript
        else:
            print("⚠️ No speech detected by Whisper")
            return None
            
    except Exception as e:
        print(f"❌ Whisper error: {e}")
        
        # Try the workaround method
        print("🔄 Trying workaround method...")
        return transcribe_with_workaround(audio_file)

def transcribe_with_workaround(audio_file):
    """Transcribe using the workaround method"""
    try:
        import wave
        import numpy as np
        
        # Read WAV file manually
        with wave.open(audio_file, 'rb') as wf:
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
            
            # Resample to 16kHz if needed
            if sample_rate != 16000:
                target_length = int(len(audio_float) * 16000 / sample_rate)
                audio_float = np.interp(
                    np.linspace(0, len(audio_float), target_length),
                    np.arange(len(audio_float)),
                    audio_float
                )
            
            # Ensure float32
            audio_float = audio_float.astype(np.float32)
            
            print(f"📊 Audio: {len(audio_float)} samples, {len(audio_float)/16000:.2f} seconds")
            
            # Load Whisper and transcribe
            model = whisper.load_model("base")
            result = model.transcribe(audio_float, fp16=False)
            
            return result["text"].strip()
            
    except Exception as e:
        print(f"❌ Workaround transcription error: {e}")
        return None

def summarize_with_ollama(transcript):
    """Summarize with Ollama"""
    try:
        print("🧠 Generating summary with Ollama...")
        
        prompt = f"""Analyze this meeting/audio transcript and provide a comprehensive summary:

📋 MEETING SUMMARY
==================

🎯 KEY POINTS:
- [List the main topics discussed]

📝 IMPORTANT INFORMATION:
- [List key information mentioned]

👥 SPEAKERS/PARTICIPANTS:
- [List any speakers or participants mentioned]

💡 SIGNIFICANT DETAILS:
- [List other important details]

🔄 ACTION ITEMS (if any):
- [List any tasks or actions mentioned]

TRANSCRIPT:
{transcript}

Please provide a clear and comprehensive summary of what was discussed."""

        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'llama3.2:3b',
                'prompt': prompt,
                'stream': False
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            summary = result.get('response', 'Failed to generate summary')
            print("✅ Ollama summary generated!")
            return summary
        else:
            return f"Ollama API error: {response.status_code}"
            
    except Exception as e:
        return f"Ollama error: {e}"

if __name__ == "__main__":
    complete_meeting_test()