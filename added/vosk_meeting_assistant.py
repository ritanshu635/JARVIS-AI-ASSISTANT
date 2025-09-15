#!/usr/bin/env python3
"""
Vosk Meeting Assistant - Whisper Replacement
Uses Vosk for fast, offline speech recognition
"""

import os
import json
import wave
import requests
import zipfile
from vosk import Model, KaldiRecognizer
from simple_meeting_recorder import SimpleMeetingRecorder
import time

class VoskMeetingAssistant:
    def __init__(self):
        self.model = None
        self.recorder = SimpleMeetingRecorder()
        self.setup_vosk_model()
    
    def setup_vosk_model(self):
        """Download and setup Vosk model"""
        print("🔧 Setting up Vosk speech recognition...")
        
        model_path = "vosk-model-en-us-0.22-lgraph"
        model_url = "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22-lgraph.zip"
        
        if os.path.exists(model_path):
            print("✅ Vosk model already exists")
            self.model = Model(model_path)
            return
        
        print("📥 Downloading Vosk model (this may take a few minutes)...")
        print("💡 Model size: ~50MB - much smaller than Whisper!")
        
        try:
            # Download model
            response = requests.get(model_url, stream=True)
            zip_path = "vosk-model.zip"
            
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print("📦 Extracting model...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall('.')
            
            # Clean up
            os.remove(zip_path)
            
            print("✅ Vosk model setup complete!")
            self.model = Model(model_path)
            
        except Exception as e:
            print(f"❌ Model setup failed: {e}")
            print("💡 You can manually download from: https://alphacephei.com/vosk/models/")
            self.model = None
    
    def transcribe_audio_file(self, audio_file):
        """Transcribe audio file using Vosk"""
        if not self.model:
            return "❌ Vosk model not available"
        
        try:
            print(f"🗣️ Transcribing with Vosk: {audio_file}")
            
            # Convert audio to Vosk-friendly format first
            converted_file = self.convert_audio_for_vosk(audio_file)
            if not converted_file:
                return "❌ Audio conversion failed"
            
            # Open converted WAV file
            wf = wave.open(converted_file, "rb")
            
            print(f"📊 Audio format: {wf.getnchannels()} channels, {wf.getframerate()} Hz")
            
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
            
            # Get final result
            final_result = json.loads(rec.FinalResult())
            if final_result.get('text'):
                transcript_parts.append(final_result['text'])
            
            wf.close()
            
            # Clean up converted file
            if converted_file != audio_file:
                try:
                    os.remove(converted_file)
                except:
                    pass
            
            # Combine all parts
            full_transcript = ' '.join(transcript_parts).strip()
            
            if full_transcript:
                print(f"✅ Vosk transcription successful!")
                print(f"📝 Length: {len(full_transcript)} characters")
                return full_transcript
            else:
                return "⚠️ No speech detected in audio"
                
        except Exception as e:
            print(f"❌ Vosk transcription error: {e}")
            return f"❌ Transcription failed: {e}"
    
    def convert_audio_for_vosk(self, audio_file):
        """Convert audio to Vosk-friendly format (mono, 16kHz)"""
        try:
            import subprocess
            
            converted_file = audio_file.replace('.wav', '_converted.wav')
            
            print("🔄 Converting audio for Vosk (mono, 16kHz)...")
            
            # Use FFmpeg to convert
            cmd = [
                'ffmpeg', '-i', audio_file,
                '-ar', '16000',  # 16kHz sample rate
                '-ac', '1',      # mono
                '-acodec', 'pcm_s16le',  # 16-bit PCM
                '-y',            # overwrite
                converted_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Audio conversion successful")
                return converted_file
            else:
                print(f"❌ FFmpeg conversion failed: {result.stderr}")
                return audio_file  # Use original if conversion fails
                
        except Exception as e:
            print(f"⚠️ Audio conversion error: {e}, using original file")
            return audio_file
    
    def record_and_process(self, duration=15):
        """Record audio and process with Vosk + Ollama"""
        print("🎤 VOSK MEETING ASSISTANT")
        print("=" * 50)
        print("🚀 Using Vosk (fast, lightweight, offline)")
        print()
        
        if not self.model:
            print("❌ Vosk model not available. Please check setup.")
            return
        
        print(f"📢 Recording desktop audio for {duration} seconds...")
        print("💡 Make sure audio with SPEECH is playing!")
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
        audio_filename = f"vosk_meeting_{timestamp}.wav"
        
        with wave.open(audio_filename, 'wb') as wf:
            wf.setnchannels(self.recorder.channels)
            wf.setsampwidth(self.recorder.audio.get_sample_size(self.recorder.format))
            wf.setframerate(self.recorder.rate)
            wf.writeframes(b''.join(self.recorder.audio_frames))
        
        duration_actual = len(self.recorder.audio_frames) * self.recorder.chunk / self.recorder.rate
        print(f"✅ Audio saved: {audio_filename} ({duration_actual:.1f} seconds)")
        
        # Transcribe with Vosk
        transcript = self.transcribe_audio_file(audio_filename)
        
        if "❌" not in transcript and "⚠️" not in transcript:
            print(f"📝 Transcript: {transcript}")
            
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
            print("🎉 VOSK MEETING ASSISTANT SUCCESS!")
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
            print("✅ VOSK WORKS PERFECTLY!")
            
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
    print("🚀 VOSK MEETING ASSISTANT")
    print("=" * 60)
    print("⚡ Fast, lightweight, offline speech recognition")
    print("🆓 Completely free and runs locally")
    print()
    
    assistant = VoskMeetingAssistant()
    
    if assistant.model:
        duration = input("Enter recording duration in seconds (default 15): ").strip()
        if not duration:
            duration = 15
        else:
            duration = int(duration)
        
        assistant.record_and_process(duration)
    else:
        print("❌ Cannot proceed without Vosk model")

if __name__ == "__main__":
    main()