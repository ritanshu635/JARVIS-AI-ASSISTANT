#!/usr/bin/env python3
"""
Simple Meeting Recorder - Direct PyAudio approach
Captures desktop audio from Google Meet using Stereo Mix
"""

import pyaudio
import wave
import whisper
import requests
import json
import time
import threading
from datetime import datetime
import numpy as np

class SimpleMeetingRecorder:
    def __init__(self):
        self.is_recording = False
        self.audio_frames = []
        self.audio = None
        self.stream = None
        self.whisper_model = None
        
        # Audio settings
        self.format = pyaudio.paInt16
        self.channels = 2
        self.rate = 44100
        self.chunk = 1024
        self.stereo_mix_index = 2  # Stereo Mix (3- Realtek(R) Audio - WORKING!
        
        # Initialize
        self.setup_audio()
        self.load_whisper()
    
    def setup_audio(self):
        """Setup PyAudio"""
        try:
            self.audio = pyaudio.PyAudio()
            
            # Check if Stereo Mix device exists
            try:
                device_info = self.audio.get_device_info_by_index(self.stereo_mix_index)
                print(f"✅ Found device at index {self.stereo_mix_index}: {device_info['name']}")
                print(f"📊 Max input channels: {device_info['maxInputChannels']}")
                
                if device_info['maxInputChannels'] > 0:
                    print("✅ Device has input channels - ready to record!")
                else:
                    print("❌ Device has no input channels - may be disabled")
                    
            except Exception as e:
                print(f"❌ Device error: {e}")
                
        except Exception as e:
            print(f"❌ PyAudio setup error: {e}")
    
    def load_whisper(self):
        """Load Whisper model"""
        try:
            print("Loading Whisper model...")
            self.whisper_model = whisper.load_model("base")
            print("✅ Whisper model loaded")
        except Exception as e:
            print(f"❌ Whisper loading error: {e}")
    
    def start_recording(self):
        """Start recording from Stereo Mix"""
        if self.is_recording:
            return "Already recording!"
        
        if not self.audio:
            return "Audio system not initialized"
        
        try:
            print("🎙️ Starting meeting recording...")
            print("📢 Make sure Google Meet audio is playing!")
            
            # Open audio stream
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                input_device_index=self.stereo_mix_index,
                frames_per_buffer=self.chunk
            )
            
            self.audio_frames = []
            self.is_recording = True
            
            # Start recording thread
            self.recording_thread = threading.Thread(target=self._record_audio)
            self.recording_thread.daemon = True
            self.recording_thread.start()
            
            return "✅ Recording started! Say 'stop' to end recording."
            
        except Exception as e:
            self.is_recording = False
            error_msg = str(e)
            
            if "Invalid device" in error_msg:
                return "❌ Stereo Mix is disabled. Run 'python fix_stereo_mix.py' to enable it."
            else:
                return f"❌ Recording error: {error_msg}"
    
    def _record_audio(self):
        """Record audio in background thread"""
        print("🔴 Recording audio...")
        
        while self.is_recording:
            try:
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                self.audio_frames.append(data)
                
                # Show progress every 5 seconds
                if len(self.audio_frames) % (self.rate // self.chunk * 5) == 0:
                    duration = len(self.audio_frames) * self.chunk / self.rate
                    print(f"   Recording... {duration:.0f} seconds")
                    
            except Exception as e:
                print(f"Recording error: {e}")
                break
    
    def stop_recording(self):
        """Stop recording and process"""
        if not self.is_recording:
            return "Not currently recording"
        
        print("🛑 Stopping recording...")
        self.is_recording = False
        
        # Stop stream
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        # Wait for recording thread
        if hasattr(self, 'recording_thread'):
            self.recording_thread.join(timeout=3)
        
        if not self.audio_frames:
            return "❌ No audio recorded. Check if Stereo Mix is enabled and audio is playing."
        
        # Save audio file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_filename = f"meeting_{timestamp}.wav"
        
        try:
            # Save WAV file
            with wave.open(audio_filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.format))
                wf.setframerate(self.rate)
                wf.writeframes(b''.join(self.audio_frames))
            
            duration = len(self.audio_frames) * self.chunk / self.rate
            print(f"📁 Audio saved: {audio_filename} ({duration:.1f} seconds)")
            
            # Check audio quality
            audio_data = np.frombuffer(b''.join(self.audio_frames), dtype=np.int16)
            max_amplitude = np.max(np.abs(audio_data))
            
            if max_amplitude < 100:
                return f"⚠️ Very quiet audio recorded. Check Stereo Mix volume levels.\nFile saved: {audio_filename}"
            
            # Process with Whisper and Ollama
            return self._process_meeting(audio_filename)
            
        except Exception as e:
            return f"❌ Error saving audio: {e}"
    
    def _process_meeting(self, audio_file):
        """Process meeting with Whisper and Ollama"""
        try:
            print("🔄 Transcribing with Whisper...")
            
            # Transcribe with proper path handling
            import os
            abs_audio_file = os.path.abspath(audio_file)
            print(f"📁 Transcribing file: {abs_audio_file}")
            
            # Verify file exists before transcribing
            if not os.path.exists(abs_audio_file):
                return f"❌ Audio file not found: {abs_audio_file}"
            
            # Use the original filename if absolute path fails
            try:
                result = self.whisper_model.transcribe(abs_audio_file)
            except:
                print("⚠️ Trying with relative path...")
                result = self.whisper_model.transcribe(audio_file)
            transcript = result["text"].strip()
            
            if not transcript:
                return f"❌ No speech detected in audio. File saved: {audio_file}"
            
            print(f"✅ Transcription completed ({len(transcript)} characters)")
            
            # Save transcript
            transcript_file = audio_file.replace('.wav', '_transcript.txt')
            with open(transcript_file, 'w', encoding='utf-8') as f:
                f.write(transcript)
            
            # Summarize with Ollama
            print("🧠 Generating summary with Ollama...")
            summary = self._summarize_with_ollama(transcript)
            
            # Save summary
            summary_file = audio_file.replace('.wav', '_summary.txt')
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary)
            
            # Keep audio file for inspection (don't delete)
            print(f"📁 Audio file kept: {audio_file}")
            
            return f"✅ Meeting processed!\n\n📋 SUMMARY:\n{summary}\n\n📁 Files: {transcript_file}, {summary_file}"
            
        except Exception as e:
            return f"❌ Processing error: {e}\nAudio file saved: {audio_file}"
    
    def _summarize_with_ollama(self, transcript):
        """Summarize with Ollama"""
        try:
            prompt = f"""Please analyze this meeting transcript and provide a comprehensive summary:

📋 MEETING SUMMARY
==================

🎯 KEY DECISIONS:
- [List important decisions made]

📝 ACTION ITEMS:
- [List tasks and assignments]

⏰ DEADLINES & DATES:
- [List mentioned deadlines]

👥 PARTICIPANTS & ROLES:
- [List participants mentioned]

💡 IMPORTANT POINTS:
- [List significant discussion points]

🔄 NEXT STEPS:
- [List planned follow-up actions]

TRANSCRIPT:
{transcript}

Please be thorough and capture all important information."""

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
                return result.get('response', 'Failed to generate summary')
            else:
                return f"Ollama API error: {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            return "❌ Could not connect to Ollama. Make sure it's running: ollama serve"
        except Exception as e:
            return f"Summary error: {e}"
    
    def __del__(self):
        """Cleanup"""
        if self.is_recording:
            self.stop_recording()
        if self.audio:
            self.audio.terminate()

# Test function
def test_simple_recorder():
    """Test the simple recorder"""
    print("🎤 Simple Meeting Recorder Test")
    print("=" * 40)
    
    recorder = SimpleMeetingRecorder()
    
    print("\nCommands:")
    print("'start' - Start recording")
    print("'stop' - Stop and process")
    print("'quit' - Exit")
    
    while True:
        cmd = input("\nEnter command: ").lower().strip()
        
        if cmd == 'start':
            result = recorder.start_recording()
            print(result)
        elif cmd == 'stop':
            result = recorder.stop_recording()
            print(result)
        elif cmd == 'quit':
            break
        else:
            print("Unknown command")

if __name__ == "__main__":
    test_simple_recorder()