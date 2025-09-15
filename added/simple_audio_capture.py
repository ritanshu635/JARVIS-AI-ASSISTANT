"""
Simple Audio Capture for Meeting Assistant
Focuses on reliable microphone recording first
"""

import os
import time
import threading
import wave
import numpy as np
from datetime import datetime

try:
    import sounddevice as sd
    import soundfile as sf
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False

class SimpleAudioCapture:
    def __init__(self):
        self.is_recording = False
        self.audio_data = []
        self.rate = 44100
        self.channels = 1  # Start with mono for simplicity
        self.recording_thread = None
        
        # Choose the best available method
        if SOUNDDEVICE_AVAILABLE:
            self.method = "sounddevice"
            self.setup_sounddevice()
        elif PYAUDIO_AVAILABLE:
            self.method = "pyaudio"
            self.setup_pyaudio()
        else:
            raise ImportError("No audio library available")
    
    def setup_sounddevice(self):
        """Setup sounddevice - simple and reliable"""
        try:
            # Get default input device
            default_device = sd.query_devices(kind='input')
            print(f"🎤 Using microphone: {default_device['name']}")
            
            # Use default input device
            self.input_device = None  # None means use default
            
        except Exception as e:
            print(f"Sounddevice setup error: {e}")
            if PYAUDIO_AVAILABLE:
                self.method = "pyaudio"
                self.setup_pyaudio()
            else:
                raise
    
    def setup_pyaudio(self):
        """Setup pyaudio as fallback"""
        try:
            self.audio = pyaudio.PyAudio()
            self.format = pyaudio.paInt16
            self.chunk = 1024
            
            # Get default input device info
            default_input = self.audio.get_default_input_device_info()
            print(f"🎤 Using microphone: {default_input['name']}")
            
        except Exception as e:
            print(f"PyAudio setup error: {e}")
            raise
    
    def start_recording(self):
        """Start recording audio"""
        if self.is_recording:
            return False, "Already recording!"
        
        try:
            self.audio_data = []
            self.is_recording = True
            
            print(f"🎙️ Starting recording with {self.method}...")
            
            if self.method == "sounddevice":
                self.recording_thread = threading.Thread(target=self._record_sounddevice)
            else:
                self.recording_thread = threading.Thread(target=self._record_pyaudio)
            
            self.recording_thread.daemon = True
            self.recording_thread.start()
            
            return True, "Recording started successfully"
            
        except Exception as e:
            self.is_recording = False
            return False, f"Error starting recording: {str(e)}"
    
    def _record_sounddevice(self):
        """Record using sounddevice"""
        try:
            def callback(indata, frames, time, status):
                if self.is_recording and status.input_underflow == False:
                    self.audio_data.append(indata.copy())
            
            with sd.InputStream(
                samplerate=self.rate,
                channels=self.channels,
                device=self.input_device,
                callback=callback,
                dtype=np.float32
            ):
                while self.is_recording:
                    time.sleep(0.1)
                    
        except Exception as e:
            print(f"Sounddevice recording error: {e}")
            self.is_recording = False
    
    def _record_pyaudio(self):
        """Record using pyaudio"""
        try:
            stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            
            while self.is_recording:
                try:
                    data = stream.read(self.chunk, exception_on_overflow=False)
                    # Convert to numpy array
                    audio_np = np.frombuffer(data, dtype=np.int16)
                    # Convert to float32 for consistency
                    audio_float = audio_np.astype(np.float32) / 32768.0
                    
                    if self.channels == 1:
                        audio_float = audio_float.reshape(-1, 1)
                    
                    self.audio_data.append(audio_float)
                    
                except Exception as e:
                    print(f"PyAudio read error: {e}")
                    break
            
            stream.stop_stream()
            stream.close()
            
        except Exception as e:
            print(f"PyAudio recording error: {e}")
            self.is_recording = False
    
    def stop_recording(self):
        """Stop recording and return audio data"""
        if not self.is_recording:
            return None, "Not currently recording"
        
        self.is_recording = False
        
        # Wait for recording thread to finish
        if self.recording_thread:
            self.recording_thread.join(timeout=3)
        
        if not self.audio_data:
            return None, "No audio data recorded"
        
        try:
            # Combine all audio chunks
            audio_array = np.concatenate(self.audio_data, axis=0)
            
            # Ensure it's the right shape
            if len(audio_array.shape) == 1:
                audio_array = audio_array.reshape(-1, 1)
            
            return audio_array, "Recording stopped successfully"
            
        except Exception as e:
            return None, f"Error processing audio data: {str(e)}"
    
    def save_audio(self, audio_array, filename):
        """Save audio array to file"""
        try:
            if self.method == "sounddevice" and SOUNDDEVICE_AVAILABLE:
                sf.write(filename, audio_array, self.rate)
            else:
                # Use wave module
                with wave.open(filename, 'wb') as wf:
                    wf.setnchannels(self.channels)
                    wf.setsampwidth(2)  # 16-bit
                    wf.setframerate(self.rate)
                    
                    # Convert float32 to int16
                    if audio_array.dtype == np.float32:
                        audio_int16 = (audio_array * 32767).astype(np.int16)
                    else:
                        audio_int16 = audio_array.astype(np.int16)
                    
                    wf.writeframes(audio_int16.tobytes())
            
            return True, f"Audio saved to {filename}"
            
        except Exception as e:
            return False, f"Error saving audio: {str(e)}"
    
    def __del__(self):
        """Cleanup"""
        if self.is_recording:
            self.stop_recording()
        
        if hasattr(self, 'audio') and self.audio:
            self.audio.terminate()

# Test function
def test_simple_audio():
    """Test simple audio capture"""
    print("🎤 Testing Simple Audio Capture")
    print("=" * 40)
    
    try:
        capture = SimpleAudioCapture()
        
        print("Starting 5-second recording test...")
        print("🗣️ Say something during the recording!")
        
        success, message = capture.start_recording()
        
        if success:
            print(f"✅ {message}")
            
            # Record for 5 seconds
            for i in range(5, 0, -1):
                print(f"   Recording... {i} seconds remaining")
                time.sleep(1)
            
            audio_data, stop_message = capture.stop_recording()
            print(f"✅ {stop_message}")
            
            if audio_data is not None:
                # Save test file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"simple_test_{timestamp}.wav"
                
                save_success, save_message = capture.save_audio(audio_data, filename)
                print(f"{'✅' if save_success else '❌'} {save_message}")
                
                if save_success:
                    print(f"📁 Test audio saved as: {filename}")
                    print(f"📊 Audio shape: {audio_data.shape}")
                    print(f"📊 Duration: {len(audio_data) / capture.rate:.2f} seconds")
                    
                    # Check audio levels
                    max_amplitude = np.max(np.abs(audio_data))
                    print(f"📊 Max amplitude: {max_amplitude:.4f}")
                    
                    if max_amplitude > 0.01:
                        print("✅ Good audio levels detected!")
                    else:
                        print("⚠️ Low audio levels - speak louder or check microphone")
            else:
                print("❌ No audio data captured")
        else:
            print(f"❌ {message}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_simple_audio()