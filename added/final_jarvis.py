#!/usr/bin/env python3
"""
Final JARVIS - Exactly what you want
- Listens to natural speech (any way you say it)
- Uses AI brain to understand intent
- Responds conversationally 
- Does only your specific tasks
- Uses your phone for calls/SMS/WhatsApp
"""

import asyncio
import speech_recognition as sr
import os
import subprocess
import webbrowser
import pyautogui
import time
import re
import certifi
from engine.database_manager import DatabaseManager
from engine.android_controller import AndroidController
from engine.ai_router import AIRouter
from engine.command import speak
from engine.pdf_reader import PDFReader
from engine.screen_analyzer import ScreenAnalyzer
# New imports for code analysis feature
try:
    import pytesseract
    from PIL import Image
    CODE_ANALYSIS_AVAILABLE = True
except ImportError:
    CODE_ANALYSIS_AVAILABLE = False
# Import meeting assistant with error handling
try:
    from meeting_assistant import meeting_assistant, handle_meeting_command
except:
    meeting_assistant = None
    handle_meeting_command = None

# Import voice email assistant
import pickle
import base64
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import wave
import json
import requests
import numpy as np
from datetime import datetime
from vosk import Model, KaldiRecognizer
from simple_meeting_recorder import SimpleMeetingRecorder

class VoiceMeetingAssistant:
    """Voice Meeting Assistant integrated with JARVIS"""
    
    def __init__(self):
        self.is_recording = False
        self.meeting_recorder = None
        self.vosk_model = None
        
        # Initialize components
        try:
            self.meeting_recorder = SimpleMeetingRecorder()
            self.setup_vosk_model()
        except Exception as e:
            print(f"⚠️ Voice Meeting Assistant init warning: {e}")
    
    def setup_vosk_model(self):
        """Setup Vosk model"""
        model_path = "vosk-model-en-us-0.22-lgraph"
        
        if os.path.exists(model_path):
            self.vosk_model = Model(model_path)
        else:
            print("⚠️ Vosk model not found")
            self.vosk_model = None
    
    def speak_fixed(self, text):
        """Fixed TTS using Windows SAPI directly"""
        try:
            text = str(text).strip()
            if not text:
                return
                
            print(f"🔊 Speaking: {text}")
            
            # Try Windows SAPI directly
            try:
                import win32com.client
                speaker = win32com.client.Dispatch("SAPI.SpVoice")
                speaker.Speak(text)
                return
            except:
                pass
            
            # Fallback to subprocess PowerShell
            try:
                ps_command = f'Add-Type -AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Speak("{text}")'
                subprocess.run(['powershell', '-Command', ps_command], check=True, capture_output=True)
                return
            except:
                pass
            
            # Final fallback to regular speak function
            speak(text)
            
        except Exception as e:
            print(f"❌ TTS error: {e}")
    
    def start_meeting_recording(self):
        """Start recording meeting audio"""
        if self.is_recording:
            return "Already recording a meeting!"
        
        if not self.meeting_recorder:
            return "Meeting recorder not available"
        
        try:
            self.speak_fixed("I will do that for you sir. Starting meeting recording now.")
            
            result = self.meeting_recorder.start_recording()
            
            if "✅" in result:
                self.is_recording = True
                return "Meeting recording started! I'm listening to Google Meet audio."
            else:
                return f"Failed to start recording: {result}"
                
        except Exception as e:
            return f"Error starting recording: {e}"
    
    def stop_and_process_meeting(self):
        """Stop recording and process meeting"""
        if not self.is_recording:
            return "No meeting is currently being recorded!"
        
        try:
            self.speak_fixed("Processing the meeting now. This may take a moment.")
            
            self.is_recording = False
            
            # Stop recording
            self.meeting_recorder.is_recording = False
            
            if self.meeting_recorder.stream:
                self.meeting_recorder.stream.stop_stream()
                self.meeting_recorder.stream.close()
            
            if hasattr(self.meeting_recorder, 'recording_thread'):
                self.meeting_recorder.recording_thread.join(timeout=3)
            
            if not self.meeting_recorder.audio_frames:
                return "No audio recorded"
            
            # Save audio
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_filename = f"jarvis_meeting_{timestamp}.wav"
            
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
            return f"Error processing meeting: {e}"
    
    def _process_meeting_complete(self, audio_file):
        """Complete meeting processing"""
        try:
            # Transcribe with Vosk
            transcript = self._transcribe_with_vosk(audio_file)
            
            if not transcript or len(transcript.strip()) < 10:
                return "Transcription failed or no speech detected"
            
            # Summarize with Ollama
            summary = self._summarize_with_ollama(transcript)
            
            # Save files
            transcript_file = audio_file.replace('.wav', '_transcript.txt')
            summary_file = audio_file.replace('.wav', '_summary.txt')
            
            with open(transcript_file, 'w', encoding='utf-8') as f:
                f.write(transcript)
            
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary)
            
            # Don't speak summary immediately - wait for user request
            self.speak_fixed("Meeting processed successfully.")
            
            return f"Meeting processed successfully!\n\nSUMMARY:\n{summary}\n\nFiles: {transcript_file}, {summary_file}"
            
        except Exception as e:
            return f"Processing error: {e}"
    
    def _transcribe_with_vosk(self, audio_file):
        """Transcribe using Vosk"""
        if not self.vosk_model:
            return "Vosk model not available"
        
        try:
            # Convert audio for Vosk
            converted_file = self._convert_audio_for_vosk(audio_file)
            if not converted_file:
                converted_file = audio_file
            
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
            
            final_result = json.loads(rec.FinalResult())
            if final_result.get('text'):
                transcript_parts.append(final_result['text'])
            
            wf.close()
            
            # Clean up converted file
            if converted_file != audio_file and os.path.exists(converted_file):
                os.remove(converted_file)
            
            return ' '.join(transcript_parts).strip()
                
        except Exception as e:
            return f"Vosk error: {e}"
    
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
            return None
    
    def _summarize_with_ollama(self, transcript):
        """Summarize with Ollama"""
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
            clean_text = text.replace("**", "")  # Remove bold asterisks
            clean_text = clean_text.replace("*", "")   # Remove italic asterisks
            clean_text = clean_text.replace("#", "")   # Remove headers
            clean_text = clean_text.replace("- ", "")  # Remove bullet points
            clean_text = clean_text.replace("  ", " ") # Remove double spaces
            clean_text = clean_text.strip()
            
            return clean_text
            
        except Exception as e:
            return text

class FinalJarvis:
    """Final JARVIS with natural speech understanding and conversational responses"""
    
    def __init__(self):
        print("🤖 Starting JARVIS...")
        speak("JARVIS starting up")
        
        # Initialize components
        self.db_manager = DatabaseManager()
        self.android_controller = AndroidController(self.db_manager)
        self.ai_router = AIRouter()
        self.pdf_reader = PDFReader()
        self.screen_analyzer = ScreenAnalyzer()
        
        # Speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Recipe state tracking
        self.current_recipe = None
        self.recipe_steps = []
        self.current_step = 0
        
        # Meeting state tracking
        self.meeting_mode = "normal"  # normal, recording, processed
        self.meeting_summary = None
        
        # Initialize Voice Meeting Assistant
        self.voice_meeting_assistant = None
        self.setup_voice_meeting_assistant()
        
        # Initialize Email Assistant
        self.setup_email_assistant()
        
        # Calibrate microphone
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        
        print("✅ JARVIS ready!")
        speak("JARVIS online and ready for your commands")
    
    def setup_voice_meeting_assistant(self):
        """Setup the voice meeting assistant"""
        try:
            print("🎤 Setting up Voice Meeting Assistant...")
            self.voice_meeting_assistant = VoiceMeetingAssistant()
            print("✅ Voice Meeting Assistant ready")
        except Exception as e:
            print(f"⚠️ Voice Meeting Assistant setup warning: {e}")
            self.voice_meeting_assistant = None
    
    def setup_email_assistant(self):
        """Setup Gmail API for email reading"""
        try:
            print("📧 Setting up Email Assistant...")
            self.gmail_service = None
            self.SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
            self.ollama_url = 'http://localhost:11434'
            self.ollama_model = 'llama3.2:3b'
            
            # Fix SSL certificate issue on Windows
            import ssl
            import certifi
            import os
            os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
            os.environ['SSL_CERT_FILE'] = certifi.where()
            
            # Setup Gmail API
            creds = None
            if os.path.exists('gmail_token.pickle'):
                with open('gmail_token.pickle', 'rb') as token:
                    creds = pickle.load(token)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                    except Exception as refresh_error:
                        print(f"⚠️ Token refresh failed: {refresh_error}")
                        # Delete old token and re-authenticate
                        if os.path.exists('gmail_token.pickle'):
                            os.remove('gmail_token.pickle')
                        creds = None
                
                if not creds:
                    print("🔑 Starting Gmail authentication...")
                    flow = InstalledAppFlow.from_client_secrets_file('gmail.json', self.SCOPES)
                    creds = flow.run_local_server(port=0)
                
                with open('gmail_token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
            
            self.gmail_service = build('gmail', 'v1', credentials=creds)
            print("✅ Email Assistant ready")
            
        except Exception as e:
            print(f"⚠️ Email Assistant setup warning: {e}")
            self.gmail_service = None
    
    def listen_for_command(self):
        """Listen for any voice command"""
        try:
            with self.microphone as source:
                print("👂 Listening...")
                audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=8)
            
            command = self.recognizer.recognize_google(audio)
            print(f"🎤 You said: {command}")
            return command
            
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            print("❌ Speech recognition error")
            return None
        except sr.WaitTimeoutError:
            return None
    
    async def understand_and_execute(self, command):
        """Use AI to understand intent and execute task"""
        try:
            print(f"🧠 Understanding: {command}")
            
            # Check meeting mode first
            if self.meeting_mode == "recording":
                # Only listen for "leave meeting" command while recording
                if any(phrase in command.lower() for phrase in [
                    "jarvis leave the meeting",
                    "jarvis you can leave the meeting", 
                    "leave the meeting jarvis",
                    "stop meeting jarvis"
                ]):
                    print("🎯 Meeting command: LEAVE_MEETING")
                    if self.voice_meeting_assistant:
                        result = self.voice_meeting_assistant.stop_and_process_meeting()
                        print(result)
                        # Store summary and change mode
                        if "SUMMARY:" in result:
                            self.meeting_summary = result.split("SUMMARY:")[1].split("Files:")[0].strip()
                            self.meeting_mode = "processed"
                            speak("Meeting processed successfully.")
                        else:
                            self.meeting_mode = "normal"
                else:
                    # Ignore all other commands while recording
                    print("🎙️ Currently recording meeting. Say 'Jarvis leave the meeting' to stop.")
                return
            
            elif self.meeting_mode == "processed":
                # Only listen for summary request
                if any(phrase in command.lower() for phrase in [
                    "jarvis please summarise the meeting for me",
                    "jarvis summarise the meeting",
                    "jarvis tell me the meeting summary",
                    "jarvis what was discussed in the meeting"
                ]):
                    print("🎯 Meeting command: SPEAK_SUMMARY")
                    if self.meeting_summary:
                        clean_summary = self.voice_meeting_assistant._clean_text_for_speech(self.meeting_summary)
                        self.voice_meeting_assistant.speak_fixed("Here is your meeting summary.")
                        time.sleep(1)
                        self.voice_meeting_assistant.speak_fixed(clean_summary)
                        # Resume normal mode
                        self.meeting_mode = "normal"
                        self.meeting_summary = None
                        speak("Meeting summary complete. I'm ready for your next command.")
                    else:
                        speak("No meeting summary available.")
                        self.meeting_mode = "normal"
                else:
                    # Remind user about summary
                    speak("Meeting is processed. Say 'Jarvis please summarise the meeting for me' to hear the summary.")
                return
            
            # Normal mode - use AI to classify the command
            analysis_prompt = f"""
            Analyze this command and determine the task: "{command}"
            
            Available tasks:
            1. OPEN_YOUTUBE - open YouTube
            2. SEARCH_YOUTUBE - search something on YouTube  
            3. PLAY_YOUTUBE - play video on YouTube
            4. CLOSE_YOUTUBE - close YouTube
            5. OPEN_GOOGLE - open Google
            6. SEARCH_GOOGLE - search something on Google
            7. CLOSE_GOOGLE - close Google browser
            8. OPEN_NOTEPAD - open notepad
            9. WRITE_LEAVE_APPLICATION - write leave application in notepad
            10. CLOSE_NOTEPAD - close notepad
            11. CALL_TOM - call Tom
            12. SMS_TOM - send SMS to Tom
            13. END_CALL - end phone call
            14. WHATSAPP_TOM - WhatsApp message to Tom
            15. VOLUME_UP - increase volume
            16. VOLUME_DOWN - decrease volume
            17. BRIGHTNESS_UP - increase brightness
            18. BRIGHTNESS_DOWN - decrease brightness
            19. TURN_ON_FLASHLIGHT - turn on phone flashlight
            20. TURN_OFF_FLASHLIGHT - turn off phone flashlight
            21. TAKE_PHOTO - take photo with laptop camera
            22. TAKE_SCREENSHOT - take screenshot of laptop screen
            23. OPEN_CHATGPT - open ChatGPT and search
            24. OPEN_RECYCLE_BIN - open recycle bin
            25. DELETE_RECYCLE_BIN - delete all items from recycle bin
            26. CLOSE_RECYCLE_BIN - close recycle bin
            27. SET_ALARM - set alarm on phone
            28. ADD_CALENDAR_EVENT - add event to Google Calendar
            29. PLAY_YOUTUBE_VIDEO - play specific YouTube video
            30. WRITE_CUSTOM - write custom content in notepad
            31. RECIPE_REQUEST - recipe requests like "tell me recipe to make burger"
            32. RECIPE_NEXT - when user says "next" during recipe
            33. READ_PDF - read PDF file like "open the PDF named amazon" or "read the PDF file report"
            34. DESCRIBE_SCREEN - describe what's on screen like "describe what's on my screen" or "what do you see on my screen"
            35. READ_EMAILS - read unread emails like "jarvis read my emails for me" or "check my emails"
            36. ATTEND_MEETING - start recording meeting like "jarvis attend the meeting for me"
            37. LEAVE_MEETING - stop recording and process meeting like "jarvis you can leave the meeting"
            38. MEETING_STATUS - check meeting recording status
            39. HELP_WITH_CODE - analyze code on screen like "jarvis help me with my code" or "check my code"
            40. CODE_SUCCESS - confirmation that code is working like "thank you jarvis my code is running successfully now"
            41. CONVERSATION - general conversation, questions, mood support
            
            Respond with:
            TASK: [task_name]
            QUERY: [search term if applicable]
            MESSAGE: [message content if applicable]
            """
            
            ai_result = await self.ai_router.process_query(analysis_prompt, "general")
            
            if ai_result['success']:
                analysis = ai_result['response']
                await self.execute_task(analysis, command)
            else:
                speak("I'm having trouble understanding that command")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            speak("I encountered an error processing that command")
    
    async def execute_task(self, analysis, original_command):
        """Execute the identified task"""
        try:
            # Parse AI analysis
            task = "UNKNOWN"
            query = ""
            message = ""
            
            lines = analysis.split('\n')
            for line in lines:
                if line.startswith('TASK:'):
                    task = line.split(':', 1)[1].strip()
                elif line.startswith('QUERY:'):
                    query = line.split(':', 1)[1].strip()
                elif line.startswith('MESSAGE:'):
                    message = line.split(':', 1)[1].strip()
            
            print(f"🎯 Task identified: {task}")
            
            # Execute based on task
            if task == "OPEN_YOUTUBE":
                speak("Sure, I'll open YouTube for you")
                webbrowser.open("https://www.youtube.com")
                speak("YouTube is now open")
            
            elif task == "SEARCH_YOUTUBE":
                if not query:
                    query = self.extract_search_term(original_command)
                speak(f"I'll search for {query} on YouTube")
                webbrowser.open(f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}")
                speak(f"Here are the search results for {query}")
            
            elif task == "PLAY_YOUTUBE":
                # Always use the original command for better detection
                search_term = self.extract_search_term(original_command)
                await self.play_youtube_video(search_term)
            
            elif task == "CLOSE_YOUTUBE":
                speak("I'll close YouTube for you")
                self.close_browser()
                speak("YouTube closed")
            
            elif task == "OPEN_GOOGLE":
                speak("Opening Google for you")
                webbrowser.open("https://www.google.com")
                speak("Google is now open")
            
            elif task == "SEARCH_GOOGLE":
                if not query:
                    query = self.extract_search_term(original_command)
                
                # Check if it's a recipe request
                if any(word in original_command.lower() for word in ['recipe', 'make', 'cook', 'prepare', 'how to make']):
                    speak("I'll help you with that recipe using my local knowledge")
                    await self.handle_recipe_request(original_command)
                    return
                
                # Check if it's a question that can be answered locally
                elif any(word in original_command.lower() for word in ['what', 'who', 'where', 'when', 'why', 'how', 'capital', 'is', 'are']):
                    speak("Let me answer that for you")
                    
                    # Try Ollama first for local AI response
                    ollama_response = await self.get_ollama_response(original_command)
                    
                    if ollama_response:
                        speak(ollama_response)
                        return  # Don't open Google if we got a local response
                    else:
                        # Fallback to Google search if Ollama is not available
                        speak(f"I'll search for {query} on Google")
                        webbrowser.open(f"https://www.google.com/search?q={query.replace(' ', '+')}")
                        speak(f"Here are the search results for {query}")
                else:
                    # Regular search for non-question queries
                    speak(f"I'll search for {query} on Google")
                    webbrowser.open(f"https://www.google.com/search?q={query.replace(' ', '+')}")
                    speak(f"Here are the search results for {query}")
            
            elif task == "CLOSE_GOOGLE":
                speak("I'll close the browser for you")
                self.close_browser()
                speak("Browser closed")
            
            elif task == "OPEN_NOTEPAD":
                speak("Opening Notepad for you")
                os.startfile("notepad.exe")
                speak("Notepad is now open")
            
            elif task == "WRITE_LEAVE_APPLICATION":
                speak("I'll help you write a leave application")
                await self.write_interactive_leave_application()
                speak("Leave application has been written in Notepad")
            
            elif "WRITE_" in task or "invitation" in original_command.lower() or "letter" in original_command.lower():
                speak("I'll write that for you in Notepad")
                self.write_custom_text(original_command, query)
                speak("I've written the content in Notepad for you")
            
            elif task == "CLOSE_NOTEPAD":
                speak("I'll close Notepad for you")
                subprocess.run(['taskkill', '/f', '/im', 'notepad.exe'], capture_output=True)
                speak("Notepad closed")
            
            elif task == "CALL_TOM":
                speak("Yes, I can call Tom for you")
                await self.call_tom()
            
            elif task == "SMS_TOM":
                speak("I'll send an SMS to Tom for you")
                await self.sms_tom(message)
            
            elif task == "END_CALL":
                speak("I'll end the call for you")
                self.android_controller._key_event(6)  # End call key
                speak("Call ended")
            
            elif task == "WHATSAPP_TOM":
                speak("I'll send a WhatsApp message to Tom")
                await self.whatsapp_tom(message, original_command)
            
            elif task == "VOLUME_UP":
                speak("I'll increase the volume for you")
                for _ in range(3):
                    pyautogui.press('volumeup')
                speak("Volume increased")
            
            elif task == "VOLUME_DOWN":
                speak("I'll decrease the volume for you")
                for _ in range(3):
                    pyautogui.press('volumedown')
                speak("Volume decreased")
            
            elif task == "BRIGHTNESS_UP":
                speak("I'll increase the brightness for you")
                self.control_brightness('up')
                speak("Brightness increased")
            
            elif task == "BRIGHTNESS_DOWN":
                speak("I'll decrease the brightness for you")
                self.control_brightness('down')
                speak("Brightness decreased")
            
            elif task == "TURN_ON_FLASHLIGHT":
                speak("I'll turn on your phone's flashlight")
                await self.control_flashlight('on')
            
            elif task == "TURN_OFF_FLASHLIGHT":
                speak("I'll turn off your phone's flashlight")
                await self.control_flashlight('off')
            
            elif task == "TAKE_PHOTO":
                speak("I'll take a photo for you using your laptop camera")
                await self.take_photo()
            
            elif task == "TAKE_SCREENSHOT":
                speak("I'll take a screenshot of your laptop screen")
                await self.take_screenshot()
            
            elif task == "OPEN_CHATGPT":
                speak("I'll open ChatGPT for you")
                await self.open_chatgpt()
            
            elif task == "OPEN_RECYCLE_BIN":
                speak("I'll open the Recycle Bin for you")
                self.open_recycle_bin()
            
            elif task == "DELETE_RECYCLE_BIN":
                speak("I'll delete all items from the Recycle Bin")
                await self.delete_recycle_bin_contents()
            
            elif task == "CLOSE_RECYCLE_BIN":
                speak("I'll close the Recycle Bin for you")
                self.close_recycle_bin()
            
            elif task == "SET_ALARM":
                speak("I'll set an alarm on your phone")
                await self.set_phone_alarm(original_command)
            
            elif task == "ADD_CALENDAR_EVENT":
                speak("I'll add an event to your Google Calendar")
                await self.add_calendar_event(original_command)
            
            elif task == "PLAY_YOUTUBE_VIDEO":
                speak("I'll play a YouTube video for you")
                await self.play_youtube_video(query)
            
            elif task == "RECIPE_REQUEST":
                speak("I'll help you with that recipe")
                await self.handle_recipe_request(original_command)
            
            elif task == "RECIPE_NEXT":
                await self.handle_recipe_next()
            
            elif task == "CONVERSATION":
                await self.handle_conversation(original_command)
            
            elif task == "READ_PDF":
                speak("I'll find and read that PDF for you")
                await self.handle_pdf_reading(original_command)
            
            elif task == "DESCRIBE_SCREEN":
                speak("Let me analyze what's on your screen")
                await self.handle_screen_description()
            
            elif task == "READ_EMAILS":
                speak("I'll check your emails for you sir")
                await self.handle_email_reading()
            
            elif task == "ATTEND_MEETING":
                if self.voice_meeting_assistant:
                    result = self.voice_meeting_assistant.start_meeting_recording()
                    print(result)
                    # Switch to recording mode
                    self.meeting_mode = "recording"
                    speak("I'm now in meeting mode. I'll only listen for 'Jarvis leave the meeting' until you're done.")
                else:
                    speak("I'll attend the meeting for you and record everything")
                    result = meeting_assistant.start_recording()
                    speak(result)
            
            elif task == "LEAVE_MEETING":
                if self.voice_meeting_assistant and self.voice_meeting_assistant.is_recording:
                    result = self.voice_meeting_assistant.stop_and_process_meeting()
                    print(result)
                else:
                    speak("Processing the meeting now. This may take a moment.")
                    result = meeting_assistant.stop_recording()
                    speak("Meeting processed successfully! Check the summary.")
                    print(f"\n{result}")
            
            elif task == "MEETING_STATUS":
                if self.voice_meeting_assistant:
                    if self.voice_meeting_assistant.is_recording:
                        status = "Currently recording meeting audio"
                    else:
                        status = "No meeting recording in progress"
                    speak(status)
                    print(status)
                else:
                    result = meeting_assistant.get_status()
                    speak(result)
                    print(result)
            
            elif task == "HELP_WITH_CODE":
                speak("I'll analyze your code for you sir")
                await self.help_with_code()
            
            elif task == "CODE_SUCCESS":
                speak("That's great to hear sir! How else can I assist you?")
                print("✅ Code success confirmed - resuming normal operation")
            
            else:
                # Check if it's a meeting command using natural language
                meeting_result = handle_meeting_command(original_command)
                if meeting_result:
                    speak(meeting_result)
                    if "processed successfully" in meeting_result:
                        print(f"\n{meeting_result}")
                else:
                    # If no specific task, treat as conversation
                    await self.handle_conversation(original_command)
                
        except Exception as e:
            print(f"❌ Execution error: {e}")
            speak("I encountered an error while executing that task")
    
    def extract_search_term(self, command):
        """Extract search term from command"""
        # Remove common words
        words_to_remove = ['search', 'for', 'play', 'find', 'look', 'up', 'on', 'youtube', 'google', 'please', 'can', 'you']
        words = command.lower().split()
        
        filtered_words = []
        for word in words:
            if word not in words_to_remove:
                filtered_words.append(word)
        
        return ' '.join(filtered_words) if filtered_words else "search query"
    
    def close_browser(self):
        """Close browser windows"""
        try:
            # Try to close Chrome
            subprocess.run(['taskkill', '/f', '/im', 'chrome.exe'], capture_output=True)
            # Try to close Edge
            subprocess.run(['taskkill', '/f', '/im', 'msedge.exe'], capture_output=True)
            # Try to close Firefox
            subprocess.run(['taskkill', '/f', '/im', 'firefox.exe'], capture_output=True)
        except:
            pass
    
    async def write_interactive_leave_application(self):
        """Write interactive leave application by asking questions"""
        try:
            # Ask for recipient
            speak("To whom should I address this leave application?")
            print("🎤 Listening for recipient (e.g., 'Manager', 'HR Department')...")
            
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=8)
                recipient = self.recognizer.recognize_google(audio)
                print(f"👤 Recipient: {recipient}")
            except:
                recipient = "Manager"
                speak("I'll address it to Manager")
            
            # Ask for from date
            speak("From which date do you need leave?")
            print("🎤 Listening for start date (e.g., '5th September' or 'tomorrow')...")
            
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=8)
                from_date = self.recognizer.recognize_google(audio)
                print(f"📅 From date: {from_date}")
            except:
                from_date = "[Start Date]"
                speak("I'll use a placeholder for the start date")
            
            # Ask for to date
            speak("Till which date do you need leave?")
            print("🎤 Listening for end date...")
            
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=8)
                to_date = self.recognizer.recognize_google(audio)
                print(f"📅 To date: {to_date}")
            except:
                to_date = "[End Date]"
                speak("I'll use a placeholder for the end date")
            
            # Ask for reason
            speak("What's the reason for your leave?")
            print("🎤 Listening for reason...")
            
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=15, phrase_time_limit=20)
                reason = self.recognizer.recognize_google(audio)
                print(f"📝 Reason: {reason}")
            except:
                reason = "personal reasons"
                speak("I'll mention personal reasons")
            
            # Write the customized leave application
            time.sleep(2)  # Wait for notepad to open
            
            leave_text = f"""Subject: Leave Application

Dear {recipient},

I am writing to request leave from work due to {reason}. 

I would like to take leave from {from_date} to {to_date}.

I will ensure that all my pending work is completed before my leave and will coordinate with my team for a smooth handover of responsibilities.

I would be grateful if you could approve my leave request.

Thank you for your consideration.

Yours sincerely,
[Your Name]
[Your Designation]
[Date]"""
            
            # Type the leave application
            pyautogui.write(leave_text, interval=0.01)
            
        except Exception as e:
            speak("I'll write a standard leave application for you")
            self.write_standard_leave_application()
    
    def write_standard_leave_application(self):
        """Write standard leave application as fallback"""
        time.sleep(2)
        
        leave_text = """Subject: Leave Application

Dear Sir/Madam,

I am writing to request leave from work due to personal reasons. I would like to take leave for [number of days] starting from [start date] to [end date].

I will ensure that all my pending work is completed before my leave and will coordinate with my team for a smooth handover.

I would be grateful if you could approve my leave request.

Thank you for your consideration.

Yours sincerely,
[Your Name]"""
        
        pyautogui.write(leave_text, interval=0.01)
    
    def write_custom_text(self, text_type, details=""):
        """Write custom text in notepad based on user request"""
        time.sleep(2)  # Wait for notepad to open
        
        if "invitation" in text_type.lower() or "birthday" in text_type.lower():
            invitation_text = f"""🎉 BIRTHDAY INVITATION 🎉

You're Invited!

Join us for a Birthday Celebration!

Date: {details if details else '[Date]'}
Time: 7:00 PM
Venue: [Your Address]

Come and celebrate with us!
Food, Fun, and Great Company Awaits!

Please RSVP by [Date]

Looking forward to seeing you there!

Best Regards,
[Your Name]"""
            pyautogui.write(invitation_text, interval=0.01)
            
        elif "letter" in text_type.lower():
            letter_text = f"""[Date]

Dear [Recipient Name],

I hope this letter finds you in good health and spirits.

{details if details else '[Your message content here]'}

I look forward to hearing from you soon.

Warm regards,

[Your Name]
[Your Address]
[Your Contact Information]"""
            pyautogui.write(letter_text, interval=0.01)
            
        else:
            # Generic text
            generic_text = f"""Document Created by JARVIS

{details if details else 'Your content will be written here.'}

Created on: {time.strftime('%Y-%m-%d %H:%M:%S')}"""
            pyautogui.write(generic_text, interval=0.01)
    
    async def call_tom(self):
        """Call Tom using phone"""
        try:
            tom_contact = self.db_manager.get_contact("Tom")
            if tom_contact:
                speak(f"Calling Tom at {tom_contact['mobile_no']}")
                result = self.android_controller.make_call(tom_contact['mobile_no'], tom_contact['name'])
                if result['success']:
                    speak("Call initiated successfully")
                else:
                    speak("I couldn't make the call. Please check your phone connection")
            else:
                speak("I couldn't find Tom in your contacts")
        except Exception as e:
            speak("I encountered an error while trying to call Tom")
    
    async def sms_tom(self, message):
        """Send SMS to Tom"""
        try:
            tom_contact = self.db_manager.get_contact("Tom")
            if tom_contact:
                if not message:
                    message = "Hello from JARVIS"
                
                speak(f"Sending SMS to Tom: {message}")
                result = self.android_controller.send_sms(tom_contact['mobile_no'], message, tom_contact['name'])
                if result['success']:
                    speak("SMS sent successfully")
                else:
                    speak("I couldn't send the SMS. Please check your phone connection")
            else:
                speak("I couldn't find Tom in your contacts")
        except Exception as e:
            speak("I encountered an error while sending the SMS")
    
    async def whatsapp_tom(self, message, original_command):
        """Send WhatsApp to Tom - with proper conversation like original folders"""
        try:
            tom_contact = self.db_manager.get_contact("Tom")
            if tom_contact:
                # Always ask for message, even if one was provided
                speak("Sure! What message would you like me to send to Tom on WhatsApp?")
                print("🎤 Listening for your message...")
                
                # Listen for message with longer timeout
                try:
                    with self.microphone as source:
                        audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=15)
                    message = self.recognizer.recognize_google(audio)
                    print(f"📝 Message: {message}")
                    speak(f"Got it! I'll send '{message}' to Tom on WhatsApp")
                except sr.UnknownValueError:
                    speak("I didn't catch that clearly. Let me try again.")
                    try:
                        with self.microphone as source:
                            audio = self.recognizer.listen(source, timeout=8, phrase_time_limit=12)
                        message = self.recognizer.recognize_google(audio)
                        print(f"📝 Message: {message}")
                        speak(f"Perfect! I'll send '{message}' to Tom")
                    except:
                        message = "Hello from JARVIS"
                        speak("I'll send a default greeting message")
                except sr.WaitTimeoutError:
                    message = "Hello from JARVIS"
                    speak("I didn't hear anything, so I'll send a default greeting")
                except Exception as e:
                    message = "Hello from JARVIS"
                    speak("I'll send a default message")
                
                speak("Opening WhatsApp on your phone and sending the message")
                result = self.android_controller.whatsapp_automation(tom_contact['name'], message, 'message')
                
                # Add a small delay and click send button
                time.sleep(2)
                
                # Click the send button at the coordinates you specified
                send_cmd = ['input', 'tap', '1150', '2558']
                self.android_controller._execute_adb_command(send_cmd)
                
                if result['success']:
                    speak(f"Perfect! WhatsApp message '{message}' sent to Tom successfully")
                else:
                    speak("WhatsApp message should be sent now. Please check your phone")
            else:
                speak("I'm sorry, I couldn't find Tom in your contacts")
        except Exception as e:
            speak("I encountered an issue while sending the WhatsApp message")
    
    def control_brightness(self, action):
        """Control screen brightness"""
        try:
            if action == 'up':
                subprocess.run(['powershell', '-Command', 
                              "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,100)"], 
                              capture_output=True)
            elif action == 'down':
                subprocess.run(['powershell', '-Command', 
                              "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,30)"], 
                              capture_output=True)
        except:
            pass
    
    async def control_flashlight(self, action):
        """Control phone flashlight via ADB using exact commands"""
        try:
            if action == 'on':
                speak("Turning on your phone's flashlight")
                # Use the exact ADB command you specified
                cmd = ['cmd', 'torch', 'on']
                result = self.android_controller._execute_adb_command(cmd)
                
                if result:
                    speak("Flashlight turned on successfully")
                else:
                    speak("Flashlight command sent, it should be on now")
                
            else:
                speak("Turning off your phone's flashlight")
                # Use the exact ADB command you specified
                cmd = ['cmd', 'torch', 'off']
                result = self.android_controller._execute_adb_command(cmd)
                
                if result:
                    speak("Flashlight turned off successfully")
                else:
                    speak("Flashlight command sent, it should be off now")
                
        except Exception as e:
            speak("I had trouble controlling the flashlight. Please check your phone connection")
    
    async def take_photo(self):
        """Take photo using laptop camera"""
        try:
            speak("Smile! Taking your photo in 3 seconds")
            time.sleep(1)
            speak("3")
            time.sleep(1)
            speak("2")
            time.sleep(1)
            speak("1")
            
            try:
                import cv2
                
                # Try different camera indices
                for camera_index in [0, 1, 2]:
                    cap = cv2.VideoCapture(camera_index)
                    if cap.isOpened():
                        ret, frame = cap.read()
                        if ret:
                            # Save photo
                            photo_name = f"jarvis_photo_{int(time.time())}.jpg"
                            cv2.imwrite(photo_name, frame)
                            speak(f"Perfect! Photo captured and saved as {photo_name}")
                            cap.release()
                            return
                        cap.release()
                
                speak("I couldn't access your camera. It might be in use by another application")
                
            except ImportError:
                # Fallback method using Windows Camera app
                speak("Opening Windows Camera app for you")
                try:
                    os.system('start microsoft.windows.camera:')
                    time.sleep(2)
                    # Take screenshot after 3 seconds
                    pyautogui.press('space')  # Camera capture key
                    speak("Photo taken using Windows Camera app")
                except:
                    speak("I need OpenCV to take photos directly. Please install it with: pip install opencv-python")
                    
        except Exception as e:
            speak("I encountered an issue while taking the photo")
    
    async def take_screenshot(self):
        """Take screenshot of laptop screen"""
        try:
            speak("Taking a screenshot of your laptop screen")
            
            # Take screenshot using pyautogui
            screenshot = pyautogui.screenshot()
            
            # Save screenshot
            screenshot_name = f"jarvis_screenshot_{int(time.time())}.png"
            screenshot.save(screenshot_name)
            
            speak(f"Perfect! Screenshot saved as {screenshot_name}")
            
        except Exception as e:
            speak("I encountered an issue while taking the screenshot")
    
    def extract_code_from_screen(self, screenshot=None):
        """Extract code text from right side of screen using OCR"""
        try:
            if not CODE_ANALYSIS_AVAILABLE:
                return "OCR libraries not available. Please install pytesseract and Pillow."
            
            # Take screenshot if not provided
            if screenshot is None:
                screenshot = pyautogui.screenshot()
            
            # Get screen dimensions
            width, height = screenshot.size
            
            # Crop to focus on right side of screen (where code editor usually is)
            # Assuming code editor is on right 60% of screen
            left = int(width * 0.4)  # Start from 40% from left
            top = int(height * 0.1)   # Start from 10% from top
            right = int(width * 0.95) # End at 95% from left
            bottom = int(height * 0.9) # End at 90% from top
            
            code_area = screenshot.crop((left, top, right, bottom))
            
            # Use pytesseract to extract text
            extracted_text = pytesseract.image_to_string(code_area)
            
            # Clean up the extracted text
            cleaned_text = self.clean_extracted_code(extracted_text)
            
            return cleaned_text
            
        except Exception as e:
            print(f"❌ OCR extraction error: {e}")
            return f"Error extracting code from screen: {str(e)}"
    
    def clean_extracted_code(self, raw_text):
        """Clean and format extracted code text"""
        try:
            if not raw_text or not raw_text.strip():
                return "No code detected on screen"
            
            # Remove extra whitespace and empty lines
            lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
            
            # Filter out non-code lines (common OCR artifacts)
            code_lines = []
            for line in lines:
                # Skip lines that are too short or contain only special characters
                if len(line) > 2 and any(c.isalnum() for c in line):
                    code_lines.append(line)
            
            # Join the cleaned lines
            cleaned_code = '\n'.join(code_lines)
            
            # If no meaningful code found
            if not cleaned_code or len(cleaned_code) < 10:
                return "No readable code found on screen. Please ensure code is clearly visible."
            
            return cleaned_code
            
        except Exception as e:
            return f"Error cleaning extracted text: {str(e)}"
    
    async def help_with_code(self):
        """Analyze code on screen and provide 3-line mistake explanation"""
        try:
            speak("Let me analyze your code sir")
            
            # Take screenshot and extract code
            print("📸 Taking screenshot...")
            screenshot = pyautogui.screenshot()
            
            print("🔍 Extracting code from screen...")
            extracted_code = self.extract_code_from_screen(screenshot)
            
            if "Error" in extracted_code or "No" in extracted_code:
                speak("I couldn't read the code clearly from your screen. Please make sure your code is visible and try again.")
                return
            
            print(f"📝 Extracted code:\n{extracted_code}")
            
            # Analyze code with OpenAI
            print("🧠 Analyzing code with AI...")
            analysis_result = await self.ai_router.analyze_code_with_openai(extracted_code)
            
            if analysis_result['success']:
                mistakes = analysis_result['mistakes']
                
                # Speak the 3-line analysis
                speak("Here's what I found wrong with your code:")
                time.sleep(0.5)
                
                for i, mistake in enumerate(mistakes, 1):
                    speak(f"Line {i}: {mistake}")
                    time.sleep(0.8)  # Pause between lines
                
                # No automatic fixing - user will fix manually
                print("✅ Code analysis complete")
                
            else:
                speak("I had trouble analyzing your code. Please check your OpenAI API key and try again.")
                
        except Exception as e:
            print(f"❌ Code analysis error: {e}")
            speak("I encountered an error while analyzing your code. Please try again.")
    
    async def open_chatgpt(self):
        """Open ChatGPT and ask what to search for"""
        try:
            speak("Opening ChatGPT for you")
            webbrowser.open("https://chat.openai.com")
            
            time.sleep(3)  # Wait for page to load
            
            speak("What would you like me to search for on ChatGPT?")
            print("🎤 Listening for your ChatGPT search query...")
            
            # Listen for search query
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=15)
                search_query = self.recognizer.recognize_google(audio)
                print(f"🔍 Search query: {search_query}")
                speak(f"I'll search for '{search_query}' on ChatGPT")
                
                # Wait a bit more for ChatGPT to fully load
                time.sleep(2)
                
                # Type the search query
                pyautogui.write(search_query, interval=0.05)
                time.sleep(1)
                pyautogui.press('enter')
                
                speak("Search query sent to ChatGPT")
                
            except sr.UnknownValueError:
                speak("I didn't catch that. ChatGPT is open, you can type your query manually")
            except sr.WaitTimeoutError:
                speak("I didn't hear anything. ChatGPT is open for you to use")
            except Exception as e:
                speak("ChatGPT is open, you can type your query manually")
                
        except Exception as e:
            speak("I encountered an issue opening ChatGPT")
    
    def open_recycle_bin(self):
        """Open Recycle Bin"""
        try:
            speak("Opening Recycle Bin for you")
            os.system('explorer.exe shell:RecycleBinFolder')
            speak("Recycle Bin is now open")
        except Exception as e:
            speak("I encountered an issue opening the Recycle Bin")
    
    async def delete_recycle_bin_contents(self):
        """Delete all items from Recycle Bin"""
        try:
            speak("Are you sure you want to delete all items from the Recycle Bin? This action cannot be undone.")
            speak("Say 'yes' to confirm or 'no' to cancel")
            
            print("🎤 Listening for confirmation...")
            
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=5)
                confirmation = self.recognizer.recognize_google(audio).lower()
                print(f"🔍 Confirmation: {confirmation}")
                
                if 'yes' in confirmation or 'confirm' in confirmation or 'delete' in confirmation:
                    speak("Deleting all items from Recycle Bin")
                    
                    # Empty recycle bin using PowerShell
                    cmd = 'powershell.exe -Command "Clear-RecycleBin -Force"'
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        speak("All items have been permanently deleted from the Recycle Bin")
                    else:
                        # Alternative method using rd command
                        os.system('rd /s /q %systemdrive%\\$Recycle.bin')
                        speak("Recycle Bin has been emptied")
                        
                else:
                    speak("Operation cancelled. Recycle Bin contents are safe")
                    
            except sr.UnknownValueError:
                speak("I didn't understand. Operation cancelled for safety")
            except sr.WaitTimeoutError:
                speak("No response received. Operation cancelled for safety")
            except Exception as e:
                speak("Operation cancelled for safety")
                
        except Exception as e:
            speak("I encountered an issue with the Recycle Bin operation")
    
    def close_recycle_bin(self):
        """Close Recycle Bin"""
        try:
            speak("Closing Recycle Bin for you")
            
            # Close explorer windows showing recycle bin
            subprocess.run(['taskkill', '/f', '/im', 'explorer.exe'], capture_output=True)
            time.sleep(1)
            # Restart explorer
            subprocess.Popen('explorer.exe')
            
            speak("Recycle Bin closed")
            
        except Exception as e:
            speak("I encountered an issue closing the Recycle Bin")
    
    async def set_phone_alarm(self, original_command):
        """Set alarm on phone using ADB"""
        try:
            speak("What time would you like me to set the alarm for?")
            print("🎤 Listening for alarm time (e.g., '7:30 AM' or '6:45 PM')...")
            
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=8)
                time_input = self.recognizer.recognize_google(audio)
                print(f"⏰ Alarm time: {time_input}")
                
                # Parse time input
                hour, minute = self.parse_time_input(time_input)
                
                if hour is not None and minute is not None:
                    speak(f"Setting alarm for {hour}:{minute:02d}")
                    
                    # Set alarm using ADB with correct command format
                    cmd = [
                        'am', 'start', '-a', 'android.intent.action.SET_ALARM',
                        '--ei', 'android.intent.extra.alarm.HOUR', str(hour),
                        '--ei', 'android.intent.extra.alarm.MINUTES', str(minute),
                        '--ez', 'android.intent.extra.alarm.SKIP_UI', 'true',
                        '--es', 'android.intent.extra.alarm.MESSAGE', 'JARVIS Alarm'
                    ]
                    
                    result = self.android_controller._execute_adb_command(cmd)
                    
                    if result:
                        speak(f"Alarm set successfully for {hour}:{minute:02d}")
                    else:
                        speak("Alarm command sent to your phone. Please check your Clock app")
                else:
                    speak("I couldn't understand the time. Please try again with format like '7:30 AM'")
                    
            except sr.UnknownValueError:
                speak("I didn't catch the time. Please try again")
            except sr.WaitTimeoutError:
                speak("I didn't hear anything. Please try again")
                
        except Exception as e:
            speak("I encountered an issue setting the alarm")
    
    def parse_time_input(self, time_str):
        """Parse time input like '7:30 AM' or '18:45' into hour and minute"""
        try:
            time_str = time_str.lower().strip()
            
            # Remove dots and extra spaces (e.g., "6:30 a.m." -> "6:30 am")
            time_str = time_str.replace('.', '').replace('  ', ' ')
            
            # Handle AM/PM format
            if 'am' in time_str or 'pm' in time_str or 'a.m' in time_str or 'p.m' in time_str:
                is_pm = 'pm' in time_str or 'p.m' in time_str
                # Remove all AM/PM variations
                time_str = time_str.replace('am', '').replace('pm', '').replace('a.m', '').replace('p.m', '').strip()
                
                if ':' in time_str:
                    parts = time_str.split(':')
                    hour = int(parts[0])
                    minute = int(parts[1])
                else:
                    hour = int(time_str)
                    minute = 0
                
                # Convert to 24-hour format
                if is_pm and hour != 12:
                    hour += 12
                elif not is_pm and hour == 12:
                    hour = 0
                    
            else:
                # Handle 24-hour format
                if ':' in time_str:
                    parts = time_str.split(':')
                    hour = int(parts[0])
                    minute = int(parts[1])
                else:
                    hour = int(time_str)
                    minute = 0
            
            # Validate time
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return hour, minute
            else:
                return None, None
                
        except:
            return None, None
    
    async def add_calendar_event(self, original_command):
        """Add event to Google Calendar using ADB"""
        try:
            speak("What's the title of the event?")
            print("🎤 Listening for event title...")
            
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=10)
                title = self.recognizer.recognize_google(audio)
                print(f"📝 Event title: {title}")
                
                speak("What's the description or details?")
                print("🎤 Listening for event description...")
                
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=15)
                description = self.recognizer.recognize_google(audio)
                print(f"📋 Event description: {description}")
                
                speak("Adding event to your Google Calendar")
                
                # Get current time + 1 hour for default event time
                import time as time_module
                current_time = int(time_module.time() * 1000)  # Convert to milliseconds
                end_time = current_time + (60 * 60 * 1000)  # Add 1 hour
                
                # Add calendar event using ADB
                cmd = [
                    'am', 'start', '-a', 'android.intent.action.INSERT',
                    '-d', 'content://com.android.calendar/events',
                    '--es', 'title', title,
                    '--es', 'description', description,
                    '--es', 'eventLocation', 'Set by JARVIS',
                    '--ez', 'allDay', 'false',
                    '--ei', 'beginTime', str(current_time),
                    '--ei', 'endTime', str(end_time)
                ]
                
                result = self.android_controller._execute_adb_command(cmd)
                
                if result:
                    speak(f"Calendar event '{title}' added successfully")
                else:
                    speak("Calendar event command sent. Please check your Google Calendar app")
                    
            except sr.UnknownValueError:
                speak("I didn't catch that. Please try again")
            except sr.WaitTimeoutError:
                speak("I didn't hear anything. Please try again")
                
        except Exception as e:
            speak("I encountered an issue adding the calendar event")
    
    async def play_youtube_video(self, query):
        """Play specific YouTube video or search based on query"""
        try:
            # Check if user said "play any video" or similar
            if any(phrase in query.lower() for phrase in ['any video', 'some video', 'a video', 'video']):
                speak("Playing a specific video for you")
                # Play the specific video you requested
                webbrowser.open("https://www.youtube.com/watch?v=2Ru_AM1D2Ec")
                speak("Playing the video you requested")
            else:
                speak(f"Searching and playing {query} on YouTube")
                
                # Open YouTube search
                webbrowser.open(f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}")
                
                # Wait for page to load
                time.sleep(4)
                
                speak("Clicking on the first video to play it")
                
                # Click on the first video (approximate coordinates for first video thumbnail)
                pyautogui.click(320, 250)  # First video thumbnail position
                
                speak(f"Now playing {query} on YouTube")
            
        except Exception as e:
            speak("I encountered an issue playing the YouTube video")
    
    async def handle_recipe_request(self, command):
        """Handle recipe requests with step-by-step instructions"""
        try:
            # Extract the dish name from the command
            dish_name = self.extract_dish_name(command)
            
            speak(f"Let me get the recipe for {dish_name} using my local knowledge")
            
            # Get recipe from Ollama
            recipe_prompt = f"""
            Please provide a detailed recipe for {dish_name}. 
            Format your response as exactly 5 clear steps, numbered 1-5.
            Each step should be concise but complete.
            
            Example format:
            1. [First step with ingredients and preparation]
            2. [Second step with cooking instructions]
            3. [Third step with more cooking details]
            4. [Fourth step with final cooking]
            5. [Fifth step with serving/finishing touches]
            
            Make it practical and easy to follow.
            """
            
            recipe_response = await self.get_ollama_response(recipe_prompt)
            
            if recipe_response:
                # Parse the recipe into steps
                self.recipe_steps = self.parse_recipe_steps(recipe_response)
                self.current_recipe = dish_name
                self.current_step = 0
                
                if self.recipe_steps:
                    speak(f"Great! I have a {len(self.recipe_steps)}-step recipe for {dish_name}. Let me start with step 1.")
                    speak(f"Step 1: {self.recipe_steps[0]}")
                    speak("Say 'next' when you're ready for the next step.")
                    self.current_step = 1
                else:
                    speak("I got the recipe but had trouble parsing it into steps. Let me tell you the full recipe.")
                    speak(recipe_response)
            else:
                speak("I'm having trouble getting the recipe right now. Let me search online for you.")
                # Fallback to Google search
                search_query = f"{dish_name} recipe"
                webbrowser.open(f"https://www.google.com/search?q={search_query.replace(' ', '+')}")
                speak(f"I've opened a search for {dish_name} recipe")
                
        except Exception as e:
            speak("I encountered an issue getting the recipe. Let me search online for you.")
            search_query = f"recipe {command}"
            webbrowser.open(f"https://www.google.com/search?q={search_query.replace(' ', '+')}")
    
    def extract_dish_name(self, command):
        """Extract dish name from recipe command"""
        # Remove common recipe words
        words_to_remove = ['tell', 'me', 'the', 'recipe', 'to', 'make', 'how', 'cook', 'prepare', 'for']
        words = command.lower().split()
        
        filtered_words = []
        for word in words:
            if word not in words_to_remove:
                filtered_words.append(word)
        
        return ' '.join(filtered_words) if filtered_words else "dish"
    
    def parse_recipe_steps(self, recipe_text):
        """Parse recipe text into numbered steps"""
        try:
            steps = []
            lines = recipe_text.split('\n')
            
            for line in lines:
                line = line.strip()
                # Look for numbered steps (1., 2., etc.)
                if re.match(r'^\d+\.', line):
                    # Remove the number and period, keep the rest
                    step_text = re.sub(r'^\d+\.\s*', '', line)
                    if step_text:
                        steps.append(step_text)
            
            return steps[:5]  # Limit to 5 steps as requested
            
        except Exception as e:
            return []
    
    async def handle_recipe_next(self):
        """Handle 'next' command during recipe"""
        try:
            if not self.current_recipe or not self.recipe_steps:
                speak("I don't have any recipe steps ready. Please ask for a recipe first.")
                return
            
            if self.current_step >= len(self.recipe_steps):
                speak(f"That's all the steps for {self.current_recipe}! Your dish should be ready. Enjoy your meal!")
                # Reset recipe state
                self.current_recipe = None
                self.recipe_steps = []
                self.current_step = 0
                return
            
            # Speak the next step
            step_number = self.current_step + 1
            speak(f"Step {step_number}: {self.recipe_steps[self.current_step]}")
            
            self.current_step += 1
            
            if self.current_step < len(self.recipe_steps):
                speak("Say 'next' when you're ready for the next step.")
            else:
                speak("That was the final step! Say 'next' to finish.")
                
        except Exception as e:
            speak("I had trouble with the recipe steps. Please ask for the recipe again.")
    
    async def handle_conversation(self, command):
        """Handle general conversation like the original 3 folders"""
        try:
            command_lower = command.lower()
            
            # Greeting responses
            if any(word in command_lower for word in ['hello', 'hi', 'hey']):
                responses = [
                    "Hello there! How are you doing today?",
                    "Hi! Great to hear from you. What can I help you with?",
                    "Hey! I'm here and ready to assist you with anything you need.",
                    "Hello! How's your day going so far?"
                ]
                import random
                speak(random.choice(responses))
            
            # How are you responses
            elif any(phrase in command_lower for phrase in ['how are you', 'how do you feel', 'how are things']):
                responses = [
                    "I'm doing great, thank you for asking! I'm here and ready to help you with anything you need.",
                    "I'm functioning perfectly and feeling quite energetic today! How are you doing?",
                    "I'm excellent, thanks! All my systems are running smoothly. How about you?",
                    "I'm doing wonderful! I love being able to help you. How are you feeling today?"
                ]
                import random
                speak(random.choice(responses))
            
            # Mood support
            elif any(phrase in command_lower for phrase in ['not good', 'sad', 'upset', 'bad mood', 'feeling down', 'depressed']):
                responses = [
                    "I'm sorry to hear you're not feeling well. Is there anything I can do to help cheer you up? Maybe play some music or tell you a joke?",
                    "I understand you're going through a tough time. Remember that it's okay to feel this way, and things will get better. Would you like to talk about it?",
                    "I'm here for you. Sometimes talking helps, or we could do something fun together. What usually makes you feel better?",
                    "I can sense you're not feeling your best. You're important and things will improve. Would you like me to play some uplifting music or help you with something?"
                ]
                import random
                speak(random.choice(responses))
            
            # Happy mood
            elif any(phrase in command_lower for phrase in ['happy', 'great', 'excellent', 'wonderful', 'fantastic', 'good mood']):
                responses = [
                    "That's fantastic to hear! Your positive energy is contagious. What's making you so happy today?",
                    "I'm so glad you're feeling great! It makes me happy too. What can I help you with today?",
                    "Wonderful! I love when you're in a good mood. It brightens my day as well!",
                    "That's amazing! Your happiness is the best part of my day. How can I help you today?"
                ]
                import random
                speak(random.choice(responses))
            
            # Thank you responses
            elif any(phrase in command_lower for phrase in ['thank you', 'thanks', 'appreciate']):
                responses = [
                    "You're very welcome! I'm always happy to help you.",
                    "My pleasure! That's what I'm here for.",
                    "You're most welcome! Anytime you need assistance, just ask.",
                    "It's my joy to help you! Don't hesitate to ask if you need anything else."
                ]
                import random
                speak(random.choice(responses))
            
            # What's your name
            elif any(phrase in command_lower for phrase in ['your name', 'who are you', 'what are you']):
                speak("I'm JARVIS, your personal AI assistant. I'm here to help you with various tasks and have conversations with you!")
            
            # Time and date
            elif any(word in command_lower for word in ['time', 'clock']):
                from datetime import datetime
                current_time = datetime.now().strftime("%I:%M %p")
                speak(f"The current time is {current_time}")
            
            elif any(word in command_lower for word in ['date', 'today']):
                from datetime import datetime
                current_date = datetime.now().strftime("%A, %B %d, %Y")
                speak(f"Today is {current_date}")
            
            # Weather (using AI)
            elif any(word in command_lower for word in ['weather', 'temperature']):
                speak("Let me check the weather for you")
                ai_result = await self.ai_router.process_query(command, "realtime")
                if ai_result['success']:
                    speak(ai_result['response'])
                else:
                    speak("I'm having trouble getting weather information right now")
            
            # General AI conversation using Ollama locally
            else:
                speak("Let me think about that")
                
                # Try Ollama first for local AI response
                ollama_response = await self.get_ollama_response(command)
                
                if ollama_response:
                    # Make response more conversational
                    if len(ollama_response) > 200:
                        # For long responses, summarize and offer to continue
                        short_response = ollama_response[:150] + "... Would you like me to continue with more details?"
                        speak(short_response)
                    else:
                        speak(ollama_response)
                else:
                    # Fallback to online AI if Ollama is not available
                    ai_result = await self.ai_router.process_query(command, "general")
                    
                    if ai_result['success']:
                        response = ai_result['response']
                        if len(response) > 200:
                            short_response = response[:150] + "... Would you like me to continue with more details?"
                            speak(short_response)
                        else:
                            speak(response)
                    else:
                        speak("I'm not sure about that, but I'm always learning! Is there something else I can help you with?")
                    
        except Exception as e:
            speak("I'm having a bit of trouble processing that, but I'm here to help with whatever you need!")
    
    async def get_ollama_response(self, query):
        """Get response from Ollama local AI (5GB model or smaller)"""
        try:
            import requests
            import json
            
            # Check if Ollama is running
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=2)
                if response.status_code != 200:
                    return None
            except:
                return None
            
            # Use a small model (under 5GB) - try llama3.2:3b or phi3:mini
            models_to_try = ["llama3.2:3b", "phi3:mini", "gemma2:2b", "qwen2:1.5b"]
            
            for model in models_to_try:
                try:
                    # Make request to Ollama
                    ollama_data = {
                        "model": model,
                        "prompt": f"Answer this question briefly and conversationally: {query}",
                        "stream": False
                    }
                    
                    response = requests.post(
                        "http://localhost:11434/api/generate",
                        json=ollama_data,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if 'response' in result:
                            return result['response'].strip()
                except:
                    continue
            
            return None
            
        except Exception as e:
            return None
    
    async def handle_pdf_reading(self, command):
        """Handle PDF reading requests"""
        try:
            # Extract PDF name from command
            pdf_name = self.extract_pdf_name(command)
            if not pdf_name:
                speak("Please tell me the name of the PDF you want me to read")
                return
            
            speak(f"Looking for PDF named {pdf_name}")
            
            # Use PDF reader to read the file
            success = self.pdf_reader.read_pdf_aloud(pdf_name)
            
            if not success:
                speak(f"I couldn't find or read the PDF named {pdf_name}. Please check if the file exists in your Documents, Desktop, or Downloads folder")
                
        except Exception as e:
            print(f"❌ Error reading PDF: {e}")
            speak("I encountered an error while trying to read the PDF")
    
    def extract_pdf_name(self, command):
        """Extract PDF name from command"""
        try:
            # Common patterns for PDF reading commands
            patterns = [
                r"pdf named? (.+?)(?:\s+from|\s+and|\s*$)",
                r"read (.+?)\.pdf",
                r"open (.+?)\.pdf",
                r"file (.+?)(?:\s+and|\s*$)"
            ]
            
            command_lower = command.lower()
            
            for pattern in patterns:
                import re
                match = re.search(pattern, command_lower)
                if match:
                    pdf_name = match.group(1).strip()
                    # Clean up common words
                    pdf_name = pdf_name.replace("the ", "").replace("a ", "").replace("an ", "")
                    return pdf_name
            
            # Fallback: look for words after "pdf" or "file"
            words = command_lower.split()
            for i, word in enumerate(words):
                if word in ['pdf', 'file'] and i + 1 < len(words):
                    if words[i + 1] not in ['named', 'called', 'from']:
                        return words[i + 1]
                elif word == 'named' and i + 1 < len(words):
                    return words[i + 1]
            
            return None
            
        except Exception as e:
            print(f"❌ Error extracting PDF name: {e}")
            return None
    
    async def handle_email_reading(self):
        """Handle email reading requests"""
        try:
            print("📧 Processing email reading request...")
            
            if not self.gmail_service:
                speak("Email service is not available. Please check your Gmail setup.")
                return
            
            # Fetch unread emails
            emails = self.fetch_unread_emails(5)
            
            if not emails:
                speak("You have no unread emails at the moment sir.")
                return
            
            # Generate summary with Ollama
            summary = self.summarize_emails_with_ollama(emails)
            
            # Clean and speak the summary
            clean_summary = self.clean_text_for_speech(summary)
            speak(clean_summary)
            
            # Save digest to file
            self.save_email_digest(emails, summary)
            
            print("✅ Email reading completed successfully")
                
        except Exception as e:
            print(f"❌ Error reading emails: {e}")
            speak("I encountered an error while trying to read your emails. Please try again later.")
    
    def fetch_unread_emails(self, max_results=5):
        """Fetch top unread emails"""
        try:
            print(f"📬 Fetching top {max_results} unread emails...")
            
            result = self.gmail_service.users().messages().list(
                userId='me', 
                q='is:unread', 
                maxResults=max_results
            ).execute()
            
            messages = result.get('messages', [])
            if not messages:
                return []
            
            email_list = []
            for i, msg in enumerate(messages, 1):
                print(f"📖 Reading email {i}/{len(messages)}...")
                
                msg_data = self.gmail_service.users().messages().get(
                    userId='me', 
                    id=msg['id'], 
                    format='full'
                ).execute()
                
                email_data = self.extract_email_data(msg_data)
                if email_data:
                    email_list.append(email_data)
            
            print(f"✅ Successfully processed {len(email_list)} emails")
            return email_list
            
        except Exception as e:
            print(f"❌ Error fetching emails: {e}")
            return []
    
    def extract_email_data(self, msg_data):
        """Extract subject and body from email message"""
        try:
            payload = msg_data['payload']
            headers = payload.get('headers', [])
            
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
            
            body = self.get_email_body(payload)
            
            return {
                'subject': subject,
                'sender': sender,
                'body': body[:1000]
            }
            
        except Exception as e:
            print(f"❌ Error extracting email data: {e}")
            return None
    
    def get_email_body(self, payload):
        """Extract plain text body from email payload"""
        try:
            body = ""
            
            if 'body' in payload and 'data' in payload['body']:
                body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
            elif 'parts' in payload:
                for part in payload['parts']:
                    if part.get('mimeType') == 'text/plain' and 'data' in part.get('body', {}):
                        body += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                    elif 'parts' in part:
                        body += self.get_email_body(part)
            
            return body.strip()
            
        except Exception as e:
            print(f"❌ Error extracting body: {e}")
            return ""
    
    def summarize_emails_with_ollama(self, emails):
        """Summarize emails using Ollama"""
        try:
            print("🧠 Generating summary with Ollama...")
            
            email_content = ""
            for i, email in enumerate(emails, 1):
                email_content += f"\nEMAIL {i}:\n"
                email_content += f"From: {email['sender']}\n"
                email_content += f"Subject: {email['subject']}\n"
                email_content += f"Content: {email['body'][:300]}...\n"
                email_content += "-" * 50 + "\n"
            
            prompt = f"""You are my personal AI assistant who manages my unread emails. I will provide you with around 5 unread emails. Your task:

1. Read all emails and figure out which one is the MOST IMPORTANT or URGENT for me.
   - Look for deadlines, opportunities, or reminders.
   - Talk to me directly, like: "⚠️ Hey, this one looks urgent. You should take action before the deadline on Sept 15."
   - Give advice, encouragement, or urgency context, not just dry summary.

2. After highlighting the most important email, give me a conversational digest of the remaining ones.
   - Example: "The other emails are mostly promotional: LinkedIn is inviting you to an event, DevNetwork is sharing an update, nothing too urgent."

3. The tone should feel like a **proactive personal assistant**:
   - Supportive, conversational, motivating.
   - Not just summarizing, but guiding: "I recommend you focus on this first," or "This seems like a great opportunity, worth checking out."

4. Structure your response like this:
   - 🎯 Priority Alert (the most important email, explained in a personal way, with advice)
   - 📨 Quick Rundown (other emails in a friendly, casual summary)

Keep it natural, as if you're speaking to me directly.

Here are my {len(emails)} unread emails:

{email_content}"""

            response = requests.post(
                f'{self.ollama_url}/api/generate',
                json={
                    'model': self.ollama_model,
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        'temperature': 0.7,
                        'max_tokens': 500
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                summary = result.get('response', '').strip()
                
                if summary:
                    print("✅ Summary generated successfully")
                    return summary
                else:
                    return self.generate_fallback_summary(emails)
            else:
                print(f"❌ Ollama API error: {response.status_code}")
                return self.generate_fallback_summary(emails)
                
        except Exception as e:
            print(f"❌ Ollama summarization error: {e}")
            return self.generate_fallback_summary(emails)
    
    def generate_fallback_summary(self, emails):
        """Generate a simple fallback summary without AI"""
        summary = f"You have {len(emails)} unread emails. "
        
        for i, email in enumerate(emails[:3], 1):
            sender_name = email['sender'].split('<')[0].strip().replace('"', '')
            summary += f"Email {i}: {email['subject']} from {sender_name}. "
        
        if len(emails) > 3:
            summary += f"And {len(emails) - 3} more emails."
        
        return summary
    
    def clean_text_for_speech(self, text):
        """Clean text for better speech output"""
        try:
            clean_text = text.replace("**", "")
            clean_text = clean_text.replace("*", "")
            clean_text = clean_text.replace("#", "")
            clean_text = clean_text.replace("- ", "")
            clean_text = clean_text.replace("  ", " ")
            clean_text = clean_text.replace("&", "and")
            clean_text = clean_text.replace("@", "at")
            clean_text = clean_text.replace("etc.", "etcetera")
            
            return clean_text.strip()
            
        except Exception as e:
            print(f"❌ Text cleaning error: {e}")
            return text
    
    def save_email_digest(self, emails, summary):
        """Save detailed email digest to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"jarvis_email_digest_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("JARVIS EMAIL DIGEST\n")
                f.write("=" * 60 + "\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Unread Emails: {len(emails)}\n\n")
                
                f.write("SUMMARY:\n")
                f.write("-" * 20 + "\n")
                f.write(summary + "\n\n")
                
                f.write("DETAILED EMAIL LIST:\n")
                f.write("-" * 30 + "\n")
                
                for i, email in enumerate(emails, 1):
                    f.write(f"\nEMAIL {i}:\n")
                    f.write(f"From: {email['sender']}\n")
                    f.write(f"Subject: {email['subject']}\n")
                    f.write(f"Preview: {email['body'][:200]}...\n")
                    f.write("-" * 40 + "\n")
            
            print(f"💾 Email digest saved to: {filename}")
            
        except Exception as e:
            print(f"❌ Error saving digest: {e}")
    
    async def handle_screen_description(self):
        """Handle screen description requests"""
        try:
            # Use screen analyzer to describe the screen
            success = self.screen_analyzer.describe_screen()
            
            if not success:
                speak("I'm having trouble analyzing your screen right now. Please try again in a moment")
                
        except Exception as e:
            print(f"❌ Error describing screen: {e}")
            speak("I encountered an error while analyzing your screen")

    async def start_listening(self):
        """Main listening loop"""
        print("\n🎙️ JARVIS Voice Assistant Active")
        print("Say anything naturally - I'll understand!")
        print("Available tasks: YouTube, Google, Notepad, Call Tom, Message Tom, WhatsApp Tom, Volume, Brightness")
        print("Meeting Assistant: 'Jarvis attend the meeting for me' | 'Jarvis you can leave the meeting'")
        print("Say 'JARVIS stop' to exit")
        
        # Show Tom's contact
        tom_contact = self.db_manager.get_contact("Tom")
        if tom_contact:
            print(f"📞 Tom's contact: {tom_contact['mobile_no']}")
        
        while True:
            try:
                command = self.listen_for_command()
                
                if command:
                    if any(word in command.lower() for word in ['stop', 'quit', 'exit', 'goodbye']):
                        speak("Goodbye! JARVIS shutting down")
                        break
                    
                    # Process any natural command
                    await self.understand_and_execute(command)
                
            except KeyboardInterrupt:
                print("\n👋 JARVIS shutting down...")
                speak("JARVIS shutting down")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(1)

# Start JARVIS immediately
async def main():
    jarvis = FinalJarvis()
    await jarvis.start_listening()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()