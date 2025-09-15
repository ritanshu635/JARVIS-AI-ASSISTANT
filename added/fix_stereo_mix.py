#!/usr/bin/env python3
"""
Fix Stereo Mix - Enable it manually and test
"""

import subprocess
import sys
import os

def open_sound_settings():
    """Open Windows Sound Control Panel directly"""
    print("🔧 Opening Windows Sound Control Panel...")
    
    try:
        # Open Sound Control Panel directly
        subprocess.run(["control", "mmsys.cpl"], check=True)
        print("✅ Sound Control Panel opened!")
        return True
    except Exception as e:
        print(f"❌ Failed to open Sound Control Panel: {e}")
        
        # Alternative method
        try:
            subprocess.run(["ms-settings:sound"], shell=True)
            print("✅ Sound Settings opened (alternative method)")
            return True
        except Exception as e2:
            print(f"❌ Alternative method also failed: {e2}")
            return False

def manual_stereo_mix_setup():
    """Guide user through manual Stereo Mix setup"""
    print("\n🎯 MANUAL STEREO MIX SETUP")
    print("=" * 40)
    
    print("Follow these steps EXACTLY:")
    print()
    
    print("1️⃣ OPEN SOUND CONTROL PANEL")
    open_choice = input("   Press Enter to open Sound Control Panel automatically, or 'n' to do it manually: ")
    
    if open_choice.lower() != 'n':
        open_sound_settings()
    else:
        print("   Manual method:")
        print("   - Right-click speaker icon in system tray")
        print("   - Click 'Open Sound settings'")
        print("   - Click 'Sound Control Panel'")
    
    print("\n2️⃣ ENABLE STEREO MIX")
    print("   - Go to 'Recording' tab")
    print("   - Right-click in empty space")
    print("   - Check ✅ 'Show Disabled Devices'")
    print("   - You should see 'Stereo Mix' appear")
    print("   - Right-click 'Stereo Mix'")
    print("   - Click 'Enable'")
    
    print("\n3️⃣ SET LEVELS (IMPORTANT!)")
    print("   - Right-click 'Stereo Mix'")
    print("   - Click 'Properties'")
    print("   - Go to 'Levels' tab")
    print("   - Set volume to 70-80%")
    print("   - Click 'OK'")
    
    print("\n4️⃣ TEST IT")
    print("   - Play some audio (YouTube, music)")
    print("   - You should see green bars moving next to 'Stereo Mix'")
    
    input("\n👆 Complete the steps above, then press Enter to continue...")

def test_stereo_mix_pyaudio():
    """Test Stereo Mix using PyAudio (more reliable than sounddevice)"""
    print("\n🧪 Testing Stereo Mix with PyAudio")
    print("=" * 35)
    
    try:
        import pyaudio
        import wave
        import numpy as np
        
        # Initialize PyAudio
        audio = pyaudio.PyAudio()
        
        # Find Stereo Mix device (index 19 from your system)
        stereo_mix_index = 19
        
        try:
            # Get device info
            device_info = audio.get_device_info_by_index(stereo_mix_index)
            print(f"📱 Device: {device_info['name']}")
            print(f"📊 Max input channels: {device_info['maxInputChannels']}")
            
            if device_info['maxInputChannels'] == 0:
                print("❌ Device has no input channels")
                return False
            
            print("🎵 Make sure some audio is playing (YouTube, music, etc.)")
            input("Press Enter when audio is playing...")
            
            # Try to open stream
            print("🎙️ Opening audio stream...")
            
            stream = audio.open(
                format=pyaudio.paInt16,
                channels=2,
                rate=44100,
                input=True,
                input_device_index=stereo_mix_index,
                frames_per_buffer=1024
            )
            
            print("✅ Stream opened successfully!")
            print("🔴 Recording 5 seconds...")
            
            frames = []
            for i in range(0, int(44100 / 1024 * 5)):  # 5 seconds
                data = stream.read(1024, exception_on_overflow=False)
                frames.append(data)
                
                if i % 10 == 0:  # Progress indicator
                    print(f"   Recording... {(i * 1024 / 44100):.1f}s")
            
            stream.stop_stream()
            stream.close()
            
            # Save the recording
            filename = "stereo_mix_test_pyaudio.wav"
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(2)
                wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
                wf.setframerate(44100)
                wf.writeframes(b''.join(frames))
            
            print(f"✅ Recording saved as: {filename}")
            
            # Analyze the audio
            audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
            max_amplitude = np.max(np.abs(audio_data))
            
            print(f"📊 Max amplitude: {max_amplitude}")
            
            if max_amplitude > 1000:  # Good signal for int16
                print("🎉 SUCCESS! Stereo Mix is working!")
                print("✅ You should be able to capture Google Meet audio now")
                return True
            else:
                print("⚠️ Very low audio signal")
                print("💡 Check Stereo Mix volume levels in Sound Control Panel")
                return False
                
        except Exception as stream_error:
            print(f"❌ Stream error: {stream_error}")
            
            if "Invalid device" in str(stream_error):
                print("💡 Stereo Mix is still disabled. Follow the setup steps again.")
            elif "Device unavailable" in str(stream_error):
                print("💡 Stereo Mix might be in use by another application.")
            
            return False
            
        finally:
            audio.terminate()
            
    except ImportError:
        print("❌ PyAudio not available")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main setup and test function"""
    print("🔊 Stereo Mix Fix Tool")
    print("=" * 30)
    print("This tool will help you enable Stereo Mix to capture")
    print("Google Meet audio for the meeting assistant.")
    print()
    
    # Step 1: Manual setup
    manual_stereo_mix_setup()
    
    # Step 2: Test it
    print("\n" + "=" * 50)
    success = test_stereo_mix_pyaudio()
    
    if success:
        print("\n🎉 STEREO MIX IS WORKING!")
        print("✅ You can now use the meeting assistant")
        print("🚀 Try: python final_jarvis.py")
        print("🗣️ Say: 'Jarvis attend the meeting for me'")
    else:
        print("\n❌ Stereo Mix still not working")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure you enabled Stereo Mix in Sound Control Panel")
        print("2. Check that Stereo Mix volume is not muted")
        print("3. Try setting Stereo Mix as default recording device")
        print("4. Restart your computer and try again")
        print("5. Some laptops don't support Stereo Mix - consider VB-Audio Cable")
    
    print("\n📋 Alternative Solution:")
    print("If Stereo Mix doesn't work, download VB-Audio Virtual Cable:")
    print("https://vb-audio.com/Cable/")

if __name__ == "__main__":
    main()