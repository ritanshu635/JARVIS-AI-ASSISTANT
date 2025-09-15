#!/usr/bin/env python3
"""
Windows Stereo Mix Enabler
Helps enable Stereo Mix for capturing desktop audio from Google Meet
"""

import subprocess
import sys
import os

def check_stereo_mix_status():
    """Check if Stereo Mix is available and enabled"""
    print("🔍 Checking Stereo Mix status...")
    
    try:
        # Try to list audio devices using PowerShell
        cmd = '''
        Get-WmiObject -Class Win32_SoundDevice | 
        Where-Object {$_.Name -like "*Stereo*" -or $_.Name -like "*Mix*"} | 
        Select-Object Name, Status
        '''
        
        result = subprocess.run(
            ["powershell", "-Command", cmd], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout.strip():
            print("✅ Stereo Mix device found in system")
            print(result.stdout)
            return True
        else:
            print("⚠️ Stereo Mix not found in WMI query")
            return False
            
    except Exception as e:
        print(f"❌ Error checking Stereo Mix: {e}")
        return False

def enable_stereo_mix_instructions():
    """Provide step-by-step instructions to enable Stereo Mix"""
    print("\n🔧 How to Enable Stereo Mix on Windows:")
    print("=" * 50)
    
    print("STEP 1: Open Sound Settings")
    print("   1. Right-click the speaker icon in system tray")
    print("   2. Click 'Open Sound settings'")
    print("   3. Click 'Sound Control Panel' on the right side")
    
    print("\nSTEP 2: Enable Stereo Mix")
    print("   1. Go to the 'Recording' tab")
    print("   2. Right-click in empty space")
    print("   3. Check 'Show Disabled Devices'")
    print("   4. You should see 'Stereo Mix' appear")
    print("   5. Right-click 'Stereo Mix' and select 'Enable'")
    
    print("\nSTEP 3: Set as Default (Optional)")
    print("   1. Right-click 'Stereo Mix'")
    print("   2. Select 'Set as Default Device'")
    print("   3. Click 'OK'")
    
    print("\n💡 Alternative: Use Virtual Audio Cable")
    print("   If Stereo Mix isn't available:")
    print("   1. Download VB-Audio Virtual Cable")
    print("   2. Install it")
    print("   3. Set CABLE Input as recording device")

def test_audio_capture_methods():
    """Test different audio capture methods"""
    print("\n🧪 Testing Audio Capture Methods")
    print("=" * 40)
    
    # Test 1: Check available devices with sounddevice
    try:
        import sounddevice as sd
        print("✅ sounddevice available")
        
        devices = sd.query_devices()
        stereo_mix_found = False
        
        print("\n📋 Available Recording Devices:")
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                device_name = device['name']
                is_stereo_mix = 'stereo mix' in device_name.lower()
                marker = " 🎯 STEREO MIX!" if is_stereo_mix else ""
                print(f"   {i}: {device_name}{marker}")
                
                if is_stereo_mix:
                    stereo_mix_found = True
        
        if stereo_mix_found:
            print("\n✅ Stereo Mix found and should work!")
        else:
            print("\n⚠️ Stereo Mix not found in available devices")
            
    except ImportError:
        print("❌ sounddevice not available")
    
    # Test 2: Check with PyAudio
    try:
        import pyaudio
        print("\n✅ pyaudio available")
        
        audio = pyaudio.PyAudio()
        stereo_mix_found = False
        
        print("\n📋 PyAudio Recording Devices:")
        for i in range(audio.get_device_count()):
            info = audio.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                device_name = info['name']
                is_stereo_mix = 'stereo mix' in device_name.lower()
                marker = " 🎯 STEREO MIX!" if is_stereo_mix else ""
                print(f"   {i}: {device_name}{marker}")
                
                if is_stereo_mix:
                    stereo_mix_found = True
        
        audio.terminate()
        
        if stereo_mix_found:
            print("\n✅ Stereo Mix found in PyAudio!")
        else:
            print("\n⚠️ Stereo Mix not found in PyAudio")
            
    except ImportError:
        print("❌ pyaudio not available")

def quick_stereo_mix_test():
    """Quick test to see if Stereo Mix is working"""
    print("\n🎵 Quick Stereo Mix Test")
    print("=" * 30)
    
    print("1. Play some audio (YouTube, music, etc.)")
    print("2. We'll try to record it using Stereo Mix")
    
    input("Press Enter when audio is playing...")
    
    try:
        import sounddevice as sd
        import numpy as np
        
        # Find Stereo Mix device
        devices = sd.query_devices()
        stereo_mix_device = None
        
        for i, device in enumerate(devices):
            if (device['max_input_channels'] > 0 and 
                'stereo mix' in device['name'].lower()):
                stereo_mix_device = i
                break
        
        if stereo_mix_device is None:
            print("❌ Stereo Mix device not found")
            return False
        
        print(f"🎙️ Recording 3 seconds from Stereo Mix...")
        
        # Record 3 seconds
        audio_data = sd.rec(
            int(3 * 44100), 
            samplerate=44100, 
            channels=2, 
            device=stereo_mix_device
        )
        sd.wait()
        
        # Check if we got audio
        max_amplitude = np.max(np.abs(audio_data))
        print(f"📊 Max amplitude: {max_amplitude:.4f}")
        
        if max_amplitude > 0.01:
            print("✅ SUCCESS! Stereo Mix is capturing audio!")
            
            # Save test file
            import soundfile as sf
            sf.write("stereo_mix_test.wav", audio_data, 44100)
            print("📁 Test saved as: stereo_mix_test.wav")
            return True
        else:
            print("❌ No audio captured. Stereo Mix might be disabled.")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main function to help user set up Stereo Mix"""
    print("🔊 Windows Stereo Mix Setup Helper")
    print("=" * 50)
    print("This tool helps you set up Stereo Mix to capture")
    print("desktop audio from Google Meet participants.")
    print()
    
    # Step 1: Check system
    check_stereo_mix_status()
    
    # Step 2: Test current setup
    test_audio_capture_methods()
    
    # Step 3: Provide instructions
    enable_stereo_mix_instructions()
    
    # Step 4: Quick test
    print("\n" + "=" * 50)
    test_choice = input("Want to test Stereo Mix now? (y/n): ").lower()
    
    if test_choice == 'y':
        success = quick_stereo_mix_test()
        
        if success:
            print("\n🎉 Great! Your Stereo Mix is working!")
            print("✅ You can now use the meeting assistant to capture Google Meet audio")
        else:
            print("\n❌ Stereo Mix test failed")
            print("💡 Follow the instructions above to enable Stereo Mix")
            print("💡 Or consider using VB-Audio Virtual Cable as alternative")
    
    print("\n📋 Next Steps:")
    print("1. Enable Stereo Mix using the instructions above")
    print("2. Test again with this script")
    print("3. Run: python test_meeting_assistant.py")
    print("4. Use: python final_jarvis.py")

if __name__ == "__main__":
    main()