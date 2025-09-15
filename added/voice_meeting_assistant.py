#!/usr/bin/env python3
"""
Voice-Activated Meeting Assistant for Jarvis
Features:
- Voice commands: "Jarvis attend the meeting for me" / "OK you can leave the meeting Jarvis"
- Records desktop audio from Google Meet using your Realtek speakers
- Whisper transcription + Ollama summarization
- Perfect for hackathons - judges will love this!
"""

import os
import time
import threading
import wave
import whisper
import requests
import json
import speech_recognition as sr
import pyaudio
import numpy as np
from datetime import datetime
from simple_meeting_recorder import SimpleMeetingRecorder

class VoiceMeetingAssistant:
    def __init__(self):
        self.is_recording = False
        self.is_listening_for_commands = False
        self.meeting_recorder = None
        self.voice_recognizer = None
        self.microphone = None
        self.command_thread = None
        
        print("🤖 Initializing Voice-Activated Meeting Assistant...")
        self.setup_components()
    
    def setup_components(self):
        """Initialize all components"""
        try:
            # Initialize meeting recorder (uses your Realtek Stereo Mix)
            self.meeting_recorder = SimpleMeetingRecorder()
            print("✅ Meeting recorder ready (Realtek Audio)")
            
            # Initialize voice recognition for commands
            self.voice_recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # Adjust for ambient noise
            print("🎤 Calibrating microphone for voice commands...")
            with self.microphone as source:
                self.voice_recognizer.adjust_for_ambient_noise(source, duration=1)
            print("✅ Voice command recognition ready")
            
        except Exception as e:
            print(f"❌ Setup error: {e}")
    
    def start_voice_listening(self):
        """Start listening for voice commands"""
        if self.is_listening_for_commands:
            return "Already listening for voice commands!"
        
        if not self.voice_recognizer:
            return "Voice recognition not available"
        
        self.is_listening_for_commands = True
        self.command_thread = threading.Thread(target=self._listen_for_commands, daemon=True)
        self.command_thread.start()
        
        return "🎤 Voice command listening started! Say 'Jarvis attend the meeting for me' to start recording."
    
    def stop_voice_listening(self):
        """Stop listening for voice commands"""
        self.is_listening_for_commands = False
        return "🔇 Voice command listening stopped."
    
    def _listen_for_commands(self):
        """Continuously listen for voice commands"""
        print("🎤 Listening for voice commands...")
        print("💬 Say: 'Jarvis attend the meeting for me' to start")
        print("💬 Say: 'OK you can leave the meeting Jarvis' to stop")
        
        while self.is_listening_for_commands:
            try:
                # Listen for audio
                with self.microphone as source:
                    # Listen with timeout
                    audio = self.voice_recognizer.listen(source, timeout=1, phrase_time_limit=5)
                
                # Recognize speech
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
        """Process recognized voice commands"""
        command = command.lower().strip()
        
        # Start meeting recording commands
        if any(phrase in command for phrase in [
            "jarvis attend the meeting for me",
            "jarvis attend meeting for me", 
            "jarvis attend the meeting",
            "attend the meeting for me",
            "attend meeting for me"
        ]):
            print("🎯 Command recognized: START MEETING RECORDING")
            result = self._start_meeting_recording()
            print(result)
            
        # Stop meeting recording commands  
        elif any(phrase in command for phrase in [
            "ok you can leave the meeting jarvis",
            "okay you can leave the meeting jarvis",
            "you can leave the meeting jarvis",
            "you can leave the meeting service",  # This was detected!
            "jarvis you can leave the meeting",
            "jarvis leave the meeting",
            "stop meeting jarvis",
            "end meeting jarvis",
            "stop recording",
            "end recording"
        ]):
            print("🎯 Command recognized: STOP MEETING RECORDING")
            result = self._stop_meeting_recording()
            print(result)
            
        # Status check
        elif "meeting status" in command:
            status = self._get_meeting_status()
            print(status)
    
    def _start_meeting_recording(self):
        """Start recording meeting audio"""
        if self.is_recording:
            return "📝 Already recording a meeting!"
        
        if not self.meeting_recorder:
            return "❌ Meeting recorder not available"
        
        try:
            print("🎙️ Starting meeting recording...")
            print("📢 Recording audio from your Realtek speakers (Google Meet participants)")
            
            # Start recording using your existing recorder
            result = self.meeting_recorder.start_recording()
            
            if "✅" in result:
                self.is_recording = True
                return "✅ Meeting recording started! I'm listening to Google Meet audio from your speakers."
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
            
            # Stop recording and process with Whisper + Ollama
            result = self.meeting_recorder.stop_recording()
            
            return f"✅ Meeting processed!\n{result}"
            
        except Exception as e:
            return f"❌ Error processing meeting: {e}"
    
    def _get_meeting_status(self):
        """Get current meeting status"""
        if self.is_recording:
            return "🎙️ Currently recording meeting audio from Google Meet"
        else:
            return "⏹️ No meeting recording in progress"
    
    def manual_start_recording(self):
        """Manual start for testing"""
        return self._start_meeting_recording()
    
    def manual_stop_recording(self):
        """Manual stop for testing"""
        return self._stop_meeting_recording()
    
    def get_status(self):
        """Get current status"""
        status = []
        status.append(f"Voice listening: {'ON' if self.is_listening_for_commands else 'OFF'}")
        status.append(f"Meeting recording: {'ON' if self.is_recording else 'OFF'}")
        return " | ".join(status)

# Global instance
voice_meeting_assistant = VoiceMeetingAssistant()

def start_voice_meeting_assistant():
    """Start the voice-activated meeting assistant"""
    return voice_meeting_assistant.start_voice_listening()

def stop_voice_meeting_assistant():
    """Stop the voice-activated meeting assistant"""
    return voice_meeting_assistant.stop_voice_listening()

def get_meeting_assistant_status():
    """Get meeting assistant status"""
    return voice_meeting_assistant.get_status()

# Test function
def test_voice_meeting_assistant():
    """Test the voice meeting assistant"""
    print("🎤 Voice Meeting Assistant Test")
    print("=" * 50)
    
    assistant = VoiceMeetingAssistant()
    
    print("\nCommands:")
    print("'start' - Start voice listening")
    print("'stop' - Stop voice listening") 
    print("'record' - Manual start recording")
    print("'end' - Manual stop recording")
    print("'status' - Check status")
    print("'quit' - Exit")
    
    while True:
        cmd = input("\nEnter command: ").lower().strip()
        
        if cmd == 'start':
            result = assistant.start_voice_listening()
            print(result)
        elif cmd == 'stop':
            result = assistant.stop_voice_listening()
            print(result)
        elif cmd == 'record':
            result = assistant.manual_start_recording()
            print(result)
        elif cmd == 'end':
            result = assistant.manual_stop_recording()
            print(result)
        elif cmd == 'status':
            result = assistant.get_status()
            print(result)
        elif cmd == 'quit':
            assistant.stop_voice_listening()
            break
        else:
            print("Unknown command")

if __name__ == "__main__":
    test_voice_meeting_assistant()