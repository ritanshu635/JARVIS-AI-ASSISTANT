#!/usr/bin/env python3
"""
Vosk Working Final - Convert audio in Python without FFmpeg
"""

import os
import json
import wave
import requests
import numpy as np
from vosk import Model, KaldiRecognizer
from simple_meeting_recorder import SimpleMeetingRecorder
import time

class WorkingVoskAssistant:
    def __init__(self):
        self.model = None
        self.recorder = SimpleMeetingRecorder()
        self.setup_vosk_model()
    
    def setup_vosk_model(self):
        """Setup Vosk model"""
        model_path = "vosk-model-en-us-0.22-lgraph"
        
        if os.path.exists(model_path):
            print("✅ Vosk model found")
            self.model = Model(model_path)
        else:
            print("❌ Vosk model not found")
            self.model = None
    
    def convert_audio_python(self, audio_file):
        """Convert audio using Python (no FFmpeg needed)"""
        try:
            print("🔄 Converting audio with Python...")
            
            # Read original WAV file
            with wave.open(audio_file, 'rb') as wf:
                frames = wf.readframes(wf.getnframes())
                sample_rate = wf.getframerate()
                channels = wf.getnchannels()
                sampwidth = wf.getsampwidth()
            
            # Convert to numpy array
            if sampwidth == 2:  # 16-bit
                audio_data = np.frombuffer(frames, dtype=np.int16)
            else:
                print(f"⚠️ Unsupported sample width: {sampwidth}")
                return None
            
            # Convert stereo to mono if needed
            if channels == 2:
                audio_data = audio_data.reshape(-1, 2).mean(axis=1).astype(np.int16)
                print("✅ Converted stereo to mono")
            
            # Resample to 16kHz if needed
            if sample_rate != 16000:
                # Simple resampling
                target_length = int(len(audio_data) * 16000 / sample_rate)
                audio_data = np.interp(
                    np.linspace(0, len(audio_data), target_length),
                    np.arange(len(audio_data)),
                    audio_data
                ).astype(np.int16)
                print(f"✅ Resampled from {sample_rate}Hz to 16000Hz")
            
            # Save converted audio
            converted_file = audio_file.replace('.wav', '_converted.wav')
            with wave.open(converted_file, 'wb') as wf:
                wf.setnchannels(1)  # mono
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(16000)  # 16kHz
                wf.writeframes(audio_data.tobytes())
            
            print(f"✅ Converted audio saved: {converted_file}")
            return converted_file
            
        except Exception as e:
            print(f"❌ Python conversion error: {e}")
            return None
    
    def transcribe_with_vosk(self, audio_file):
        """Transcribe using Vosk"""
        if not self.model:
            return "❌ Vosk model not available"
        
        try:
            # Convert audio first
            converted_file = self.convert_audio_python(audio_file)
            if not converted_file:
                print("⚠️ Using original file without conversion")
                converted_file = audio_file
            
            print(f"🗣️ Transcribing with Vosk...")
            
            # Open WAV file
            wf = wave.open(converted_file, "rb")
            
            print(f"📊 Audio: {wf.getnchannels()} channels, {wf.getframerate()} Hz, {wf.getnframes()} frames")
            
            # Create recognizer
            rec = KaldiRecognizer(self.model, wf.getframerate())
            rec.SetWords(True)
            
            transcript_parts = []
            
            # Process audio in chunks
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
            
            # Clean up converted file
            if converted_file != audio_file and os.path.exists(converted_file):
                os.remove(converted_file)
            
            # Combine all parts
            full_transcript = ' '.join(transcript_parts).strip()
            
            if full_transcript:
                print(f"✅ Vosk transcription successful!")
                print(f"📝 Total length: {len(full_transcript)} characters")
                return full_transcript
            else:
                return "⚠️ No speech detected in audio"
                
        except Exception as e:
            print(f"❌ Vosk transcription error: {e}")
            return f"❌ Transcription failed: {e}"
    
    def record_and_process(self, duration=20):
        """Record and process with Vosk"""
        print("🎤 WORKING VOSK MEETING ASSISTANT")
        print("=" * 50)
        
        if not self.model:
            print("❌ Vosk model not available")
            return
        
        print(f"📢 Recording desktop audio for {duration} seconds...")
        print("💡 Make sure audio with CLEAR SPEECH is playing!")
        input("👆 Press Enter when ready...")
        
        # Start recording
        result = self.recorder.start_recording()
        if "✅" not in result:
            print(f"❌ Failed to start: {result}")
            return
        
        print("🔴 Recording...")
        
        # Record for specified duration
        for i in range(duration, 0, -1):
            if i % 5 == 0:
                print(f"   {i} seconds remaining...")
            time.sleep(1)
        
        # Stop recording
        print("\n🛑 Stopping recording...")
        self.recorder.is_recording = False
        
        if self.recorder.stream:
            self.recorder.stream.stop_stream()
            self.recorder.stream.close()
        
        if hasattr(self.recorder, 'recording_thread'):
            self.recorder.recording_thread.join(timeout=3)
        
        if not self.recorder.audio_frames:
            print("❌ No audio recorded")
            return
        
        # Save audio file
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_filename = f"working_vosk_{timestamp}.wav"
        
        with wave.open(audio_filename, 'wb') as wf:
            wf.setnchannels(self.recorder.channels)
            wf.setsampwidth(self.recorder.audio.get_sample_size(self.recorder.format))
            wf.setframerate(self.recorder.rate)
            wf.writeframes(b''.join(self.recorder.audio_frames))
        
        duration_actual = len(self.recorder.audio_frames) * self.recorder.chunk / self.recorder.rate
        print(f"✅ Audio saved: {audio_filename} ({duration_actual:.1f} seconds)")
        
        # Transcribe with Vosk
        transcript = self.transcribe_with_vosk(audio_filename)
        
        if "❌" not in transcript and "⚠️" not in transcript:
            print(f"\n📝 TRANSCRIPT: {transcript}")
            
            # Summarize with Ollama
            print("\n🧠 Processing with Ollama...")
            summary = self.summarize_with_ollama(transcript)
            
            # Save results
            transcript_file = audio_filename.replace('.wav', '_transcript.txt')
            summary_file = audio_filename.replace('.wav', '_summary.txt')
            
            with open(transcript_file, 'w', encoding='utf-8') as f:
                f.write(transcript)
            
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary)
            
            # Show results
            print("\n" + "=" * 60)
            print("🎉 WORKING VOSK SUCCESS!")
            print("=" * 60)
            print(f"🎵 Audio: {audio_filename}")
            print(f"📄 Transcript: {transcript_file}")
            print(f"📋 Summary: {summary_file}")
            print("\n📝 TRANSCRIPT:")
            print("-" * 30)
            print(transcript)
            print("\n📋 MEETING SUMMARY:")
            print("-" * 30)
            print(summary)
            print("=" * 60)
            print("✅ VOSK MEETING ASSISTANT WORKING!")
            
        else:
            print(f"Result: {transcript}")
    
    def summarize_with_ollama(self, transcript):
        """Summarize with Ollama"""
        try:
            prompt = f"""Analyze this meeting transcript and provide a summary:

📋 MEETING SUMMARY
==================

🎯 KEY TOPICS:
- [Main topics discussed]

📝 IMPORTANT INFORMATION:
- [Key information shared]

💡 NOTABLE POINTS:
- [Other significant details]

🔄 ACTION ITEMS:
- [Any tasks or next steps mentioned]

TRANSCRIPT:
{transcript}

Provide a clear, professional summary."""

            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': 'llama3.2:3b',
                    'prompt': prompt,
                    'stream': False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'Summary generation failed')
            else:
                return f"Ollama API error: {response.status_code}"
                
        except Exception as e:
            return f"Ollama error: {e}"

def main():
    """Main function"""
    print("🚀 WORKING VOSK MEETING ASSISTANT")
    print("=" * 60)
    print("⚡ Python-based audio conversion (no FFmpeg needed)")
    print("🆓 Completely free and runs locally")
    print()
    
    assistant = WorkingVoskAssistant()
    
    if assistant.model:
        duration = input("Enter recording duration in seconds (default 20): ").strip()
        if not duration:
            duration = 20
        else:
            duration = int(duration)
        
        assistant.record_and_process(duration)
    else:
        print("❌ Cannot proceed without Vosk model")

if __name__ == "__main__":
    main()