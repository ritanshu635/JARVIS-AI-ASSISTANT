"""
Windows Desktop Audio Capture using WASAPI Loopback
Captures ONLY the audio coming from speakers/desktop (Google Meet participants)
No microphone input - perfect for meeting transcription
"""

import os
import time
import threading
import wave
import numpy as np
from datetime import datetime

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False

try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False

class WindowsDesktopAudio:
    def __init__(self):
        self.is_recording = False
        self.audio_data = []
        self.rate = 44100
        self.channels = 2
        self.recording_thread = None
        
        # Try different methods to capture desktop audio
        self.capture_method = self.find_best_capture_method()
        
    def find_best_capture_method(self):
        """Find the best method to capture desktop audio on Windows"""
        print("🔍 Searching for desktop audio capture method...")
        
        if SOUNDDEVICE_AVAILABLE:
            return self.setup_sounddevice_loopback()
        elif PYAUDIO_AVAILABLE:
            return self.setup_pyaudio_stereo_mix()
        else:
            raise ImportError("No audio libraries available")
    
    def setup_sounddevice_loopback(self):
        """Try to setup sounddevice with WASAPI loopback"""
        try:
            # Check if we can use WASAPI
            hostapis = sd.query_hostapis()
            wasapi_index = None
            
            for i, api in enumerate(hostapis):
                if 'WASAPI' in api['name']:
                    wasapi_index = i
                    print(f"✅ Found WASAPI: {api['name']}")
                    break
            
            if wasapi_index is not None:
                # Try to find loopback device
                devices = sd.query_devices()
                
                for i, device in enumerate(devices):
                    device_name = device['name'].lower()
                    
                    # Look for output devices that can be used as loopback
                    if (device['max_output_channels'] > 0 and 
                        device['hostapi'] == wasapi_index and
                        ('speakers' in device_name or 'headphones' in device_name or 'output' in device_name)):
                        
                        print(f"🎯 Found potential loopback device: {device['name']}")
                        self.loopback_device = i
                        return "sounddevice_loopback"
            
            # Fallback to regular sounddevice
            return self.setup_sounddevice_stereo_mix()
            
        except Exception as e:
            print(f"WASAPI loopback setup failed: {e}")
            return self.setup_sounddevice_stereo_mix()
    
    def setup_sounddevice_stereo_mix(self):
        """Setup sounddevice with Stereo Mix"""
        try:
            devices = sd.query_devices()
            
            # Look for Stereo Mix or similar
            for i, device in enumerate(devices):
                device_name = device['name'].lower()
                
                if (device['max_input_channels'] > 0 and 
                    ('stereo mix' in device_name or 'what u hear' in device_name)):
                    
                    print(f"✅ Found Stereo Mix: {device['name']}")
                    self.stereo_mix_device = i
                    return "sounddevice_stereo_mix"
            
            print("⚠️ No Stereo Mix found, using default input")
            self.stereo_mix_device = None
            return "sounddevice_default"
            
        except Exception as e:
            print(f"Sounddevice setup failed: {e}")
            if PYAUDIO_AVAILABLE:
                return self.setup_pyaudio_stereo_mix()
            else:
                raise e
    
    def setup_pyaudio_stereo_mix(self):
        """Setup PyAudio with Stereo Mix"""
        try:
            self.audio = pyaudio.PyAudio()
            
            # Look for Stereo Mix device
            stereo_mix_index = None
            
            print("PyAudio devices:")
            for i in range(self.audio.get_device_count()):
                info = self.audio.get_device_info_by_index(i)
                device_name = info['name'].lower()
                
                print(f"  {i}: {info['name']} - Inputs: {info['maxInputChannels']}")
                
                if (info['maxInputChannels'] > 0 and 
                    ('stereo mix' in device_name or 'what u hear' in device_name)):
                    stereo_mix_index = i
                    print(f"  🎯 Found Stereo Mix at index {i}")
            
            if stereo_mix_index is not None:
                self.stereo_mix_device = stereo_mix_index
                return "pyaudio_stereo_mix"
            else:
                print("⚠️ No Stereo Mix found in PyAudio")
                self.stereo_mix_device = None
                return "pyaudio_default"
                
        except Exception as e:
            print(f"PyAudio setup failed: {e}")
            raise e
    
    def start_recording(self):
        """Start recording desktop audio"""
        if self.is_recording:
            return False, "Already recording!"
        
        try:
            self.audio_data = []
            self.is_recording = True
            
            print(f"🎙️ Starting desktop audio capture using: {self.capture_method}")
            
            if "sounddevice" in self.capture_method:
                self.recording_thread = threading.Thread(target=self._record_sounddevice)
            else:
                self.recording_thread = threading.Thread(target=self._record_pyaudio)
            
            self.recording_thread.daemon = True
            self.recording_thread.start()
            
            return True, "Desktop audio recording started"
            
        except Exception as e:
            self.is_recording = False
            return False, f"Error starting recording: {str(e)}"
    
    def _record_sounddevice(self):
        """Record using sounddevice"""
        try:
            def callback(indata, frames, time, status):
                if self.is_recording and status.input_overflow == False:
                    self.audio_data.append(indata.copy())
            
            # Choose device based on method
            if self.capture_method == "sounddevice_stereo_mix":
                device = getattr(self, 'stereo_mix_device', None)
            elif self.capture_method == "sounddevice_loopback":
                device = getattr(self, 'loopback_device', None)
            else:
                device = None
            
            print(f"📡 Recording from device: {device}")
            
            with sd.InputStream(
                samplerate=self.rate,
                channels=self.channels,
                device=device,
                callback=callback
            ):
                while self.is_recording:
                    time.sleep(0.1)
                    
        except Exception as e:
            print(f"Sounddevice recording error: {e}")
            self.is_recording = False
    
    def _record_pyaudio(self):
        """Record using PyAudio"""
        try:
            device_index = getattr(self, 'stereo_mix_device', None)
            
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=1024
            )
            
            print(f"📡 Recording from PyAudio device: {device_index}")
            
            while self.is_recording:
                try:
                    data = stream.read(1024, exception_on_overflow=False)
                    # Convert to numpy array
                    audio_np = np.frombuffer(data, dtype=np.int16)
                    if self.channels == 2:
                        audio_np = audio_np.reshape(-1, 2)
                    
                    # Convert to float32
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
        
        # Wait for recording thread
        if self.recording_thread:
            self.recording_thread.join(timeout=3)
        
        if not self.audio_data:
            return None, "No desktop audio captured. Check if Stereo Mix is enabled and Google Meet is playing audio."
        
        try:
            # Combine audio data
            audio_array = np.concatenate(self.audio_data, axis=0)
            
            # Check if we actually captured audio
            max_amplitude = np.max(np.abs(audio_array))
            if max_amplitude < 0.001:  # Very quiet
                return None, "Desktop audio too quiet. Make sure Google Meet is playing and volume is up."
            
            print(f"✅ Captured {len(audio_array) / self.rate:.2f} seconds of desktop audio")
            print(f"📊 Max amplitude: {max_amplitude:.4f}")
            
            return audio_array, "Desktop audio captured successfully"
            
        except Exception as e:
            return None, f"Error processing audio: {str(e)}"
    
    def save_audio(self, audio_array, filename):
        """Save audio to file"""
        try:
            if SOUNDDEVICE_AVAILABLE:
                import soundfile as sf
                sf.write(filename, audio_array, self.rate)
            else:
                # Use wave module
                with wave.open(filename, 'wb') as wf:
                    wf.setnchannels(self.channels)
                    wf.setsampwidth(2)
                    wf.setframerate(self.rate)
                    
                    # Convert to int16
                    audio_int16 = (audio_array * 32767).astype(np.int16)
                    wf.writeframes(audio_int16.tobytes())
            
            return True, f"Desktop audio saved to {filename}"
            
        except Exception as e:
            return False, f"Error saving audio: {str(e)}"
    
    def __del__(self):
        """Cleanup"""
        if self.is_recording:
            self.stop_recording()
        
        if hasattr(self, 'audio'):
            self.audio.terminate()

# Test function
def test_desktop_audio():
    """Test desktop audio capture"""
    print("🖥️ Testing Windows Desktop Audio Capture")
    print("=" * 50)
    print("📢 This will capture ONLY desktop audio (Google Meet participants)")
    print("🔇 Your microphone will NOT be recorded")
    print()
    
    try:
        capture = WindowsDesktopAudio()
        
        print("🎵 Play some audio (YouTube, music, etc.) and press Enter...")
        input()
        
        print("Starting 10-second desktop audio test...")
        success, message = capture.start_recording()
        
        if success:
            print(f"✅ {message}")
            
            for i in range(10, 0, -1):
                print(f"   Recording desktop audio... {i} seconds remaining")
                time.sleep(1)
            
            audio_data, stop_message = capture.stop_recording()
            print(f"✅ {stop_message}")
            
            if audio_data is not None:
                # Save test file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"desktop_audio_test_{timestamp}.wav"
                
                save_success, save_message = capture.save_audio(audio_data, filename)
                print(f"{'✅' if save_success else '❌'} {save_message}")
                
                if save_success:
                    print(f"\n🎉 Success! Desktop audio captured and saved.")
                    print(f"📁 File: {filename}")
                    print(f"⏱️ Duration: {len(audio_data) / capture.rate:.2f} seconds")
                    print(f"📊 Audio shape: {audio_data.shape}")
            else:
                print("❌ No desktop audio captured")
                print("💡 Try:")
                print("   1. Enable Stereo Mix in Windows Sound settings")
                print("   2. Make sure audio is playing from speakers")
                print("   3. Check Windows audio permissions")
        else:
            print(f"❌ {message}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_desktop_audio()