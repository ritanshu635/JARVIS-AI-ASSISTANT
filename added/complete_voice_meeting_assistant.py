#!/usr/bin/env python3
"""
Complete Voice-Activated Meeting Assistant
Integrates with your existing JARVIS system using the same patterns:
- Uses Whisper for voice command recognition
- Uses pyttsx3 for audio responses
- Uses Vosk for meeting transcription
- Uses Ollama for summarization
"""

import os
import time
import threading
import wave
import json
import requests
import speech_recognition as sr
import pyttsx3
import numpy as np
from datetime import datetime
from vosk import Model, KaldiRecognizer
from simple_meeting_recorder import SimpleMeetingRecorder

class CompleteVoiceMeetingAssistant:
    def __init__(self):
        self.is_recording = False
        self.is_listening_for_commands = False
        self.meeting_recorder = None
        self.voice_recognizer = None
        self.microphone = None
        self.tts_engine = None
        self.vosk_model = None
        self.command_thread = None
        
        print("🤖 Initializing Complete Voice Meeting Assistant...")
        self.setup_components()
    
    def setup_components(self):
        """Initialize all components like your other features"""
        try:
            # Initialize TTS engine (same as your command.py)
            self.tts_engine = pyttsx3.init('sapi5')
            voices = self.tts_engine.getProperty('voices')
            if voices and len(voices) > 0:
                self.tts_engine.setProperty('voice', voices[0].id)
            self.tts_engine.setProperty('rate', 174)
            self.tts_engine.setProperty('volume', 1.0)
            print("✅ TTS engine initialized")
            
            # Initialize meeting recorder
            self.meeting_recorder = SimpleMeetingRecorder()
            print("✅ Meeting recorder ready")
            
            # Initialize voice recognition (same as your system)
            self.voice_recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # Calibrate microphone
            print("🎤 Calibrating microphone...")
            with self.microphone as source:
                self.voice_recognizer.adjust_for_ambient_noise(source, duration=1)
            print("✅ Voice recognition ready")
            
            # Initialize Vosk model
            self.setup_vosk_model()
            
        except Exception as e:
            print(f"❌ Setup error: {e}")
    
    def setup_vosk_model(self):
        """Setup Vosk model for transcription"""
        model_path = "vosk-model-en-us-0.22-lgraph"
        
        if os.path.exists(model_path):
            print("✅ Loading Vosk model...")
            self.vosk_model = Model(model_path)
            print("✅ Vosk model ready")
        else:
            print("❌ Vosk model not found")
            self.vosk_model = None
    
    def speak(self, text):
        """Speak text using TTS (same as your command.py)"""
        try:
            text = str(text).strip()
            if not text:
                return
                
            print(f"🔊 Speaking: {text}")
            
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            
        except Exception as e:
            print(f"❌ TTS error: {e}")
            print(f"🔊 Fallback: {text}")
    
    def start_voice_listening(self):
        """Start listening for voice commands"""
        if self.is_listening_for_commands:
            return "Already listening for voice commands!"
        
        if not self.voice_recognizer:
            return "Voice recognition not available"
        
        self.is_listening_for_commands = True
        self.command_thread = threading.Thread(target=self._listen_for_commands, daemon=True)
        self.command_thread.start()
        
        self.speak("Voice command listening started. Say Jarvis attend the meeting for me to start recording.")
        return "🎤 Voice command listening started!"
    
    def stop_voice_listening(self):
        """Stop listening for voice commands"""
        self.is_listening_for_commands = False
        self.speak("Voice command listening stopped.")
        return "🔇 Voice command listening stopped."
    
    def _listen_for_commands(self):
        """Continuously listen for voice commands (like your system)"""
        print("🎤 Listening for voice commands...")
        print("💬 Say: 'Jarvis attend the meeting for me' to start")
        print("💬 Say: 'Jarvis leave the meeting' to stop")
        
        while self.is_listening_for_commands:
            try:
                # Listen for audio (same timeout as your system)
                with self.microphone as source:
                    audio = self.voice_recognizer.listen(source, timeout=1, phrase_time_limit=5)
                
                # Recognize speech using Google (like your system)
                try:
                    command = self.voice_recognizer.recognize_google(audio).lower()
                    print(f"🗣️ Heard: '{command}'")
                    
                    # Process the command
                    self._process_voice_command(command)
                    
                except sr.UnknownValueError:
                    # No speech detected, continue listening
                    pass
                except sr.RequestError as e:
                    print(f"⚠️ Speech recognition error: {e}")
                    time.sleep(1)
                    
            except sr.WaitTimeoutError:
                # Timeout, continue listening
                pass
            except Exception as e:
                print(f"❌ Voice listening error: {e}")
                time.sleep(1)
    
    def _process_voice_command(self, command):
        """Process voice commands (same pattern as your final_jarvis.py)"""
        command = command.lower().strip()
        
        # Start meeting recording commands
        if any(phrase in command for phrase in [
            "jarvis attend the meeting for me",
            "jarvis attend meeting for me", 
            "jarvis attend the meeting",
            "attend the meeting for me",
            "attend meeting for me"
        ]):
            print("🎯 Command recognized: ATTEND_MEETING")
            self.speak("I will do that for you sir. Starting meeting recording now.")
            result = self._start_meeting_recording()
            print(result)
            
        # Stop meeting recording commands  
        elif any(phrase in command for phrase in [
            "jarvis leave the meeting",
            "jarvis you can leave the meeting",
            "leave the meeting jarvis",
            "stop meeting jarvis",
            "end meeting jarvis"
        ]):
            print("🎯 Command recognized: LEAVE_MEETING")
            self.speak("Processing the meeting now. This may take a moment.")
            result = self._stop_meeting_recording()
            if "✅" in result:
                self.speak("Meeting processed successfully! Here is your summary.")
                # Extract and speak the summary
                if "SUMMARY:" in result:
                    summary_part = result.split("SUMMARY:")[1].split("📁")[0].strip()
                    self.speak(summary_part)
            else:
                self.speak("There was an issue processing the meeting.")
            print(result)
            
        # Status check
        elif "meeting status" in command:
            status = self._get_meeting_status()
            self.speak(status)
            print(status)
    
    def _start_meeting_recording(self):
        """Start recording meeting audio"""
        if self.is_recording:
            return "📝 Already recording a meeting!"
        
        if not self.meeting_recorder:
            return "❌ Meeting recorder not available"
        
        try:
            print("🎙️ Starting meeting recording...")
            print("📢 Recording audio from your speakers (Google Meet participants)")
            
            # Start recording using your existing recorder
            result = self.meeting_recorder.start_recording()
            
            if "✅" in result:
                self.is_recording = True
                return "✅ Meeting recording started! I'm listening to Google Meet audio."
            else:
                return f"❌ Failed to start recording: {result}"
                
        except Exception as e:
            return f"❌ Error starting recording: {e}"
    
    def _stop_meeting_recording(self):
        """Stop recording and process meeting"""
        if not self.is_recording:
            return "📝 No meeting is currently being recorded!"
        
        try:
            print("🛑 Stopping meeting recording and processing...")
            self.is_recording = False
            
            # Stop recording manually
            self.meeting_recorder.is_recording = False
            
            if self.meeting_recorder.stream:
                self.meeting_recorder.stream.stop_stream()
                self.meeting_recorder.stream.close()
            
            if hasattr(self.meeting_recorder, 'recording_thread'):
                self.meeting_recorder.recording_thread.join(timeout=3)
            
            if not self.meeting_recorder.audio_frames:
                return "❌ No audio recorded"
            
            # Save audio file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_filename = f"voice_meeting_{timestamp}.wav"
            
            with wave.open(audio_filename, 'wb') as wf:
                wf.setnchannels(self.meeting_recorder.channels)
                wf.setsampwidth(self.meeting_recorder.audio.get_sample_size(self.meeting_recorder.format))
                wf.setframerate(self.meeting_recorder.rate)
                wf.writeframes(b''.join(self.meeting_recorder.audio_frames))
            
            duration = len(self.meeting_recorder.audio_frames) * self.meeting_recorder.chunk / self.meeting_recorder.rate
            print(f"✅ Audio saved: {audio_filename} ({duration:.1f} seconds)")
            
            # Process with Vosk + Ollama
            return self._process_meeting_complete(audio_filename)
            
        except Exception as e:
            return f"❌ Error processing meeting: {e}"
    
    def _process_meeting_complete(self, audio_file):
        """Complete meeting processing with Vosk + Ollama"""
        try:
            # Step 1: Transcribe with Vosk
            print("🗣️ Transcribing with Vosk...")
            transcript = self._transcribe_with_vosk(audio_file)
            
            if not transcript or "❌" in transcript:
                return f"❌ Transcription failed: {transcript}"
            
            print(f"✅ Transcription successful: {len(transcript)} characters")
            
            # Step 2: Summarize with Ollama
            print("🧠 Generating summary with Ollama...")
            summary = self._summarize_with_ollama(transcript)
            
            # Step 3: Save files
            transcript_file = audio_file.replace('.wav', '_transcript.txt')
            summary_file = audio_file.replace('.wav', '_summary.txt')
            
            with open(transcript_file, 'w', encoding='utf-8') as f:
                f.write(transcript)
            
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary)
            
            # Return complete result
            return f"""✅ Meeting processed successfully!

📋 SUMMARY:
{summary}

📁 Files saved: {transcript_file}, {summary_file}"""
            
        except Exception as e:
            return f"❌ Processing error: {e}"
    
    def _transcribe_with_vosk(self, audio_file):
        """Transcribe using Vosk (same as working version)"""
        if not self.vosk_model:
            return "❌ Vosk model not available"
        
        try:
            # Convert audio for Vosk
            converted_file = self._convert_audio_for_vosk(audio_file)
            if not converted_file:
                converted_file = audio_file
            
            # Transcribe
            wf = wave.open(converted_file, "rb")
            rec = KaldiRecognizer(self.vosk_model, wf.getframerate())
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
            
            # Get final result
            final_result = json.loads(rec.FinalResult())
            if final_result.get('text'):
                transcript_parts.append(final_result['text'])
            
            wf.close()
            
            # Clean up converted file
            if converted_file != audio_file and os.path.exists(converted_file):
                os.remove(converted_file)
            
            full_transcript = ' '.join(transcript_parts).strip()
            return full_transcript if full_transcript else "⚠️ No speech detected"
                
        except Exception as e:
            return f"❌ Vosk error: {e}"
    
    def _convert_audio_for_vosk(self, audio_file):
        """Convert audio for Vosk (Python-based)"""
        try:
            # Read original WAV file
            with wave.open(audio_file, 'rb') as wf:
                frames = wf.readframes(wf.getnframes())
                sample_rate = wf.getframerate()
                channels = wf.getnchannels()
                sampwidth = wf.getsampwidth()
            
            if sampwidth != 2:
                return None
            
            # Convert to numpy array
            audio_data = np.frombuffer(frames, dtype=np.int16)
            
            # Convert stereo to mono if needed
            if channels == 2:
                audio_data = audio_data.reshape(-1, 2).mean(axis=1).astype(np.int16)
            
            # Resample to 16kHz if needed
            if sample_rate != 16000:
                target_length = int(len(audio_data) * 16000 / sample_rate)
                audio_data = np.interp(
                    np.linspace(0, len(audio_data), target_length),
                    np.arange(len(audio_data)),
                    audio_data
                ).astype(np.int16)
            
            # Save converted audio
            converted_file = audio_file.replace('.wav', '_vosk.wav')
            with wave.open(converted_file, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(16000)
                wf.writeframes(audio_data.tobytes())
            
            return converted_file
            
        except Exception as e:
            print(f"⚠️ Audio conversion error: {e}")
            return None
    
    def _summarize_with_ollama(self, transcript):
        """Summarize with Ollama"""
        try:
            prompt = f"""Analyze this meeting transcript and provide a comprehensive summary:

📋 MEETING SUMMARY
==================

🎯 KEY TOPICS DISCUSSED:
- [List the main topics and subjects covered]

📝 IMPORTANT DECISIONS:
- [List any decisions made during the meeting]

👥 PARTICIPANTS & CONTRIBUTIONS:
- [List any participants mentioned and their contributions]

💡 SIGNIFICANT POINTS:
- [List other important information shared]

⏰ DEADLINES & ACTION ITEMS:
- [List any deadlines, tasks, or follow-up actions mentioned]

🔄 NEXT STEPS:
- [List planned next steps or future meetings]

TRANSCRIPT:
{transcript}

Please provide a clear, professional summary that captures all important information from the meeting."""

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
                return result.get('response', 'Summary generation failed')
            else:
                return f"Ollama API error: {response.status_code}"
                
        except Exception as e:
            return f"Ollama error: {e}"
    
    def _get_meeting_status(self):
        """Get current meeting status"""
        if self.is_recording:
            return "Currently recording meeting audio from Google Meet"
        else:
            return "No meeting recording in progress"

# Global instance (like your other features)
complete_voice_meeting_assistant = CompleteVoiceMeetingAssistant()

def main():
    """Main function for testing"""
    print("🚀 COMPLETE VOICE MEETING ASSISTANT")
    print("=" * 60)
    print("🎤 Integrated with your JARVIS system patterns")
    print("🗣️ Uses same voice recognition and TTS as your other features")
    print()
    
    # Start voice listening
    result = complete_voice_meeting_assistant.start_voice_listening()
    print(result)
    
    print("\n" + "=" * 60)
    print("🎤 VOICE COMMANDS ARE NOW ACTIVE!")
    print("🗣️ Say: 'Jarvis attend the meeting for me'")
    print("💡 Then play Google Meet or any audio with speech")
    print("🗣️ Later say: 'Jarvis leave the meeting'")
    print("⏹️ Press Ctrl+C to stop")
    print("=" * 60)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
        complete_voice_meeting_assistant.stop_voice_listening()
        print("✅ Complete!")

if __name__ == "__main__":
    main()