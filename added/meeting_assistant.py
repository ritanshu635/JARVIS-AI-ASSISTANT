"""
Enhanced Meeting Assistant Module for Jarvis
Handles meeting recording, transcription, and summarization with voice commands
Features:
- Voice-activated meeting recording ("Jarvis attend the meeting for me")
- Desktop audio capture from Google Meet
- Whisper transcription
- Ollama summarization
- Voice command integration
"""

import os
import time
import threading
import wave
import whisper
import requests
import json
from datetime import datetime
import speech_recognition as sr
import numpy as np
from windows_desktop_audio import WindowsDesktopAudio

class EnhancedMeetingAssistant:
    def __init__(self):
        self.is_recording = False
        self.whisper_model = None
        self.meeting_active = False
        self.audio_capture = None
        self.voice_listening = False
        self.voice_thread = None
        
        # Load Whisper model
        print("🤖 Loading Whisper model for meeting transcription...")
        try:
            self.whisper_model = whisper.load_model("base")
            print("✅ Whisper model loaded successfully!")
        except Exception as e:
            print(f"❌ Error loading Whisper: {e}")
            self.whisper_model = None
        
        # Initialize audio capture
        try:
            from simple_meeting_recorder import SimpleMeetingRecorder
            self.audio_capture = SimpleMeetingRecorder()
            print("✅ Meeting recorder initialized with working Stereo Mix")
        except Exception as e:
            print(f"⚠️ Audio capture initialization warning: {e}")
            self.audio_capture = None
        
        # Initialize voice recognition for commands
        try:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            print("✅ Voice command recognition initialized")
        except Exception as e:
            print(f"⚠️ Voice recognition warning: {e}")
            self.recognizer = None
    
    def start_recording(self):
        """Start recording meeting audio"""
        if self.is_recording:
            return "Already recording a meeting!"
        
        if not self.audio_capture:
            return "Audio capture system not available. Please check your audio setup."
        
        try:
            self.is_recording = True
            self.meeting_active = True
            
            print("🎙️ Started recording meeting audio...")
            print("📢 Recording both your voice and system audio from Google Meet...")
            
            # Start recording using the meeting recorder
            result = self.audio_capture.start_recording()
            
            if "✅" in result:
                return "Meeting recording started! I'm now listening to Google Meet. Say 'Jarvis, you can leave the meeting' to stop."
            else:
                self.is_recording = False
                return f"Error starting recording: {result}"
            
        except Exception as e:
            self.is_recording = False
            return f"Error starting recording: {str(e)}"
    

    
    def stop_recording(self):
        """Stop recording and process the meeting"""
        if not self.is_recording:
            return "No meeting is currently being recorded!"
        
        print("🛑 Stopping meeting recording...")
        self.is_recording = False
        self.meeting_active = False
        
        if not self.audio_capture:
            return "Audio capture system not available."
        
        try:
            # Stop recording and process with the meeting recorder
            result = self.audio_capture.stop_recording()
            return result
            
        except Exception as e:
            return f"Error processing meeting: {str(e)}"
    
    def _process_meeting(self, audio_file):
        """Transcribe and summarize the meeting"""
        try:
            print("🔄 Transcribing meeting audio with Whisper...")
            
            # Transcribe with Whisper
            result = self.whisper_model.transcribe(audio_file)
            transcript = result["text"]
            
            print("✅ Transcription completed!")
            
            # Save transcript
            transcript_file = audio_file.replace('.wav', '_transcript.txt')
            with open(transcript_file, 'w', encoding='utf-8') as f:
                f.write(transcript)
            
            print(f"📄 Transcript saved as {transcript_file}")
            
            # Summarize with Ollama
            summary = self._summarize_with_ollama(transcript)
            
            # Save summary
            summary_file = audio_file.replace('.wav', '_summary.txt')
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary)
            
            print(f"📋 Summary saved as {summary_file}")
            
            # Clean up audio file (optional)
            try:
                os.remove(audio_file)
                print(f"🗑️ Cleaned up audio file {audio_file}")
            except:
                pass
            
            return f"Meeting processed successfully!\n\n📋 MEETING SUMMARY:\n{summary}"
            
        except Exception as e:
            return f"Error processing meeting: {str(e)}"
    
    def _summarize_with_ollama(self, transcript):
        """Summarize transcript using Ollama"""
        try:
            print("🧠 Generating summary with Ollama...")
            
            # Prepare the prompt for Ollama
            prompt = f"""Please analyze this meeting transcript and provide a comprehensive summary with the following structure:

📋 MEETING SUMMARY
==================

🎯 KEY DECISIONS:
- [List all important decisions made]

📝 ACTION ITEMS:
- [List all tasks assigned with responsible persons if mentioned]

⏰ DEADLINES & DATES:
- [List all mentioned deadlines and important dates]

👥 PARTICIPANTS & ROLES:
- [List participants and their roles/responsibilities if mentioned]

💡 IMPORTANT POINTS:
- [List other significant discussion points]

🔄 NEXT STEPS:
- [List planned follow-up actions]

TRANSCRIPT:
{transcript}

Please be thorough and capture all important information from the meeting."""

            # Call Ollama API
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': 'llama3',  # You can change this to your preferred model
                    'prompt': prompt,
                    'stream': False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                summary = result.get('response', 'Failed to generate summary')
                print("✅ Summary generated successfully!")
                return summary
            else:
                return f"Ollama API error: {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            return "❌ Could not connect to Ollama. Please make sure Ollama is running (ollama serve)"
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def get_status(self):
        """Get current recording status"""
        if self.is_recording:
            return "🎙️ Currently recording meeting audio..."
        else:
            return "⏹️ No meeting recording in progress"
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        if self.is_recording:
            self.stop_recording()

# Global instance
meeting_assistant = MeetingAssistant()

def handle_meeting_command(command):
    """Handle meeting-related voice commands"""
    command = command.lower()
    
    if "attend the meeting" in command or "attend meeting" in command:
        return meeting_assistant.start_recording()
    
    elif "leave the meeting" in command or "stop meeting" in command or "end meeting" in command:
        return meeting_assistant.stop_recording()
    
    elif "meeting status" in command:
        return meeting_assistant.get_status()
    
    return None

if __name__ == "__main__":
    # Test the meeting assistant
    print("Meeting Assistant Test")
    print("Commands:")
    print("1. 'start' - Start recording")
    print("2. 'stop' - Stop recording and process")
    print("3. 'status' - Check status")
    print("4. 'quit' - Exit")
    
    while True:
        cmd = input("\nEnter command: ").lower()
        
        if cmd == 'start':
            result = meeting_assistant.start_recording()
            print(result)
        elif cmd == 'stop':
            result = meeting_assistant.stop_recording()
            print(result)
        elif cmd == 'status':
            result = meeting_assistant.get_status()
            print(result)
        elif cmd == 'quit':
            break
        else:
            print("Unknown command")