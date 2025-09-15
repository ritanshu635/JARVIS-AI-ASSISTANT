"""
Windows System Audio Capture for Meeting Assistant
Captures both microphone and system audio (Google Meet audio)
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

class SystemAudioCapture:
    def __init__(self):
        self.is_recording = False
        self.audio_data = []
        self.rate = 44100
        self.channels = 2
        self.recording_thread = None
        self.use_sounddevice = SOUNDDEVICE_AVAILABLE
        
        if not SOUNDDEVICE_AVAILABLE and not PYAUDIO_AVAILABLE:
            raise ImportError("Neither sounddevice nor pyaudio is available")
        
        self.setup_audio()
    
    def setup_audio(self):
        """Setup audio capture method"""
        if self.use_sounddevice:
            self.setup_sounddevice()
        else:
            self.setup_pyaudio()
    
    def setup_sounddevice(self):
        """Setup sounddevice for audio capture"""
        try:
            # List all devices for debugging
            devices = sd.query_devices()
            print("\nAvailable audio devices:")
            
            # Look for system audio devices (Stereo Mix, WASAPI loopback, etc.)
            system_audio_devices = []
            
            for i, device in enumerate(devices):
                device_name = device['name'].lower()
                print(f"  {i}: {device['name']} - Inputs: {device['max_input_channels']}")
                
                # Look for system audio capture devices
                if device['max_input_channels'] > 0:
                    if any(keyword in device_name for keyword in [
                        'stereo mix', 'what u hear', 'wave out mix', 'sum', 
                        'loopback', 'speakers', 'output'
                    ]):
                        system_audio_devices.append((i, device))
                        print(f"  🎯 Found system audio device: {device['name']}")
            
            # Try to use system audio device
            if system_audio_devices:
                # Use the first system audio device found
                self.input_device, device_info = system_audio_devices[0]
                print(f"✅ Using system audio: {device_info['name']}")
                print("📢 This will capture ONLY Google Meet audio (no microphone)")
            else:
                # Fallback: try to use Stereo Mix by index (19 from your system)
                if len(devices) > 19 and 'stereo mix' in devices[19]['name'].lower():
                    self.input_device = 19
                    print(f"✅ Using Stereo Mix (index 19): {devices[19]['name']}")
                    print("📢 This will capture desktop audio from Google Meet")
                else:
                    # Last resort: use default but warn user
                    self.input_device = None
                    print("⚠️ No system audio device found. Using default input.")
                    print("⚠️ You may need to enable Stereo Mix in Windows Sound settings.")
            
        except Exception as e:
            print(f"Sounddevice setup error: {e}")
            self.use_sounddevice = False
            if PYAUDIO_AVAILABLE:
                self.setup_pyaudio()
    
    def setup_pyaudio(self):
        """Setup pyaudio for audio capture"""
        try:
            self.audio = pyaudio.PyAudio()
            self.format = pyaudio.paInt16
            self.chunk = 1024
            
            # List audio devices
            print("\nAvailable PyAudio devices:")
            for i in range(self.audio.get_device_count()):
                info = self.audio.get_device_info_by_index(i)
                if info['maxInputChannels'] > 0:
                    print(f"  {i}: {info['name']}")
            
        except Exception as e:
            print(f"PyAudio setup error: {e}")
    
    def start_recording(self):
        """Start recording system audio"""
        if self.is_recording:
            return False, "Already recording!"
        
        try:
            self.audio_data = []
            self.is_recording = True
            
            if self.use_sounddevice:
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
                if self.is_recording:
                    self.audio_data.append(indata.copy())
            
            with sd.InputStream(
                samplerate=self.rate,
                channels=self.channels,
                device=self.input_device,
                callback=callback
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
                    if self.channels == 2:
                        audio_np = audio_np.reshape(-1, 2)
                    else:
                        audio_np = audio_np.reshape(-1, 1)
                    
                    # Convert to float32 for consistency
                    audio_float = audio_np.astype(np.float32) / 32768.0
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
            return audio_array, "Recording stopped successfully"
            
        except Exception as e:
            return None, f"Error processing audio data: {str(e)}"
    
    def save_audio(self, audio_array, filename):
        """Save audio array to file"""
        try:
            if self.use_sounddevice and SOUNDDEVICE_AVAILABLE:
                sf.write(filename, audio_array, self.rate)
            else:
                # Use wave module for pyaudio
                with wave.open(filename, 'wb') as wf:
                    wf.setnchannels(self.channels)
                    wf.setsampwidth(2)  # 16-bit
                    wf.setframerate(self.rate)
                    
                    # Convert float32 back to int16
                    audio_int16 = (audio_array * 32767).astype(np.int16)
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
def test_system_audio():
    """Test system audio capture"""
    print("🎤 Testing System Audio Capture")
    print("=" * 40)
    
    try:
        capture = SystemAudioCapture()
        
        print("Starting 5-second recording test...")
        success, message = capture.start_recording()
        
        if success:
            print(f"✅ {message}")
            time.sleep(5)
            
            audio_data, stop_message = capture.stop_recording()
            print(f"✅ {stop_message}")
            
            if audio_data is not None:
                # Save test file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"test_audio_{timestamp}.wav"
                
                save_success, save_message = capture.save_audio(audio_data, filename)
                print(f"{'✅' if save_success else '❌'} {save_message}")
                
                if save_success:
                    print(f"📁 Test audio saved as: {filename}")
                    print(f"📊 Audio shape: {audio_data.shape}")
                    print(f"📊 Duration: {len(audio_data) / capture.rate:.2f} seconds")
            else:
                print("❌ No audio data captured")
        else:
            print(f"❌ {message}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_system_audio()