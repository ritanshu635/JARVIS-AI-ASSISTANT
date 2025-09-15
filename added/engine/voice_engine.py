import os
import time
import threading
import queue
import numpy as np
import pyaudio
import pyttsx3
import whisper
import pvporcupine
import struct
from typing import Optional, Callable, Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

class VoiceEngine:
    """Handles all voice-related functionality including STT, TTS, and wake word detection"""
    
    def __init__(self):
        # Configuration
        self.whisper_model_name = os.getenv('WHISPER_MODEL', 'base')
        self.tts_rate = int(os.getenv('TTS_RATE', '174'))
        self.tts_voice = int(os.getenv('TTS_VOICE', '0'))
        
        # Audio settings
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.audio_format = pyaudio.paInt16
        self.channels = 1
        
        # State management
        self.is_listening = False
        self.is_speaking = False
        self.wake_word_active = False
        self.audio_queue = queue.Queue()
        
        # Components
        self.whisper_model = None
        self.tts_engine = None
        self.porcupine = None
        self.pyaudio_instance = None
        self.audio_stream = None
        
        # Callbacks
        self.on_wake_word_detected = None
        self.on_speech_recognized = None
        self.on_listening_started = None
        self.on_listening_stopped = None
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all voice components"""
        try:
            # Initialize Whisper
            print(f"🎤 Loading Whisper model: {self.whisper_model_name}")
            self.whisper_model = whisper.load_model(self.whisper_model_name)
            print("✅ Whisper model loaded successfully")
            
            # Initialize TTS
            self.tts_engine = pyttsx3.init('sapi5')  # Windows SAPI
            voices = self.tts_engine.getProperty('voices')
            if voices and len(voices) > self.tts_voice:
                self.tts_engine.setProperty('voice', voices[self.tts_voice].id)
            self.tts_engine.setProperty('rate', self.tts_rate)
            print("✅ TTS engine initialized")
            
            # Initialize PyAudio
            self.pyaudio_instance = pyaudio.PyAudio()
            print("✅ PyAudio initialized")
            
            # Initialize Porcupine for wake word detection
            try:
                self.porcupine = pvporcupine.create(keywords=["jarvis", "alexa"])
                print("✅ Porcupine wake word detection initialized")
            except Exception as e:
                print(f"⚠️ Porcupine initialization failed: {e}")
                self.porcupine = None
            
        except Exception as e:
            print(f"❌ Voice engine initialization error: {e}")
    
    def set_callbacks(self, 
                     on_wake_word_detected: Optional[Callable] = None,
                     on_speech_recognized: Optional[Callable] = None,
                     on_listening_started: Optional[Callable] = None,
                     on_listening_stopped: Optional[Callable] = None):
        """Set callback functions for voice events"""
        self.on_wake_word_detected = on_wake_word_detected
        self.on_speech_recognized = on_speech_recognized
        self.on_listening_started = on_listening_started
        self.on_listening_stopped = on_listening_stopped
    
    def start_wake_word_detection(self):
        """Start continuous wake word detection"""
        if not self.porcupine:
            print("⚠️ Wake word detection not available")
            return False
        
        self.wake_word_active = True
        wake_word_thread = threading.Thread(target=self._wake_word_loop, daemon=True)
        wake_word_thread.start()
        print("🎧 Wake word detection started")
        return True
    
    def stop_wake_word_detection(self):
        """Stop wake word detection"""
        self.wake_word_active = False
        print("🔇 Wake word detection stopped")
    
    def _wake_word_loop(self):
        """Continuous wake word detection loop"""
        try:
            audio_stream = self.pyaudio_instance.open(
                rate=self.porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.porcupine.frame_length
            )
            
            while self.wake_word_active:
                try:
                    pcm = audio_stream.read(self.porcupine.frame_length, exception_on_overflow=False)
                    pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
                    
                    keyword_index = self.porcupine.process(pcm)
                    
                    if keyword_index >= 0:
                        print("🎯 Wake word detected!")
                        if self.on_wake_word_detected:
                            self.on_wake_word_detected()
                        
                        # Start listening for command
                        self.start_listening()
                        
                except Exception as e:
                    if self.wake_word_active:  # Only log if we're still supposed to be active
                        print(f"Wake word detection error: {e}")
                    break
            
            audio_stream.close()
            
        except Exception as e:
            print(f"❌ Wake word loop error: {e}")
    
    def start_listening(self, duration: int = 5):
        """Start listening for speech input"""
        if self.is_listening or self.is_speaking:
            return False
        
        self.is_listening = True
        if self.on_listening_started:
            self.on_listening_started()
        
        # Start listening in a separate thread
        listen_thread = threading.Thread(
            target=self._listen_for_speech, 
            args=(duration,), 
            daemon=True
        )
        listen_thread.start()
        return True
    
    def stop_listening(self):
        """Stop listening for speech input"""
        self.is_listening = False
        if self.on_listening_stopped:
            self.on_listening_stopped()
    
    def _listen_for_speech(self, duration: int):
        """Listen for speech and convert to text"""
        try:
            print(f"🎤 Listening for {duration} seconds...")
            
            # Record audio
            audio_data = self._record_audio(duration)
            
            if audio_data is not None and len(audio_data) > 0:
                # Convert to text using Whisper
                text = self._speech_to_text(audio_data)
                
                if text and text.strip():
                    print(f"🗣️ Recognized: {text}")
                    if self.on_speech_recognized:
                        self.on_speech_recognized(text.strip())
                else:
                    print("🔇 No speech detected")
            else:
                print("🔇 No audio recorded")
                
        except Exception as e:
            print(f"❌ Speech listening error: {e}")
        finally:
            self.is_listening = False
            if self.on_listening_stopped:
                self.on_listening_stopped()
    
    def _record_audio(self, duration: int) -> Optional[np.ndarray]:
        """Record audio for specified duration"""
        try:
            audio_stream = self.pyaudio_instance.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            frames = []
            frames_to_record = int(self.sample_rate / self.chunk_size * duration)
            
            for _ in range(frames_to_record):
                if not self.is_listening:
                    break
                try:
                    data = audio_stream.read(self.chunk_size, exception_on_overflow=False)
                    frames.append(data)
                except Exception as e:
                    print(f"Audio recording error: {e}")
                    break
            
            audio_stream.close()
            
            if frames:
                # Convert to numpy array
                audio_data = b''.join(frames)
                audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
                return audio_np
            
            return None
            
        except Exception as e:
            print(f"❌ Audio recording error: {e}")
            return None
    
    def _speech_to_text(self, audio_data: np.ndarray) -> Optional[str]:
        """Convert audio data to text using Whisper"""
        try:
            if self.whisper_model is None:
                print("❌ Whisper model not loaded")
                return None
            
            # Use Whisper to transcribe
            result = self.whisper_model.transcribe(
                audio_data,
                language='en',
                task='transcribe',
                fp16=False  # Use fp32 for better compatibility
            )
            
            text = result.get('text', '').strip()
            return text if text else None
            
        except Exception as e:
            print(f"❌ Speech-to-text error: {e}")
            return None
    
    def speak(self, text: str, interrupt: bool = True):
        """Convert text to speech"""
        if not text or not text.strip():
            return False
        
        if interrupt and self.is_speaking:
            self.stop_speaking()
        
        # Start speaking in a separate thread
        speak_thread = threading.Thread(
            target=self._text_to_speech, 
            args=(text.strip(),), 
            daemon=True
        )
        speak_thread.start()
        return True
    
    def _text_to_speech(self, text: str):
        """Convert text to speech using pyttsx3"""
        try:
            self.is_speaking = True
            print(f"🔊 Speaking: {text}")
            
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            
        except Exception as e:
            print(f"❌ Text-to-speech error: {e}")
        finally:
            self.is_speaking = False
    
    def stop_speaking(self):
        """Stop current speech"""
        try:
            if self.tts_engine and self.is_speaking:
                self.tts_engine.stop()
                self.is_speaking = False
        except Exception as e:
            print(f"❌ Stop speaking error: {e}")
    
    def set_voice_properties(self, rate: Optional[int] = None, 
                           voice_index: Optional[int] = None,
                           volume: Optional[float] = None):
        """Set TTS voice properties"""
        try:
            if rate is not None:
                self.tts_engine.setProperty('rate', rate)
                self.tts_rate = rate
            
            if voice_index is not None:
                voices = self.tts_engine.getProperty('voices')
                if voices and 0 <= voice_index < len(voices):
                    self.tts_engine.setProperty('voice', voices[voice_index].id)
                    self.tts_voice = voice_index
            
            if volume is not None:
                self.tts_engine.setProperty('volume', max(0.0, min(1.0, volume)))
            
            print("✅ Voice properties updated")
            return True
            
        except Exception as e:
            print(f"❌ Voice properties error: {e}")
            return False
    
    def get_available_voices(self) -> List[Dict[str, Any]]:
        """Get list of available TTS voices"""
        try:
            voices = self.tts_engine.getProperty('voices')
            voice_list = []
            
            for i, voice in enumerate(voices):
                voice_info = {
                    'index': i,
                    'id': voice.id,
                    'name': voice.name,
                    'languages': getattr(voice, 'languages', []),
                    'gender': getattr(voice, 'gender', 'unknown'),
                    'age': getattr(voice, 'age', 'unknown')
                }
                voice_list.append(voice_info)
            
            return voice_list
            
        except Exception as e:
            print(f"❌ Get voices error: {e}")
            return []
    
    def test_microphone(self) -> bool:
        """Test microphone functionality"""
        try:
            print("🎤 Testing microphone...")
            
            # Record 2 seconds of audio
            audio_data = self._record_audio(2)
            
            if audio_data is not None and len(audio_data) > 0:
                # Check if there's actual audio (not just silence)
                audio_level = np.max(np.abs(audio_data))
                if audio_level > 0.01:  # Threshold for detecting sound
                    print(f"✅ Microphone working - Audio level: {audio_level:.3f}")
                    return True
                else:
                    print("⚠️ Microphone detected but no sound input")
                    return False
            else:
                print("❌ No audio data recorded")
                return False
                
        except Exception as e:
            print(f"❌ Microphone test error: {e}")
            return False
    
    def test_speakers(self) -> bool:
        """Test speaker functionality"""
        try:
            print("🔊 Testing speakers...")
            test_text = "Testing speakers. Can you hear me?"
            self.speak(test_text)
            return True
        except Exception as e:
            print(f"❌ Speaker test error: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current voice engine status"""
        return {
            'whisper_model': self.whisper_model_name,
            'whisper_loaded': self.whisper_model is not None,
            'tts_initialized': self.tts_engine is not None,
            'porcupine_available': self.porcupine is not None,
            'is_listening': self.is_listening,
            'is_speaking': self.is_speaking,
            'wake_word_active': self.wake_word_active,
            'tts_rate': self.tts_rate,
            'tts_voice': self.tts_voice
        }
    
    def cleanup(self):
        """Clean up resources"""
        try:
            self.stop_wake_word_detection()
            self.stop_listening()
            self.stop_speaking()
            
            if self.audio_stream:
                self.audio_stream.close()
            
            if self.porcupine:
                self.porcupine.delete()
            
            if self.pyaudio_instance:
                self.pyaudio_instance.terminate()
            
            print("🧹 Voice engine cleaned up")
            
        except Exception as e:
            print(f"❌ Cleanup error: {e}")

# Test the Voice Engine
if __name__ == "__main__":
    import time
    
    def on_wake_word():
        print("🎯 Wake word callback triggered!")
    
    def on_speech(text):
        print(f"🗣️ Speech callback: {text}")
    
    def on_listening_start():
        print("🎤 Listening started callback")
    
    def on_listening_stop():
        print("🔇 Listening stopped callback")
    
    # Test the voice engine
    voice_engine = VoiceEngine()
    
    # Set callbacks
    voice_engine.set_callbacks(
        on_wake_word_detected=on_wake_word,
        on_speech_recognized=on_speech,
        on_listening_started=on_listening_start,
        on_listening_stopped=on_listening_stop
    )
    
    # Test components
    print("\n🧪 Testing Voice Engine Components:")
    print(f"Status: {voice_engine.get_status()}")
    
    # Test microphone
    voice_engine.test_microphone()
    
    # Test speakers
    voice_engine.test_speakers()
    
    # Test wake word detection
    print("\n🎧 Starting wake word detection (say 'jarvis' or 'alexa')...")
    voice_engine.start_wake_word_detection()
    
    try:
        # Keep running for 30 seconds
        time.sleep(30)
    except KeyboardInterrupt:
        print("\n⏹️ Stopping...")
    
    # Cleanup
    voice_engine.cleanup()