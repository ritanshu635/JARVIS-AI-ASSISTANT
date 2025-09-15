#!/usr/bin/env python3
"""
Fix TTS and Complete Pipeline
Fix pyttsx3 issues and ensure complete processing
"""

import os
import time
import threading
import wave
import json
import requests
import speech_recognition as sr
import subprocess
import numpy as np
from datetime import datetime
from vosk import Model, KaldiRecognizer
from simple_meeting_recorder import SimpleMeetingRecorder

class FixedVoiceMeetingAssistant:
    def __init__(self):
        self.is_recording = False
        self.is_listening_for_commands = False
        self.meeting_recorder = None
        self.voice_recognizer = None
        self.microphone = None
        self.vosk_model = None
        self.command_thread = None
        
        print("🤖 Initializing Fixed Voice Meeting Assistant...")
        self.setup_components()
    
    def setup_components(self):
        """Initialize all components"""
        try:
            # Initialize meeting recorder
            self.meeting_recorder = SimpleMeetingRecorder()
            print("✅ Meeting recorder ready")
            
            # Initialize voice recognition
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
        """Setup Vosk model"""
        model_path = "vosk-model-en-us-0.22-lgraph"
        
        if os.path.exists(model_path):
            print("✅ Loading Vosk model...")
            self.vosk_model = Model(model_path)
            print("✅ Vosk model ready")
        else:
            print("❌ Vosk model not found")
            self.vosk_model = None
    
    def speak_fixed(self, text):
        """Fixed TTS using Windows SAPI directly"""
        try:
            text = str(text).strip()
            if not text:
                return
                
            print(f"🔊 Speaking: {text}")
            
            # Method 1: Try Windows SAPI directly
            try:
                import win32com.client
                speaker = win32com.client.Dispatch("SAPI.SpVoice")
                speaker.Speak(text)
                print("✅ Windows SAPI TTS successful")
                return
            except:
                pass
            
            # Method 2: Use Windows built-in PowerShell TTS
            try:
                ps_command = f'Add-Type -AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Speak("{text}")'
                subprocess.run(['powershell', '-Command', ps_command], check=True, capture_output=True)
                print("✅ PowerShell TTS successful")
                return
            except:
                pass
            
            # Method 3: Fallback to pyttsx3 with different settings
            try:
                import pyttsx3
                engine = pyttsx3.init()
                engine.setProperty('rate', 150)
                engine.setProperty('volume', 1.0)
                engine.say(text)
                engine.runAndWait()
                engine.stop()
                print("✅ pyttsx3 TTS successful")
                return
            except:
                pass
            
            print(f"⚠️ TTS failed, text was: {text}")
            
        except Exception as e:
            print(f"❌ TTS error: {e}")
    
    def start_voice_listening(self):
        """Start listening for voice commands"""
        if self.is_listening_for_commands:
            return "Already listening for voice commands!"
        
        self.is_listening_for_commands = True
        self.command_thread = threading.Thread(target=self._listen_for_commands, daemon=True)
        self.command_thread.start()
        
        self.speak_fixed("Voice command listening started. Say Jarvis attend the meeting for me to start recording.")
        return "🎤 Voice command listening started!"
    
    def _listen_for_commands(self):
        """Listen for voice commands"""
        print("🎤 Listening for voice commands...")
        print("💬 Say: 'Jarvis attend the meeting for me' to start")
        print("💬 Say: 'Jarvis leave the meeting' to stop")
        
        while self.is_listening_for_commands:
            try:
                with self.microphone as source:
                    audio = self.voice_recognizer.listen(source, timeout=1, phrase_time_limit=5)
                
                try:
                    command = self.voice_recognizer.recognize_google(audio).lower()
                    print(f"🗣️ Heard: '{command}'")
                    
                    # Process the command
                    self._process_voice_command(command)
                    
                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    print(f"⚠️ Speech recognition error: {e}")
                    time.sleep(1)
                    
            except sr.WaitTimeoutError:
                pass
            except Exception as e:
                print(f"❌ Voice listening error: {e}")
                time.sleep(1)
    
    def _process_voice_command(self, command):
        """Process voice commands"""
        command = command.lower().strip()
        
        # Start meeting recording
        if any(phrase in command for phrase in [
            "jarvis attend the meeting for me",
            "jarvis attend meeting for me", 
            "attend the meeting for me"
        ]):
            print("🎯 Command recognized: ATTEND_MEETING")
            self.speak_fixed("I will do that for you sir. Starting meeting recording now.")
            result = self._start_meeting_recording()
            print(result)
            
        # Stop meeting recording and PROCESS
        elif any(phrase in command for phrase in [
            "jarvis leave the meeting",
            "jarvis you can leave the meeting",
            "leave the meeting jarvis"
        ]):
            print("🎯 Command recognized: LEAVE_MEETING")
            self.speak_fixed("Processing the meeting now. This may take a moment.")
            result = self._stop_and_process_meeting()
            print(result)
            
            # Speak the summary if successful
            if "SUMMARY:" in result:
                summary_part = result.split("SUMMARY:")[1].split("📁")[0].strip()
                
                # Clean the summary for speaking (remove markdown formatting)
                clean_summary = self._clean_text_for_speech(summary_part)
                
                self.speak_fixed("Meeting processed successfully. Here is your summary.")
                time.sleep(1)
                self.speak_fixed(clean_summary)
    
    def _start_meeting_recording(self):
        """Start recording"""
        if self.is_recording:
            return "Already recording!"
        
        try:
            result = self.meeting_recorder.start_recording()
            
            if "✅" in result:
                self.is_recording = True
                return "✅ Meeting recording started!"
            else:
                return f"❌ Failed to start: {result}"
                
        except Exception as e:
            return f"❌ Error: {e}"
    
    def _stop_and_process_meeting(self):
        """Stop recording and COMPLETE processing"""
        if not self.is_recording:
            return "No meeting being recorded!"
        
        try:
            print("🛑 Stopping recording...")
            self.is_recording = False
            
            # Stop recording
            self.meeting_recorder.is_recording = False
            
            if self.meeting_recorder.stream:
                self.meeting_recorder.stream.stop_stream()
                self.meeting_recorder.stream.close()
            
            if hasattr(self.meeting_recorder, 'recording_thread'):
                self.meeting_recorder.recording_thread.join(timeout=3)
            
            if not self.meeting_recorder.audio_frames:
                return "❌ No audio recorded"
            
            # Save audio
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_filename = f"complete_meeting_{timestamp}.wav"
            
            with wave.open(audio_filename, 'wb') as wf:
                wf.setnchannels(self.meeting_recorder.channels)
                wf.setsampwidth(self.meeting_recorder.audio.get_sample_size(self.meeting_recorder.format))
                wf.setframerate(self.meeting_recorder.rate)
                wf.writeframes(b''.join(self.meeting_recorder.audio_frames))
            
            duration = len(self.meeting_recorder.audio_frames) * self.meeting_recorder.chunk / self.meeting_recorder.rate
            print(f"✅ Audio saved: {audio_filename} ({duration:.1f} seconds)")
            
            # FORCE COMPLETE PROCESSING
            return self._force_complete_processing(audio_filename)
            
        except Exception as e:
            return f"❌ Error: {e}"
    
    def _force_complete_processing(self, audio_file):
        """Force complete processing - transcription + summary"""
        try:
            print("🗣️ FORCING Vosk transcription...")
            
            # Step 1: Convert audio for Vosk
            converted_file = self._convert_audio_for_vosk(audio_file)
            if not converted_file:
                converted_file = audio_file
            
            # Step 2: Transcribe with Vosk
            transcript = self._transcribe_with_vosk_force(converted_file)
            
            if not transcript or len(transcript.strip()) < 10:
                return "❌ Transcription failed or no speech detected"
            
            print(f"✅ Transcription: {transcript[:100]}...")
            
            # Step 3: Summarize with Ollama
            print("🧠 FORCING Ollama summary...")
            summary = self._summarize_with_ollama_force(transcript)
            
            # Step 4: Save files
            transcript_file = audio_file.replace('.wav', '_transcript.txt')
            summary_file = audio_file.replace('.wav', '_summary.txt')
            
            with open(transcript_file, 'w', encoding='utf-8') as f:
                f.write(transcript)
            
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary)
            
            # Clean up
            if converted_file != audio_file and os.path.exists(converted_file):
                os.remove(converted_file)
            
            return f"""✅ COMPLETE PROCESSING SUCCESSFUL!

📋 SUMMARY:
{summary}

📁 Files: {transcript_file}, {summary_file}"""
            
        except Exception as e:
            return f"❌ Processing error: {e}"
    
    def _convert_audio_for_vosk(self, audio_file):
        """Convert audio for Vosk"""
        try:
            with wave.open(audio_file, 'rb') as wf:
                frames = wf.readframes(wf.getnframes())
                sample_rate = wf.getframerate()
                channels = wf.getnchannels()
                sampwidth = wf.getsampwidth()
            
            if sampwidth != 2:
                return None
            
            audio_data = np.frombuffer(frames, dtype=np.int16)
            
            if channels == 2:
                audio_data = audio_data.reshape(-1, 2).mean(axis=1).astype(np.int16)
            
            if sample_rate != 16000:
                target_length = int(len(audio_data) * 16000 / sample_rate)
                audio_data = np.interp(
                    np.linspace(0, len(audio_data), target_length),
                    np.arange(len(audio_data)),
                    audio_data
                ).astype(np.int16)
            
            converted_file = audio_file.replace('.wav', '_vosk.wav')
            with wave.open(converted_file, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(16000)
                wf.writeframes(audio_data.tobytes())
            
            return converted_file
            
        except Exception as e:
            print(f"❌ Conversion error: {e}")
            return None
    
    def _transcribe_with_vosk_force(self, audio_file):
        """Force transcription with Vosk"""
        if not self.vosk_model:
            return "Vosk model not available"
        
        try:
            wf = wave.open(audio_file, "rb")
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
                        print(f"📝 Partial: {result['text']}")
            
            final_result = json.loads(rec.FinalResult())
            if final_result.get('text'):
                transcript_parts.append(final_result['text'])
                print(f"📝 Final: {final_result['text']}")
            
            wf.close()
            
            return ' '.join(transcript_parts).strip()
                
        except Exception as e:
            print(f"❌ Vosk error: {e}")
            return ""
    
    def _summarize_with_ollama_force(self, transcript):
        """Force summarization with Ollama"""
        try:
            prompt = f"""Summarize this meeting transcript in a clear, concise way:

TRANSCRIPT:
{transcript}

Provide a brief summary covering:
- Main topics discussed
- Key points mentioned
- Any important information

Keep it concise and professional."""

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
    
    def _clean_text_for_speech(self, text):
        """Clean text for speech - remove markdown formatting"""
        try:
            # Remove markdown formatting
            clean_text = text.replace("**", "")  # Remove bold asterisks
            clean_text = clean_text.replace("*", "")   # Remove italic asterisks
            clean_text = clean_text.replace("#", "")   # Remove headers
            clean_text = clean_text.replace("- ", "")  # Remove bullet points
            clean_text = clean_text.replace("  ", " ") # Remove double spaces
            clean_text = clean_text.strip()
            
            return clean_text
            
        except Exception as e:
            print(f"⚠️ Text cleaning error: {e}")
            return text

def main():
    """Test the fixed version"""
    print("🚀 FIXED VOICE MEETING ASSISTANT")
    print("=" * 60)
    print("🔧 Fixed TTS issues")
    print("🔧 Fixed complete processing pipeline")
    print()
    
    assistant = FixedVoiceMeetingAssistant()
    
    # Start voice listening
    result = assistant.start_voice_listening()
    print(result)
    
    print("\n" + "=" * 60)
    print("🎤 VOICE COMMANDS ARE NOW ACTIVE!")
    print("🗣️ Say: 'Jarvis attend the meeting for me'")
    print("💡 Then play audio with speech")
    print("🗣️ Say: 'Jarvis leave the meeting' (WILL PROCESS COMPLETELY)")
    print("⏹️ Press Ctrl+C to stop")
    print("=" * 60)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
        assistant.is_listening_for_commands = False
        print("✅ Complete!")

if __name__ == "__main__":
    main()